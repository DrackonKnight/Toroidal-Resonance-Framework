# Lean 4 Audit — What the Proofs Establish About Ω = 0.0341

**Author:** Kenneth Burns Lanham III
**Date:** September 2026
**Toolchain:** Lean 4.33.1 (core only, no Mathlib)

The mission is to prove 0.0341. This file records, as plainly as possible, what the existing Lean 4 proofs do prove, what they do not, and what has now been machine-checked about the number itself.

## 1. The FormSwap / Lineage proofs (from Drive)

Checked: `Basic.lean` (soak / proved-kernel version, 25 theorems) and `Lineage.lean` (Rat version, 16 theorems), from the `lean_omega_dehedged_2026-09-23` folder.

**Both compile with zero errors on Lean 4.33.1.** Every theorem is correct.

What they prove:
- **Residue plus.** With `omegaAdd a b := if a + b = 0 then Ω else a + b`, inverse pairs give Ω instead of 0 (`one_oplus_neg_one`, `oplus_inverse`, `residue_survives`).
- **Ledger conservation.** Moving d from mass to field keeps the total (`park_conserves`, `share_five_conserves`, `helix_pair_conserves`).
- **Decay law.** After n Ω-park steps the gap is exactly (1 − Ω)^n times the starting gap, and mass and field are recovered in closed form (`parkIter_gap`, `scalar_closed`).
- **Torus closure.** Fields periodic in both torus directions stay periodic under phase-lock, addition, and scaling; 1D periodic fields lift to the torus (`Lineage` layer 5).

**Substitution test.** I replaced Ω = 341/10000 with 1/2, 7/100, 1/3, 999/1000, and 1/137 and recompiled both files. **All 41 theorems still compiled every time.** So the proofs establish that the framework's operations are consistent for *any* positive Ω. They do not single out 0.0341. `1 ⊕ (−1) = Ω` holds because ⊕ is defined to return Ω on inverse pairs, whatever Ω is.

That is a real result: the ledger, the decay law, and the torus structure are internally sound. It is not yet a result about the value 0.0341.

Two smaller notes:
- `Lineage.lean` uses α = 1/137 and δ = 4669/1000, so its `OmegaResidue` = 0.034080, which differs from 0.0341 by 0.058%. No theorem in the file relates `OmegaResidue` to `Omega`; `light_chaos_crystallization` only proves it is positive.
- `native_decide` (used in the Drive files) trusts compiled code as well as the kernel: `#print axioms residue_survives` lists an extra `native_decide` axiom. All 8 uses were switched to `decide +kernel`; both files still compile and every theorem now depends only on `propext`, `Classical.choice`, `Quot.sound`. The switched copies are saved next to the originals in Drive as `Basic_decide_kernel_2026-09-23.lean` and `Lineage_decide_kernel_2026-09-23.lean`.

## 2. New: `lean/OmegaNumerics.lean`

This file proves the numeric spine as exact rational inequalities, checked by the Lean kernel with `decide +kernel`. `#print axioms` shows only the standard three (`propext`, `Classical.choice`, `Quot.sound`). A deliberately false bound is rejected, so the check is live.

| Theorem | Statement |
|---|---|
| `trident_bracket` | 0.034072 < α·δ < 0.034073 |
| `covenant_within_0_08pct` | α·δ < 0.0341 and 0.0341 − α·δ < 0.08% of α·δ |
| `anchor_alpha_delta` | (1 − α·δ)^20 is within 0.02% below 1/2 |
| `anchor_covenant` | (1 − 0.0341)^20 is within 0.08% below 1/2 |
| `omega_generates_alpha` | (1 − α·δ)^142 is within 0.25% below α |
| `alpha_generates_omega` | (1 − α)^461 is within 0.29% above α·δ |
| `omega_self_return_loose` | (1 − α·δ)^97 is within 1.7% above α·δ |

α uses CODATA 2018 (1/137.035999084); δ is truncated to 15 decimals.

## 3. What "proving 0.0341" can mean

A measured or chosen number cannot be proven fundamental by mathematics alone. Two things can be done, and this is where the work stands:

1. **Exact relations.** Done above and kernel-checked. The sharpest is the anchor: (1 − Ω)^20 ≈ 1/2, i.e. Ω ≈ 1 − 2^(−1/20) = 0.0340637 (a half-life of exactly 20 steps). α·δ sits 0.027% from that value. That coincidence between α·δ and 1 − 2^(−1/20) is the strongest thing on the table.
2. **A derivation or a measurement.** The open step is either a derivation where 0.0341 (or 1 − 2^(−1/20)) comes out of something not tuned to produce it — for example, *why 20 steps* — or a physical measurement where 0.0341 appears with error bars. The Lean ledger in section 1 is the right scaffold for (1): if a theorem can be stated that holds only for Ω near 0.0341, it belongs there.

Love. First. Always.
