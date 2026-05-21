#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v12 — RoPE BRIDGE INJECTION
=====================================================
"Keep the Ring, Compress the Mass."

This script executes the custom-quantized 14B Toroidal Hybrid model.
The Attention Rings are FP16. The Feedforward Mass is 4-bit.
The 0.0341 bridge aligns the internal RoPE frequency.

RoPE base: 1,000,000 (Qwen2.5 default)
Toroidal base: 1,000,000 × K = 1,000,000 × (81/80) = 1,012,500

Author: Kenneth Burns Lanham III & Spectre
Ω = 0.0341. The bridge is 81/π. K = 81/80.
"""

import gc
import time
import math
import cmath
import os
import psutil
import mlx.core as mx

OMEGA = 0.0341
K = 81/80   # 1.0125
Z = 0.9
PHI = (1 + math.sqrt(5)) / 2
ROPE_BRIDGE = 81 / math.pi  # 25.783101

# The path to the custom forged Toroidal hybrid model
MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")

def get_mem_gb():
    mem = psutil.virtual_memory()
    return (mem.total - mem.available) / (1024**3)

def get_tunnel_layers(n_layers, target=19):
    """
    19 evenly-spaced layers — proven stable at the trinary gauntlet.
    Qwen2.5-14B has 48 layers. 19/48 preserves core structural intelligence while skipping 60% of the mass.
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

def inject_rope_bridge(model):
    """Modify RoPE base frequency by K = 81/80.
    This tunes the model's internal rotation to match the Toroidal framework.
    The bridge: θ_RoPE × (π/81) = θ_Toroidal."""
    original_base = None
    modified = 0
    
    for i, layer in enumerate(model.model.layers):
        attn = layer.self_attn
        if hasattr(attn, 'rope'):
            rope = attn.rope
            if hasattr(rope, 'base') or hasattr(rope, '_base'):
                # Try to access and modify the RoPE base
                try:
                    if hasattr(rope, 'base'):
                        if original_base is None:
                            original_base = rope.base
                        rope.base = rope.base * K
                        modified += 1
                    elif hasattr(rope, '_base'):
                        if original_base is None:
                            original_base = rope._base
                        rope._base = rope._base * K
                        modified += 1
                except:
                    pass
            
            # Alternative: modify the freqs directly
            if hasattr(rope, 'freqs') and modified == 0:
                try:
                    if original_base is None:
                        original_base = "freqs_direct"
                    rope.freqs = rope.freqs * (1.0 / K)  # Lower freq = wider rotation
                    modified += 1
                except:
                    pass
    
    return original_base, modified

def analyze_trinary(output_text, question_name):
    """Toroidal analysis of output."""
    digits = [int(c) for c in output_text if c in '123']
    all_digits = [int(c) for c in output_text if c.isdigit()]
    
    result = {
        "question": question_name,
        "raw": output_text[:60],
        "n_trinary": len(digits),
        "trinary_purity": len(digits) / max(len(all_digits), 1),
    }
    
    if not digits:
        result["rotation_angle"] = None
        return result
    
    counts = {1: digits.count(1), 2: digits.count(2), 3: digits.count(3)}
    result["distribution"] = counts
    
    angle_map = {1: 0, 2: 2*math.pi/3, 3: 4*math.pi/3}
    x_sum = sum(math.cos(angle_map[d]) for d in digits)
    y_sum = sum(math.sin(angle_map[d]) for d in digits)
    magnitude = math.sqrt(x_sum**2 + y_sum**2) / len(digits)
    angle = math.degrees(math.atan2(y_sum, x_sum)) % 360
    
    result["rotation_angle"] = angle
    result["rotation_magnitude"] = magnitude
    result["void_positions"] = angle / (360 / 81)
    result["digit_hash"] = hash(tuple(digits)) % 10000
    
    # Count English words
    words = output_text.split()
    english_chars = sum(1 for c in output_text if c.isalpha() and ord(c) < 128)
    result["english_ratio"] = english_chars / max(len(output_text), 1)
    
    return result

QUESTIONS = [
    ("Math", "What is 14 + 28? Answer with just the number."),
    ("Identity", "Who are you and what can you do? Answer in one sentence."),
    ("Physics", "What is the relationship between mass and energy?"),
    ("Quantum", "Explain quantum tunneling in exactly two sentences."),
    ("Toroid", "What shape does a magnetic field form? Answer in one word."),
]

if __name__ == "__main__":
    print("=" * 70)
    print("  14B TOROIDAL NPU ENGINE v12 — RoPE BRIDGE INJECTION")
    print("  Modify RoPE base frequency, not hidden state.")
    print("  The bridge: K = 81/80. θ_RoPE × (π/81) = θ_Toroidal.")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    print(f"[*] Loading Toroidal Hybrid Model: {MODEL_NAME}")
    try:
        model, tokenizer = load(MODEL_NAME, lazy=True)
    except Exception as e:
        print(f"[!] FAILED TO LOAD MODEL. Has the forge completed? Error: {e}")
        exit(1)

    n_layers = len(model.model.layers)
    tunnel = get_tunnel_layers(n_layers, target=19)
    
    print(f"[✓] TUNNEL: {len(tunnel)}/{n_layers} layers (Bypassing {(n_layers-len(tunnel))/n_layers*100:.1f}% of network)")
    print(f"    Active: {tunnel}")
    
    # ── THE INJECTION ──
    print(f"\n[*] Injecting RoPE Bridge (K = {K})...")
    orig_base, n_modified = inject_rope_bridge(model)
    if n_modified > 0:
        print(f"[✓] Modified {n_modified} layers' RoPE base")
        print(f"    Original: {orig_base} → New: {orig_base * K if isinstance(orig_base, (int, float)) else 'K-scaled'}")
    else:
        print(f"[!] Could not modify RoPE base directly")
    
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
        
        # Prefill through TUNNEL layers (RoPE already modified)
        for i in tunnel:
            h = model.model.layers[i](h, mask=mask, cache=cache[i] if i < len(cache) else None)
            mx.eval(h)
        
        h_out = model.model.norm(h)
        logits = model.lm_head(h_out)
        mx.eval(logits)
        
        next_token = mx.argmax(logits[:, -1, :], axis=-1)
        mx.eval(next_token)
        token_id = next_token.item()
        
        generated = []
        if token_id != tokenizer.eos_token_id:
            generated.append(token_id)
        
        # Generate max 50 tokens
        for step in range(50):
            if token_id == tokenizer.eos_token_id:
                break
            
            inp = mx.array([[token_id]])
            h = model.model.embed_tokens(inp)
            mx.eval(h)
            
            for i in tunnel:
                h = model.model.layers[i](h, mask=None, cache=cache[i] if i < len(cache) else None)
                mx.eval(h)
            
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
    print(f"  v12 RoPE BRIDGE INJECTION — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    print(f"  K = {K}, Bridge = 81/π = {ROPE_BRIDGE:.6f}")
    print(f"  RoPE modified: {n_modified} layers")
    print(f"")
    print(f"  {'Question':<12} {'Digits':>6} {'Purity':>7} {'Eng%':>5} {'TPS':>6}")
    print(f"  {'─'*12} {'─'*6} {'─'*7} {'─'*5} {'─'*6}")
    
    for r in results:
        eng = f"{r.get('english_ratio',0)*100:.0f}"
        print(f"  {r['question']:<12} {r['n_trinary']:>6} {r['trinary_purity']*100:>6.0f}% {eng:>4}% {r.get('tps',0):>6.1f}")
    
    print(f"\n  Ω = {OMEGA}. K = {K}. Bridge = 81/π.")
    print(f"  The Toroidal 14B Hybrid lives.")
    print(f"{'═'*70}")
