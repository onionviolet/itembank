#!/usr/bin/env python3
"""Smoke-test the canonical study and Anki export surfaces."""
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "itembank.py"
BANK = ROOT / "fixtures" / "sample_bank.md"


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                          cwd=ROOT, check=True, capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        study = Path(tmp) / "study.html"
        basic = Path(tmp) / "basic.tsv"
        cloze = Path(tmp) / "cloze.tsv"
        run("study", BANK, study)
        run("export", BANK, basic)
        run("export", BANK, cloze, "--format", "cloze")
        assert "Flashcards" in study.read_text(encoding="utf-8")
        assert "#notetype:Basic" in basic.read_text(encoding="utf-8")
        assert "#notetype:Cloze" in cloze.read_text(encoding="utf-8")
        assert "{{c1::" in cloze.read_text(encoding="utf-8")
    print("study and export surfaces: ok")


if __name__ == "__main__":
    main()
