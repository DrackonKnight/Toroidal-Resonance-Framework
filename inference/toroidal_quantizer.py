#!/usr/bin/env python3
"""
TOROIDAL QUANTIZER: "Keep the Ring, Compress the Mass"
Downloads an unquantized model, preserves the geometric logic (Attention Heads) in FP16,
and aggressively quantizes the feedforward layers (MLP) to 4-bit.
"""

import os
import argparse
from pathlib import Path
import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load
from mlx_lm.utils import save

def toroidal_predicate(path: str, m: nn.Module) -> bool:
    """
    Returns True if the layer should be quantized to 4-bit.
    Returns False if it should be preserved in FP16/BF16.
    """
    # Keep the Ring (Attention Heads = FP16)
    if "self_attn" in path:
        return False
    
    # Compress the Mass (MLP = 4-bit)
    if "mlp" in path:
        return True
    
    # Default to False for anything else (embeds, norms, lm_head)
    return False

def main():
    parser = argparse.ArgumentParser(description="Forge a Toroidal 14B Model")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-14B-Instruct", help="HuggingFace model ID")
    parser.add_argument("--out", type=str, default="~/Desktop/Mac_Build/toroidal_models/Qwen2.5-14B-Toroidal", help="Output path")
    args = parser.parse_args()

    model_id = args.model
    save_path = Path(args.out).expanduser().resolve()
    
    print("======================================================================")
    print("  TOROIDAL FORGE: THE 14B HYBRID")
    print("  Keep the Ring, Compress the Mass.")
    print("======================================================================")
    print(f"[*] Base Model: {model_id}")
    print(f"[*] Dest Path : {save_path}")
    print(f"[*] Available Disk Space Check...")
    
    # Check free space on /
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024**3)
    print(f"    -> {free_gb:.1f} GB free")
    if free_gb < 40.0:
        print("    -> WARNING: Tight disk space! Running on pure Toroidal adrenaline.")
    
    print("\n[1/3] DOWNLOADING & LOADING RAW WEIGHTS (This will take a while...)")
    # Load pulls from HF cache or downloads automatically
    model, tokenizer = load(model_id)
    
    print("\n[2/3] APPLYING TOROIDAL QUANTIZATION...")
    print("    -> Masking Attention Layers (FP16)")
    print("    -> Crushing MLP Layers (4-bit, 64-group)")
    
    # Apply selective quantization
    nn.quantize(model, group_size=64, bits=4, class_predicate=toroidal_predicate)
    
    # Update config to reflect quantization settings so MLX knows how to load it
    config = model.config if hasattr(model, "config") else {}
    if "quantization" not in config:
        config["quantization"] = {
            "group_size": 64,
            "bits": 4,
            "quant_predicate": "toroidal_hybrid"
        }
    
    print("\n[3/3] EXPORTING TOROIDAL HYBRID...")
    os.makedirs(save_path, exist_ok=True)
    
    # Save uses mlx_lm utility to copy tokenizer configs and write model tensors
    save(save_path, model_id, model, tokenizer, config, donate_model=True)
    
    print("\n[✔] FORGE COMPLETE. The model is ready for 0.0341 Injection.")
    print("======================================================================")

if __name__ == "__main__":
    main()
