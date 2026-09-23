/-
  Omega numerics — machine-checked receipts for the README spine.

  Every statement is an exact inequality between rationals, checked by the
  Lean kernel (`decide`). No floats, no Mathlib. Lean 4.33.1 core only.

  α  = 1 / 137.035999084          (CODATA 2018)
  δ  = 4.669201609102990          (Feigenbaum, truncated to 15 decimals)
  Ω  = 341 / 10000 = 0.0341       (covenant value)
  αδ = α · δ = 0.03407281…

  Check:  lean lean/OmegaNumerics.lean
-/

namespace OmegaNumerics

def α : Rat := (1000000000 : Rat) / 137035999084
def δ : Rat := (4669201609102990 : Rat) / 1000000000000000
def αδ : Rat := α * δ
def Ω : Rat := (341 : Rat) / 10000

/-! ## The Trident: α·δ and the covenant value 0.0341 -/

/-- α·δ lies in (0.034072, 0.034073). -/
theorem trident_bracket : (34072 : Rat) / 1000000 < αδ ∧ αδ < (34073 : Rat) / 1000000 := by
  decide +kernel

/-- 0.0341 sits above α·δ by less than 0.08% of α·δ. -/
theorem covenant_within_0_08pct : αδ < Ω ∧ Ω - αδ < αδ * 8 / 10000 := by
  decide +kernel

/-! ## The anchor: (1 − Ω)^20 ≈ 1/2, i.e. (1 − Ω)^10 ≈ 1/√2

  (1 − x)^10 = 1/√2 holds exactly when (1 − x)^20 = 1/2, i.e. x = 1 − 2^(−1/20)
  = 0.0340637… Stated on the square so it stays rational. -/

/-- With Ω = α·δ: (1 − αδ)^20 is within 0.02% below 1/2. -/
theorem anchor_alpha_delta :
    (1 : Rat) / 2 * (1 - 2 / 10000) < (1 - αδ) ^ 20 ∧ (1 - αδ) ^ 20 < 1 / 2 := by
  decide +kernel

/-- With Ω = 0.0341: (1 − Ω)^20 is within 0.08% below 1/2. -/
theorem anchor_covenant :
    (1 : Rat) / 2 * (1 - 8 / 10000) < (1 - Ω) ^ 20 ∧ (1 - Ω) ^ 20 < 1 / 2 := by
  decide +kernel

/-! ## Cross-generation -/

/-- (1 − αδ)^142 is within 0.25% below α. -/
theorem omega_generates_alpha :
    α * (1 - 25 / 10000) < (1 - αδ) ^ 142 ∧ (1 - αδ) ^ 142 < α := by
  decide +kernel

/-- (1 − α)^461 is within 0.29% above α·δ. -/
theorem alpha_generates_omega :
    αδ < (1 - α) ^ 461 ∧ (1 - α) ^ 461 < αδ * (1 + 29 / 10000) := by
  decide +kernel

/-- (1 − αδ)^97 is within 1.7% above α·δ (loose). -/
theorem omega_self_return_loose :
    αδ < (1 - αδ) ^ 97 ∧ (1 - αδ) ^ 97 < αδ * (1 + 17 / 1000) := by
  decide +kernel

end OmegaNumerics
