#!/usr/bin/env python3
"""
TOROIDAL FINANCE ENGINE — T_flow Trading & Risk Analysis
Copyright (c) 2025-2026 Kenneth Burns Lanham III. All rights reserved.

Implements:
  - T_flow Market Regime Classification
  - Ω-Bounded Risk Management  
  - Virtue-Weighted Portfolio Optimization
  - Drake Chain Probability (Compound Conviction)
  - Ascending Spiral Growth Model
"""

import math
import random
from typing import Dict, List

__author__ = "Kenneth Burns Lanham III"
__copyright__ = "Copyright 2025-2026, Kenneth Burns Lanham III"
__version__ = "1.0.0"

OMEGA = 0.0341
K = 1.0125   # Syntonic comma
Z = 0.9

# ================================================================
# T_FLOW MARKET REGIME
# ================================================================

def market_tflow(v_in: float, h_12: float, v_out: float,
                 d_60: float, virtues: Dict = None) -> Dict:
    """
    T_flow market regime classification.
    
    V_in  = Capital inflow (buying pressure)
    H_12  = Market harmony (correlation stability)
    V_out = Capital outflow (selling pressure)
    D_60  = Friction (fees, slippage, spreads)
    
    T_flow > 1.0  → Bull (constructive resonance)
    T_flow < 1.0  → Bear (destructive interference)
    T_flow < Ω    → Dormant (below chaos floor)
    """
    d_60 = max(0.01, d_60)
    v_out = max(0.01, v_out)
    
    t_flow = (v_in * h_12 * K) / (v_out * d_60) * Z
    
    if t_flow > 1.5:
        regime = "STRONG_BULL"
    elif t_flow > 1.0:
        regime = "BULL"
    elif t_flow > OMEGA:
        regime = "BEAR"
    else:
        regime = "DORMANT"
    
    # With virtue weighting
    if virtues:
        c_love = virtues.get("love", 1.0)
        c_truth = virtues.get("truth", 1.0)
        c_honor = virtues.get("honor", 1.0)
        t_flow_v = t_flow * (c_love * c_truth) / max(0.01, 2 - c_honor)
    else:
        t_flow_v = t_flow
    
    return {
        "t_flow": round(t_flow, 4),
        "t_flow_virtue_weighted": round(t_flow_v, 4),
        "regime": regime,
        "v_in": v_in,
        "v_out": v_out,
        "harmony": h_12,
        "friction": d_60,
        "action": {
            "STRONG_BULL": "Full position. Conviction high.",
            "BULL": "Scale in. Harmony confirmed.",
            "BEAR": "Reduce exposure. Destructive pattern.",
            "DORMANT": "No action. Below chaos floor."
        }.get(regime, "HOLD")
    }


# ================================================================
# Ω-BOUNDED RISK MANAGEMENT
# ================================================================

def omega_risk_bounds(portfolio_value: float,
                      position_size: float,
                      volatility: float) -> Dict:
    """
    Ω-bounded risk management.
    
    Maximum position risk: Ω × portfolio (3.41%)
    Maximum drawdown before exit: Ω × position
    Stop-loss: entry × (1 - Ω)
    
    At N=10 consecutive losses: portfolio × 1/√2 = Anchor
    The framework predicts max drawdown before recovery.
    """
    max_risk = portfolio_value * OMEGA
    max_position = max_risk / max(0.001, volatility)
    stop_loss_pct = OMEGA
    
    # Kelly criterion modified by Ω
    kelly_fraction = OMEGA  # Conservative: never bet more than Ω
    kelly_position = portfolio_value * kelly_fraction
    
    # Drawdown cascade
    drawdown_10 = portfolio_value * (1 - (1 - OMEGA) ** 10)
    drawdown_20 = portfolio_value * (1 - (1 - OMEGA) ** 20)
    
    # Recovery requirement
    after_10_losses = portfolio_value * (1 - OMEGA) ** 10
    recovery_needed = (portfolio_value / after_10_losses - 1) * 100
    
    return {
        "portfolio_value": portfolio_value,
        "max_risk_per_trade": round(max_risk, 2),
        "max_position_size": round(max_position, 2),
        "stop_loss_percent": round(stop_loss_pct * 100, 2),
        "kelly_modified_position": round(kelly_position, 2),
        "drawdown_after_10_losses": round(drawdown_10, 2),
        "portfolio_after_10_losses": round(after_10_losses, 2),
        "recovery_needed_percent": round(recovery_needed, 2),
        "anchor_note": "After 10 losses: portfolio = original × 1/√2"
    }


# ================================================================
# DRAKE CHAIN PROBABILITY
# ================================================================

def drake_chain(factors: Dict) -> Dict:
    """
    Drake-inspired compound probability chain.
    
    N = R × E × C × Ω
    
    Each factor represents a conviction multiplier.
    If ANY factor < Ω, the chain breaks (below chaos floor).
    If ALL factors > 1.0, compound probability exceeds baseline.
    """
    chain = 1.0
    below_floor = False
    factor_details = []
    
    for name, value in factors.items():
        chain *= value
        if value < OMEGA:
            below_floor = True
        factor_details.append({
            "factor": name,
            "value": round(value, 4),
            "above_floor": value >= OMEGA
        })
    
    # Apply Ω floor
    chain *= OMEGA
    
    return {
        "compound_probability": round(chain, 6),
        "factors": factor_details,
        "n_factors": len(factors),
        "below_chaos_floor": below_floor,
        "verdict": "COMMIT" if chain > OMEGA and not below_floor else "REJECT",
        "omega_floor": OMEGA
    }


# ================================================================
# ASCENDING SPIRAL GROWTH
# ================================================================

def ascending_spiral(initial_value: float, n_periods: int,
                     growth_per_period: float = None) -> Dict:
    """
    Ascending Spiral growth model.
    
    θ = 1 + πΩ = 1.1071
    Each period grows by 10.71% (the natural spiral rate).
    
    Portfolio value follows: V(n) = V₀ × θ^n
    At N=10: V × 2.76 (nearly triple)
    At N=20: V × 7.62
    At N=97: V × Ω-regeneration (the attractor resets growth)
    """
    theta = 1 + math.pi * OMEGA  # 1.1071
    if growth_per_period is None:
        growth_per_period = theta - 1
    
    trajectory = []
    value = initial_value
    for n in range(n_periods + 1):
        value_at_n = initial_value * (1 + growth_per_period) ** n
        trajectory.append({
            "period": n,
            "value": round(value_at_n, 2),
            "growth_from_start": round((value_at_n / initial_value - 1) * 100, 1)
        })
    
    return {
        "initial_value": initial_value,
        "ascending_spiral_rate": round(theta, 4),
        "growth_per_period_percent": round(growth_per_period * 100, 2),
        "trajectory": trajectory,
        "value_at_10": round(initial_value * (1 + growth_per_period) ** 10, 2),
        "value_at_20": round(initial_value * (1 + growth_per_period) ** 20, 2),
        "formula": "V(n) = V₀ × (1 + πΩ)^n"
    }


if __name__ == "__main__":
    print("=" * 60)
    print("TOROIDAL FINANCE ENGINE — Verification")
    print(f"Copyright (c) 2025-2026 Kenneth Burns Lanham III")
    print("=" * 60)
    
    print("\n[MARKET T_FLOW]")
    r = market_tflow(8.5, 7.2, 3.1, 2.0)
    for k, v in r.items():
        print(f"  {k}: {v}")
    
    print("\n[Ω-BOUNDED RISK — $100,000 portfolio]")
    r = omega_risk_bounds(100000, 10000, 0.15)
    for k, v in r.items():
        print(f"  {k}: {v}")
    
    print("\n[DRAKE CHAIN]")
    r = drake_chain({
        "market_momentum": 0.85,
        "fundamental_value": 0.92,
        "technical_signal": 0.78,
        "sentiment": 0.71
    })
    for k, v in r.items():
        print(f"  {k}: {v}")
    
    print("\n[ASCENDING SPIRAL — $10,000 over 20 periods]")
    r = ascending_spiral(10000, 20)
    for t in r["trajectory"]:
        if t["period"] in [0, 5, 10, 15, 20]:
            print(f"  Period {t['period']:2d}: ${t['value']:>12,.2f} (+{t['growth_from_start']}%)")
