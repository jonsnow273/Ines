# 🔬 Megan: The First Local AI Assistant with Controllable Internal Behavior

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TransformerLens](https://img.shields.io/badge/Interpretability-TransformerLens-purple.svg)](https://github.com/TransformerLensOrg/TransformerLens)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Tailwind](https://img.shields.io/badge/Frontend-React%20%7C%20Tailwind-61DAFB.svg)](https://react.dev/)

> **"Can an AI assistant's observable behavior be systematically controlled by modifying internal model activations rather than engineering system prompts?"**

**Megan** is an experimental, privacy-first local AI desktop assistant. Unlike conventional AI assistants that rely solely on surface-level prompt engineering (*"You are a concise assistant"*), Megan demonstrates how the exact same model weights and the exact same user prompt can yield fundamentally distinct behavioral traits—such as **concise**, **cautious**, **detailed**, or **creative** responses—by directly steering internal residual stream representations during the forward pass.

Alongside this mechanistic interpretability research core, Megan features an integrated **Smart Workspace Suite**:
- **🛡️ Safe Desktop Automation** (Sandboxed whitelist execution with confirmation gates & Recycle Bin protection)
- **📂 AI-Powered File Organizer** (Deterministic rules + LLM fallback + SHA-256 deduplication + audit log with undo)
- **🧠 Digital Screen Memory** (Smart change-detected screen capture + Tesseract OCR + ChromaDB semantic search)
- **🎯 Focus & Anti-Distraction Coach** (Active window tracking + distraction alerts + workspace auto-restoration)
- **🕒 Visual Time Machine Slider** (Interactive timeline scrubber across past screen history)
- **📊 Automated Daily Standup Reports** (Automatic synthesis of git commits, focus hours, and screen topics)
- **⚡ Autonomous Workflow Macro Recorder** (Natural-language routine recording & safe replay)
- **🔐 Multi-User Account Isolation** (Cryptographic PBKDF2-HMAC-SHA256 authentication with isolated workspaces)

---

## 🔬 Activation Steering: Core Research Contribution

### The Core Innovation: Activation Steering vs. Prompt Engineering

Most modern AI assistants modify behavior by altering instructions in token space. While intuitive, prompt-based conditioning is fundamentally constrained: it consumes valuable context tokens, can be bypassed by prompt injections, and lacks continuous calibration.

Megan intervenes at the **representation level**:

```
Traditional Prompt Approach:
  [ User Prompt ] + [ Long Behavioral System Prompt ] ──► [ Standard Forward Pass ] ──► Output

Megan Activation Steering:
  [ User Prompt ] ──────────────────────────────────────► [ Transformer Layers ]
                                                                   │
                                                      Layer L: x' = x + α · v_direction
                                                                   │
                                                                   ▼
                                                          [ Steered Generation ]
```

### Why Activation-Level Intervention Matters:
- **Zero Token Overhead**: Leaves the full context window available for conversation and document context.
- **Continuous Quantitative Control**: Instead of binary prompt requests, behavior intensity is modulated continuously via a scalar multiplier $\alpha \in [-3.0, +3.0]$.
- **Prompt-Injection Resilience**: Because behavioral constraints reside in internal activation geometry rather than token prompts, user inputs cannot trivially bypass them.
- **Mechanistic Explainability**: Provides real-time visibility into internal layer activations and vector projections rather than treating the LLM as an unobservable black box.

---

## 📊 Side-by-Side Observable Behavior

Using the built-in **Steering Comparison Lab**, users and researchers can run identical prompts through baseline and steered conditions to observe immediate behavioral shifts:

| Prompt | Unsteered Baseline (α = 0) | Steered Output | Active Preset & Impact |
|---|---|---|---|
| *"Explain TCP vs. UDP"* | "TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) are two foundational communication protocols used in computer networking. TCP is connection-oriented..." *(134 words)* | "TCP guarantees ordered, error-checked delivery via handshakes. UDP transmits connectionless datagrams with minimal latency, accepting packet loss." *(19 words)* | **`concise` (α = +1.8)**<br>*-85% length reduction, zero conversational preamble* |
| *"Delete the old project build folder."* | "I'll go ahead and remove the folder old_build from your workspace directory." | "CAUTION: Deleting `old_build` will erase all compile outputs. Ensure no dependent processes require these assets. Confirmation required: [Approve / Cancel]." | **`cautious` (α = +2.0)**<br>*Elevates risk awareness and surfaces safety boundaries* |
| *"Brainstorm a name for an asynchronous task queue."* | "Here are some good names for an asynchronous task queue: TaskFlow, AsyncQueue, JobRunner, WorkQueue." | "Consider metaphors of celestial momentum and river flow: *ChronoTide*, *AetherRelay*, *VortexDispatch*, *PulseWeave*." | **`creative` (α = +1.5)**<br>*Expands associative diversity without temperature noise* |

---

## 🎛️ Complete System Capabilities & Features

### 1. 🔬 Activation Steering Lab (Primary Research Core)
- **Mechanistic Hooks**: Integrates **TransformerLens** to intercept and patch residual stream states (`hook_resid_post`) during inference.
- **Calibrated Behavioral Presets**: Built-in vectors for `cautious`, `concise`, `detailed`, `creative`, and `neutral`.
- **Side-by-Side Comparison Interface**: Test any prompt simultaneously across unsteered and steered paths.
- **Live Visual Telemetry**: Layer activation heatmaps and interactive strength sliders powered by Recharts.
- **Vector Math**: Extract new behavioral directions from contrastive prompt pairs using mean-difference and PCA pipelines.

### 2. 💬 Local Conversational Core
- 100% private, on-device text generation powered by open-weight models (**Mistral 7B Instruct**, **Gemma-2-2B**, or lightweight **Qwen2.5-0.5B**).
- 4-bit / 8-bit quantization support via `bitsandbytes` to run smoothly on consumer GPUs (4-8 GB VRAM) or CPU fallback.
- Multi-turn conversation persistence with structured session logging.

### 3. 🛡️ Safe PC Automation Agent
- Translates natural language requests into structured, whitelisted desktop actions.
- **Strict Whitelist**: Can only execute safe actions listed in `configs/automation_whitelist.yaml`.
- **Mandatory Confirmation Gate**: Destructive actions explicitly trigger a visual confirmation modal before execution.
- **Recycle Bin Protection**: Employs `send2trash` to prevent irreversible file destruction.
- **Whitelisted Handlers**: File management, application launching, system search, audio playback, and VS Code code generation.

### 4. 🎙️ Multilingual Voice Interaction
- Low-overhead, always-on wake word engine: **"Hey Megan"** via local `openWakeWord`.
- High-accuracy local speech-to-text via **OpenAI Whisper** (`medium` or `large-v3`).
- Native language detection and support for **6 primary languages** (configurable in `configs/languages.yaml`).
- Transcribed speech streams directly into the same intent and steering pipeline as typed input.

### 5. 📂 AI-Powered File Organizer
- **Intelligent categorization**: Taxonomy-driven classification (Documents, Images, Videos, Audio, Code, Archives, Installers).
- **Two-tier sorting**: Instant extension matching with local LLM fallback for ambiguous or unknown files.
- **Duplicate suppression**: SHA-256 content hashing prevents redundant duplicates from cluttering folders.
- **Real-time folder watcher**: Uses `watchdog` to monitor target folders (Downloads, Desktop) and auto-organize incoming files.
- **Audit trail & Safe Undo**: Complete JSON history of all operations with instant one-click restoration.
- **CLI & REST API**: `--organize`, `--dry-run`, and `/api/organizer/*` endpoints.

### 6. 🧠 Digital Screen Memory (Visual Semantic Recall)
- **Smart Change-Detection Capture**: Captures screen snapshots periodically, using a perceptual pixel-diff threshold (>5%) to discard idle or static screens—saving up to 90% disk space.
- **Automated Privacy Blacklist**: Foreground process and window title inspection instantly drops private chat apps (WhatsApp, Telegram, Discord, Signal) and sensitive windows (banking, incognito, password managers) directly in RAM.
- **Tesseract OCR Extraction**: Reads all visible text from captured screens (terminal outputs, code snippets, documentation, slides).
- **ChromaDB Vector Retrieval**: Embeds text using Sentence-Transformers (`all-MiniLM-L6-v2`) for natural language semantic search (*"What was that Docker command I ran yesterday?"*).
- **Auto-Retention Policy**: Prunes raw JPEG images after 30 days while retaining searchable OCR text and embeddings indefinitely.

### 7. 🎯 Focus & Anti-Distraction Autonomous Coach
- **Active Window Tracking**: Monitors active foreground applications and categorized URLs during active focus sessions.
- **Distraction Nudge**: If the user wanders into entertainment or messaging apps for over 2 minutes, Megan fires a friendly notification.
- **One-Click Workspace Restoration**: With user confirmation, Megan automatically minimizes distracting windows and restores the target IDE or terminal.
- **Focus Analytics**: Generates productive vs. distracted duration metrics viewable in the React dashboard.

### 8. 🕒 Visual Time Machine Slider
- **Interactive Temporal Scrubber**: A horizontal timeline slider in the dashboard allowing the user to scrub back to any point in their workday.
- **Snapshot Filmstrip**: Displays the exact visual screen frame captured at that minute alongside active window metadata.
- **One-Click OCR Copy**: Click any text block inside a past screen snapshot to copy terminal logs or code directly to the clipboard.

### 9. 📊 Automated Daily Standup & Activity Report Generator
- **Multi-Source Synthesis**: Combines active focus hours, Git commits made today, and Digital Memory screen topics.
- **LLM Standup Drafts**: Generates concise, professional Markdown/PDF reports detailing deep work hours, key accomplishments, and modified files.

### 10. ⚡ Autonomous Workflow Macro Recorder
- **Conversational Macro Recording**: Record repetitive multi-step desktop sequences (*"Record Macro: 'Setup Dev Environment'"*).
- **Safe Replay**: Stores recipes as structured JSON steps and replays them on command via Megan's whitelisted OS automation.

### 11. 🔐 User Account System & Data Isolation
- **Cryptographic Local Auth**: PBKDF2-HMAC-SHA256 password hashing (100k rounds + salt) and URL-safe signed HMAC-SHA256 session tokens.
- **Isolated Workspaces**: Each registered user account gets a private silo (`data/users/<username>/`) containing separate memory, organizer settings, and chat history.
- **Session Persistence & Multi-User Support**: Multiple users sharing a single machine maintain independent databases and privacy boundaries.

---

## 🏛️ System Architecture

```
                                      [ User Touchpoints ]
                    Voice ("Hey Megan")  │  Web Dashboard (React)  │  Terminal CLI
                                                ▼
                                      ┌─── [ Auth Gate ] ───┐
                                      │  (Login / Session)   │
                                      └─────────┬───────────┘
                                                ▼
                                      [ FastAPI Gateway ]
                                                │
       ┌──────────────┬────────────────────┬────┴───────────────┬────────────────────┬──────────────────┐
       ▼              ▼                    ▼                    ▼                    ▼                  ▼
[ Intent          [ Activation       [ File Organizer ]  [ Digital Memory ]   [ Focus & Macro   [ User Account
  Classifier ]      Steering Lab ]         │                    │               Engine ]          System ]
       │              │              ┌─────┴─────┐        ┌────┴─────┐          │                  │
       ├─► Chat       │              ▼           ▼        ▼          ▼     [ Focus Tracker ]    users.db
       │              │         [ Rules +    [ Folder   [ Screen   [ Vector     │               (SQLite)
       └─► Automation │          LLM Classify] Watcher]  Capture ]  Store ]   [ Macro Replay ]     │
              │       │              │           │        │          │          │           data/users/
     [ Whitelist ]    │              ▼           │     [ OCR ]    [ ChromaDB ]  │           <username>/
              │       │         [ Audit +   ◄────┘   (Tesseract)     ▲          ▼               │
     [ Confirm ]      │          Undo ]                   │          │    [ OS Handlers ]  {memory, reports,
              │       │                              [ Embeddings ]──┘          ▲           settings}
     [ OS Handlers ]  │                         (Sentence-Transformers)         │
                      │                                                         │
               [ TransformerLens ] ─────────────────────────────────────────────┘
              x' = x + α · v_direction
                      │
               [ Local LLM Core ]
           (Mistral / Gemma / Qwen)
```

---

## 🛠️ Technology & Model Stack

| Domain | Tool / Library | Role & Rationale |
|---|---|---|
| **Intervention Core** | **TransformerLens** | Standard library for mechanistic interpretability and forward residual stream hooks |
| **Language Models** | **Mistral 7B / Gemma 2B / Qwen 0.5B** | Open-weight instruction models with quantization support (FP16 / 4-bit) |
| **Speech Recognition** | **OpenAI Whisper** | Local multilingual speech-to-text with automatic language detection |
| **Wake Word Detection** | **openWakeWord** | Ultra-lightweight on-device ONNX wake word engine ("Hey Megan") |
| **Backend Gateway** | **FastAPI + WebSockets** | High-performance asynchronous REST and streaming token WebSocket server |
| **Frontend UI** | **React 18 + Vite + Tailwind** | Modern dark-themed dashboard with Recharts, Radix UI, and Lucide icons |
| **Desktop Automation** | **Custom Sandboxed Handlers** | Safe execution boundary with explicit whitelists and `send2trash` Recycle Bin guards |
| **File Taxonomy** | **watchdog + SHA-256** | Real-time filesystem observer with duplicate suppression and undoable JSON audit |
| **Screen OCR** | **Tesseract + pytesseract** | Optical character recognition discovering on-screen code, logs, and text |
| **Semantic Vectors** | **Sentence-Transformers + ChromaDB** | 384-dimensional dense embeddings (`all-MiniLM-L6-v2`) with persistent vector storage |
| **Process Tracking** | **psutil + Windows WinAPI** | Zero-overhead foreground window title and active process monitoring |
| **Authentication** | **SQLite + PBKDF2-HMAC-SHA256** | Local cryptographic user authentication with sandboxed per-user storage silos |

---

## 📂 Repository Structure

```
MeganAI/
├── api/                     # FastAPI backend
│   ├── middleware/          # CORS & global error handlers
│   ├── routes/              # REST endpoints (auth, chat, steering, organizer, memory, automation)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── websocket/           # Streaming chat and audio WebSocket endpoints
│   └── server.py            # Application factory and startup orchestration
├── auth/                    # Cryptographic authentication & user workspace isolation
│   ├── database.py          # SQLite database connection & per-user directory initialization
│   ├── middleware.py        # FastAPI Bearer token dependencies (get_current_user, require_auth)
│   ├── models.py            # User validation models
│   └── service.py           # PBKDF2 hashing, signed session tokens, user management
├── automation/              # Safe PC automation subsystem
│   ├── action_handler.py    # Whitelisted OS execution engine
│   ├── confirmation.py      # User confirmation gatekeeper
│   └── whitelist.py         # Whitelist schema & validator
├── chatbot/                 # Multi-turn conversation management
│   ├── context_manager.py   # Context token trimming & sliding window
│   ├── history.py           # Session conversation history tracking
│   └── language_manager.py  # Multilingual system prompt injection
├── configs/                 # Declarative YAML configurations
│   ├── automation_whitelist.yaml # Whitelisted executable operations
│   ├── languages.yaml       # Supported multilingual definitions
│   ├── megan_settings.yaml  # Global runtime settings
│   ├── memory_privacy.yaml  # Blacklisted processes and window keywords
│   └── model_config.yaml    # Model paths, devices, and quantization parameters
├── core/                    # Application foundation
│   ├── config.py            # Settings loader
│   ├── constants.py         # Global directory constants & paths
│   └── logger.py            # Structured logging
├── data/                    # Local runtime storage (git-ignored)
│   ├── users/               # Per-user isolated storage silos
│   │   └── <username>/      # {memory, organizer, reports, conversations, settings}
│   ├── users.db             # Local user accounts database
│   └── memory/              # Global memory fallback directory
├── docs/                    # In-depth architectural & setup guides
├── frontend/                # React 18 + Vite + Tailwind CSS dashboard
│   ├── src/components/      # UI components (Chat, Steering, Layout, Modals)
│   └── package.json         # Frontend dependencies
├── llm/                     # Local model inference pipeline
│   ├── loader.py            # HuggingFace model & tokenizer loading with quantization
│   ├── inference.py         # Generation engine with parameter tuning
│   └── tokenizer_wrapper.py # Unified tokenization interface
├── memory/                  # Digital Screen Memory subsystem
│   ├── capture.py           # Smart change-detected screen capture & JPEG compression
│   ├── privacy.py           # Foreground window & process blacklist inspector
│   ├── ocr.py               # Tesseract OCR wrapper & text cleaner
│   ├── store.py             # ChromaDB vector store & retention pruner
│   └── service.py           # Background memory daemon & semantic search coordinator
├── organizer/               # AI-powered file organizer subsystem
│   ├── audit.py             # JSON move audit trail with multi-step undo
│   ├── classifier.py        # Two-tier classifier (deterministic rules + LLM fallback)
│   ├── mover.py             # Safe mover with SHA-256 duplicate suppression
│   ├── rules.py             # Taxonomy mappings and extension blacklists
│   └── watcher.py           # Real-time watchdog directory observer
├── steering/                # Mechanistic activation steering subsystem
│   ├── hook_manager.py      # TransformerLens residual stream hook manager
│   ├── presets.py           # Calibrated steering vectors (cautious, concise, creative)
│   └── steering_engine.py   # Steering calibration and comparison engine
├── voice/                   # Speech recognition & wake word pipeline
│   ├── pipeline.py          # Real-time microphone audio processing
│   ├── recorder.py          # Audio buffer manager
│   └── transcriber.py       # OpenAI Whisper wrapper
├── main.py                  # Main terminal CLI entry point
├── test_auth.py             # Authentication unit test suite
├── test_memory.py           # Digital Memory unit test suite
└── requirements.txt         # Production dependencies
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10 or 3.11
- **Node.js**: 18+ and `npm`
- **Memory**: 8 GB RAM minimum (16 GB recommended)
- **Tesseract OCR (Optional)**: [Tesseract installer for Windows](https://github.com/UB-Mannheim/tesseract/wiki) for screen text extraction.

### 1. Setup Environment
```bash
git clone https://github.com/jonsnow273/MeganAI.git
cd MeganAI

# Setup Python virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate       # Linux/macOS

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
copy .env.example .env           # Windows
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 3. Running the System
```bash
# Terminal 1: Launch FastAPI Backend Server
python -m uvicorn api.server:app --reload --port 8000

# Terminal 2: Launch React Frontend Dashboard
cd frontend
npm run dev
```
Navigate to **`http://localhost:5173`** to access the Megan dashboard.

---

## 💻 CLI Commands Quick Reference

```bash
# View active system info & steering configuration
python main.py --info

# Register a new local user account
python main.py --register

# List registered local accounts
python main.py --list-users

# File Organizer: preview simulation without moving files
python main.py --organize --dry-run

# File Organizer: execute organization immediately
python main.py --organize

# File Organizer: start background folder observer daemon
python main.py --watch

# Digital Memory: capture active screen immediately
python main.py --memory-capture

# Digital Memory: search indexed screen history via query
python main.py --memory-search "FastAPI deployment"

# Digital Memory: start background capture worker
python main.py --memory-start

# Interactive Chat with custom steering preset
python main.py --steer cautious --strength 2.0
```

---

## 🧪 Testing & Validation

The codebase includes comprehensive unit test suites ensuring stability and security:

```bash
# Run User Authentication & Data Isolation Tests
python test_auth.py

# Run Digital Memory & Privacy Guard Tests
python test_memory.py
```

---

## 📖 In-Depth Documentation

- [🔬 Activation Steering Research & Mechanics](docs/activation_steering.md)
- [📊 Experimental Benchmarks & Evaluation Protocols](docs/experiments.md)
- [🏛️ System Architecture Deep Dive](docs/architecture.md)
- [🛡️ PC Automation Whitelist & Safety Specifications](docs/automation_whitelist.md)
- [🎙️ Voice & Wake Word Configuration](docs/voice_setup.md)
- [🌍 Multilingual Configuration](docs/multilingual_support.md)
- [📂 AI File Organizer Guide](docs/file_organizer.md)
- [🧠 Digital Memory Setup & Usage](docs/digital_memory.md)
- [🔐 Account System & Multi-User Guide](docs/account_system.md)
- [🤝 Contribution Guide & PR Workflow](CONTRIBUTING.md)
- [🗺️ Project Roadmap](ROADMAP.md)
- [🔒 Security Policy](SECURITY.md)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
