# 🔬 Megan: The First Local AI Assistant with Controllable Internal Behavior

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TransformerLens](https://img.shields.io/badge/Interpretability-TransformerLens-purple.svg)](https://github.com/TransformerLensOrg/TransformerLens)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Tailwind](https://img.shields.io/badge/Frontend-React%20%7C%20Tailwind-61DAFB.svg)](https://react.dev/)

> **"Can an AI assistant's observable behavior be systematically controlled by modifying internal model activations rather than engineering system prompts?"**

**Megan** is an experimental, privacy-first local AI assistant that explores controlling an LLM's observable behavior through **activation-level interventions** during the forward pass. While conventional assistants rely entirely on prompt engineering to tweak their tone and behavior, Megan demonstrates how the exact same model weights and the exact same user prompt can yield radically different behavioral characteristics—such as **concise**, **cautious**, **detailed**, or **creative** responses—by directly steering internal residual stream representations.

Alongside this mechanistic research core, Megan remains a fully functional, user-friendly personal desktop assistant featuring **local multilingual voice interaction**, **safe whitelisted PC automation**, **AI-powered file organization**, **on-device digital memory with OCR & vector search**, and a **modern React + Tailwind dashboard** — all running 100% locally with no cloud dependencies.

---

## 🔬 Activation Steering: Core Research Contribution

### The Core Innovation: Activation Steering vs. Prompt Engineering

Most modern AI assistants modify behavior by altering instructions in token space (e.g., adding *"You are a concise assistant"* to the prompt). While intuitive, prompt-based conditioning is fundamentally constrained: it consumes valuable context tokens, can be overridden by user prompt injections, and lacks continuous calibration.

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

## 🎛️ System Capabilities & Feature Hierarchy

### 1. 🔬 Activation Steering Lab (Primary Research Core)
- **Mechanistic Hooks**: Integrates **TransformerLens** to intercept and patch residual stream states (`hook_resid_post`) during inference.
- **Calibrated Behavioral Presets**: Built-in vectors for `cautious`, `concise`, `detailed`, `creative`, and `neutral`.
- **Side-by-Side Comparison Interface**: Test any prompt simultaneously across unsteered and steered paths.
- **Live Visual Telemetry**: Layer activation heatmaps and interactive strength sliders powered by Recharts.
- **Vector Math**: Extract new behavioral directions from contrastive prompt pairs using mean-difference and PCA pipelines.

### 2. 💬 Local Conversational Core
- 100% private, on-device text generation powered by open-weight models (**Mistral 7B Instruct** or **Gemma-2-2B**).
- 4-bit / 8-bit quantization support via `bitsandbytes` to run smoothly on consumer GPUs (4-8 GB VRAM) or CPU.
- Multi-turn conversation persistence with structured session logging.

### 3. 🛡️ Safe PC Automation Agent
- Translates natural language requests into structured, whitelisted desktop actions.
- **Strict Whitelist**: Can only execute safe actions listed in `configs/automation_whitelist.yaml`.
- **Mandatory Confirmation Gate**: Destructive actions (deleting files, overwriting directories) explicitly trigger a visual confirmation prompt before execution.
- **Recycle Bin Protection**: Employs `send2trash` to prevent irreversible file destruction.
- **Whitelisted Handlers**: File management, application launching, system search, audio playback, and VS Code code generation.

### 4. 🎙️ Multilingual Voice Interaction
- Low-overhead, always-on wake word engine: **"Hey Megan"** via local `openWakeWord`.
- High-accuracy local speech-to-text via **OpenAI Whisper** (`medium` or `large-v3`).
- Native language detection and support for **6 primary languages** (configurable in `configs/languages.yaml`).
- Transcribed speech streams directly into the same intent and steering pipeline as typed input.

### 5. 📂 AI-Powered File Organizer
- **Intelligent categorization** of files using extension-based rules with LLM fallback for ambiguous types.
- **Taxonomy-driven folder structure**: Documents, Images, Videos, Audio, Code, Archives, and more — auto-created under the user's target directory.
- **LLM-powered classification**: When a file can't be categorized by extension alone, the local LLM analyzes file metadata (name, size, type) to pick the best category.
- **Duplicate detection**: SHA-256 hashing prevents duplicate files from cluttering organized folders.
- **Real-time folder watcher**: Uses `watchdog` to monitor directories and auto-organize new files as they arrive.
- **Full audit trail**: Every move is logged to a JSON audit file with undo support — any organized file can be restored to its original location.
- **Dry-run mode**: Preview what the organizer would do without actually moving any files.
- **CLI integration**: `--organize`, `--dry-run`, and `--watch` flags for terminal usage.
- **REST API**: Endpoints at `/api/organizer/` for scan, start, stop, undo, and audit retrieval.

### 6. 🧠 Digital Memory *(Coming Soon)*
A privacy-first, on-device screen memory system that captures, indexes, and makes searchable everything the user sees on their screen.
- **Smart screenshot capture**: Background process captures the screen only when content **changes significantly** (pixel-diff threshold), avoiding redundant storage.
- **OCR text extraction**: Each screenshot is processed through **Tesseract OCR** (`pytesseract`) to extract searchable text — every word on your screen becomes searchable.
- **Optional image captioning**: A local vision-language model (e.g., LLaVA) generates short natural-language descriptions for screenshots with primarily visual content (diagrams, charts, UI).
- **Vector embedding & search**: Extracted text is embedded via **Sentence-Transformers** (`all-MiniLM-L6-v2`) and stored in a local **ChromaDB** vector database, enabling natural-language similarity search.
- **Privacy controls**: Configurable blacklist to exclude sensitive windows (incognito browsers, banking apps, password managers) from capture.
- **Auto-cleanup & retention**: Old screenshots are automatically purged after a configurable retention period (default 30 days) while OCR text and embeddings are retained indefinitely.
- **Storage-efficient**: Compressed JPEG capture (~50-100 KB each) with smart deduplication caps storage at approximately **~2 GB/month**.
- **100% local & free**: Tesseract, Sentence-Transformers, and ChromaDB are all open-source. No cloud APIs, no subscriptions, no data leaves the device.

### 7. 🔐 User Account System *(Coming Soon)*
- **Local authentication** with username + bcrypt-hashed password stored in SQLite.
- **Per-user data isolation**: Each user gets their own private memory silo, organizer settings, conversation history, and steering preferences.
- **Session persistence**: Close and reopen the app — log back in and all your data (Digital Memory, organized files, chat history) is exactly where you left it.
- **Multi-user support**: Multiple people sharing the same PC each get their own private, sandboxed workspace.

---

## 🏛️ System Architecture

```
                                  [ User Touchpoints ]
                    Voice ("Hey Megan")  │  Web Dashboard  │  CLI
                                           ▼
                                  ┌─── [ Auth Gate ] ───┐
                                  │  (Login / Session)   │
                                  └────────┬─────────────┘
                                           ▼
                                  [ FastAPI Gateway ]
                                           │
       ┌──────────────┬────────────────────┼────────────────────┬──────────────────┐
       ▼              ▼                    ▼                    ▼                  ▼
[ Intent          [ Activation       [ File Organizer ]  [ Digital Memory ]  [ Account
  Classifier ]      Steering Lab ]         │                    │              System ]
       │              │              ┌─────┴─────┐        ┌────┴─────┐          │
       ├─► Chat       │              ▼           ▼        ▼          ▼        users.db
       │              │         [ Rules +    [ Folder   [ Screen   [ Vector    (SQLite)
       └─► Automation │          LLM Classify] Watcher]  Capture ]  Store ]
              │       │              │           │        │          │
     [ Whitelist ]    │              ▼           │     [ OCR ]    [ ChromaDB ]
              │       │         [ Audit +   ◄────┘   (Tesseract)     ▲
     [ Confirm ]      │          Undo ]                   │          │
              │       │                              [ Embeddings ]──┘
     [ OS Handlers ]  │                         (Sentence-Transformers)
                      │
               [ TransformerLens ]
              x' = x + α · v_direction
                      │
               [ Local LLM ]
              (Mistral / Gemma)
```

---

## 🛠️ Technology & Model Stack

| Domain | Tool / Model | Rationale & Role |
|---|---|---|
| **Intervention Core** | **TransformerLens** | Standard library for mechanistic interpretability and forward hooks |
| **Primary LLM** | **Mistral 7B Instruct v0.3** | High-performance open-weight model with rich residual representation |
| **Lightweight LLM** | **Gemma-2-2B-IT** | Compact alternative optimal for low-VRAM machines (4 GB) |
| **Speech Recognition** | **OpenAI Whisper** | State-of-the-art local multilingual speech-to-text |
| **Wake Word Detection** | **openWakeWord** | Lightweight on-device ONNX wake word classifier |
| **Backend Gateway** | **FastAPI + WebSockets** | Asynchronous streaming API for tokens and real-time audio |
| **Frontend UI** | **React 18 + Vite + Tailwind** | Modern dark-themed dashboard with Recharts & Radix UI |
| **OS Automation** | **Custom Sandboxed Handlers** | Safe execution boundary with explicit whitelists and Recycle Bin guards |
| **File Organizer** | **watchdog + SHA-256** | Real-time folder monitoring with duplicate detection and LLM-based classification |
| **OCR Engine** | **Tesseract + pytesseract** | Open-source optical character recognition for screenshot text extraction |
| **Vector Embeddings** | **Sentence-Transformers** (`all-MiniLM-L6-v2`) | Lightweight local text embeddings for similarity search |
| **Vector Store** | **ChromaDB** | Persistent on-disk vector database for Digital Memory retrieval |
| **User Auth** | **SQLite + bcrypt** | Lightweight local user authentication with secure password hashing |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10 or 3.11
- **Node.js**: 18+ and `npm`
- **Memory**: 8 GB RAM minimum (16 GB recommended)
- **GPU (Optional)**: 6+ GB NVIDIA VRAM for optimal inference speeds (CPU mode supported)

### 1. Repository Setup
```bash
git clone https://github.com/your-org/megan.git
cd megan

# Setup Python virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate       # Linux/macOS

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
copy .env.example .env           # Windows
# cp .env.example .env           # Linux/macOS
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 3. Model Acquisition
```bash
python scripts/download_models.py
python scripts/setup_wake_word.py
```

### 4. Running the System
```bash
# Terminal 1: Launch FastAPI Backend Server
python -m uvicorn api.server:app --reload --port 8000

# Terminal 2: Launch React Frontend Dashboard
cd frontend
npm run dev
```
Navigate to **`http://localhost:5173`** to access both the conversational assistant and the Activation Steering Lab.

*(For terminal-only interaction, run `python main.py --cli`)*

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

## 🤝 Team Contribution & Research Collaboration

Megan is actively developed as a modular research project. We follow structured peer reviews and strict branch naming conventions. Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting pull requests.

---

## ⚖️ Scientific Rigor & Limitations
Megan is an experimental system. We explicitly acknowledge observed research limitations:
1. **Saturation Limits**: Steering values |α| > 2.8 can degrade grammar or trigger token repetition.
2. **Quantization Effects**: 4-bit quantization slightly degrades steering vector resolution relative to FP16.
3. **Task Generalization**: Vectors derived from conversational corpora may show reduced efficacy on specialized syntax tasks (e.g., deep code compilation).

See [`docs/experiments.md`](docs/experiments.md) for full evaluation metrics and failure mode analyses.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
