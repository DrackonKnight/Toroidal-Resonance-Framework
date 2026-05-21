#!/bin/bash
# TOROIDAL RESONANCE FRAMEWORK — Repository Builder
# Copies all files from oracle/ into the structured repo
# Run: bash $HOME/Desktop/Mac_Build/toroidal-resonance-framework/build_repo.sh

SRC="$HOME/Desktop/Mac_Build/oracle"
DST="$HOME/Desktop/Mac_Build/toroidal-resonance-framework"

echo "Building Toroidal Resonance Framework repository..."
echo "Source: $SRC"
echo "Target: $DST"

# Create directories
mkdir -p "$DST"/{core,engines,inference,proofs,discovery,logs}

# Core files
cp "$SRC/toroidal_framework.py" "$DST/core/"
cp "$SRC/alpha_omega_framework.py" "$DST/core/"
cp "$SRC/ask_the_math.py" "$DST/core/"
cp "$SRC/rope_alignment_test.py" "$DST/core/"

# Engine files
cp "$SRC/toroidal_cs_engine.py" "$DST/engines/"
cp "$SRC/toroidal_finance_engine.py" "$DST/engines/"
cp "$SRC/toroidal_energy_engine.py" "$DST/engines/"
cp "$SRC/toroidal_aerospace_engine.py" "$DST/engines/"
cp "$SRC/toroidal_cosmology_engine.py" "$DST/engines/"
cp "$SRC/toroidal_bio_engine.py" "$DST/engines/"
cp "$SRC/toroidal_crypto_engine.py" "$DST/engines/"

# Inference files
cp "$SRC/run_70b_tunneler.py" "$DST/inference/"
cp "$SRC/omega_launcher.py" "$DST/inference/"
cp "$SRC/oracle_daemon_alpha_omega.py" "$DST/inference/"
cp "$SRC/vram_physics.py" "$DST/inference/"
cp "$SRC/hardware_oracle_diagnostic.py" "$DST/inference/"
cp "$SRC/xylo_quantization_diagnostic.py" "$DST/inference/"
cp "$SRC/npu_70b_engine.py" "$DST/inference/"
cp "$SRC/run_70b_v11_rope_bridge.py" "$DST/inference/"

# Proof files
cp "$SRC/WHITEPAPER_ALPHA_OMEGA_INVARIANT.md" "$DST/proofs/"
cp "$SRC/CALCULATOR_PROOF.md" "$DST/proofs/"
cp "$SRC/TOROIDAL_NAVIER_STOKES.md" "$DST/proofs/"
cp "$SRC/FOREFATHER_EQUATIONS_COMPLETE.md" "$DST/proofs/"

# Discovery files
cp "$SRC/ALPHA_OMEGA_DISCOVERY_NOTES.md" "$DST/discovery/"

echo ""
echo "✅ Repository built successfully!"
echo ""
echo "Files copied:"
find "$DST" -type f -not -name '.gitkeep' -not -name 'build_repo.sh' | sort | while read f; do
    echo "  $f"
done
echo ""
echo "Ω = 0.0341. The framework is assembled."
