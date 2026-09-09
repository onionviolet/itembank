# Third-party notices

## DeepTutor selection grounding

`grounding.py` adapts the whitespace-normalization and selection-window approach from `deeptutor/reading/_grounding.py` in [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor), pinned at revision `7a96bba1ae03401644c17763a2411c28aff3dcc9`.

Copyright 2025 Data Intelligence Lab, The University of Hong Kong.

DeepTutor is licensed under the Apache License, Version 2.0. A complete copy is in `LICENSE-DeepTutor.txt`. This prototype adds source fingerprint verification, rights gates, exact remote-target approval, duplicate-selection rejection, explicit range disambiguation, canonical window offsets, and typed failures. It does not reuse DeepTutor's reader store, API router, extension system, LLM client, or quiz handling.
