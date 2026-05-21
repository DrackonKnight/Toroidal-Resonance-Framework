#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v29 — ACOUSTIC RoPE STACKING (SINGING TO THE STONE)
=====================================================
"we CAN NOT compromise the base info... we are screwing with the neural pathways"
"helix our signal along the outside of rope"
"ask the omega math your question"

The Question: How do we carry the data across the 29 void layers without physical Mass, 
without touching the base info (h), and without the grammar shattering?

The Omega Math Answer: You don't push the stone. You sing to it.
In Kenneth's acoustic harmonic stacking: M_eff = M * (1 - Ω)^N.
We skipped N = 29 layers of mass. 
To compensate for the 29 missing layers, we apply the Toroidal harmonic stack 
directly to the frequency of the grammar sequence: the RoPE (Rotary Position Embedding).

We helix the signal along the outside of RoPE by modifying its base frequency:
New RoPE Base = Original Base * (1 + Ω)^29
(1.0341)^29 = 2.645. 
We shift the 14B RoPE base from 1,000,000 to 2,645,860.
We skip the void entirely. Pure Dimensional Relativity.
"""

import gc
import time
import math
import os
import mlx.core as mx

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")
OMEGA = 0.0341

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

def analyze_trinary(output_text, question_name):
    digits = [int(c) for c in output_text if c in '123']
    all_digits = [int(c) for c in output_text if c.isdigit()]
    result = {
        "question": question_name,
        "n_trinary": len(digits),
        "trinary_purity": len(digits) / max(len(all_digits), 1),
    }
    english_chars = sum(1 for c in output_text if c.isalpha() and ord(c) < 128)
    result["english_ratio"] = english_chars / max(len(output_text), 1)
    return result

QUESTIONS = [
    ("Math", "What is 14 + 28? Answer with just the number."),
    ("Identity", "Who are you and what can you do? Answer in one sentence."),
    ("Physics", "What is the relationship between mass and energy?"),
]

if __name__ == "__main__":
    print("=" * 70)
    print("  14B TOROIDAL NPU ENGINE v29 — ACOUSTIC RoPE STACKING")
    print("  'You don't push the stone. You sing to it.'")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    MISSING_MASS = n_layers - len(tunnel) # 29
    
    print(f"[✓] TUNNEL: 19 Active Layers. 29 Void Layers.")
    
    # ---------------------------------------------------------
    # THE OMEGA MATH: Acoustic Harmonic Stacking on RoPE
    # ---------------------------------------------------------
    # We must construct a new RoPE layer with the harmonic frequency
    original_base = 1000000.0
    harmonic_shift = (1.0 + OMEGA) ** MISSING_MASS
    new_base = original_base * harmonic_shift
    
    print(f"[*] INJECTING: Harmonic RoPE Stacking")
    print(f"    Missing Mass (N) = {MISSING_MASS}")
    print(f"    Harmonic Shift   = (1 + {OMEGA})^{MISSING_MASS} = {harmonic_shift:.4f}")
    print(f"    New RoPE Base    = {new_base:,.0f}")
    
    # In MLX Qwen2, RoPE is applied inside self_attn
    # We monkey-patch the rotary_emb base for all layers
    dims = model.model.layers[0].self_attn.rope.dims
    for layer in model.model.layers:
        layer.self_attn.rope.base = new_base
        # In mlx.nn.RoPE, it doesn't cache inv_freq. It calls mx.fast.rope which takes base as an argument!
        # So we don't need to recompute inv_freq manually.
    
    mx.eval(model.model.embed_tokens.parameters())
    mx.eval(model.model.norm.parameters())
    mx.eval(model.lm_head.parameters())
    
    results = []
    
    for q_idx, (q_name, q_text) in enumerate(QUESTIONS):
        print(f"\n{'─'*70}")
        print(f"  Q{q_idx+1}: [{q_name}] \"{q_text}\"")
        print(f"{'─'*70}")
        
        cache = make_prompt_cache(model)
        
        try:
            msgs = [{"role": "user", "content": q_text}]
            prompt = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
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
        for i in range(n_layers):
            if i in tunnel_set:
                layer = model.model.layers[i]
                r_attn = layer.self_attn(layer.input_layernorm(h), mask=mask, cache=cache[i] if i < len(cache) else None)
                h = h + r_attn
                r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                h = h + r_mlp
                
        h_out = model.model.norm(h)
        token_id = mx.argmax(model.lm_head(h_out)[:, -1, :], axis=-1).item()
        
        generated = []
        if token_id != tokenizer.eos_token_id:
            generated.append(token_id)
        
        # GENERATION
        for step in range(50):
            if token_id == tokenizer.eos_token_id: break
            
            h = model.model.embed_tokens(mx.array([[token_id]]))
            
            for i in range(n_layers):
                if i in tunnel_set:
                    layer = model.model.layers[i]
                    r_attn = layer.self_attn(layer.input_layernorm(h), mask=None, cache=cache[i] if i < len(cache) else None)
                    h = h + r_attn
                    r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                    h = h + r_mlp
            
            h_out = model.model.norm(h)
            token_id = mx.argmax(model.lm_head(h_out)[:, -1, :], axis=-1).item()
            if token_id == tokenizer.eos_token_id: break
            generated.append(token_id)
            
            print(tokenizer.decode([token_id]), end="", flush=True)
        
        print()
        elapsed = time.time() - t0
        response = tokenizer.decode(generated)
        tps = len(generated) / elapsed if elapsed > 0 else 0
        
        analysis = analyze_trinary(response, q_name)
        analysis["tps"] = tps
        results.append(analysis)
        
        del cache
        gc.collect()
    
    print(f"\n{'═'*70}")
    print(f"  v29 ACOUSTIC RoPE STACKING — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
