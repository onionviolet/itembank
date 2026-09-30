#!/usr/bin/env python3
"""Teaching color roles remain readable and independent of assessment and accents."""
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from contextlib import ExitStack

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import theme, looks, settings, lesson, presentation


def check_roles():
    config = settings.defaults_from_schema(settings.load_schema())
    assert config["accent"]["source"] == theme.DEFAULT_ACCENT
    for mode in ("light", "dark", "oled"):
        for look in looks.LOOK_IDS:
            for accent in (theme.DEFAULT_ACCENT, "#0e6e62", "#ffff00", "#ff0000"):
                tokens = theme._grounded(theme.derive_theme(accent)[mode], look, mode)
                for role in ("source", "note"):
                    mark, bg = tokens[role + "_mark"], tokens[role + "_bg"]
                    assert mark == theme.CONTENT_TOKENS[mode][role + "_mark"]
                    for foreground in (mark, tokens["ink"], tokens["mut"]):
                        ratio = theme.contrast_ratio(foreground, bg)
                        assert ratio >= 4.5, (mode, look, role, foreground, bg, ratio)
                    for verdict in ("ok", "bad", "warn", "pending"):
                        assert mark != tokens[verdict], "teaching color aliases a verdict"
                for foreground in ("ink", "mut"):
                    for bg in ("bg", "card", "chip"):
                        assert theme.contrast_ratio(tokens[foreground], tokens[bg]) >= 4.5
                css = theme.theme_css({"theme": mode, "look": look, "accent": {"source": accent}})
                for token in ("source-mark", "source-bg", "note-mark", "note-bg"):
                    assert "--" + token + ":" in css
    assert theme.BASE_TOKENS["oled"]["bg"] == "#000000"
    assert theme.BASE_TOKENS["dark"]["bg"] != "#000000"
    assert theme.derive_theme("#0e6e62")["source"] == "#0e6e62"


def check_shared_finish():
    css = lesson.product_reader_css()
    for token in (".callout-excerpt", "var(--source-mark)", "var(--note-mark)",
                  ".callout-example", "#lesson-content pre"):
        assert token in css
    assert "prefers-reduced-motion:reduce" in presentation.PRODUCT_CSS
    assert "transition-duration:0s!important" in presentation.PRODUCT_CSS
    assert "var(--note-bg)" in presentation.PRODUCT_CSS
    assert "var(--source-mark)" in presentation.PRODUCT_CSS


def browser_preview():
    """Hold disposable live light/dark routes, never the installed learner root."""
    import sample_course
    from daemon_roundtrip import start_daemon
    processes = []
    with ExitStack() as stack:
        try:
            for mode in ("light", "dark"):
                root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="visual_character_")))
                directory = root / "sample"
                sample_course.write_sample_course(str(directory))
                bank = directory / "study_skills_sample.md"
                body = bank.read_text()
                body = body.replace("Q1.", "> [!NOTE]\n> A private note is your own record, separate from the source.\n\n"
                                    "> [!EXCERPT]\n> Synthetic source: this passage exists only to exercise the reader.\n\n"
                                    "```python\nfor day in [1, 3, 7]:\n    print(day)\n```\n\nQ1.", 1)
                bank.write_text(body)
                config = settings.defaults_from_schema(settings.load_schema())
                config["theme"] = mode
                settings.write_settings(str(root), config)
                proc, url, _ = start_daemon(str(root))
                processes.append(proc)
                print(mode + " Home: " + url, flush=True)
                print(mode + " Reading: " + url + "lesson/study_skills_sample", flush=True)
                print(mode + " Practice: " + url + "quiz/study_skills_sample", flush=True)
            input("Press Enter to stop these disposable preview servers.\n")
        finally:
            for proc in processes:
                proc.terminate()
                proc.wait(timeout=5)


def check_packaged_palette(runtime_path):
    """Exercise the shipped render path instead of assuming source parity."""
    executable = Path(runtime_path).resolve()
    command = [sys.executable, str(executable)] if executable.suffix == ".pyz" else [str(executable)]
    with tempfile.TemporaryDirectory(prefix="packaged_palette_") as temp:
        bank = Path(temp) / "synthetic.md"
        bank.write_bytes((Path(ROOT) / "fixtures" / "sample_bank.md").read_bytes())
        out = Path(temp) / "quiz.html"
        result = subprocess.run(command + ["build", str(bank), str(out)],
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, (result.stdout, result.stderr)
        page = out.read_text()
        for token in ("--bg:#f5f4f0", "--bg:#14161b", "--source-mark:", "--note-bg:"):
            assert token in page, "packaged output omitted " + token


if __name__ == "__main__":
    check_roles()
    check_shared_finish()
    if "--browser-hold" in sys.argv:
        browser_preview()
    if "--runtime" in sys.argv:
        check_packaged_palette(sys.argv[sys.argv.index("--runtime") + 1])
    print("visual character: readable teaching roles, custom accents, OLED and reduced motion ok")
