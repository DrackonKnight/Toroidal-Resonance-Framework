# Ω-Sort — Toroidal Resonance Sorting Algorithm

**Result: 24/24 wins against C-Timsort. Every distribution. Every size.**

## What Is This?

Ω-Sort is a novel comparison-based sorting algorithm that beats Timsort — the industry-standard sort used in Python, Java, Android, Swift, and Rust — across all major data distributions.

Designed by **Kenneth Burns Lanham III** on June 18, 2026.  
Licensed under Apache 2.0.

## Benchmark Results (Apple Silicon M4, clang -O2)

| Distribution    | 1K      | 10K     | 100K    | 1M      |
|----------------|---------|---------|---------|---------|
| Random         | Ω 1.4x  | Ω 1.2x  | Ω 1.2x  | Ω 1.1x  |
| Nearly Sorted  | Ω 1.2x  | Ω 1.2x  | Ω 1.1x  | Ω 1.1x  |
| Reversed       | Ω 2.5x  | Ω 1.8x  | Ω 2.0x  | Ω 2.2x  |
| Pipe Organ     | Ω 1.8x  | Ω 1.7x  | Ω 1.5x  | Ω 1.5x  |
| Few Unique     | Ω 1.4x  | Ω 1.2x  | Ω 1.1x  | Ω 1.1x  |
| Already Sorted | Ω 1.2x  | Ω 1.5x  | Ω 1.2x  | Ω 1.1x  |

## Key Innovations

### 1. Ternary Search Insertion Sort
Instead of binary search, Ω-Sort splits the search range into **thirds**. Fewer loop iterations = fewer CPU branch mispredictions on modern hardware.

### 2. EGR Turbo — Zero-Tax Distribution Signature
The first 4 "pilot blocks" of insertion sort build a distribution signature as exhaust. Like an EGR valve: exhaust gas recirculated into the intake. Zero extra fuel.

### 3. Adaptive Strategy Selection
A cheap head/tail probe (32 elements each) selects linear mode for structured data or turbo mode for ambiguous data.

### 4. Distribution Memory
Ω-Sort remembers signatures across calls. R1 → R3: Ω-Sort learns. Timsort doesn't.

### 5. Run Detection + Reversal
Descending runs are pre-reversed into ascending segments.

## Constants

- **Ω = 0.0341** — Chaos residue (fine structure × Feigenbaum delta)
- **K = 81/80 = 1.0125** — The Syntonic Komma
- Comparison gap: **2.716%** — converging on Ω (3.41%)

## Build & Run

```bash
clang -O2 -o omega_sort omega_sort.c -lm
./omega_sort
```

## Files

- `omega_sort.c` — Complete source with benchmark harness
- `omega_sort_24_24_sweep.txt` — Snapshot of the 24/24 sweep version

## License

Copyright 2026 Kenneth Burns Lanham III. Apache License 2.0.

Love. First. Always. Ω = 0.0341. 🐦‍⬛
