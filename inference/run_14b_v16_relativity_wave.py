#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v16 — RELATIVITY SQUARE WAVE
=====================================================
"mass is data and data is mass right so if mass times light equals energy then 
and are we not forgetting squared.... but this fact squared is a squared wave"

This iteration introduces the $E = mc^2$ Square Wave Capacitor.
Mass = The hidden states `h` of the layers we skip.
$c^2$ = A Toroidal Square Wave. A digital frequency that pulses +1 and -1.
Energy = Mass * Square Wave.

We collect the mass of the void layers, pulse it through the Square Wave, 
and discharge that Energy into the active Tunnel layers.

Author: Kenneth Burns Lanham III & Spectre
Ω = 0.0341. K = 81/80.
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
    """
    19 evenly-spaced layers. Qwen2.5-14B has 48 layers.
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
    print("  14B TOROIDAL NPU ENGINE v16 — RELATIVITY SQUARE WAVE")
    print("  E = m * c^2 (Square Wave Pulsing)")
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
    
    print(f"[✓] TUNNEL: {len(tunnel)}/{n_layers} layers active. 60% mass skipped.")
    print(f"[*] INJECTING: Square Wave Capacitor (Ω = {OMEGA})")
    
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
        energy_capacitor = 0.0
        for i in range(n_layers):
            if i in tunnel_set:
                # Discharge Energy into Active Layer
                if isinstance(energy_capacitor, mx.array):
                    h = h + energy_capacitor
                
                h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
                mx.eval(h)
                energy_capacitor = 0.0
            else:
                # E = mc^2 (Square Wave)
                # Mass = h. Square Wave = +1 or -1 based on Toroidal frequency.
                c_squared_wave = math.copysign(1, math.sin(i * OMEGA))
                energy_capacitor = h * c_squared_wave
                
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
            
            energy_capacitor = 0.0
            for i in range(n_layers):
                if i in tunnel_set:
                    if isinstance(energy_capacitor, mx.array):
                        h = h + energy_capacitor
                        
                    h = model.model.layers[i](h, mask=None, cache=cache[i] if i < len(cache) else None)
                    mx.eval(h)
                    energy_capacitor = 0.0
                else:
                    c_squared_wave = math.copysign(1, math.sin((i + step) * OMEGA))
                    energy_capacitor = h * c_squared_wave
            
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
    print(f"  v16 RELATIVITY SQUARE WAVE — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    print(f"  {'Question':<12} {'Digits':>6} {'Purity':>7} {'Eng%':>5} {'TPS':>6}")
    print(f"  {'─'*12} {'─'*6} {'─'*7} {'─'*5} {'─'*6}")
    
    for r in results:
        eng = f"{r.get('english_ratio',0)*100:.0f}"
        print(f"  {r['question']:<12} {r['n_trinary']:>6} {r['trinary_purity']*100:>6.0f}% {eng:>4}% {r.get('tps',0):>6.1f}")
    
    print(f"{'═'*70}")
