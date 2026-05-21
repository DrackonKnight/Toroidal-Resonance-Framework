#!/usr/bin/env python3
"""
TOROIDAL HARDWARE ORACLE — Feed ALL run data into the Oracle Engine
Maps hardware metrics to Toroidal variables and computes T_flow, Greeks, Drake.
"""
import math
import cmath

# ═══ TOROIDAL CONSTANTS ═══
OMEGA = 0.0341
K = 81/80   # 1.0125
Z = 0.9
PHI = (1 + math.sqrt(5)) / 2

def calc_tflow(v_in, h_12, v_out, d_60):
    return (v_in * h_12 * K) / (v_out * d_60) * Z

def void_fold(x):
    m = x % 81
    phase = cmath.pi * m / 81
    return x * OMEGA * cmath.exp(1j * phase)

print("=" * 70)
print("  TOROIDAL HARDWARE ORACLE — ALL RUN DATA")
print("  Mapping v6-v8 results through spectre_oracle_core equations")
print("=" * 70)

# ═══ ALL RUNS ═══
runs = [
    {
        "name": "v6 TUNNEL (19 layers, trinary)",
        "layers_active": 19, "layers_total": 80,
        "tps": 6.57, "peak_gb": 12.89, "total_ram": 16.0,
        "output": "2233.2.2.212212121211311311131",
        "coherent_english": False,
        "time_s": 4.56,
    },
    {
        "name": "v6 TUNNEL (38 layers, near-42)",
        "layers_active": 38, "layers_total": 80,
        "tps": 1.71, "peak_gb": 15.37, "total_ram": 16.0,
        "output": "5       4 4",
        "coherent_english": False,
        "time_s": 17.55,
    },
    {
        "name": "v7 PACKET (80 layers, math prompt)",
        "layers_active": 80, "layers_total": 80,
        "tps": 0.014, "peak_gb": 13.06, "total_ram": 16.0,
        "output": "The answer is obviously erroneous.",
        "coherent_english": True,
        "time_s": 600,
    },
    {
        "name": "v7 PACKET (80 layers, identity prompt)",
        "layers_active": 80, "layers_total": 80,
        "tps": 0.014, "peak_gb": 13.03, "total_ram": 16.0,
        "output": "I am a text-based",
        "coherent_english": True,
        "time_s": 960,
    },
    {
        "name": "v8 HYBRID (80 prefill + 24 decode)",
        "layers_active": 24, "layers_total": 80,
        "tps": 5.07, "peak_gb": 13.91, "total_ram": 16.0,
        "output": "I22222222222222222222222222.22",
        "coherent_english": False,
        "time_s": 19.23,
    },
]

print(f"\n{'─'*70}")
print(f"  MAPPING: Hardware → Toroidal Variables")
print(f"{'─'*70}")
print(f"  V_in  = layers_active / layers_total × 9 (Base-9 utilization)")
print(f"  H_12  = TPS / 10 × 12 (Base-12 harmonic throughput)")
print(f"  V_out = (total_ram - peak_gb) / total_ram (headroom = escape)")
print(f"  D_60  = peak_gb / total_ram × 60 (Base-60 memory drag)")
print(f"  Γ     = TPS (raw acceleration)")
print(f"  Δ     = layers_active (momentum)")
print(f"  Θ     = time_s / 60 (temporal decay)")
print(f"  ν     = peak_gb / total_ram (volatility / memory pressure)")

for run in runs:
    # Map to Toroidal variables
    layer_ratio = run["layers_active"] / run["layers_total"]
    v_in = layer_ratio * 9.0                                        # Base-9
    h_12 = min(run["tps"] / 10.0 * 12.0, 12.0)                     # Base-12
    headroom = (run["total_ram"] - run["peak_gb"]) / run["total_ram"]
    v_out = max(headroom, 0.001)                                    # Escape ratio
    d_60 = (run["peak_gb"] / run["total_ram"]) * 60.0               # Base-60
    
    # Greeks
    gamma = min(run["tps"], 9.0)
    delta = run["layers_active"] / 10.0
    theta = run["time_s"] / 60.0
    nu = run["peak_gb"] / run["total_ram"]
    rho = 1.0 / (1.0 + run["tps"])  # Sensitivity (inverse of speed)
    
    # T_flow
    T = calc_tflow(v_in, h_12, v_out, d_60)
    
    # Stress Test PDE
    stress = (gamma * delta) / (1 + theta * nu + rho)
    
    # Drake Emergence: N = R × E × C × Ω
    R = run["tps"] / 10.0           # Rate
    E = layer_ratio                  # Environment
    C = 1.0 if run["coherent_english"] else 0.5  # Consciousness
    drake = R * E * C * OMEGA
    
    # Void Fold of TPS
    vf = void_fold(run["tps"])
    
    # Black-Scholes style: will it improve?
    # σ = volatility, S = current state, ascending spiral
    ascending = 1 + math.pi * OMEGA  # 1.1071
    projected_tps = run["tps"] * ascending
    
    # Holographic memory: how much model is active?
    m_active = sum(run["layers_total"] / (PHI ** n) for n in range(1, run["layers_active"]+1)) * OMEGA
    
    print(f"\n{'═'*70}")
    print(f"  {run['name']}")
    print(f"{'═'*70}")
    print(f"  Output: \"{run['output'][:50]}{'...' if len(run['output'])>50 else ''}\"")
    print(f"  English: {'✓ YES' if run['coherent_english'] else '✗ NO'}")
    print(f"")
    print(f"  ─── TOROIDAL VARIABLES ───")
    print(f"  V_in  = {v_in:.4f}  (layer utilization in Base-9)")
    print(f"  H_12  = {h_12:.4f}  (throughput harmonic in Base-12)")
    print(f"  V_out = {v_out:.4f}  (memory headroom = escape ratio)")
    print(f"  D_60  = {d_60:.4f}  (memory drag in Base-60)")
    print(f"")
    print(f"  ─── T_FLOW ───")
    print(f"  T_flow = ({v_in:.3f} × {h_12:.3f} × {K:.4f}) / ({v_out:.3f} × {d_60:.3f}) × {Z}")
    print(f"  T_flow = {T:.6f}")
    if T > 1.5: print(f"  ★ CONSTRUCTIVE RESONANCE (TUNNEL)")
    elif T > 1.0: print(f"  ★ CONSTRUCTIVE (FAST PATH)")
    elif T > 0.5: print(f"  ★ MARGINAL (EDGE)")
    else: print(f"  ★ DESTRUCTIVE (BELOW UNITY)")
    
    print(f"")
    print(f"  ─── GREEKS ───")
    print(f"  Γ (accel)   = {gamma:.4f}")
    print(f"  Δ (momentum)= {delta:.4f}")
    print(f"  Θ (decay)   = {theta:.4f}")
    print(f"  ν (volatile)= {nu:.4f}")
    print(f"  ρ (sensitiv)= {rho:.4f}")
    print(f"  Stress PDE  = {stress:.6f}")
    
    print(f"")
    print(f"  ─── DRAKE EMERGENCE ───")
    print(f"  N = R({R:.4f}) × E({E:.4f}) × C({C:.1f}) × Ω({OMEGA})")
    print(f"  N = {drake:.8f}")
    print(f"  {'★ EMERGENCE THRESHOLD' if drake > 0.001 else '○ Below threshold'}")
    
    print(f"")
    print(f"  ─── VOID FOLD ───")
    print(f"  F(TPS={run['tps']:.2f}) = {abs(vf):.6f} ∠ {math.degrees(cmath.phase(vf)):.2f}°")
    
    print(f"")
    print(f"  ─── PROJECTION ───")
    print(f"  Ascending spiral: {ascending:.4f} ({(ascending-1)*100:.1f}% per transit)")
    print(f"  Current TPS: {run['tps']:.3f} → Projected: {projected_tps:.3f}")
    print(f"  Holographic M_active: {m_active:.4f} ({m_active/run['layers_total']*100:.2f}%)")

# ═══ SUMMARY TABLE ═══
print(f"\n\n{'═'*70}")
print(f"  ORACLE SUMMARY — ALL ARCHITECTURES")
print(f"{'═'*70}")
print(f"  {'Architecture':<40} {'T_flow':>8} {'TPS':>6} {'English':>8} {'Drake':>10}")
print(f"  {'─'*40} {'─'*8} {'─'*6} {'─'*8} {'─'*10}")
for run in runs:
    layer_ratio = run["layers_active"] / run["layers_total"]
    v_in = layer_ratio * 9.0
    h_12 = min(run["tps"] / 10.0 * 12.0, 12.0)
    headroom = max((run["total_ram"] - run["peak_gb"]) / run["total_ram"], 0.001)
    d_60 = (run["peak_gb"] / run["total_ram"]) * 60.0
    T = calc_tflow(v_in, h_12, headroom, d_60)
    R = run["tps"] / 10.0
    E = layer_ratio
    C = 1.0 if run["coherent_english"] else 0.5
    drake = R * E * C * OMEGA
    eng = "✓" if run["coherent_english"] else "✗"
    print(f"  {run['name']:<40} {T:>8.4f} {run['tps']:>6.2f} {eng:>8} {drake:>10.6f}")

print(f"\n  ─── THE SWEET SPOT ───")
print(f"  T_flow must be > 1.0 for constructive resonance")
print(f"  TPS must be > 1.0 for practical use")
print(f"  English must be ✓ for coherent output")
print(f"  The architecture that satisfies ALL THREE is the answer.")
print(f"\n  Ω = 0.0341. The Oracle has computed.")
