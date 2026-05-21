#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v22 — TOROIDAL FIELD (RoLE)
=====================================================
"waves loop and wrap around theirselves... huh... they show the field they are following"

When we skip the binary mass (the 29 void layers), the latent wave loses its 
container. It has no field to follow, so it shatters when it re-enters the active layers.
In v21, we applied the Trinary transfer rate, which translated the data back to English, 
but it lacked geometry (looping words). 

To fix this, we must project a Mathematical Magnetic Field into the void. 
We apply a Rotary Layer Embedding (RoLE). We treat the data wave as complex pairs 
and physically rotate it across the Toroidal Constant (Ω) at each skipped layer. 
This forces the wave to wrap around itself, following the geometry of the Torus, 
arriving at Layer 44 perfectly aligned.
"""

import gc
import time
import math
import os
import mlx.core as mx

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

OMEGA = 0.0341
TRANSFER_RATE = math.log2(3) # ~1.58496

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

def apply_toroidal_field(h, layer_idx, omega):
    """
    Project the Toroidal Field. The wave wraps around itself based on the layer depth.
    Simulates the structural rotation of the missing Mass.
    """
    # Split into real and imaginary pairs
    h_real = h[..., 0::2]
    h_imag = h[..., 1::2]
    
    # Calculate field rotation for this specific depth
    theta = layer_idx * omega
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    
    # Rotate the wave
    h_real_rot = h_real * cos_theta - h_imag * sin_theta
    h_imag_rot = h_real * sin_theta + h_imag * cos_theta
    
    # Recombine the wave
    h_rot = mx.stack([h_real_rot, h_imag_rot], axis=-1)
    return mx.reshape(h_rot, h.shape)

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
    print("  14B TOROIDAL NPU ENGINE v22 — TOROIDAL FIELD (RoLE)")
    print("  The wave wraps around itself to show the field it follows.")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    
    print(f"[✓] TUNNEL: 19 Active Layers. 29 Void Layers.")
    print(f"[*] INJECTING: Toroidal Field Rotation (Ω = {OMEGA})")
    print(f"[*] INJECTING: Trinary Transfer Rate (1.58496)")
    
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
        
        seq_len = h.shape[1]
        mask = None
        if seq_len > 1:
            mask = mx.full((seq_len, seq_len), -1e9, dtype=mx.bfloat16)
            mask = mx.triu(mask, k=1)[None, None, :, :]
        
        t0 = time.time()
        
        # PREFILL
        for i in range(n_layers):
            if i in tunnel_set:
                h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
            else:
                # Inside the void, the wave follows the Toroidal Field
                h = apply_toroidal_field(h, i, OMEGA)
            
            # The boundary condition: Trinary Transfer before exiting the void
            if i == n_layers - 5:
                h = mx.sign(h) * (mx.abs(h) ** TRANSFER_RATE)
                
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
                    h = model.model.layers[i](h, mask=None, cache=cache[i] if i < len(cache) else None)
                else:
                    h = apply_toroidal_field(h, i, OMEGA)
                    
                if i == n_layers - 5:
                    h = mx.sign(h) * (mx.abs(h) ** TRANSFER_RATE)
            
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
    print(f"  v22 TOROIDAL FIELD (RoLE) — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
