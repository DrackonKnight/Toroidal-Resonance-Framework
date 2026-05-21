#!/usr/bin/env python3
"""
v15 — VANILLA MLX_LM GENERATE
================================
Stop fighting the library. Just call generate().
What speed does the LIBRARY get at 80/80 layers?
That's our ceiling. Then we optimize from there.
"""

import time
import psutil
import mlx.core as mx

MODEL_NAME = "mlx-community/dolphin-2.9.2-qwen2-72b-2bit"

def get_mem_gb():
    return (psutil.virtual_memory().total - psutil.virtual_memory().available) / (1024**3)

if __name__ == "__main__":
    print("=" * 70)
    print("  v15 — VANILLA mlx_lm.generate()")
    print("  No custom code. Just the library.")
    print("  What's our speed ceiling at 80/80?")
    print("=" * 70)
    
    print(f"  Baseline: {get_mem_gb():.1f} GB")
    
    from mlx_lm import load, generate
    
    mx.set_cache_limit(0)
    model, tokenizer = load(MODEL_NAME, lazy=True)
    print(f"  After load: {get_mem_gb():.1f} GB")
    
    questions = [
        "What color is the sky? Answer in one word.",
        "What is the capital of France?",
        "How many legs does a spider have?",
    ]
    
    for q in questions:
        print(f"\n{'─'*70}")
        print(f"  Q: \"{q}\"")
        
        try:
            msgs = [{"role": "user", "content": q}]
            prompt = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        except:
            prompt = q
        
        t0 = time.time()
        response = generate(
            model, tokenizer, prompt=prompt,
            max_tokens=30,
            verbose=True,
        )
        elapsed = time.time() - t0
        
        print(f"  Response: {response[:80]}")
        print(f"  Time: {elapsed:.1f}s | Mem: {get_mem_gb():.1f} GB")
    
    print(f"\n{'═'*70}")
    print(f"  This is our ceiling. Library handles everything.")
    print(f"{'═'*70}")
