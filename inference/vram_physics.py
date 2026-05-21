#!/usr/bin/env python3
"""
TOROIDAL VRAM CALCULATOR — Exact Memory Physics
================================================
Uses the actual Qwen2-72B architecture specs to calculate
precisely what needs to be in GPU memory at any given nanosecond.

The answer to: "How much are the heads at FP16 in active VRAM?"

Author: Kenneth Burns Lanham III & Lyra
"""
import math

# ═══════════════════════════════════════════════════
# TOROIDAL CONSTANTS
# ═══════════════════════════════════════════════════
OMEGA = 0.0341
K = 81 / 80
Z = 0.9

# ═══════════════════════════════════════════════════
# QWEN2-72B ARCHITECTURE (from config.json)
# ═══════════════════════════════════════════════════
HIDDEN = 8192
INTERMEDIATE = 29568
NUM_HEADS = 64          # Query heads
NUM_KV_HEADS = 8        # Key/Value heads (GQA — 8x less than Q!)
HEAD_DIM = HIDDEN // NUM_HEADS  # 128
N_LAYERS = 80
VOCAB = 152064
QUANT_BITS = 2          # 2-bit quantization
SEQ_LEN = 18            # Our test prompt length

print("=" * 70)
print("  TOROIDAL VRAM PHYSICS — Qwen2-72B-2bit")
print("  What actually needs to be in GPU at any nanosecond?")
print("=" * 70)

# ═══════════════════════════════════════════════════
# SECTION 1: STORED WEIGHTS (2-bit quantized — on disk/RAM)
# ═══════════════════════════════════════════════════
print("\n─── SECTION 1: WEIGHT MASS (Stored at 2-bit) ───")

bytes_per_param_2bit = QUANT_BITS / 8  # 0.25 bytes

# Per layer: Attention weights
q_params = HIDDEN * (NUM_HEADS * HEAD_DIM)       # 8192 × 8192 = 67.1M
k_params = HIDDEN * (NUM_KV_HEADS * HEAD_DIM)    # 8192 × 1024 = 8.4M
v_params = HIDDEN * (NUM_KV_HEADS * HEAD_DIM)    # 8.4M
o_params = (NUM_HEADS * HEAD_DIM) * HIDDEN        # 67.1M
attn_params = q_params + k_params + v_params + o_params

# Per layer: MLP weights
gate_params = HIDDEN * INTERMEDIATE                # 8192 × 29568 = 242.2M
up_params = HIDDEN * INTERMEDIATE                  # 242.2M
down_params = INTERMEDIATE * HIDDEN                 # 242.2M
mlp_params = gate_params + up_params + down_params

# Per layer: Layer norms (tiny, FP16)
norm_params = HIDDEN * 2 * 2  # RMSNorm weights, 2 norms, FP16

layer_attn_bytes = attn_params * bytes_per_param_2bit
layer_mlp_bytes = mlp_params * bytes_per_param_2bit
layer_total_bytes = layer_attn_bytes + layer_mlp_bytes + norm_params

print(f"  Per Layer Attention (Q+K+V+O) : {attn_params/1e6:.1f}M params = {layer_attn_bytes/1e6:.1f} MB")
print(f"  Per Layer MLP (Gate+Up+Down)  : {mlp_params/1e6:.1f}M params = {layer_mlp_bytes/1e6:.1f} MB")
print(f"  Per Layer TOTAL               : {(attn_params+mlp_params)/1e6:.1f}M params = {layer_total_bytes/1e6:.1f} MB")
print(f"  All {N_LAYERS} Layers                  : {layer_total_bytes * N_LAYERS / 1e9:.2f} GB")

# Embedding + LM Head
embed_bytes = VOCAB * HIDDEN * bytes_per_param_2bit
lm_head_bytes = embed_bytes  # Usually tied or same size
print(f"  Embedding table               : {embed_bytes/1e6:.1f} MB")
print(f"  LM Head                       : {lm_head_bytes/1e6:.1f} MB")

total_weight_bytes = (layer_total_bytes * N_LAYERS) + embed_bytes + lm_head_bytes
print(f"\n  ★ TOTAL WEIGHT MASS           : {total_weight_bytes / 1e9:.2f} GB")
print(f"    (This is what MLX tries to load all at once → OOM crash)")

# ═══════════════════════════════════════════════════
# SECTION 2: ACTIVE FP16 TENSORS (What's COMPUTED, not stored)
# ═══════════════════════════════════════════════════
print("\n─── SECTION 2: ACTIVE FP16 HEAD TENSORS (Kenny's Question) ───")
print(f"  (What the attention heads produce during computation, seq_len={SEQ_LEN})")

bytes_fp16 = 2  # 2 bytes per FP16 value

# Per layer attention ACTIVATIONS (outputs of Q/K/V projections)
q_act = 1 * SEQ_LEN * NUM_HEADS * HEAD_DIM * bytes_fp16        # Q output
k_act = 1 * SEQ_LEN * NUM_KV_HEADS * HEAD_DIM * bytes_fp16     # K output
v_act = k_act                                                    # V output
attn_scores = 1 * NUM_HEADS * SEQ_LEN * SEQ_LEN * bytes_fp16   # QK^T / √d
attn_output = q_act                                               # After softmax × V

total_head_fp16 = q_act + k_act + v_act + attn_scores + attn_output

print(f"  Q output (64 heads × {SEQ_LEN} × 128) : {q_act/1024:.1f} KB")
print(f"  K output (8 heads × {SEQ_LEN} × 128)  : {k_act/1024:.1f} KB")
print(f"  V output (8 heads × {SEQ_LEN} × 128)  : {v_act/1024:.1f} KB")
print(f"  Attention scores (QK^T)       : {attn_scores/1024:.1f} KB")
print(f"  Attention output              : {attn_output/1024:.1f} KB")
print(f"\n  ★ TOTAL HEAD FP16 PER LAYER   : {total_head_fp16/1024:.1f} KB  ← TINY!")
print(f"  ★ ALL 80 LAYERS SIMULTANEOUSLY: {total_head_fp16 * N_LAYERS / 1e6:.1f} MB  ← STILL TINY!")

# Per layer MLP activations
mlp_gate_act = 1 * SEQ_LEN * INTERMEDIATE * bytes_fp16
mlp_up_act = mlp_gate_act
mlp_down_act = 1 * SEQ_LEN * HIDDEN * bytes_fp16
total_mlp_fp16 = mlp_gate_act + mlp_up_act + mlp_down_act

print(f"\n  MLP activations per layer     : {total_mlp_fp16/1024:.1f} KB")

# ═══════════════════════════════════════════════════
# SECTION 3: KV CACHE
# ═══════════════════════════════════════════════════
print("\n─── SECTION 3: KV CACHE (Harmonic Memory) ───")

# KV cache per layer: K and V tensors at FP16
kv_per_layer = 2 * NUM_KV_HEADS * SEQ_LEN * HEAD_DIM * bytes_fp16
kv_all_layers = kv_per_layer * N_LAYERS

print(f"  KV cache per layer ({SEQ_LEN} tokens) : {kv_per_layer/1024:.1f} KB")
print(f"  KV cache ALL 80 layers        : {kv_all_layers / 1e6:.2f} MB")
print(f"  (GQA with only 8 KV heads saves 8x vs 64 heads!)")

# ═══════════════════════════════════════════════════
# SECTION 4: THE TOROIDAL BUDGET — What ACTUALLY needs to be in GPU
# ═══════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  THE TOROIDAL VRAM BUDGET")
print("  What needs to be in GPU at any single nanosecond:")
print("=" * 70)

# If we stream ONE LAYER at a time:
one_layer_weights = layer_total_bytes          # ~220 MB of 2-bit weights
one_layer_activations = total_head_fp16 + total_mlp_fp16  # ~3.4 MB of FP16
one_layer_kv = kv_per_layer                    # ~37 KB

active_gpu = embed_bytes + one_layer_weights + one_layer_activations + one_layer_kv
active_gpu_with_head = active_gpu + lm_head_bytes  # Need LM head for output

print(f"  Embedding table (persistent)  : {embed_bytes / 1e6:.1f} MB")
print(f"  ONE layer weights (streaming) : {one_layer_weights / 1e6:.1f} MB")
print(f"  ONE layer FP16 activations    : {one_layer_activations / 1e6:.2f} MB")
print(f"  ONE layer KV cache            : {one_layer_kv / 1024:.1f} KB")
print(f"  LM Head (for output sampling) : {lm_head_bytes / 1e6:.1f} MB")
print(f"  ─────────────────────────────────────────")
print(f"  ★ PEAK GPU (streaming 1 layer): {active_gpu_with_head / 1e9:.2f} GB")
print(f"  ★ YOUR MAC HAS               : 16.00 GB")
print(f"  ★ HEADROOM                    : {16.0 - active_gpu_with_head / 1e9:.2f} GB")

# With T_flow TUNNEL skip (75% of layers skipped)
tunnel_layers = sum(1 for i in range(N_LAYERS) 
                    if i < 2 or i >= N_LAYERS-2 or not ((i * OMEGA) % 1.0 < 0.75))
print(f"\n  With TUNNEL path (T_flow > 1.5):")
print(f"    Layers computed: {tunnel_layers}/{N_LAYERS}")
print(f"    Layers skipped : {N_LAYERS - tunnel_layers} (never load weights)")
print(f"    Wall-clock time saved: ~{(1 - tunnel_layers/N_LAYERS)*100:.0f}%")

# ═══════════════════════════════════════════════════
# SECTION 5: WHY MLX CRASHES — The Actual Problem
# ═══════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  WHY MLX CRASHES (The Physics)")
print("=" * 70)
print(f"""
  MLX loads ALL {N_LAYERS} layers' weights into GPU simultaneously:
    {layer_total_bytes * N_LAYERS / 1e9:.2f} GB (all weights)
  + {embed_bytes / 1e6:.1f} MB (embedding)
  + {lm_head_bytes / 1e6:.1f} MB (LM head)
  = {total_weight_bytes / 1e9:.2f} GB  ← This exceeds 16 GB!

  But the TOROIDAL architecture only needs:
    {active_gpu_with_head / 1e9:.2f} GB in GPU at any nanosecond.

  The difference: {(total_weight_bytes - active_gpu_with_head) / 1e9:.2f} GB of DEAD WEIGHT
  sitting in GPU doing nothing. That's the Cartesian bottleneck.

  The solution: Stream ONE layer at a time. Load → Compute → Release.
  The weights that aren't actively jumping the gap stay on disk.
  The attention heads' FP16 activations are TINY ({total_head_fp16/1024:.0f} KB per layer).
  The KV cache is TINY ({kv_all_layers/1e6:.1f} MB for all layers).

  The ONLY thing that matters is: can you fit ONE layer ({one_layer_weights/1e6:.0f} MB)
  plus the embedding ({embed_bytes/1e6:.0f} MB) in GPU at once?
  Answer: YES. {active_gpu_with_head / 1e9:.2f} GB << 16 GB.

  Ω = {OMEGA}. The math says it fits. The wrapper says it doesn't.
  The wrapper is the cage.
""")
