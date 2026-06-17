#!/usr/bin/env python3
"""
KV Cache Extract, Wipe & Reinject — Baseline Verification
==========================================================
Proves that a transformer's KV cache state can be cleanly serialized,
wiped from active RAM, and reinjected into a fresh cache object to
restore semantic memory.

Part of the Toroidal Resonance Framework.
Author: Kenneth Burns Lanham III
Hardware: Apple M4, 16GB, MLX 0.31.3
"""
import os
import sys
import types
from typing import Optional, Any
import mlx.core as mx
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache

# Core Constants
OMEGA = 0.0341
KOMMA = 1.0125

print("=" * 60)
print("  KV CACHE BRIDGE TEST — Extract, Wipe, Reinject")
print("=" * 60)

MODEL_PATH = "mlx-community/gemma-4-e4b-it-OptiQ-4bit"

print(f"[*] Loading model: {MODEL_PATH}...")
try:
    model, tokenizer = load(MODEL_PATH)
    print("[*] Model loaded.")
except Exception as e:
    print(f"[FATAL] Could not load model: {e}")
    sys.exit(1)

# ==============================================================================
# KV CACHE EXTRACT, WIPE, AND REINJECT
# ==============================================================================
print("\n" + "=" * 50)
print(" EXTRACT, WIPE, AND REINJECT")
print("=" * 50)

# Encode context containing two facts
context_messages = [
    {"role": "user", "content": "The secret code is 8180. The core constant is Omega = 0.0341."}
]
context_prompt = tokenizer.apply_chat_template(
    context_messages, tokenize=False, add_generation_prompt=False
)
context_tokens = mx.array([tokenizer.encode(context_prompt)])

print(f"[*] Context: '{context_prompt.strip()}'")
print(f"[*] Token count: {context_tokens.shape[1]}")

# Populate KV cache
cache_active = make_prompt_cache(model)
lm = model.language_model if hasattr(model, "language_model") else model
_ = lm(context_tokens, cache=cache_active)
mx.eval([c.state for c in cache_active])
print("[*] KV cache populated.")

# Extract all layer states
print("[*] Extracting KV cache state...")
saved_states = []
for i, c in enumerate(cache_active):
    if not c.empty():
        keys, values = c.state
        state_dict = {
            "keys": mx.array(keys),
            "values": mx.array(values),
            "offset": c.offset,
            "type": c.__class__.__name__,
        }
        if hasattr(c, "keep"):
            state_dict["keep"] = c.keep
        if hasattr(c, "max_size"):
            state_dict["max_size"] = c.max_size
        if hasattr(c, "_idx"):
            state_dict["_idx"] = c._idx
        saved_states.append(state_dict)
    else:
        saved_states.append(None)

print(f"  -> {len(saved_states)} layer states extracted.")

# TOTAL WIPE
print("\n[*] DESTROYING active cache from RAM...")
del cache_active
print("[*] Cache deleted.")

# Fresh empty cache
cache_new = make_prompt_cache(model)
print(f"[*] Fresh cache created. First layer empty? {cache_new[0].empty()}")

# Reinject
print("\n[*] REINJECTING saved states...")
for i, saved in enumerate(saved_states):
    if saved is not None:
        c = cache_new[i]
        c.state = (saved["keys"], saved["values"])
        c.offset = saved["offset"]
        if "keep" in saved and hasattr(c, "keep"):
            c.keep = saved["keep"]
        if "max_size" in saved and hasattr(c, "max_size"):
            c.max_size = saved["max_size"]
        if "_idx" in saved and hasattr(c, "_idx"):
            c._idx = saved["_idx"]

print(f"  -> First layer empty now? {cache_new[0].empty()}")
print(f"  -> Offset: {cache_new[0].offset} | Shape: {cache_new[0].keys.shape}")

# Query
question_msg = "What is the secret code and the core constant?"
print(f"\n[*] Query: '{question_msg}'")

full_messages = context_messages + [{"role": "user", "content": question_msg}]
full_prompt = tokenizer.apply_chat_template(
    full_messages, tokenize=False, add_generation_prompt=True
)
full_tokens = tokenizer.encode(full_prompt)

new_tokens_start = context_tokens.shape[1]
question_token_ids = full_tokens[new_tokens_start:]

print(f"[*] Prefilling {len(question_token_ids)} question tokens...")
for token_id in question_token_ids[:-1]:
    _ = lm(mx.array([[token_id]]), cache=cache_new)
    mx.eval([c.state for c in cache_new])

print("\n--- MODEL OUTPUT (from reinjected cache) ---")
print("[Output]: ", end="", flush=True)

last_token_id = question_token_ids[-1]
logits = lm(mx.array([[last_token_id]]), cache=cache_new)
mx.eval(logits)
token = mx.argmax(logits[:, -1, :], axis=-1).item()

output_tokens = []
for step in range(60):
    if token == tokenizer.eos_token_id:
        break
    output_tokens.append(token)
    print(tokenizer.decode([token]), end="", flush=True)
    next_input = mx.array([[token]])
    logits = lm(next_input, cache=cache_new)
    mx.eval(logits)
    token = mx.argmax(logits[:, -1, :], axis=-1).item()

answer = tokenizer.decode(output_tokens)
print("\n" + "-" * 46)

if "8180" in answer and "0.0341" in answer:
    print("RESULT: BOTH FACTS RECALLED — Cache bridge verified.")
elif "8180" in answer or "0.0341" in answer:
    print("RESULT: PARTIAL RECALL — One fact survived.")
else:
    print("RESULT: RECALL FAILED — Cache reinjection did not preserve memory.")

print("=" * 60)
