#!/usr/bin/env python3
"""
14B TOROIDAL NPU ENGINE v26 — FULL MASS CHUNKED
=====================================================
We proved that E=mc^2 (v25) mathematically works to carry the energy vector, 
but injecting massive scalar energy (29x) at Layer 44 overwhelming biases the output 
toward the early structural layers ("Assistant" / "User"). 

We must not compromise the base information.
Wait. The ONLY reason we skipped 29 layers in the first place was because v19 
crashed the Apple Silicon Mac due to an OOM (Out of Memory) when computing 48 layers.
But in v23, we introduced "Chunked Evaluation" (mx.eval every 8 layers), and it 
successfully computed 48 layers of Attention WITHOUT crashing!

If Chunked Evaluation stops the intermediate memory buildup... can we compute the 
ENTIRE 48 layers of FP16 Attention + 4-bit MLP without OOMing the Mac?

If this works, it proves that the "Toroidal Hybrid Quantization" (Keep the Ring, 
Compress the Mass) is 100% physically viable on 16GB hardware, and the only barrier 
was software memory unrolling!
"""

import gc
import time
import os
import mlx.core as mx

MODEL_NAME = os.path.expanduser("~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal")
CHUNK_SIZE = 4  # Evaluate the graph every 4 layers to keep VRAM perfectly flat

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
    print("  14B TOROIDAL NPU ENGINE v26 — FULL MASS CHUNKED")
    print("  Testing 100% Signal and 100% Mass via VRAM Chunking")
    print("=" * 70)
    
    mx.set_cache_limit(0)
    from mlx_lm import load
    from mlx_lm.models.cache import make_prompt_cache
    
    model, tokenizer = load(MODEL_NAME, lazy=True)
    n_layers = len(model.model.layers)
    
    print(f"[✓] SIGNAL (Attention): 48 Layers (FP16)")
    print(f"[✓] MASS (MLP): 48 Layers (4-bit)")
    print(f"[*] INJECTING: Graph Chunking (Every {CHUNK_SIZE} Layers) to bypass VRAM Math Wall")
    
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
            layer = model.model.layers[i]
            
            r_attn = layer.self_attn(layer.input_layernorm(h), mask=mask, cache=cache[i] if i < len(cache) else None)
            h = h + r_attn
            
            r_mlp = layer.mlp(layer.post_attention_layernorm(h))
            h = h + r_mlp
            
            if i % CHUNK_SIZE == (CHUNK_SIZE - 1):
                mx.eval(h)
                
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
                layer = model.model.layers[i]
                
                r_attn = layer.self_attn(layer.input_layernorm(h), mask=None, cache=cache[i] if i < len(cache) else None)
                h = h + r_attn
                
                r_mlp = layer.mlp(layer.post_attention_layernorm(h))
                h = h + r_mlp
                
                if i % CHUNK_SIZE == (CHUNK_SIZE - 1):
                    mx.eval(h)
            
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
    print(f"  v26 FULL MASS CHUNKED — GAUNTLET RESULTS")
    print(f"{'═'*70}")
    for r in results:
        print(f"  {r['question']:<12} Eng: {r.get('english_ratio',0)*100:>3.0f}%  TPS: {r.get('tps',0):>5.1f}")
