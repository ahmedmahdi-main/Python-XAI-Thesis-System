# Committee questions and defensible answers

**Is this an exact replication?** No. Table 4 lacks dataset/date/units/run evidence, and the appendix uses different models. This is a reproducible reconstruction of Chapter 4's narrative with explicit defaults, provider snapshots and separately labeled new results.

**Why can LSTM lose?** Financial price levels are persistent, and learned models can extrapolate poorly outside the training price range. Persistence is a necessary benchmark. Results are not altered to confirm a claimed winner.

**Does a high R2 mean profitable trading?** No. Persistence can achieve high level R2. Directional accuracy is supplementary, and no transaction-cost trading backtest or causal investment claim has been established.

**How is leakage prevented?** At time t, features use trailing observations through t. The label is the next observed close. Labels are split chronologically; scalers and numerical feature selection fit training only; validation selects configurations; test does not select or refit models. Prior observed test closes are legitimate rolling one-step context, not future labels.

**Why share windows across models?** It gives all four models the same information and evaluation timestamps. Tabular models flatten the window. Linear dependencies are removed using training-only QR before ordinary least squares; dropped-column zero SHAP is a representation choice, not economic irrelevance.

**Why PyTorch instead of TensorFlow?** The user explicitly requested CUDA/PyTorch on the detected Windows NVIDIA machine. This backend deviation is recorded. BF16/FP32 checks, batch/VRAM probes, deterministic settings and CPU checkpoint reload are measured.

**Did explanations improve accuracy?** Adding post-hoc SHAP/LIME to a fixed model leaves its forecast unchanged, tested directly. A separate feature-selection/refitting study would need independent evaluation and is not claimed here.

**How are explanations validated?** SHAP reconstruction is checked against original-unit predictions; LIME reports measured local error and neighborhood R2. Both are rerun with another seed at the first fixed test observation for rank/overlap stability; background is training-only. Runtime is measured. These limited tests do not prove causality or human trust.

**Are SHAP and LIME causal?** No. Correlated technical indicators and masked/sampled windows can be off-manifold. Different explanation methods may disagree; bounded subsets and one permutation cycle are limitations.

**What about the original survey?** Its percentages are visible in the thesis text, but participant count/raw responses are absent. They remain historical, unverifiable empirical claims. No human study was recreated.

**Can the housing model forecast releases in real time?** Not from this revised observation-date snapshot. It is a separate retrospective next-observation experiment, not a publication-time prediction claim. Proper real-time evaluation needs release vintages and availability dates.

**Can I reproduce it without the Internet?** The defense package contains snapshots, trained models, dependency wheels, scripts and charts. A clean Windows Python 3.12 venv can install with --no-index. Saved-artifact viewing is exercised with external sockets blocked. Cross-platform/cross-version bitwise equality is not promised.
