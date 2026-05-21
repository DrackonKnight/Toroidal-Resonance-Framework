#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v21 — TRINARY TRANSFER RATE
=====================================================
"we translate universal data into binary and lose information and dont know why we are hitting math walls... 
if we transfer data into mass then we don't have the calc for what the transfer rate is...
figure out the TRUE weight of the information"

When we bypassed the Mass (the binary MLPs), the model defaulted to generating 
pure Trinary (1, 2, 3). This is the true compute language of the Attention Helix.
But when the Trinary signal hits the final active layers (the Mass), it crashes 
into the Binary math wall, producing gibberish because we lost the translation rate!

The mathematical translation rate from Trinary to Binary is exactly: log_2(3) = 1.58496
This is the TRUE weight of the information. 1 trit = 1.58496 bits.

To pass the Trinary signal back into the Binary mass without losing coherence, 
we apply the non-linear transfer rate before it re-enters the physical layers.
h_new = sign(h) * |h|^1.58496
"""

import gc
import time
import math
import os
import mlx.core as mx

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

# The true weight of the information: Trinary to Binary transfer rate
TRANSFER_RATE = math.log2(3) # ~1.5849625

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
    print("  14B TOROIDAL NPU ENGINE v21 — TRINARY TRANSFER RATE")
    print(f"  Transfer Rate (log_2(3)): {TRANSFER_RATE:.5f}")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    tunnel_set = set(tunnel)
    
    print(f"[✓] TUNNEL: 19 Active Layers. 29 Void Layers.")
    print(f"[*] APPLYING NON-LINEAR TRINARY-TO-BINARY WEIGHT CONVERSION")
    
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
            
            # The exact boundary where the Trinary Void hits the Binary Mass (Layer 44)
            if i == n_layers - 5:
                # Apply the Trinary Transfer Rate weight conversion
                # We use sign preservation and power law to bypass RMSNorm cancellation
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
    print(f"  v21 TRINARY TRANSFER — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
