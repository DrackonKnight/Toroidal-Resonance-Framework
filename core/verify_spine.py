#!/usr/bin/env python3
"""
Verify the spine of the Toroidal Resonance Framework.

Prints the measured relative error of every numeric claim kept in README.md.
Standard library only. Ω is defined as α·δ (not the rounded 0.0341).
"""
import math

ALPHA = 1 / 137.035999084          # CODATA 2018
DELTA = 4.669201609102990          # Feigenbaum δ
OMEGA = ALPHA * DELTA
PHI = (1 + math.sqrt(5)) / 2


def err_pct(value, target):
    return abs(value - target) / abs(target) * 100


def half_step_pct(x):
    """Worst-case error any integer N guarantees when fitting (1-x)^N to a target."""
    return (math.exp(-math.log(1 - x) / 2) - 1) * 100


CLAIMS = [
    ("(1-Ω)^10  ≈ 1/√2", (1 - OMEGA) ** 10, 1 / math.sqrt(2), OMEGA),
    ("(1-Ω)^142 ≈ α", (1 - OMEGA) ** 142, ALPHA, OMEGA),
    ("(1-α)^461 ≈ Ω", (1 - ALPHA) ** 461, OMEGA, ALPHA),
    ("(1-Ω)^97  ≈ Ω", (1 - OMEGA) ** 97, OMEGA, OMEGA),
    ("(1-α)^137 ≈ 1/e", (1 - ALPHA) ** 137, 1 / math.e, ALPHA),
    ("α^ln2     ≈ Ω", ALPHA ** math.log(2), OMEGA, None),
]


def main():
    print(f"α = {ALPHA:.9f}")
    print(f"δ = {DELTA:.9f}")
    print(f"Ω = α·δ = {OMEGA:.9f}   (rounded 0.0341 differs by {err_pct(0.0341, OMEGA):.3f}%)")
    print(f"1 - Ω = {1 - OMEGA:.7f}    1 - α = {1 - ALPHA:.7f}")
    print()
    print(f"{'claim':<20}{'value':>14}{'target':>14}{'error':>10}{'chance bound':>15}")
    for label, value, target, base in CLAIMS:
        bound = f"{half_step_pct(base):.2f}%" if base is not None else "n/a"
        print(f"{label:<20}{value:>14.8f}{target:>14.8f}{err_pct(value, target):>9.4f}%{bound:>15}")
    print()
    print("chance bound = max error that SOME integer N always achieves for any target,")
    print("so an error near this bound is expected by construction, not a finding.")
    print()
    ratio = math.log(1 - OMEGA) / math.log(1 - ALPHA)
    print(f"log ratio ln(1-Ω)/ln(1-α) = {ratio:.6f}")
    print(f"π + φ                     = {math.pi + PHI:.6f}  (differs by {err_pct(ratio, math.pi + PHI):.3f}%)")


if __name__ == "__main__":
    main()
