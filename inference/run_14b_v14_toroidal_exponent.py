#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v14 — INVERSE K-ROPE SHIFT
=====================================================
"If we modify the base, it crashes. If we wrap it, it loops words."
Solution: Intercept the actual RoPE frequencies and apply Toroidal Shift.

θ_new = θ_old ^ (1/K)
"""

import gc
import time
import math
import os
import mlx.core as mx

OMEGA = 0.0341
K = 81/80

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

def get_tunnel_layers(n_layers, target=19):
    active = set()
    active.update(range(0, 4))
    active.update(range(n_layers - 4, n_layers))
    remaining = target - len(active)
    if remaining > 0:
        mid_s, mid_e = 4, n_layers - 4
        step = max(1, (mid_e - mid_s) // remaining)
        for i in range(mid_s, mid_e, step):
            active.add(i)
            if len(active) >= target:
                break
    return sorted(active)

def apply_toroidal_rope_shift(model):
    """
    Directly accesses the RoPE layer and shifts the pre-computed frequency array.
    This avoids MLX property errors while directly twisting the rotation angle by K.
    """
    modified = 0
    for i, layer in enumerate(model.model.layers):
        if hasattr(layer.self_attn, "rope"):
            rope = layer.self_attn.rope
            # RoPE in MLX often stores `_freqs` or calculates it on the fly.
            # We scale the `base` property safely via monkey patching if needed.
            if hasattr(rope, "base"):
                rope.base = rope.base ** (1/K)
                modified += 1
            elif hasattr(rope, "_base"):
                rope._base = rope._base ** (1/K)
                modified += 1
    return modified

QUESTIONS = [
    ("Math", "What is 14 + 28? Answer with just the number."),
    ("Identity", "Who are you?"),
]

if __name__ == "__main__":
    print("=" * 70)
    print("  14B TOROIDAL NPU ENGINE v14 — K-ROPE EXPONENT SHIFT")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    
    mods = apply_toroidal_rope_shift(model)
    print(f"[✓] TUNNEL: {len(tunnel)}/{n_layers} layers. RoPE Base modified on {mods} layers.")
    
    mx.eval(model.model.embed_tokens.parameters())
    mx.eval(model.model.norm.parameters())
    mx.eval(model.lm_head.parameters())
    
    for q_idx, (q_name, q_text) in enumerate(QUESTIONS):
        print(f"\n  Q{q_idx+1}: [{q_name}] \"{q_text}\"")
        cache = make_prompt_cache(model)
        
        try:
            prompt = tokenizer.apply_chat_template([{"role": "user", "content": q_text}], tokenize=False, add_generation_prompt=True)
        except:
            prompt = q_text
        
        tokens = tokenizer.encode(prompt)
        h = model.model.embed_tokens(mx.array([tokens]))
        mx.eval(h)
        
        seq_len = h.shape[1]
        mask = None
        if seq_len > 1:
            mask = mx.full((seq_len, seq_len), -1e9, dtype=mx.bfloat16)
            mask = mx.triu(mask, k=1)[None, None, :, :]
            mx.eval(mask)
        
        t0 = time.time()
        
        # PREFILL
        for i in tunnel:
            h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
        h = model.model.norm(h)
        
        token_id = mx.argmax(model.lm_head(h)[:, -1, :], axis=-1).item()
        generated = [token_id] if token_id != tokenizer.eos_token_id else []
        
        # GENERATE
        for step in range(30):
            if token_id == tokenizer.eos_token_id: break
            h = model.model.embed_tokens(mx.array([[token_id]]))
            
            for i in tunnel:
                h = model.model.layers[i](h, mask=None, cache=cache[i] if i < len(cache) else None)
            
            h = model.model.norm(h)
            token_id = mx.argmax(model.lm_head(h)[:, -1, :], axis=-1).item()
            if token_id != tokenizer.eos_token_id: generated.append(token_id)
            
        tps = len(generated) / (time.time() - t0)
        print(f"  Output ({tps:.1f} TPS): {tokenizer.decode(generated)[:60]}")
