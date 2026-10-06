# 🧠 Ines Digital Memory

## Overview
Ines Digital Memory is a privacy-first, on-device visual memory engine. It periodically snapshots what the user sees on their screen, extracts text via Tesseract OCR, indexes the visual semantics into ChromaDB using dense vector embeddings, and allows natural-language recall ("Where did I see that receipt?", "What was that terminal command?").

All captures and embeddings are processed 100% locally on the device with zero cloud dependencies.

---

## 🏗️ Architecture & Pipeline

```
[ Screen ] 
    │
    ▼
[ 1. Privacy Filter ] ──► Matches process/title against blacklist? ──► [ Skip & Drop ]
    │ (Safe)
    ▼
[ 2. Smart Diff Check ] ──► Pixel change < 5%? ──► [ Skip & Drop ]
    │ (Changed)
    ▼
[ 3. Downscale & Compress ] ──► Max 1280px width, JPEG Quality 75 (~60 KB)
    │
    ▼
[ 4. Tesseract OCR ] ──► Extracts visible text, lines, words
    │
    ▼
[ 5. Vector Store ] ──► Sentence-Transformers (all-MiniLM-L6-v2) ──► ChromaDB
    │
    ▼
[ 6. Natural Language Search ] ──► Cosine similarity search over past sessions
```

---

## 🛡️ Privacy & Blacklist Rules (`configs/memory_privacy.yaml`)

Digital Memory incorporates strict foreground window and process detection:

- **Personal Chat Applications**: `WhatsApp`, `Telegram`, `Signal`, `Discord`, `Slack`, `Skype` are automatically blocked whenever focused.
- **Sensitive Windows**: Windows containing titles like `Incognito`, `InPrivate`, `Bitwarden`, `1Password`, `Bank`, `Checkout`, `Credit Card` are dropped immediately in RAM and never written to disk.
- **Master Switch & Temporary Pause**: Memory capture is off by default and can be paused with one click or API call (`POST /api/memory/pause`).

---

## 📂 Per-User Workspace Storage Layout

```
data/
└── users/
    └── <username>/
        └── memory/
            ├── screenshots/           # Lightweight compressed JPEGs (~50-80 KB each)
            │   ├── screen_20261006_120001.jpg
            │   └── screen_20261006_120530.jpg
            ├── vector_store/          # ChromaDB on-disk embeddings
            └── memories.json          # Fallback metadata index
```

### Auto-Retention Policy
- **Screenshots (Images)**: Automatically pruned after 30 days (configurable in `memory_privacy.yaml`).
- **OCR Text & Embeddings**: Kept permanently (taking up <20 MB per month). You can always search past work history even after raw images are cleaned up.

---

## 💻 CLI Commands

```bash
# Capture the current screen immediately and index it
python main.py --memory-capture

# Search digital memory via natural language query
python main.py --memory-search "docker run postgres"

# Run background memory capture daemon
python main.py --memory-start
```

---

## 🌐 REST API Endpoints (`/api/memory`)

| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/api/memory/status` | Current worker state, total captures, skips, and telemetry |
| `POST` | `/api/memory/start` | Start the background screen capture daemon |
| `POST` | `/api/memory/stop` | Stop the background screen capture daemon |
| `POST` | `/api/memory/pause` | Pause recording for `X` minutes (`{"minutes": 15}`) |
| `POST` | `/api/memory/resume` | Resume memory capture |
| `POST` | `/api/memory/capture-now` | Force an immediate single screen capture |
| `GET`  | `/api/memory/search?q=...&limit=5` | Semantic vector search across past screen history |
| `GET`  | `/api/memory/screenshot/{filename}` | Retrieve the JPEG image of a specific screenshot |
| `GET`  | `/api/memory/privacy` | View active blacklist and privacy configuration |
