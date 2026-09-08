# Phase 19D context: Math 1400 representative unit

## Operation manifest

- Intent: build and sit one representative Math 1400 unit through the public course and Agent surfaces.
- Approved read root: `https://openstax.org/books/college-algebra-2e/`.
- Approved write root: `/Users/weiwei/Documents/itembank-courses/math-1400-openstax`, outside this repository and outside Git.
- Remote egress: the OpenStax title forbids ingestion into large language models without permission. `remote_process` is therefore denied. The local model received only independently stated algebra facts, the configured task, and public URLs. No captured OpenStax text or learner evidence was sent.
- Authority: the executor may create reviewed local course records. The model may only propose. The runtime remains the scoring and keyed-disclosure authority. Human visual, screen-reader, and instructional acceptance remains owed.

## Verified title and rights

Accessed 2026-09-07 from the exact title and section pages.

| Field | Recorded value |
|---|---|
| Title | *College Algebra 2e* |
| Edition and publication | Second edition, published December 21, 2021 |
| Author and publisher | Jay Abramson, OpenStax, Rice University |
| Canonical book URL | https://openstax.org/books/college-algebra-2e/pages/1-introduction-to-prerequisites |
| Representative section | https://openstax.org/books/college-algebra-2e/pages/2-2-linear-equations-in-one-variable |
| Licence | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 |
| Licence URL | https://creativecommons.org/licenses/by-nc-sa/4.0/ |
| Attribution | Access for free at the canonical book URL above. Credit Jay Abramson, OpenStax, Rice University. |
| Permitted for this personal course | read, quote with attribution, transform noncommercially under share-alike, package, export, and share under the same restrictions |
| Restricted | no commercial use; preserve attribution and share-alike; trademarks are excluded; do not ingest the book into a large language model without OpenStax permission |
| Captured source id | `9645e62714424417` |
| Normalized source SHA-256 | `001ff4ac6f48ef31d06b9c559dc22c7914c5166f32a0cfecfda45ff96c3cdd13` |
| Snapshot SHA-256 | `bb4557f279e0a5254f79ce88430d17376fb8f2e54b10f30d16677a79eb93366d` |

The live web title and section displayed the current licence and the separate model-ingestion restriction. An older downloadable PDF reports CC BY 4.0. The current title page was used because rights were read per title at execution time and the more restrictive current statement controls this operation.

## Representative scope and treatments

Course object `95dbccc7716142cc` contains unit `07c579b90823454e` and two locally authored objectives:

1. `88962d96fe7048bd`: solve linear equations while preserving equality, distributing correctly, and isolating the variable.
2. `ddcef5efe9a44762`: classify a simplified linear equation as conditional, an identity, or inconsistent and justify the classification.

Both objectives bind to the captured section at its stable solving-linear-equations locator. Objective 2 uses `direct-reading`, because the source gives the three classifications, definitions, and worked examples together. Objective 1 needs a short guided lesson that foregrounds error checking, substitution, and changed-context transfer. That treatment was requested through the Agent door, but no proposal was accepted because the local backend response was malformed.
