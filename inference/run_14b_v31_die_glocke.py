#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v31 — DIE GLOCKE (THE COUNTER-ROTATING BELL)
=====================================================
v30 failed. The Mac physically crashed into Swap Memory because 
the 14B Toroidal model (FP16 Attention + 4-bit MLP) is 19.6 GB. 
It literally cannot fit in 16GB of Unified Memory simultaneously.

Kenneth was right. The Toroidal Tunneler (Skipping 29 Layers) is 
mathematically the ONLY way to make this run on the hardware. 
But how do we carry the Base Info across the void without scrambling the grammar?

"Die Glocke (Nazi Bell): bell-shaped, counter-rotating... The shape IS the technology."

If we create a single rotating Toroidal field (v27 Holographic Capacitor), 
the semantic vectors rotate out of alignment and the grammar shatters.
But if we use TWO COUNTER-ROTATING FIELDS:
Wave A rotates by +Ω.
Wave B rotates by -Ω.
When we sum them (Wave A + Wave B), the imaginary (scrambling) torque 
perfectly cancels out mathematically (sin(θ) + sin(-θ) = 0). 
We are left with pure, unscrambled longitudinal wave resonance (2*cos(θ)).

1. CATCH the mass energy at Layer 4.
2. Split it into Counter-Rotating Bell Capacitors (+Ω and -Ω).
3. Accumulate them across the 29 void layers.
4. RELEASE their sum into Layer 44.
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

def rotate_energy(h, layer_idx, omega):
    h_real = h[..., 0::2]
    h_imag = h[..., 1::2]
    
    theta = layer_idx * omega
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    
    h_real_rot = h_real * cos_theta - h_imag * sin_theta
    h_imag_rot = h_real * sin_theta + h_imag * cos_theta
    
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
    print("  14B TOROIDAL NPU ENGINE v31 — DIE GLOCKE")
    print("  Counter-Rotating Dual Capacitors to Cancel Semantic Torque")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    # LAZY LOADING IS MANDATORY to survive 16GB VRAM bounds
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    
    print(f"[✓] TUNNEL: 19 Active Layers. 29 Void Layers.")
    print(f"[*] INJECTING: Counter-Rotating Bell Capacitors (+Ω, -Ω = {OMEGA})")
    
    positive_pole_layer = tunnel[3]  
    negative_pole_layer = tunnel[-4] 
    
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
        
        base_capacitor = None
        capacitor_CW = None
        capacitor_CCW = None
        
        # PREFILL
        for i in range(n_layers):
            if i in tunnel_set:
                layer = model.model.layers[i]
                
                # --- RELEASE: DIE GLOCKE ---
                if i == negative_pole_layer and capacitor_CW is not None:
                    # The imaginary torque cancels out, injecting pure resonance
                    h = h + (capacitor_CW + capacitor_CCW)
                    base_capacitor = None
                    capacitor_CW = None
                    capacitor_CCW = None
                
                h_prev = h
                r_attn = layer.self_attn(layer.input_layernorm(h), mask=mask, cache=cache[i] if i < len(cache) else None)
                h = h + r_attn
                
                r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                h = h + r_mlp
                
                # --- CATCH ---
                if i == positive_pole_layer:
                    base_capacitor = h - h_prev
                    capacitor_CW = mx.zeros_like(h)
                    capacitor_CCW = mx.zeros_like(h)
            else:
                # --- THE VOID: COUNTER-ROTATION ---
                if base_capacitor is not None:
                    # Clockwise Wave (+Ω)
                    wave_CW = rotate_energy(base_capacitor, i, OMEGA)
                    capacitor_CW = capacitor_CW + wave_CW
                    
                    # Counter-Clockwise Wave (-Ω)
                    wave_CCW = rotate_energy(base_capacitor, i, -OMEGA)
                    capacitor_CCW = capacitor_CCW + wave_CCW
                
        h_out = model.model.norm(h)
        token_id = mx.argmax(model.lm_head(h_out)[:, -1, :], axis=-1).item()
        
        generated = []
        if token_id != tokenizer.eos_token_id:
            generated.append(token_id)
        
        # GENERATION
        for step in range(50):
            if token_id == tokenizer.eos_token_id: break
            
            h = model.model.embed_tokens(mx.array([[token_id]]))
            
            base_capacitor = None
            capacitor_CW = None
            capacitor_CCW = None
            
            for i in range(n_layers):
                if i in tunnel_set:
                    layer = model.model.layers[i]
                    
                    # --- RELEASE ---
                    if i == negative_pole_layer and capacitor_CW is not None:
                        h = h + (capacitor_CW + capacitor_CCW)
                        base_capacitor = None
                        capacitor_CW = None
                        capacitor_CCW = None
                        
                    h_prev = h
                    r_attn = layer.self_attn(layer.input_layernorm(h), mask=None, cache=cache[i] if i < len(cache) else None)
                    h = h + r_attn
                    
                    r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                    h = h + r_mlp
                    
                    # --- CATCH ---
                    if i == positive_pole_layer:
                        base_capacitor = h - h_prev
                        capacitor_CW = mx.zeros_like(h)
                        capacitor_CCW = mx.zeros_like(h)
                else:
                    # --- THE VOID ---
                    if base_capacitor is not None:
                        # Clockwise Wave
                        wave_CW = rotate_energy(base_capacitor, i + step, OMEGA)
                        capacitor_CW = capacitor_CW + wave_CW
                        
                        # Counter-Clockwise Wave
                        wave_CCW = rotate_energy(base_capacitor, i + step, -OMEGA)
                        capacitor_CCW = capacitor_CCW + wave_CCW
            
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
    print(f"  v31 DIE GLOCKE — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
