"""
Vector storage and semantic search engine for Ines Digital Memory.
Stores screenshot metadata and OCR text embeddings in ChromaDB per-user,
with a lightweight built-in fallback store when ML dependencies are not yet installed.
"""

import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from core import logger


class VectorMemoryStore:
    """Manages semantic vector indexing and similarity retrieval for Digital Memory."""

    def __init__(self, persist_dir: Path, collection_name: str = "screen_memories"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._has_chroma = False
        self._has_transformer = False
        self.collection = None
        self.embed_model = None

        # Fallback local store files
        self._fallback_file = self.persist_dir / "memories.json"
        self._fallback_memories: List[Dict[str, Any]] = self._load_fallback()

        self._init_backends()

    def _init_backends(self):
        """Attempt to load ChromaDB and SentenceTransformers with safe fallback."""
        try:
            import chromadb
            from chromadb.config import Settings
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.collection = client.get_or_create_collection(name=self.collection_name)
            self._has_chroma = True
            logger.info(f"ChromaDB persistent store initialized at {self.persist_dir}")
        except Exception as e:
            logger.debug(f"ChromaDB not initialized: {e}. Using lightweight fallback store.")
            self._has_chroma = False

        try:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            self._has_transformer = True
            logger.info("SentenceTransformer embedding model loaded.")
        except Exception as e:
            logger.debug(f"SentenceTransformer not loaded: {e}. Using keyword semantic search.")
            self._has_transformer = False

    def _load_fallback(self) -> List[Dict[str, Any]]:
        if self._fallback_file.exists():
            try:
                with open(self._fallback_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_fallback(self):
        try:
            with open(self._fallback_file, "w", encoding="utf-8") as f:
                json.dump(self._fallback_memories, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving fallback memories: {e}")

    def add_memory(
        self,
        memory_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> bool:
        """Add an indexed memory record with text and metadata."""
        # Sanitize metadata for ChromaDB (must only contain str, int, float, bool)
        clean_meta = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v)

        # 1. Add to ChromaDB if available
        if self._has_chroma:
            try:
                embeddings = None
                if self._has_transformer and text.strip():
                    embeddings = [self.embed_model.encode(text).tolist()]

                kwargs = {
                    "ids": [memory_id],
                    "metadatas": [clean_meta],
                    "documents": [text if text.strip() else "[Visual Snapshot]"],
                }
                if embeddings:
                    kwargs["embeddings"] = embeddings

                self.collection.upsert(**kwargs)
            except Exception as e:
                logger.error(f"Failed to upsert to ChromaDB: {e}")

        # 2. Always persist to fallback/backup JSON
        entry = {
            "id": memory_id,
            "text": text,
            "metadata": clean_meta,
            "timestamp": clean_meta.get("timestamp", datetime.now().isoformat()),
        }
        # Update if exists, else append
        self._fallback_memories = [m for m in self._fallback_memories if m["id"] != memory_id]
        self._fallback_memories.append(entry)
        self._save_fallback()

        return True

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic similarity search across memories.
        Returns sorted list of matches: [{"id", "text", "metadata", "score"}].
        """
        query_clean = query.strip()
        if not query_clean:
            return []

        # Use ChromaDB if active
        if self._has_chroma:
            try:
                kwargs = {
                    "n_results": min(top_k, max(1, self.count())),
                }
                if self._has_transformer:
                    q_embed = self.embed_model.encode(query_clean).tolist()
                    kwargs["query_embeddings"] = [q_embed]
                else:
                    kwargs["query_texts"] = [query_clean]

                results = self.collection.query(**kwargs)
                out = []
                if results and "ids" in results and results["ids"]:
                    for i in range(len(results["ids"][0])):
                        mid = results["ids"][0][i]
                        doc = results["documents"][0][i] if "documents" in results else ""
                        meta = results["metadatas"][0][i] if "metadatas" in results else {}
                        dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                        score = round(max(0.0, 1.0 - (dist / 2.0)), 4)

                        out.append({
                            "id": mid,
                            "text": doc,
                            "metadata": meta,
                            "score": score,
                        })
                return out
            except Exception as e:
                logger.debug(f"ChromaDB query error, falling back: {e}")

        # Fallback keyword and token-overlap search
        tokens = set(re.findall(r"\w+", query_clean.lower()))
        scored = []
        for m in self._fallback_memories:
            doc_lower = (m.get("text", "") + " " + m.get("metadata", {}).get("window_title", "")).lower()
            doc_tokens = set(re.findall(r"\w+", doc_lower))
            overlap = len(tokens.intersection(doc_tokens))
            if overlap > 0 or query_clean.lower() in doc_lower:
                score = (overlap / max(1, len(tokens))) * 0.9
                if query_clean.lower() in doc_lower:
                    score += 0.1
                scored.append({
                    "id": m["id"],
                    "text": m.get("text", ""),
                    "metadata": m.get("metadata", {}),
                    "score": round(min(1.0, score), 4),
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        """Total number of indexed memories."""
        if self._has_chroma:
            try:
                return self.collection.count()
            except Exception:
                pass
        return len(self._fallback_memories)

    def prune_older_than(self, days: int) -> int:
        """Remove memory records and file references older than X days."""
        cutoff = datetime.now() - timedelta(days=days)
        removed_count = 0
        retained = []

        for m in self._fallback_memories:
            ts_str = m.get("timestamp") or m.get("metadata", {}).get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts < cutoff:
                    removed_count += 1
                    # Remove screenshot file if present
                    shot_path = m.get("metadata", {}).get("screenshot_path")
                    if shot_path:
                        p = Path(shot_path)
                        if p.exists():
                            p.unlink(missing_ok=True)
                    continue
            except Exception:
                pass
            retained.append(m)

        self._fallback_memories = retained
        self._save_fallback()
        return removed_count
