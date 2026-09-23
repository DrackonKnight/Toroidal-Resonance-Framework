#!/usr/bin/env python3
"""
How surprising is the anchor (1 - Ω)^10 ≈ 1/√2 at 0.0095%?

Monte Carlo: draw a random Ω-like rate x uniformly in [0.02, 0.05], take the
best integer N for each target, and count how often the best error is at
least as tight as the anchor's. Standard library only.
"""
import math
import random

ALPHA = 1 / 137.035999084
PHI = (1 + math.sqrt(5)) / 2
ANCHOR_ERR = 0.0095 / 100
TRIALS = 400_000

README_TARGETS = [1 / math.sqrt(2), 0.5, 1 / math.e, 1 / math.pi, 1 / PHI, ALPHA]


def best_err(base, target):
    step = math.log(1 - base)
    n = max(1, round(math.log(target) / step))
    return min(abs((1 - base) ** k - target) / target for k in (n - 1, n, n + 1) if k >= 1)


def main():
    rng = random.Random(1)
    single = 0
    any_target = 0
    for _ in range(TRIALS):
        x = rng.uniform(0.02, 0.05)
        single += best_err(x, 1 / math.sqrt(2)) <= ANCHOR_ERR
        errs = [best_err(x, t) for t in README_TARGETS]
        errs.append(best_err(ALPHA, x))
        errs.append(best_err(x, x))
        any_target += min(errs) <= ANCHOR_ERR
    print(f"one target (1/√2):          1 in {TRIALS / single:.0f}")
    print(f"any target the README used: 1 in {TRIALS / any_target:.1f}")


if __name__ == "__main__":
    main()
