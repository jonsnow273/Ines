# 🏛️ Megan System Architecture

> **Architectural Philosophy**: Megan positions **internal activation steering at the cognitive center** of the local assistant. The OS automation, multilingual voice capture, and React interface are structured around a controllable, steerable inference core.

---

## 📐 End-to-End System Topology

```
+-------------------------------------------------------------------------------+
|                           User Touchpoints                                    |
|   [ Multilingual Voice / Mic ]      [ Modern React UI ]      [ Terminal CLI ]  |
+-------------------------------------------------------------------------------+
                 │                                │                      │
                 ▼                                ▼                      ▼
    [ openWakeWord & Whisper ]            [ HTTP / WebSockets ]    [ Rich Console ]
                 │                                │                      │
                 +────────────────────────────────┼──────────────────────+
                                                  │
                                                  ▼
+-------------------------------------------------------------------------------+
|                         FastAPI Application Layer                             |
|   - Streaming Token WebSocket (/ws/chat)                                      |
|   - Audio Ingestion WebSocket (/ws/voice)                                     |
|   - Steering Calibration & Comparison API (/api/steering/*)                   |
|   - Whitelisted Automation Dispatcher (/api/automation/*)                     |
+-------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+-------------------------------------------------------------------------------+
|                       MEGAN COGNITIVE ENGINE (Core)                         |
|                                                                               |
|   +───────────────────────────────────────────────────────────────────────+   |
|   |         Activation Steering Subsystem (TransformerLens)               |   |
|   |   - Calibrated Steering Vectors (cautious, concise, detailed, etc.)   |   |
|   |   - Dynamic Forward Hooks: h'(L) = h(L) + α * v_direction            |   |
|   |   - Real-Time Activation Extraction & Visual Telemetry                |   |
|   |   - Side-by-Side Steered vs. Unsteered Comparison Engine              |   |
|   +───────────────────────────────────────────────────────────────────────+   |
|                                         ▲                                     |
|                                         │ Intervenes during Forward Pass      |
|                                         ▼                                     |
|   +───────────────────────────────────────────────────────────────────────+   |
|   |          Local LLM Engine (Mistral 7B / Gemma 2B via FP16/4-Bit)       |   |
|   |   - Autoregressive Generation Pipeline                               |   |
|   |   - Multi-Turn Conversation Context & State Store                     |   |
|   +───────────────────────────────────────────────────────────────────────+   |
+-------------------------------------------------------------------------------+
                                                  │
                                                  ▼
                                      [ Intent Classification ]
                                     /                         \
                       +────────────+                           +────────────+
                       │                                                     │
               [ Casual Chat ]                                      [ System Action ]
                       │                                                     │
             (Steered Output to UI)                                 [ Whitelist Guard ]
                                                                             │
                                                                   [ Confirmation Gate ]
                                                                             │
                                                                   [ Sandboxed OS Handlers ]
                                                                   (Files / Apps / Search / Code)
```

---

## 🧩 Architectural Layers & Responsibilities

### 1. The Steering & Cognitive Core (`llm/`, `steering/`)
Unlike traditional wrappers that only see inputs and outputs, Megan taps directly into the model's forward execution pass:
- **`steering/hook_manager.py`**: Manages registration and clean detachment of PyTorch forward hooks using TransformerLens.
- **`steering/direction_finder.py`**: Calculates contrastive activation directions and PCA decomposition from calibrated reference sets.
- **`steering/steering_engine.py`**: Dynamically injects perturbations during generation based on user slider coefficients $\alpha$.
- **`llm/loader.py`**: Loads quantized local weights (Mistral 7B or Gemma 2B) while preserving internal tensor hook access.

### 2. The Application Gateway (`api/`)
- Asynchronous FastAPI server facilitating low-latency token streaming over WebSockets.
- Exposes dedicated endpoints for the **Steering Lab**:
  - `POST /api/steering/compare`: Runs identical prompts through unsteered and steered forward passes for immediate side-by-side evaluation.
  - `GET /api/steering/activations`: Streams real-time layer activation magnitudes to the frontend charts.

### 3. Safe PC Automation Agent (`automation/`)
- **Intent Classifier**: Parses natural language requests into structured actions.
- **Whitelist Boundary**: Enforces strict conformance with `configs/automation_whitelist.yaml`.
- **Confirmation Subsystem**: Halts destructive commands (deletion, overwriting) pending explicit human approval via the React modal or CLI confirmation.

### 4. Multilingual Voice Pipeline (`voice/`)
- Always-on background listener triggered by local `openWakeWord` ("Hey Megan").
- Speech-to-text powered by local OpenAI `whisper` with automatic language identification across 6 primary languages.

### 5. Reactive Frontend (`frontend/`)
- Built with **React 18**, **TypeScript**, and **Tailwind CSS**.
- Houses the **Behavioral Steering Lab** alongside the conversational interface, allowing users to visually manipulate internal vectors and inspect comparative response variations in real time.
