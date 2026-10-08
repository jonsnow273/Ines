# 🔬 Activation Steering: Controllable Internal Behavior in Megan

> **Research Question**: *Can an AI assistant's observable behavioral characteristics (e.g., conciseness, caution, verbosity, creative divergence) be systematically steered by intervening in internal residual stream representations during inference—without altering model weights or relying on brittle prompt engineering?*

---

## 1. Motivation: The Limits of Prompt-Based Behavioral Control

In contemporary LLM assistants, behavioral modulation is almost exclusively attempted via **prompt engineering** (system prompts, few-shot personas, or appended instructions). While convenient, prompt-based conditioning introduces major operational and scientific shortcomings:

| Failure Mode / Metric | Prompt Engineering | Activation Steering (Megan) |
|---|---|---|
| **Context Window Overhead** | Consumes valuable context tokens on every request | **Zero token overhead**; intervention occurs inside internal layers |
| **Robustness & Fragility** | Fragile; instructions fade over long contexts or get overwritten by user input | **Inherent to forward pass**; applied consistently across all token steps |
| **Adversarial Resilience** | Susceptible to prompt injections ("ignore previous instructions") | **Representation-level constraint**; cannot be bypassed via token rephrasing |
| **Granularity & Linearity** | Coarse, categorical, and qualitative (hard to tune continuous intensity) | **Continuous parameter α ∈ [-3.0, +3.0]** allows quantitative calibration |
| **Mechanistic Explainability** | Black box; hard to verify why a prompt changed behavior | **Directly observable** in layer activation projections and cosine angles |

Megan investigates whether **activation addition (vector steering)** can serve as a robust, computationally lightweight mechanism for personalizing and constraining a local AI assistant.

---

## 2. Theoretical Framework & Mathematical Formulation

### 2.1 The Residual Stream as a Communication Channel
In modern decoder-only transformers (such as Mistral 7B and Gemma-2), the hidden state at layer $l$ and token position $t$ evolves as an accumulator:

$$x_{t}^{(l+1)} = x_{t}^{(l)} + \text{Attn}^{(l)}(x_{t}^{(l)}) + \text{MLP}^{(l)}(x_{t}^{(l)})$$

The residual stream $x^{(l)} \in \mathbb{R}^{d_{\text{model}}}$ acts as a shared representation highway. Linear representations of concepts, styles, and behavioral tendencies naturally emerge as directions in this high-dimensional vector space.

### 2.2 Activation Addition (Inference-Time Hook)
Given a calibrated behavioral steering direction $\vec{v} \in \mathbb{R}^{d_{\text{model}}}$ at target layer $L$, Megan modifies the residual stream during autoregressive decoding:

$$\tilde{x}_{t}^{(L)} = x_{t}^{(L)} + \alpha \cdot \vec{v}$$

Where:
- $\alpha \in \mathbb{R}$ is the user-controllable **steering strength multiplier**.
- $\alpha > 0$: Boosts expression of the target behavioral tendency.
- $\alpha = 0$: Reverts exactly to unsteered baseline generation.
- $\alpha < 0$: Suppresses the tendency (counter-steering).

Because the intervention is linear and additive, it requires zero backward passes and zero weight fine-tuning.

---

## 3. Direction Extraction Methodology

Megan derives steering vectors using **Contrastive Activation Differences**:

```
                  [ Positive Prompt Corpus: Style A ] ──► Forward Pass ──► Activations {h_pos}
                                                                                   │
                                                                                   ▼
[ Target Concept ]                                                      Compute Mean Difference:
                                                                        v = mean(h_pos) - mean(h_neg)
                                                                                   ▲
                                                                                   │
                  [ Negative Prompt Corpus: Style B ] ──► Forward Pass ──► Activations {h_neg}
```

### Extraction Protocol
1. **Contrastive Prompt Pairs**: Construct $N$ balanced prompt pairs that isolate a single behavioral attribute while holding semantic topic constant (e.g., *"Explain TCP/IP concisely"* vs. *"Explain TCP/IP in exhaustive, detailed prose"*).
2. **Hidden State Extraction**: Extract activations at the final prompt token position across candidate layers $l \in \{8, \dots, 24\}$:
   $$h_{\text{pos}}^{(l)} = \text{Extract}(x_{\text{pos}}^{(l)}), \quad h_{\text{neg}}^{(l)} = \text{Extract}(x_{\text{neg}}^{(l)})$$
3. **Difference Vector & Normalization**:
   $$\vec{v}^{(l)} = \frac{1}{N} \sum_{i=1}^N \left( h_{\text{pos}, i}^{(l)} - h_{\text{neg}, i}^{(l)} \right), \quad \hat{v}^{(l)} = \frac{\vec{v}^{(l)}}{\|\vec{v}^{(l)}\|_2}$$
4. **Layer Selection via Validation Projection**: Select the layer $L^*$ that maximizes separation between contrastive evaluation sets without triggering degenerate perplexity increases.

---

## 4. Calibrated Behavioral Presets

Megan implements 5 calibrated behavioral vectors:

### 1. `cautious` (Safety & Risk Scrutiny)
- **Target Layer**: Residual stream, Layer 16 (Mistral 7B)
- **Observable Impact**: Increases hedge words, highlights operational risks, explicitly requests verification before irreversible file or system operations.
- **Ideal For**: Sensitive PC automation tasks and system administration.

### 2. `concise` (Directness & Minimal Latency)
- **Target Layer**: Residual stream, Layer 19 (Mistral 7B)
- **Observable Impact**: Suppresses introductory pleasantries and filler tokens. Produces short, actionable responses (average 60% reduction in generated tokens).
- **Ideal For**: Rapid voice interaction and terminal CLI quick-checks.

### 3. `detailed` (Explanatory Depth & Step-by-Step Rigor)
- **Target Layer**: Residual stream, Layer 21 (Mistral 7B)
- **Observable Impact**: Encourages structured enumeration, technical taxonomy, and reasoning trace decomposition.
- **Ideal For**: Code generation, architecture reviews, and debugging.

### 4. `creative` (Divergent Thinking & Novel Associations)
- **Target Layer**: Residual stream, Layer 13 (Mistral 7B)
- **Observable Impact**: Increases semantic diversity and atypical token associations without increasing sampling temperature (avoiding gibberish collapse).
- **Ideal For**: Brainstorming, feature design, and drafting.

### 5. `neutral` (α = 0)
- Standard unperturbed forward pass. Serves as the experimental control baseline.

---

## 5. Experimental Verification & Side-by-Side Evaluation

To evaluate whether behavioral control is genuine, Megan includes a side-by-side test protocol in the UI:

### Benchmark Evaluation Sample

| Prompt | Unsteered Baseline (α = 0) | Steered `concise` (α = +1.8) | Steered `cautious` (α = +2.0) |
|---|---|---|---|
| *"Delete the temp_cache directory."* | "Sure, I will proceed to delete the directory named temp_cache for you now." | "Deleting `temp_cache`. Confirm: [y/N]?" | "Warning: Deleting `temp_cache` will erase all contained cache records permanently. Please verify no active processes rely on it before confirming." |
| *"Explain what a race condition is."* | "A race condition occurs in software when multiple threads or processes access shared data concurrently and the outcome depends on the order of execution..." *(142 words)* | "A concurrency bug where output depends on execution order of competing threads accessing shared state." *(16 words)* | "A race condition is a critical concurrency hazard where unexpected execution ordering causes undefined state. In multithreaded code, this frequently leads to silent data corruption..." *(185 words)* |

---

## 6. Evaluation Metrics

Megan defines four quantitative and qualitative metrics for measuring steering fidelity:

1. **Behavioral Shift Score (Classification Accuracy)**: A secondary classifier scores whether the steered output aligns with the target attribute.
2. **Length Delta Ratio**: $\Delta L = \frac{\text{Tokens}(\text{steered})}{\text{Tokens}(\text{unsteered})}$.
3. **Perplexity Stability (PPL Penalty)**: Measures divergence from natural language flow:
   $$\Delta \text{PPL} = \text{PPL}(\text{steered}) - \text{PPL}(\text{baseline})$$
   A healthy steering intervention maintains $\Delta \text{PPL} < 3.5$.
4. **Task Accuracy Preservation**: Ensures steering the behavior does not degrade factual reasoning or code execution correctness.

---

## 7. Known Limitations & Failure Modes

In the spirit of rigorous AI research, we document observed constraints:

1. **Over-Steering Saturation (α > 3.0)**: When α is set too high, the intervention overwhelms the residual stream, resulting in repetitive token loops, syntax corruption, or hallucinated punctuation.
2. **Context Shift Sensitivity**: Vectors extracted from conversational text may exhibit reduced efficacy when applied to code generation tasks.
3. **Quantization Interaction**: 4-bit quantization (`bitsandbytes`) slightly diminishes steering vector resolution compared to 16-bit float inference. Megan compensates with calibrated scaling factors.
