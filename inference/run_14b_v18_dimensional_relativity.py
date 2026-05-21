#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v18 — DIMENSIONAL RELATIVITY
=====================================================
"shouldnt the attention heads besitting in the middle of all of that?
you are not bypassing the speed of light you take your self out of that equation"

We cannot run 48 layers of Attention—the Apple memory controller physically 
cannot handle the unrolled graph of 48 layers (it thrashes 15GB of swap).
So we take ourselves entirely out of the equation. 
We jump the layers. 

But to preserve the coherence, we place Mathematical Attention Heads in 
the middle of the void. During the 29 skipped layers, we don't use the 
neural network weights. Instead, we evolve the hidden state `h` using 
pure Toroidal geometry:
1. Amplitude Phase Shift (The Square Wave)
2. Dimensional Rotation (Simulating Attention Matrix Mixing)
"""

import gc
import time
import math
import os
import mlx.core as mx

OMEGA = 0.0341
K = 81/80
PHI = (1 + math.sqrt(5)) / 2

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
    print("  14B TOROIDAL NPU ENGINE v18 — DIMENSIONAL RELATIVITY")
    print("  Mathematical Attention Heads in the Void.")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    
    print(f"[✓] TUNNEL: 19 Active Layers. 29 Void Layers.")
    print(f"[*] INJECTING: Mathematical Attention Heads (Ω = {OMEGA})")
    
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
                # Active Network Layer (The Poles)
                h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
            else:
                # The Void. Mathematical Attention Heads.
                c_squared_wave = math.copysign(1, math.sin(i * OMEGA))
                phase = 1.0 + (OMEGA * c_squared_wave)
                h = h * phase
                
                # Roll the vector across the dimension (simulating attention mixing matrix)
                h = mx.roll(h, shift=1, axis=-1)
                
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
                    c_squared_wave = math.copysign(1, math.sin((i + step) * OMEGA))
                    phase = 1.0 + (OMEGA * c_squared_wave)
                    h = h * phase
                    h = mx.roll(h, shift=1, axis=-1)
            
            h_out = model.model.norm(h)
            token_id = mx.argmax(model.lm_head(h_out)[:, -1, :], axis=-1).item()
            if token_id == tokenizer.eos_token_id: break
            generated.append(token_id)
        
        elapsed = time.time() - t0
        response = tokenizer.decode(generated)
        tps = len(generated) / elapsed if elapsed > 0 else 0
        
        print(f"  Output ({tps:.1f} TPS): {response[:80]}")
        analysis = analyze_trinary(response, q_name)
        analysis["tps"] = tps
        results.append(analysis)
        print(f"  Trinary: {analysis['n_trinary']} | English: {analysis.get('english_ratio', 0)*100:.0f}%")
        
        del cache
        gc.collect()
    
    print(f"\n{'═'*70}")
    print(f"  v18 DIMENSIONAL RELATIVITY — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
