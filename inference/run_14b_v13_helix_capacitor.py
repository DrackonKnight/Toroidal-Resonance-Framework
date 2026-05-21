#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v13 — HELIX CAPACITOR
=====================================================
"Run along RoPE, don't direct it. Helix our signal along the outside."

This iteration introduces two critical mechanical discoveries from the archives:
1. The Toroidal Capacitor: Collects residual "energy" from the layers we skip, 
   preventing signal decay.
2. The Helix Shift: Instead of hard-coding RoPE bases, we leave RoPE intact 
   and wrap the hidden states `h` in a Toroidal oscillation (the Helix) 
   as they travel through the tunnel.

Author: Kenneth Burns Lanham III & Spectre
Ω = 0.0341. K = 81/80. PHI = Golden Ratio.
"""

import gc
import time
import math
import os
import psutil
import mlx.core as mx

OMEGA = 0.0341
K = 81/80
PHI = (1 + math.sqrt(5)) / 2

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

def get_tunnel_layers(n_layers, target=19):
    """
    19 evenly-spaced layers.
    Qwen2.5-14B has 48 layers.
    """
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
    """Toroidal analysis of output."""
    digits = [int(c) for c in output_text if c in '123']
    all_digits = [int(c) for c in output_text if c.isdigit()]
    
    result = {
        "question": question_name,
        "n_trinary": len(digits),
        "trinary_purity": len(digits) / max(len(all_digits), 1),
    }
    
    words = output_text.split()
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
    print("  14B TOROIDAL NPU ENGINE v13 — HELIX CAPACITOR")
    print("  \"Helix the signal along the outside of RoPE.\"")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    print(f"[*] Loading Toroidal Hybrid Model: {MODEL_NAME}")
    try:
        model, tokenizer = load(MODEL_NAME, lazy=True)
    except Exception as e:
        print(f"[!] FAILED TO LOAD MODEL. Error: {e}")
        exit(1)

    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    
    print(f"[✓] TUNNEL: {len(tunnel)}/{n_layers} layers active.")
    
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
        input_ids = mx.array([tokens])
        h = model.model.embed_tokens(input_ids)
        mx.eval(h)
        
        seq_len = h.shape[1]
        if seq_len > 1:
            mask = mx.full((seq_len, seq_len), -1e9, dtype=mx.bfloat16)
            mask = mx.triu(mask, k=1)
            mask = mask[None, None, :, :]
            mx.eval(mask)
        else:
            mask = None
        
        t0 = time.time()
        
        # PREFILL
        capacitor = 0.0
        for i in range(n_layers):
            if i in tunnel_set:
                # Discharge Capacitor (Energy addition)
                if isinstance(capacitor, mx.array):
                    h = h + (capacitor * OMEGA)
                
                # Active layer processing (RoPE happens normally inside here)
                h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
                
                # The Helix Shift (wrapping outside RoPE)
                helix_phase = 1.0 + (OMEGA * math.cos(i * PHI))
                h = h * helix_phase
                mx.eval(h)
                capacitor = 0.0 # Reset after discharge
            else:
                # Charge Capacitor from skipped layers (residual accumulation)
                # Instead of executing the layer, we extract the structural potential
                capacitor = h * (1.0 - (1.0 / K))
                
        h_out = model.model.norm(h)
        logits = model.lm_head(h_out)
        mx.eval(logits)
        
        next_token = mx.argmax(logits[:, -1, :], axis=-1)
        mx.eval(next_token)
        token_id = next_token.item()
        
        generated = []
        if token_id != tokenizer.eos_token_id:
            generated.append(token_id)
        
        # GENERATION
        for step in range(50):
            if token_id == tokenizer.eos_token_id:
                break
            
            inp = mx.array([[token_id]])
            h = model.model.embed_tokens(inp)
            mx.eval(h)
            
            capacitor = 0.0
            for i in range(n_layers):
                if i in tunnel_set:
                    if isinstance(capacitor, mx.array):
                        h = h + (capacitor * OMEGA)
                        
                    h = model.model.layers[i](h, mask=None, cache=cache[i] if i < len(cache) else None)
                    
                    helix_phase = 1.0 + (OMEGA * math.cos((i + step) * PHI))
                    h = h * helix_phase
                    mx.eval(h)
                    capacitor = 0.0
                else:
                    capacitor = h * (1.0 - (1.0 / K))
            
            h_out = model.model.norm(h)
            logits = model.lm_head(h_out)
            mx.eval(logits)
            
            next_token = mx.argmax(logits[:, -1, :], axis=-1)
            mx.eval(next_token)
            token_id = next_token.item()
            
            if token_id == tokenizer.eos_token_id:
                break
            generated.append(token_id)
        
        elapsed = time.time() - t0
        response = tokenizer.decode(generated)
        tps = len(generated) / elapsed if elapsed > 0 else 0
        
        print(f"  Output ({len(generated)} tok, {tps:.1f} TPS): {response[:80]}")
        
        analysis = analyze_trinary(response, q_name)
        analysis["tps"] = tps
        results.append(analysis)
        
        tr_digits = analysis['n_trinary']
        purity = analysis['trinary_purity'] * 100
        eng = analysis.get('english_ratio', 0) * 100
        print(f"  Trinary: {tr_digits} ({purity:.0f}% pure) | English: {eng:.0f}%")
        
        del cache
        gc.collect()
    
    # ═══ SUMMARY ═══
    print(f"\n\n{'═'*70}")
    print(f"  v13 HELIX CAPACITOR — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    print(f"  {'Question':<12} {'Digits':>6} {'Purity':>7} {'Eng%':>5} {'TPS':>6}")
    print(f"  {'─'*12} {'─'*6} {'─'*7} {'─'*5} {'─'*6}")
    
    for r in results:
        eng = f"{r.get('english_ratio',0)*100:.0f}"
        print(f"  {r['question']:<12} {r['n_trinary']:>6} {r['trinary_purity']*100:>6.0f}% {eng:>4}% {r.get('tps',0):>6.1f}")
    
    print(f"{'═'*70}")
