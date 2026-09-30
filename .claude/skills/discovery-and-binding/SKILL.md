---
name: discovery-and-binding
description: "Stub: the integrated guided discovery workflow has not shipped. For approved read-only inventory and source, rights, objective, or treatment binding, use the documented existing CLI fallback."
---

# Discover and bind sources

The integrated guided skill remains unavailable. Discovery and binding primitives exist; use them explicitly instead of inventing an all-roots discovery command.

Read [OPERATION-CONTRACT.md](../OPERATION-CONTRACT.md). Repository paths are relative to the checkout root; reference links are relative to this skill directory. Check `python itembank.py course --help` and `python itembank.py bind --help` for this build's arguments.

Inventory only approved roots, read-only. Record path, stable ID, fingerprint, provenance, source rights, objective links and extraction limits. Same ID with divergent bytes is a conflict; matching names never prove identity. Report roots not scanned. Check the current course policy before inspecting source content.

Use `course show` and `bind list` for existing records. `source import --preview` can inspect extraction without accepting an import. Creating or registering a source, importing, granting rights and binding are separate mutations; execute only the operations already authorized under the declared manifest. `course register-source`, `course add-source`, `bind rights`, `bind source` and `bind treatment` provide the bounded surfaces. Preserve unknown rights as unknown.

Review the proposed identity and bindings before acceptance. Verify the resulting records, citations and source availability afterward. Use the operation's journal and tested reversal path; a reversible claim requires an actual restore check on representative synthetic data. Report conflicts without merging or overwriting accepted material.
