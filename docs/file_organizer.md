# 📂 AI-Powered Local File Organizer

## Overview
The Megan File Organizer is an intelligent, privacy-first file taxonomy system. It monitors target directories (such as Downloads, Desktop, Documents) in real-time, categorizes incoming and existing files using extension-based deterministic rules, falls back to a local LLM for ambiguous or unknown extensions, avoids duplicates using SHA-256 hashing, and maintains an undoable JSON audit log.

---

## 🏗️ Core Subsystems

| Module | File | Purpose |
|---|---|---|
| **Rules Engine** | `organizer/rules.py` | Taxonomy mapping, file extensions, and blacklist definitions |
| **Classifier** | `organizer/classifier.py` | Two-tier classification: Fast deterministic match + Local LLM fallback |
| **Safe Mover** | `organizer/mover.py` | Conflict resolution, duplicate suppression via SHA-256, atomic moves |
| **Audit Log** | `organizer/audit.py` | JSON move history and multi-step undo engine |
| **Folder Watcher** | `organizer/watcher.py` | Real-time filesystem observer using `watchdog` with debounce |
| **API Endpoints** | `api/routes/organizer.py` | REST endpoints for dashboard control |

---

## 🗂️ Default Taxonomy

```
Organized/
├── Documents/       # pdf, docx, txt, epub, md, csv, xlsx
├── Images/          # png, jpg, jpeg, svg, gif, webp
├── Videos/          # mp4, mkv, avi, mov, flv
├── Audio/           # mp3, wav, flac, aac, m4a
├── Code/            # py, js, ts, html, css, json, yaml, c, cpp, rs
├── Archives/        # zip, tar, gz, 7z, rar
├── Installers/      # exe, msi, dmg, deb, rpm
└── Miscellaneous/   # Unknown/unclassified items
```

---

## 💻 CLI Usage

```bash
# Preview what would be organized without moving anything
python main.py --organize --dry-run

# Scan and organize files immediately
python main.py --organize

# Run continuous background watcher daemon
python main.py --watch
```

---

## 🌐 REST API Endpoints (`/api/organizer`)

| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/api/organizer/status` | Current watcher status and active folders |
| `POST` | `/api/organizer/scan` | Trigger a manual scan (`{"dry_run": true/false}`) |
| `POST` | `/api/organizer/start` | Start the real-time folder watcher |
| `POST` | `/api/organizer/stop` | Stop the folder watcher |
| `POST` | `/api/organizer/undo` | Undo recent file moves |
| `GET`  | `/api/organizer/audit` | Retrieve recent move audit history |
