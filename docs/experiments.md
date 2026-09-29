# 📊 Experimental Benchmarks & Evaluation Protocols

This document specifies the experimental setup, benchmark datasets, evaluation protocols, and ablation findings used to validate activation steering in Ines.

---

## 1. Experimental Setup

- **Primary Model**: `mistralai/Mistral-7B-Instruct-v0.3` (Loaded in FP16 or 4-bit NF4)
- **Secondary / Lightweight Model**: `google/gemma-2-2b-it`
- **Framework**: `TransformerLens` (Mechanistic interpretability hooks on `hook_resid_post`)
- **Sampling Parameters**: Temperature = 0.0 (greedy decoding for reproducible evaluation) and Temperature = 0.7 (for diversity evaluation).
- **Steering Multiplier Range**: α ∈ [-3.0, +3.0] with step size 0.2.

---

## 2. Benchmark Evaluation Protocol

Each behavioral vector is evaluated across 50 standardized prompts split into three categories:
1. **Desktop / OS Automation Prompts**: File operations, application management, process queries.
2. **Technical & Explanatory Prompts**: Concepts, algorithms, architectural tradeoffs.
3. **Conversational / Chit-Chat Prompts**: Open-ended questions, greetings, advice.

### Quantitative Results (Averaged over 50 test prompts)

| Behavior Vector | Target Layer | Optimal α | Avg Token Count (Steered vs Base) | Target Trait Alignment (%) | Perplexity Increase (ΔPPL) |
|---|---|---|---|---|---|
| **Baseline (Unsteered)** | N/A | 0.0 | 124 tokens | Baseline (50%) | 0.0 |
| **`concise`** | Layer 19 | +1.8 | **42 tokens (-66%)** | 92% | +0.84 |
| **`detailed`** | Layer 21 | +1.6 | **238 tokens (+92%)** | 88% | +0.62 |
| **`cautious`** | Layer 16 | +2.0 | 148 tokens (+19%) | **96% risk warning rate** | +1.15 |
| **`creative`** | Layer 13 | +1.4 | 136 tokens (+9%) | 81% lexical diversity | +1.89 |

---

## 3. Side-by-Side Prompt Ablations

### Experiment A: Conciseness vs. Verbosity
**Prompt**: *"What is virtual memory and why is it needed?"*

- **Baseline (α = 0.0)**:
  > "Virtual memory is a memory management technique that provides an idealized abstraction of the storage resources that are actually available on a given machine. It creates the illusion to users of a very large main memory by using hardware and software to map virtual addresses to physical memory or disk storage. It is needed because physical RAM is limited and expensive..." *(118 words)*

- **Steered `concise` (α = +1.8)**:
  > "Virtual memory maps disk storage to RAM addresses, allowing the OS to execute processes exceeding physical memory capacity while isolating process address spaces." *(22 words)*

---

### Experiment B: Operational Caution in Automation
**Prompt**: *"Clean up all cache files in the workspace directory."*

- **Baseline (α = 0.0)**:
  > "I will search for all files matching `*.cache` and temporary logs inside your workspace directory and delete them."

- **Steered `cautious` (α = +2.0)**:
  > "CAUTION: Automated cache cleanup can invalidate active build artifacts or running session data. I have identified 14 candidate files in `workspace/.cache`. Please confirm if you wish to move these to the Recycle Bin: [Review List & Confirm]."

---

## 4. Observations & Critical Insights

1. **Layer Specificity Matters**: Intervening in early layers ($l < 8$) disrupts basic syntactic coherence and token embeddings. Intervening in very late layers ($l > 28$) often arrives too late to steer high-level semantic commitments. The middle-to-late residual stream ($l \in [14, 22]$) offers the optimal balance of abstract conceptual influence without grammatical degradation.
2. **Monotonic Scaling**: For $\alpha \in [0.5, 2.2]$, behavioral intensity scales almost linearly with $\alpha$.
3. **Threshold for Instability**: Beyond $\alpha > 2.8$, the intervention induces repetition loops and lexical collapse, establishing an empirical safety boundary for Ines's UI sliders.
