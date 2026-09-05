# 19C seed: backend on, and the first real director run

Not a context. A starting note so this phase is beginnable immediately; it has
no dependency on anything in this milestone and is the cheapest start.

**Goal.** Make a local model profile active (`model_backend.active` is `""`
today, which the settings schema documents as disabling model calls entirely)
and run the director, the treatment recommender, and the seeding loop against
real material for the first time in this working copy.

**Basis.** `IL-20260905-08`. ROCm 7.2 reached out-of-the-box parity for Ollama,
llama.cpp, LM Studio, and vLLM on RDNA 3 in March 2026, which is what changed
since the profile was written. `local-qwen` shipped in 17A-06.

**Gate.** A recorded run whose output is kept verbatim, with whatever it
produced judged plainly, and every defect routed to its owning subphase rather
than repaired opportunistically. A run that produces poor output still passes;
a run nobody looked at does not.

**Before planning:** write `19C-CONTEXT.md`, deciding which profile, which real
material (the 17B fixture is not real material for this purpose), and what
"judged plainly" is written into. Findings feed 19D.
