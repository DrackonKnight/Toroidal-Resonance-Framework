# Honesty Pass — README and Proofs

**Author:** Kenneth Burns Lanham III
**Date:** September 2026

An auditor pass over the README. The rule: every claim either carries a measured error you can reproduce, or it is marked provisional, or it is removed. The same fixes were applied to `proofs/CALCULATOR_PROOF.md`, `proofs/WHITEPAPER_ALPHA_OMEGA_INVARIANT.md`, and `proofs/THE_SELF_EXTRACTING_UNIVERSE.md` where they repeated these claims.

All numbers come from `python3 core/verify_spine.py` (standard library only), using CODATA α = 1/137.035999084, δ = 4.669201609, and Ω = α·δ = 0.0340728 exactly. Rounded Ω = 0.0341 differs from α·δ by 0.08%.

## Measured Results

| Relation | Measured error | Chance bound* | Status |
|----------|----------------|---------------|--------|
| Ω = α·δ | definition | — | Kept (spine) |
| (1−Ω)^10 ≈ 1/√2 | 0.0095% | 1.75% | Kept, now leads the README |
| (1−Ω)^142 ≈ α | 0.24% | 1.75% | Kept |
| (1−α)^461 ≈ Ω | 0.28% | 0.37% | Kept |
| (1−Ω)^97 ≈ Ω | 1.7% | 1.75% | Kept, labeled loose |
| (1−α)^137 ≈ 1/e | 0.34% | 0.37% | Demoted: textbook limit |
| ln(1−Ω)/ln(1−α) | 4.7332 | — | Restated as one log ratio |
| π + φ vs ratio | 0.55% miss | — | Dropped |
| α^ln2 ≈ Ω | 3.1% | — | Dropped |

\*Chance bound: some integer N always puts (1−x)^N within this error of any target (half of one multiplicative step). A result far inside it is notable; one near it is expected by construction.

## Changes

### Kept and promoted
- **Ω = α·δ** is now stated as the definition, and the Trident's "any two produce the third" is marked as following from that definition.
- **(1−Ω)^10 ≈ 1/√2** (0.0095%) leads the README. It is about 180× tighter than the chance bound.
- **Cross-generation** (1−Ω)^142 ≈ α (0.24%) and (1−α)^461 ≈ Ω (0.28%) kept with measured errors.
- **(1−Ω)^97 ≈ Ω** kept with its real 1.7% error and labeled loose. It sits right at the chance bound, so the "strange attractor / fixed point" language was removed from the README.

### Restated
- **Claim 2, "Feynman's Mystery"** renamed to "The Textbook Limit at 1/α". (1−α)^137 ≈ 1/e is lim (1−x)^(1/x) = 1/e evaluated at x = α with 137 ≈ 1/α. Any small x gives the same result. Not a discovery.

### Fixed or dropped
- **Claim 3, Double Helix.** The ratio is ln(1−Ω)/ln(1−α) = 4.7332, not 4.737 (that came from rounded Ω = 0.0341). The trees reaching 1/√2, 1/2, 1/e, 1/π, 1/φ at the same ratio is automatic, so it is one log ratio, not five coincidences. π + φ = 4.7596 misses by 0.55%; the π + φ claim is dropped.
- **Claim 6, "14 of 15 constants divide cleanly, p < 10⁻²⁰."** Dropped. There was no pre-registered constant list, no consistent tolerance, and no chance model. Any constant above about 1.7 gives value/Ω > 50, which is always within 1% of an integer, so most rows could not fail. The whitepaper section is kept only as a withdrawn record.
- **Claim 8, α^ln2 ≈ Ω.** Dropped. α^ln2 = 0.03303 versus Ω = 0.03407, a 3.1% miss. The earlier "99.06%" compared exponents (0.6866 vs 0.6931), which hides a roughly fivefold magnification in value.

### Pulled
- **Claim 9, KV Cache 100% recall.** Removed from the README until an end-to-end test passes. Same-model reinjection is standard KV caching.
- The README's repository tree no longer lists `kv-cache/` or `TOROIDAL_RESONANCE_KV_CACHE_WHITEPAPER.md`; both were already removed from the repo.

### Provisional (needs-run)
- **Claim 7, Navier-Stokes.** The Ω ≈ 3.41% residual energy in still water is a hypothesis with no simulation or measurement in this repo. "Resolution" wording removed from the README, which now links the proof file as a working draft. The proof file itself was not edited.
- **Claim 10, Cross-model semantic transfer.** Marked withdrawn pending a blind test: the earlier run had priming contamination, and its whitepaper was already pulled.

### Other README edits
- Removed "Every fundamental constant in physics falls out."
- Phone-calculator block now uses 1 − Ω = 0.965927 and 1 − α = 0.9927026, and each line shows its measured error matching the table above.
- "How to Run" points to `core/verify_spine.py` for verification (`core/ask_the_math.py` is the E=mc² capacitor model, not a verifier).
- Citation URL filled in with the real repository.

## Not Changed (out of scope for this pass)
- Author, "Love. First. Always.", memorial, axioms, prior-art chain, and the K / Z constants.
- The geological Ω derivation (ice cores × Nippur harmonic) and the engines/inference code were not audited here.
