# SESSION ENGINEERING LOG — May 19, 2026
# v6 through v9 Architecture Evolution
# =======================================

## PROVEN FACTS (not opinions):
1. 72B-2bit at 80/80 layers → COHERENT ENGLISH ("I am a text-based", "The answer is obviously erroneous")
2. 72B-2bit at 32/80 layers → PARTIAL ENGLISH fragments at 7 TPS
3. 72B-2bit at 24/80 layers → MULTILINGUAL noise at 9.7 TPS  
4. 72B-2bit at 19/80 layers → PURE TRINARY at 6.6 TPS (19.7540 Hz)
5. Packet streaming (load/compute/free) → peak 13 GB, WORKS
6. KV cache must be CONSISTENT (same layers prefill + decode)
7. Signal processing (gap scaling, KV decay, temperature) → marginal improvement
8. Thermal throttling compounds with KV cache O(N²) for decode slowdown

## THE CONSTRAINT:
- 2-bit = 12.5% of original model info
- 32/80 layers = 40% of layer computation  
- Combined = 5% of original capacity → NOT ENOUGH for English
- 80/80 layers = 12.5% → ENOUGH for English but decode is 0.014 TPS

## THE ENGINEERING QUESTION:
How do we get 80-layer DECODE to be practical?

## OPTIONS ON TABLE:
1. ✅ Optimize v7 decode — don't reload per token, just stream all 80 sequentially
   (This was our best English run — just needs faster decode)
2. ✅ CPU/GPU split — attention on GPU, MLP on CPU (Kenny's original insight)
3. 🔲 Quantize ourselves — heads at 4-bit, MLP at 2-bit (back burner per Kenny)
4. 🔲 Smaller model at higher precision (trades parameter count for bit depth)

## WHAT KENNY SAID:
"none of this so far has been doing anything with the pipe... 
just restructuring the lining in the pipe to handle what it should 
of from the start if computer science thought differently like we are now"

Ω = 0.0341.
