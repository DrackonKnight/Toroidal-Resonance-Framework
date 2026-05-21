#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v15 — FULL RESONANCE
=====================================================
"The energy of the data. Helix our signal."

We tried layer-skipping (the tunnel) on the 14B architecture. 
But Qwen 14B is too dense; removing 60% of the layers shatters the coherence.
Instead, we rely entirely on the Toroidal Forge Quantization we just completed:
- Attention Rings (The Signal) are in pure FP16.
- MLP Mass (The Weight) is crushed to 4-bit.

We run ALL 48 layers. Because the mass is crushed, the Mac can spin it at high TPS.
Because the rings are FP16, the intelligence stays pure.
"""

import gc
import time
import math
import os
import mlx.core as mx

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

QUESTIONS = [
    ("Math", "What is 14 + 28? Answer with just the number."),
    ("Identity", "Who are you and what can you do? Answer in one sentence."),
    ("Physics", "What is the relationship between mass and energy?"),
]

if __name__ == "__main__":
    print("=" * 70)
    print("  14B TOROIDAL NPU ENGINE v15 — PURE RESONANCE")
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
    
    print(f"[✓] ACTIVE LAYERS: {n_layers}/{n_layers} (Running pure Toroidal geometry)")
    
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
        for i in range(n_layers):
            h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
        
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
            
            for i in range(n_layers):
                h = model.model.layers[i](h, mask=None, cache=cache[i] if i < len(cache) else None)
            
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
        
        del cache
        gc.collect()
    
    print(f"\n{'═'*70}")
    print(f"  v15 RESONANCE COMPLETE.")
    print(f"{'═'*70}")
