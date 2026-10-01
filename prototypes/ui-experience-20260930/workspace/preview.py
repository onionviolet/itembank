"""Render only synthetic workspace material and record bounded interaction evidence."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    for width, height in [(1440, 1000), (390, 844)]:
        for theme in ["light", "dark"]:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(f"http://127.0.0.1:8843/?theme={theme}")
            prefix = f"{width}-{theme}"
            page.screenshot(path=str(ROOT / "evidence" / f"{prefix}-reading.png"), full_page=True)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            if width > 760:
                page.locator("#divider").focus()
                page.keyboard.press("ArrowLeft")
                assert page.locator("#divider").get_attribute("aria-valuenow") == "62"
                divider = page.locator("#divider").bounding_box()
                page.mouse.move(divider["x"] + 6, divider["y"] + 100)
                page.mouse.down()
                page.mouse.move(divider["x"] + 65, divider["y"] + 100)
                page.mouse.up()
            page.locator("#elapsed").fill("8")
            assert "gap is 16 metres" in page.locator("#meaning").inner_text()
            page.locator("#note-open").click()
            page.locator("#note").fill("The gap adds 2 metres each second.")
            page.locator("#save").click()
            assert page.locator("#save-status").inner_text() == "Saved in this browser"
            page.screenshot(path=str(ROOT / "evidence" / f"{prefix}-note.png"), full_page=True)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.locator("#note-panel .return-passage").click()
            assert page.evaluate("document.activeElement.id") == "note-open"
            page.locator("#reference-open").click()
            page.screenshot(path=str(ROOT / "evidence" / f"{prefix}-reference.png"), full_page=True)
            page.locator("#reference-panel .return-passage").click()
            assert page.evaluate("document.activeElement.id") == "reference-open"
            page.locator("#practice-bottom").click()
            page.locator("#answer").fill("16")
            page.locator("#reveal").click()
            assert page.locator("#worked").is_visible()
            page.screenshot(path=str(ROOT / "evidence" / f"{prefix}-prediction.png"), full_page=True)
            page.locator("#practice-return").click()
            assert page.evaluate("document.activeElement.id") == "practice-bottom"
            page.locator("#practice-bottom").click()
            assert page.locator("#answer").input_value() == "16"
            page.locator("#practice-return").click()
            page.reload()
            page.locator("#note-open").click()
            assert page.locator("#note").input_value() == "The gap adds 2 metres each second."
            page.evaluate("() => { Storage.prototype.setItem = function(){throw new Error('synthetic unavailable storage')}; }")
            page.locator("#note").fill("Keep this draft when saving fails.")
            page.locator("#save").click()
            assert "Draft retained" in page.locator("#save-status").inner_text()
            assert page.locator("#note").input_value() == "Keep this draft when saving fails."
            assert not errors, errors
            results.append({"viewport": [width, height], "theme": theme, "overflow": False,
                            "journey": "read, manipulate, note, save, reference, return, prediction, return, reload, save failure",
                            "focus_return": True, "note_restore": True, "draft_on_failure": True,
                            "keyboard_resize": width > 760, "page_errors": errors})
            page.close()
    for width in [320, 768]:
        page = browser.new_page(viewport={"width": width, "height": 844})
        page.goto("http://127.0.0.1:8843/")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator("#elapsed").focus()
        page.keyboard.press("ArrowRight")
        assert page.locator("#elapsed").input_value() == "7"
        results.append({"viewport": [width, 844], "overflow": False, "keyboard_time_control": True})
        page.close()
    page = browser.new_page(java_script_enabled=False, viewport={"width": 390, "height": 844})
    page.goto("http://127.0.0.1:8843/")
    assert page.locator("#meaning").is_visible()
    assert "18 metres" in page.locator("#meaning").inner_text()
    assert page.locator("#bar-a").evaluate("el => el.getBoundingClientRect().width") > 0
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    results.append({"viewport": [390, 844], "javascript": False, "static_meaning": True, "overflow": False})
    page.close()
    browser.close()
(ROOT / "evidence" / "preview.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
