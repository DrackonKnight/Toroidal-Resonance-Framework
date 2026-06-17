# KV Cache Bridge & Cross-Model Semantic Transfer

## What This Proves

A transformer's KV cache is a **complete, portable geometric representation of semantic memory**. It can be:

1. **Extracted** from active VRAM
2. **Serialized** to disk (14 MB `.npz` file)
3. **Wiped** entirely from RAM
4. **Reinjected** into a fresh cache object
5. **Recalled** with 100% fidelity across multiple semantic domains

This also works **across model architectures** — memory encoded by Qwen 1.5 (1.8B) can be read by Gemma 4 E4B after Toroidal Head Folding and alignment.

## Results

### Same-Model Cache Bridge (test_kv_reinject.py, long_horizon_kv_test.py)

| Condition | Score | Retention |
|-----------|:-----:|:---------:|
| Baseline (original cache) | 5/5 | 100% |
| Control (empty cache) | 0/5 | 0% |
| **Reinjected (from disk)** | **5/5** | **100%** |

Five unrelated facts (music theory, military codes, GPS coordinates, recipe details, project names) — all recalled perfectly after full RAM wipe and disk round-trip.

### Cross-Model Wormhole (cross_model_wormhole.py)

| Source | Target | Fact | Result |
|--------|--------|------|--------|
| Qwen 1.5 1.8B | Gemma 4 E4B | "HourGlass" | **Recalled** |

Gemma read Qwen's encoded memory after Toroidal Head Folding (16×128 → 2×512) and least-squares alignment.

## Requirements

- Apple Silicon Mac (M1/M2/M3/M4)
- Python 3.11+
- MLX ≥ 0.29
- mlx_lm ≥ 0.31 (required for Gemma 4 support)

```bash
pip install mlx mlx-lm numpy
```

## How to Run

```bash
# Single-fact baseline
python3 test_kv_reinject.py

# Multi-fact long-horizon (5 facts, full wipe/reinject cycle)
python3 long_horizon_kv_test.py

# Cross-model wormhole (Qwen -> Gemma)
python3 cross_model_wormhole.py
```

## Key Finding: Alignment Method Matters

| Method | Same-Model | Cross-Model |
|--------|:----------:|:-----------:|
| Orthogonal Procrustes (SVD rotation) | ✅ Recommended | ❌ Fails |
| Least Squares (with scaling) | ✅ Works | ✅ Required |

Cross-model transfer requires scaling to bridge different normalization regimes between architectures. Pure rotation cannot bridge this gap.

## How It Works

1. **Toroidal Head Folding**: Maps between incompatible head configurations (e.g., 16×128 → 2×512) using alternating-phase stacking instead of destructive SVD
2. **Procrustes Alignment**: Learns rotation/scaling matrices from calibration context run through both models
3. **Thermodynamic Gas Diffusion**: Injects foreign KV states only into full-attention layers; SWA layers are primed natively
4. **Digital EGR Valve**: Recirculates evicted sliding-window tokens (scaled by Ω) back into the attention computation

See the [full white paper](../TOROIDAL_RESONANCE_KV_CACHE_WHITEPAPER.md) for mathematical details and complete experimental results.
