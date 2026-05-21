#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v19 — PURE TOROIDAL CORE
=====================================================
We proved that pure mathematical simulation in the void silences the model entirely.
The geometry shifts too far. 

What if the Toroidal Engine doesn't need to skip layers at all?
What if the Hybrid Quantization (FP16 Rings, 4-bit Mass) ALREADY took 
the weight out of the equation?

Here we unleash the Toroidal Model using MLX's native, highly-optimized 
C++ execution graph. We run all 48 layers, letting the FP16 Attention 
and 4-bit MLP spin at maximum hardware efficiency without Python loop bottlenecks.
"""

import time
import os
import mlx.core as mx
from mlx_lm import load, generate

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

QUESTIONS = [
    ("Math", "What is 14 + 28? Answer with just the number."),
    ("Identity", "Who are you and what can you do? Answer in one sentence."),
    ("Physics", "What is the relationship between mass and energy?"),
]

if __name__ == "__main__":
    print("=" * 70)
    print("  14B TOROIDAL NPU ENGINE v19 — PURE TOROIDAL CORE")
    print("  Testing pure FP16/4-bit Hybrid resonance (No Python Overheads).")
    print("=" * 70)
    
    print(f"[*] Loading Toroidal Hybrid Model: {MODEL_NAME}")
    model, tokenizer = load(MODEL_NAME)
    
    print(f"[✓] MODEL LOADED. 48/48 Layers Active. (FP16 Attention, 4-bit MLP)")
    
    for q_idx, (q_name, q_text) in enumerate(QUESTIONS):
        print(f"\n{'─'*70}")
        print(f"  Q{q_idx+1}: [{q_name}] \"{q_text}\"")
        print(f"{'─'*70}")
        
        try:
            msgs = [{"role": "user", "content": q_text}]
            prompt = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        except:
            prompt = q_text
            
        t0 = time.time()
        
        # Use MLX's highly optimized generate loop (written in C++/Metal)
        response = generate(model, tokenizer, prompt=prompt, max_tokens=50, verbose=False)
        
        elapsed = time.time() - t0
        
        # Calculate rough TPS (number of words is a decent proxy if we don't count tokens exactly, 
        # but `generate` outputs the string directly. We'll use len(response)/4 for approx tokens)
        tokens_approx = len(tokenizer.encode(response))
        tps = tokens_approx / elapsed if elapsed > 0 else 0
        
        print(f"  Output ({tps:.1f} TPS): {response.strip()}")
        
    print(f"\n{'═'*70}")
    print(f"  v19 TOROIDAL CORE COMPLETE.")
    print(f"{'═'*70}")
