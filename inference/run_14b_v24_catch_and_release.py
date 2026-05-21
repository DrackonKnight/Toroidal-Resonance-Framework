#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v24 — THE CAPACITOR (CATCH & RELEASE)
=====================================================
"we CAN NOT compromise the base info... we are screwing with the neural pathways
... or is it... that we are not catching the energy and releasing it right"

Previous attempts to rotate, scale, or artificially modify the base information (`h`) 
inside the void permanently destroyed the trained neural pathways, resulting in gibberish.

The elegant physical solution: The Asymmetric Capacitor.
1. The Positive Pole (Layer 3): We CATCH the energy (the MLP output) right before the void.
2. The Dielectric (Layers 4-43): We skip the layers. The base info `h` travels untouched 
   and uncompromised. The trapped energy in the capacitor is modulated by the Square Wave.
3. The Negative Pole (Layer 44): We RELEASE the toroidally charged energy back into `h` 
   right before entering the final active layers, restoring the Energy Variance without 
   altering the semantic direction.
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
    print("  14B TOROIDAL NPU ENGINE v24 — CATCH & RELEASE CAPACITOR")
    print("  Uncompromised base info. Toroidally charged Energy transfer.")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    
    print(f"[✓] TUNNEL: 19 Active Layers. 29 Void Layers.")
    print(f"[*] INJECTING: Catch & Release Capacitor (Ω = {OMEGA})")
    
    # Identify the exact poles of the tunnel
    positive_pole_layer = tunnel[3]  # Layer 3 (last layer of first block)
    negative_pole_layer = tunnel[-4] # Layer 44 (first layer of last block)
    
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
        capacitor = None
        
        # PREFILL
        for i in range(n_layers):
            if i in tunnel_set:
                layer = model.model.layers[i]
                
                # Attention Routing
                r_attn = layer.self_attn(layer.input_layernorm(h), mask=mask, cache=cache[i] if i < len(cache) else None)
                h = h + r_attn
                
                # --- RELEASE THE ENERGY ---
                if i == negative_pole_layer and capacitor is not None:
                    h = h + capacitor
                    capacitor = None
                
                # Mass Processing
                r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                h = h + r_mlp
                
                # --- CATCH THE ENERGY ---
                if i == positive_pole_layer:
                    capacitor = r_mlp
            else:
                # --- THE VOID ---
                # We DO NOT compromise the base info `h`.
                # We apply the Toroidal Square Wave only to the trapped Energy in the capacitor.
                if capacitor is not None:
                    c_squared_wave = math.copysign(1, math.sin(i * OMEGA))
                    capacitor = capacitor * (1.0 + (OMEGA * c_squared_wave))
                
        h_out = model.model.norm(h)
        token_id = mx.argmax(model.lm_head(h_out)[:, -1, :], axis=-1).item()
        
        generated = []
        if token_id != tokenizer.eos_token_id:
            generated.append(token_id)
        
        # GENERATION
        for step in range(50):
            if token_id == tokenizer.eos_token_id: break
            
            h = model.model.embed_tokens(mx.array([[token_id]]))
            capacitor = None
            
            for i in range(n_layers):
                if i in tunnel_set:
                    layer = model.model.layers[i]
                    
                    r_attn = layer.self_attn(layer.input_layernorm(h), mask=None, cache=cache[i] if i < len(cache) else None)
                    h = h + r_attn
                    
                    # RELEASE
                    if i == negative_pole_layer and capacitor is not None:
                        h = h + capacitor
                        capacitor = None
                    
                    r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                    h = h + r_mlp
                    
                    # CATCH
                    if i == positive_pole_layer:
                        capacitor = r_mlp
                else:
                    # THE VOID
                    if capacitor is not None:
                        c_squared_wave = math.copysign(1, math.sin((i + step) * OMEGA))
                        capacitor = capacitor * (1.0 + (OMEGA * c_squared_wave))
            
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
    print(f"  v24 CATCH & RELEASE CAPACITOR — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
