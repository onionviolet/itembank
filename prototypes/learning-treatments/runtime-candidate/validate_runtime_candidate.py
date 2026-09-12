"""Exercise the synthetic candidate through the shipped CLI and runtime only."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BANK = Path(__file__).with_name("water-process-hotspot.txt")
PLACEMENT = BANK.with_name("water-process-placement.txt")
TABLE = BANK.with_name("rainfall-comparison.txt")
SOURCE = BANK.parent.parent / "figures.md"


def run(*args):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "itembank.py"), *map(str, args)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.stdout


def start_and_next(bank_path, session_path):
    run("start", bank_path, "--count", "1", "--mode", "practice", "--out", session_path)
    return json.loads(run("next", session_path))


def assert_no_key(payload):
    private = {"scoring", "correct", "why_best", "trap", "model", "rubric", "cat"}
    if isinstance(payload, dict):
        if "accepted" in payload and not isinstance(payload["accepted"], bool):
            raise AssertionError("private accepted-state mapping in public payload")
        if private.intersection(payload):
            raise AssertionError("private fields in public payload: " + str(private.intersection(payload)))
        for value in payload.values():
            assert_no_key(value)
    elif isinstance(payload, list):
        for value in payload:
            assert_no_key(value)


def validate_placement(bank, root):
    session = root / "placement-right.json"
    public = start_and_next(bank, session)
    assert_no_key(public)
    item = public["item"]
    assert item["type"] == "dnd"
    assert len(item["rows"]) == 4
    assert item["categories"] == ["Location 1", "Location 2", "Location 3", "Location 4"]
    expected = {"Evaporation": "Location 1", "Condensation": "Location 2",
                "Precipitation": "Location 3", "Runoff": "Location 4"}
    assert {row["text"] for row in item["rows"]} == set(expected)
    assert "figures.md#source-figure-2" in item["stem"]
    assert all(set(row) == {"id", "text"} for row in item["rows"])
    answer = {str(row["id"]): expected[row["text"]] for row in item["rows"]}
    right = json.loads(run("submit", session, "--answer", json.dumps(answer)))
    assert right["score"] is True
    wrong_session = root / "placement-wrong.json"
    wrong_item = start_and_next(bank, wrong_session)["item"]
    wrong_answer = {str(row["id"]): "Location 1" for row in wrong_item["rows"]}
    wrong = json.loads(run("submit", wrong_session, "--answer", json.dumps(wrong_answer)))
    assert wrong["score"] is False
    print("placement: four supplied labels, no private mapping, correct=true, incorrect=false")


def validate_table(bank, root):
    responses = ["Gauge B is 6 mm higher. Both readings cover 24 hours.",
                 "Gauge A is 100 mm higher because it was collected for a week.",
                 "I cannot tell."]
    for index, answer in enumerate(responses):
        session = root / f"table-{index}.json"
        public = start_and_next(bank, session)
        assert_no_key(public)
        item = public["item"]
        assert item["type"] == "short"
        for context in ("12 mm", "18 mm", "24 hours", "figures.md#source-table-1"):
            assert context in item["stem"]
        result = json.loads(run("submit", session, "--answer", json.dumps(answer)))
        assert result["score"] is None
        assert result["action"] == "defer_feedback"
        assert_no_key(result)
        report = json.loads(run("report", session))
        assert report["summary"]["pending_manual"] == 1
        assert json.loads(run("next", session))["item"]["id"] == item["id"]
    print("table: source values and locator present, three prose responses score=null, pending_manual=1 each")


def main():
    source_text = SOURCE.read_text(encoding="utf-8")
    for anchor in ('id="source-figure-2"', 'id="source-table-1"'):
        assert anchor in source_text

    with tempfile.TemporaryDirectory(prefix="itembank-runtime-candidate-") as root:
        root = Path(root)
        banks = root / "runtime-candidate"
        banks.mkdir()
        shutil.copy2(SOURCE, root / SOURCE.name)
        for candidate in (BANK, PLACEMENT, TABLE):
            copied = banks / candidate.name
            shutil.copy2(candidate, copied)
            lint = run("lint", copied)
            assert "0 errors" in lint, lint
            print(candidate.name + ": " + lint.strip().splitlines()[-1])
            stats = run("stats", copied)
            coverage = run("coverage", copied)
            print(stats.strip())
            print(coverage.strip())
            run("build", copied, root / (candidate.stem + ".html"))
        temp_bank = banks / BANK.name
        public = start_and_next(temp_bank, root / "wrong.json")
        assert_no_key(public)
        rendered = json.dumps(public).lower()
        for private_fragment in ('"scoring"', '"accepted"', "evaporation"):
            if private_fragment in rendered:
                raise AssertionError("public item leaked private material: " + private_fragment)
        item = public["item"]
        if item["type"] != "visual" or item["interaction_contract"]["type"] != "visual":
            raise AssertionError("runtime did not serve the visual interaction contract")
        if "region-a" not in rendered or "region-b" not in rendered:
            raise AssertionError("public contract omitted the response identifiers")

        wrong = json.loads(run("submit", root / "wrong.json", "--answer", json.dumps({"kind": "hotspot", "region": "region-b"})))
        if wrong.get("score") is not False:
            raise AssertionError("runtime did not determine the wrong response")

        run("start", temp_bank, "--count", "1", "--mode", "practice", "--out", root / "right.json")
        right = json.loads(run("submit", root / "right.json", "--answer", json.dumps({"kind": "hotspot", "region": "region-a"})))
        if right.get("score") is not True:
            raise AssertionError("runtime did not determine the correct response")
        print("hotspot: no private scoring, incorrect=false, correct=true")
        validate_placement(banks / PLACEMENT.name, root)
        validate_table(banks / TABLE.name, root)
        assert list(banks.rglob("evidence.jsonl")), "runtime evidence missing from disposable root"

    print("PASS: three candidates, rich builds, source locators, disclosure and runtime results. Temporary outputs removed.")


if __name__ == "__main__":
    main()
