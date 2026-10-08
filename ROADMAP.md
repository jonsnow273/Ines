# 🗺️ Megan Project Roadmap: Controllable Local AI

This document details development milestones, research objectives, and implementation phases for the Megan project.

---

## 🔬 Core Research Track: Activation Steering & Internal Control (Priority)
- [x] Theoretical formulation & contrastive extraction methodology (`docs/activation_steering.md`)
- [x] Side-by-side comparison benchmarks & evaluation protocol (`docs/experiments.md`)
- [ ] TransformerLens forward hook injection engine (`steering/hook_manager.py`)
- [ ] Automated steering vector extractor from contrastive prompt pairs (`steering/direction_finder.py`)
- [ ] Pre-calibrated vector registry (`cautious`, `concise`, `detailed`, `creative`, `neutral`)
- [ ] Side-by-side steered vs. unsteered evaluation API (`/api/steering/compare`)
- [ ] Interactive React Steering Dashboard with Recharts layer heatmaps & dynamic sliders

---

## 🎯 Phase 1: Foundation & High-Performance API Bridge
- [x] Architectural design prioritizing internal model interventions
- [x] Centralized configuration system (`configs/*.yaml` and `.env`)
- [x] FastAPI REST & WebSocket streaming architecture (`/ws/chat`, `/ws/voice`)
- [x] React 18 + Vite + Tailwind CSS dashboard scaffold
- [ ] Local quantized model loader (Mistral 7B / Gemma 2B via `bitsandbytes` 4-bit)
- [ ] High-throughput inference pipeline preserving internal tensor hook access

---

## 🛡️ Phase 2: Safe PC Automation Agent
- [x] Whitelist registry and parameter validation specification (`docs/automation_whitelist.md`)
- [ ] Intent classifier separating casual conversation from desktop automation commands
- [ ] Handlers implementation:
  - File/directory management with `send2trash` Recycle Bin protection
  - Application launcher & file search
  - Code synthesizer targeting VS Code
- [ ] Human-in-the-loop confirmation modal (UI + CLI) for destructive operations
- [ ] Operational caution steering integration (evaluating how `cautious` vectors reduce automation errors)

---

## 🎙️ Phase 3: Multilingual Voice Interaction
- [x] Microphone streaming & language configuration specs (`docs/voice_setup.md`, `docs/multilingual_support.md`)
- [ ] Background openWakeWord listener targeting "Hey Megan"
- [ ] Local OpenAI Whisper integration (`medium` / `large-v3`)
- [ ] Dynamic language routing across 6 primary languages
- [ ] Low-latency audio ingestion WebSocket

---

## 🎨 Phase 4: Integrated System Polishing & Evaluation
- [ ] Complete React dashboard integration uniting Chat, Steering Lab, and Automation Logs
- [ ] Empirical validation of steering stability across 50 benchmark test prompts
- [ ] Perplexity stability analysis (monitoring ΔPPL across steering magnitudes)
- [ ] Windows system tray daemon (`pystray`) for unobtrusive background monitoring
- [ ] End-to-end automated test suite and reproducibility report
