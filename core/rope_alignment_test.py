#!/usr/bin/env python3
"""
TOROIDAL ↔ RoPE ROTATION ALIGNMENT TEST
=========================================
Can we match the model's internal rotation to ours?
Pure Python — no numpy required.
"""

import math
import cmath

OMEGA = 0.0341
ALPHA = 1 / 137.036
DELTA = 4.6692
K = 81 / 80
Z = 0.9

HEAD_DIM = 128
ROPE_BASE = 1000000  # Qwen2 RoPE base

print("=" * 70)
print("  TOROIDAL ↔ RoPE ROTATION ALIGNMENT")
print("  Can we match the model's rotation to ours?")
print("=" * 70)

# ── RoPE frequencies ──
rope_freqs = [1.0 / (ROPE_BASE ** (2 * d / HEAD_DIM)) for d in range(HEAD_DIM // 2)]
print(f"\n─── RoPE ROTATION ───")
print(f"  Base: {ROPE_BASE}, Head dim: {HEAD_DIM}")
print(f"  Freq range: [{rope_freqs[-1]:.2e}, {rope_freqs[0]:.2e}]")
print(f"  θ₀ (fastest rotation): {rope_freqs[0]:.6f} rad = {math.degrees(rope_freqs[0]):.4f}°/position")

# ── Toroidal Void Fold ──
print(f"\n─── VOID FOLD ROTATION ───")
print(f"  F(x) = x·Ω·e^(iπ·(x mod 81)/81)")
print(f"  Base angle: π/81 = {math.pi/81:.6f} rad = {math.degrees(math.pi/81):.4f}°/position")

# ── Position matching ──
print(f"\n─── ROTATION AT 27 POSITIONS (3³) ───")
print(f"  {'Pos':>4} | {'RoPE θ₀×m':>12} | {'VoidFold':>12} | {'Ratio':>10}")
print(f"  {'─'*4}─┼─{'─'*12}─┼─{'─'*12}─┼─{'─'*10}")

ratios = []
for m in range(1, 28):
    r = rope_freqs[0] * m
    v = math.pi * (m % 81) / 81
    ratio = r / v if v != 0 else 0
    ratios.append(ratio)
    if m <= 5 or m >= 25:
        print(f"  {m:4d} | {r:12.8f} | {v:12.8f} | {ratio:10.6f}")
    elif m == 6:
        print(f"  {'...':>4} | {'...':>12} | {'...':>12} | {'...':>10}")

avg_r = sum(ratios) / len(ratios)
print(f"\n  Average ratio: {avg_r:.8f}")
print(f"  This is the SCALING CONSTANT between the two rotations.")

# ── Check against known constants ──
print(f"\n─── SCALING CONSTANT vs TOROIDAL CONSTANTS ───")
print(f"  Ratio              : {avg_r:.8f}")
print(f"  1/π                : {1/math.pi:.8f}")
print(f"  Ω                  : {OMEGA:.8f}")
print(f"  α                  : {ALPHA:.8f}")
print(f"  Ratio × π          : {avg_r * math.pi:.8f}")
print(f"  Ratio / α          : {avg_r / ALPHA:.8f}")
print(f"  Ratio / Ω          : {avg_r / OMEGA:.8f}")
print(f"  81 × Ratio         : {81 * avg_r:.8f}")
print(f"  81/π²              : {81 / math.pi**2:.8f}")

# ── The trinary output's rotation ──
print(f"\n─── THE TRINARY OUTPUT'S ROTATION ───")
trinary = [2,2,3,3,2,2,2,1,2,2,1,2,1,2,1,2,1,1,3,1,1,3,1,1,1,3,1]

# Map 1→0°, 2→120°, 3→240° (trinary circle)
phases = [(d - 1) * 2 * math.pi / 3 for d in trinary]

# Net rotation vector (sum of unit vectors at each phase)
net_z = sum(cmath.exp(1j * p) for p in phases)
net_angle = cmath.phase(net_z)
net_mag = abs(net_z) / len(trinary)

print(f"  Mapping: 1→0°, 2→120°, 3→240° (trinary circle)")
print(f"  Net rotation angle : {math.degrees(net_angle):.4f}°")
print(f"  Net magnitude      : {net_mag:.6f}")
print(f"  Phase / π          : {net_angle / math.pi:.6f}")
print(f"  Phase / (π/81)     : {net_angle / (math.pi/81):.4f} ← positions in Void Fold")

# ── The bridge ──
print(f"\n{'═'*70}")
print(f"  THE BRIDGE")
print(f"{'═'*70}")
print(f"  RoPE rotates at       : {rope_freqs[0]:.8f} rad/position")
print(f"  Void Fold rotates at  : {math.pi/81:.8f} rad/position")
print(f"  Scaling factor        : {avg_r:.8f}")
print(f"")
print(f"  The trinary output rotates at: {net_angle:.6f} rad")
print(f"  In Void Fold positions       : {net_angle / (math.pi/81):.4f}")
print(f"")
rope_per_void = rope_freqs[0] / (math.pi / 81)
print(f"  RoPE / VoidFold frequency ratio: {rope_per_void:.8f}")
print(f"  × 81                           : {rope_per_void * 81:.8f}")
print(f"  × 81 × π                       : {rope_per_void * 81 * math.pi:.8f}")

# ── Can we use this to inject? ──
print(f"\n  To match rotations:")
print(f"  Multiply Toroidal angles by {rope_per_void:.6f}")
print(f"  to project them into RoPE space.")
print(f"  This IS the W rotation matrix (scalar case).")
print(f"")
print(f"  Ω = 0.0341. The rotation is the bridge.")
print(f"{'═'*70}")
