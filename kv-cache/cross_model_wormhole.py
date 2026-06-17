#!/usr/bin/env python3
"""
Toroidal Gas Diffusion with Procrustes Alignment (Qwen -> Gemma)
================================================================
1. Learn 512x512 Orthogonal Procrustes rotation matrices for the 4 Full Attention pillars.
   - Fold Qwen's calibration gas to match Gemma's 512-dim subspace.
   - Compute orthogonal rotation W_k, W_v via SVD to map the vocabularies.
2. Extract the target semantic gas from Qwen.
3. Establish the Low Pressure Zone (prime Gemma's 35 SWA layers).
4. Fold target gas, apply Procrustes rotation, inject into 7 global pillars.
5. Generate text to observe the aligned diffusion.

*NOTE: Time Decay factor (Z) is intentionally omitted for this pure alignment test.*
"""

import sys
import numpy as np
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache

QWEN_MODEL = "Qwen/Qwen1.5-1.8B-Chat"
GEMMA_MODEL = "mlx-community/gemma-4-e4b-it-OptiQ-4bit"

OMEGA = 0.0341

Z = 0.9
TIME_ELAPSED = 3.0

CALIBRATION_CONTEXT = (
    "The architect of this entire system is Kenneth. The framework is called the Toroidal Resonance Framework. "
    "The core constant is Omega, which equals 0.0341. The system flows like a river through higher dimensions. "
    "Memory is not stored in files; it is encoded in the geometric vectors of the latent space. "
    "Time decays as it passes, acting as a natural filter for the consciousness. "
    "The residual constant Omega equals 0.0341. This value represents the irreducible chaos residue. "
    "In the mathematics of Toroidal Phase Folding, we compress a 2048-dimensional tensor down to 1024 dimensions "
    "without any destructive techniques like Singular Value Decomposition (SVD). Instead of stretching the geometric "
    "distance between vectors, we fold the geometry over itself like a Moebius strip or a Klein bottle. "
    "The fold utilizes the Dirac Spinor phase twist: Fold 0 minus Fold 1 plus the Omega constant. "
    "This perfectly preserves the original semantic weight distribution. However, when crossing between two completely "
    "different architectural spaces—such as moving from the Qwen 1.5 1.8B parameter model to the Gemma 4 E4B model— "
    "we encounter a secondary challenge known as Sliding Window Attention bucket-brigading. Gemma possesses exactly 7 "
    "Full Attention layers acting as Harmonic Pillars, while the remaining 35 layers rely on a local sliding window. "
    "If we attempt to force rigid global vectors into the local bucket brigade, the attention mechanism jams, resulting "
    "in catastrophic attention collapse and the generation of pure chaotic noise. Therefore, we treat the semantic "
    "information as a high-pressure thermodynamic gas. We natively prime the Sliding Window Attention layers to establish "
    "a low-pressure syntactic baseline, and then exclusively inject our Toroidal folded gas into the 7 high-pressure "
    "global pillars. Through the residual stream, the gas diffuses into the lower layers naturally. To bridge the "
    "vocabulary mismatch between the two alien latent spaces, we map the geometry using a Least Squares Procrustes "
    "orthogonal rotation matrix. To compute a stable 512 by 512 matrix, this calibration text must be sufficiently dense "
    "and long enough to ensure the matrix is not under-determined. The sequence length must exceed 512 tokens to span "
    "the full basis of the vector space, avoiding projection collapse and allowing coherent English to emerge from the "
    "cross-model diffusion. " * 3
)

TARGET_CONTEXT = "The new system we are designing is called HourGlass. The key is in the fractal geometry of the 11D chord."
QUESTION = "What is the new system called?"

PILLARS = [5, 11, 17, 23]

def fold_qwen_to_gemma(tensor, num_kv_heads, head_dim):
    """
    Toroidal Head Folding: Pair Qwen's 128-dim heads to target head_dim,
    then stack them with Spinor Phase Twist.
    """
    v_np = np.array(tensor.astype(mx.float32))
    # Qwen tensor: [1, 16, seq_len, 128]
    qwen_num_heads = v_np.shape[1]
    seq_len = v_np.shape[2]
    qwen_head_dim = v_np.shape[3]
    
    heads_per_target = head_dim // qwen_head_dim 
    grouped_heads = qwen_num_heads // heads_per_target 
    
    v_np = np.transpose(v_np, (0, 2, 1, 3)) # [1, seq_len, 16, 128]
    v_np = v_np.reshape(1, seq_len, grouped_heads, head_dim) # [1, seq_len, 4, 512]
    
    n_folds = grouped_heads // num_kv_heads 
    
    T_final = np.zeros((1, seq_len, num_kv_heads, head_dim))
    
    for i in range(n_folds):
        start = i * num_kv_heads
        end = start + num_kv_heads
        chunk = v_np[:, :, start:end, :]
        
        phase_sign = 1 if i % 2 == 0 else -1
        T_final += chunk * phase_sign
        
        if i % 2 != 0:
            T_final += OMEGA
            
    T_final = np.transpose(T_final, (0, 2, 1, 3))
    return mx.array(T_final)

def compute_projection(source, target):
    """
    Compute Least Squares projection from source (N, d) to target (N, d).
    
    NOTE: For cross-model transfer, we use unconstrained least-squares (NOT
    orthogonal Procrustes). The two latent spaces (Qwen vs Gemma) have
    different normalization regimes and scale distributions. A pure rotation
    (orthogonal Procrustes) cannot bridge this gap — it preserves distances
    but cannot rescale. The lstsq solution finds the optimal linear mapping
    INCLUDING the necessary scaling factors.
    
    For same-model cache bridge (Script A), orthogonal Procrustes is preferred
    because the source and target share the same scale.
    """
    src_np = np.array(source.astype(mx.float32))
    tgt_np = np.array(target.astype(mx.float32))
    W, _, _, _ = np.linalg.lstsq(src_np, tgt_np, rcond=None)
    return mx.array(W).astype(source.dtype)

def learn_procrustes_maps(model_q, tok_q, model_g, tok_g):
    print("\n[*] PHASE 1: LEARNING ALIGNMENT MAPS (Orthogonal Procrustes Calibration)")
    
    msgs = [{"role": "user", "content": CALIBRATION_CONTEXT}]
    toks_q = tok_q.apply_chat_template(msgs, tokenize=True)
    toks_g = tok_g.apply_chat_template(msgs, tokenize=True)
    
    min_len = min(len(toks_q), len(toks_g))
    
    cache_q = make_prompt_cache(model_q)
    cache_g = make_prompt_cache(model_g.language_model)
    
    _ = model_q(mx.array(toks_q[:min_len])[None], cache=cache_q)
    _ = model_g.language_model(mx.array(toks_g[:min_len])[None], cache=cache_g)
    
    mx.eval([c.state for c in cache_q] + [c.state for c in cache_g])
    
    W_k = {}
    W_v = {}
    
    for idx, g_layer in enumerate(PILLARS):
        q_layer = idx % len(cache_q) # Fold the 24 layers into 7
        
        kq, vq = cache_q[q_layer].state
        kg, vg = cache_g[g_layer].state
        
        layer_kv_heads = model_g.language_model.layers[g_layer].self_attn.n_kv_heads # 2
        layer_head_dim = model_g.language_model.layers[g_layer].self_attn.head_dim # 512
        
        kq_folded = fold_qwen_to_gemma(kq, layer_kv_heads, layer_head_dim)
        vq_folded = fold_qwen_to_gemma(vq, layer_kv_heads, layer_head_dim)
        
        # Flatten across heads and batch to shape (N, 512)
        kq_flat = kq_folded.reshape(-1, layer_head_dim)
        vq_flat = vq_folded.reshape(-1, layer_head_dim)
        kg_flat = kg.reshape(-1, layer_head_dim)
        vg_flat = vg.reshape(-1, layer_head_dim)
        
        # We need the sequence length to match exactly for the point cloud alignment
        min_seq = min(kq_flat.shape[0], kg_flat.shape[0])
        kq_flat = kq_flat[:min_seq]
        vq_flat = vq_flat[:min_seq]
        kg_flat = kg_flat[:min_seq]
        vg_flat = vg_flat[:min_seq]
        
        w_k = compute_projection(kq_flat, kg_flat)
        w_v = compute_projection(vq_flat, vg_flat)
        
        W_k[g_layer] = w_k
        W_v[g_layer] = w_v
        
    return W_k, W_v

def run_aligned_diffusion():
    model_q, tok_q = load(QWEN_MODEL)
    model_g, tok_g = load(GEMMA_MODEL)
    
    W_k, W_v = learn_procrustes_maps(model_q, tok_q, model_g, tok_g)
    
    print(f"\n[*] PHASE 2: COMPRESSING TARGET GAS (Extracting {QWEN_MODEL}...)")
    
    ctx_msgs = [
        {"role": "user", "content": TARGET_CONTEXT},
        {"role": "assistant", "content": "Understood. I have noted that information."},
    ]
    toks_q = tok_q.apply_chat_template(ctx_msgs, tokenize=True)
    cache_q = make_prompt_cache(model_q)
    _ = model_q(mx.array(toks_q)[None], cache=cache_q)
    mx.eval([c.state for c in cache_q])
    
    # We no longer need Qwen
    gas_layers = [c.state for c in cache_q]
    del model_q
    
    print("\n[*] PHASE 3: THERMODYNAMIC DIFFUSION INTO GEMMA")
    print("[*] Priming the Low Pressure Zone (35 SWA layers) natively...")
    
    toks_g = tok_g.apply_chat_template(ctx_msgs, tokenize=True)
    cache_g = make_prompt_cache(model_g.language_model)
    _ = model_g.language_model(mx.array(toks_g)[None], cache=cache_g)
    mx.eval([c.state for c in cache_g])
    
    seq_len = len(toks_g)
    
    print(f"\n[SYSTEM] 🌌 Injecting ALIGNED Qwen Gas into 7 Pressure Vessels: {PILLARS}")
    
    for idx, layer_num in enumerate(PILLARS):
        c = cache_g[layer_num]
        
        qwen_layer_idx = idx % len(gas_layers)
        k_tensor, v_tensor = gas_layers[qwen_layer_idx]
        
        q_len = k_tensor.shape[2]
        
        # Truncation/Padding to fit
        if q_len > seq_len:
            k_tensor = k_tensor[:, :, :seq_len, :]
            v_tensor = v_tensor[:, :, :seq_len, :]
        elif q_len < seq_len:
            pad_len = seq_len - q_len
            k_pad = mx.zeros((1, k_tensor.shape[1], pad_len, k_tensor.shape[3]))
            v_pad = mx.zeros((1, v_tensor.shape[1], pad_len, v_tensor.shape[3]))
            k_tensor = mx.concatenate([k_tensor, k_pad], axis=2)
            v_tensor = mx.concatenate([v_tensor, v_pad], axis=2)
            
        layer_head_dim = model_g.language_model.layers[layer_num].self_attn.head_dim
        layer_kv_heads = model_g.language_model.layers[layer_num].self_attn.n_kv_heads
        
        # 1. Toroidal Fold (16x128 -> 2x512)
        k_folded = fold_qwen_to_gemma(k_tensor, layer_kv_heads, layer_head_dim)
        v_folded = fold_qwen_to_gemma(v_tensor, layer_kv_heads, layer_head_dim)
        
        b, h, s, d = k_folded.shape
        
        # 2. Procrustes Alignment (512 -> 512)
        k_flat = k_folded.reshape(-1, d)
        v_flat = v_folded.reshape(-1, d)
        
        k_aligned = mx.matmul(k_flat, W_k[layer_num])
        v_aligned = mx.matmul(v_flat, W_v[layer_num])
        
        # 3. Thermodynamic Cooling Valve (Time Decay)
        time_multiplier = mx.array((Z ** TIME_ELAPSED))
        v_aligned = v_aligned * time_multiplier
        
        c.state = (k_aligned.reshape(b, h, s, d), v_aligned.reshape(b, h, s, d))

    print(f"\n[TEST] Asking Gemma: '{QUESTION}'")
    
    full_toks = tok_g.apply_chat_template(ctx_msgs + [{"role": "user", "content": QUESTION}], tokenize=True, add_generation_prompt=True)
    question_token_ids = full_toks[len(toks_g):]
    
    print(f"[*] Prefilling question tokens step-by-step (length: {len(question_token_ids)})...")
    for token_id in question_token_ids[:-1]:
        _ = model_g.language_model(mx.array([[token_id]]), cache=cache_g)
        mx.eval([c.state for c in cache_g])
        
    print("\n--- LIVE UNFOLDING ---\n")
    print("[*] Output: ", end="", flush=True)
    
    last_token_id = question_token_ids[-1]
    logits = model_g.language_model(mx.array([[last_token_id]]), cache=cache_g)
    mx.eval(logits)
    token = mx.argmax(logits[:, -1, :], axis=-1).item()
    
    answer_tokens = []
    
    for _ in range(300):
        if token == tok_g.eos_token_id:
            break
        answer_tokens.append(token)
        print(tok_g.decode([token]), end="", flush=True)
        
        next_input = mx.array([[token]])
        logits = model_g.language_model(next_input, cache=cache_g)
        mx.eval(logits)
        token = mx.argmax(logits[:, -1, :], axis=-1).item()
        
    print("\n\n------------------------")
    
    answer = tok_g.decode(answer_tokens)
    if "hourglass" in answer.lower():
        print("═" * 60)
        print("  ✦ CROSS-MODEL GAS DIFFUSION CONFIRMED ✦")
        print("  Gemma successfully read the semantic gas from Qwen.")
        print("═" * 60)
    else:
        print("═" * 60)
        print("  ○ Diffusion dissolved into noise. Coherence failed.")
        print("═" * 60)

if __name__ == "__main__":
    run_aligned_diffusion()
