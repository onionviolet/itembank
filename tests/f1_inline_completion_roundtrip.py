#!/usr/bin/env python3
"""Inline completion preserves the existing category assignment contract."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from surfaces import quiz_page


def main():
    item = {"type": "dnd", "categories": ["red", "blue"],
            "rows": [{"id": "same1", "text": "A ___ token."},
                     {"id": "same2", "text": "A ___ token."},
                     {"id": "plain", "text": "Plain row"}]}
    rendered = quiz_page._form_controls(item, {"row_1": ["blue"]})
    assert rendered.count('class="inline-completion"') == 2
    assert 'name="row_0"' in rendered and 'name="row_1"' in rendered
    assert 'value="blue" selected' in rendered
    assert 'Blank 1: A ___ token.' in rendered
    assert 'class="rowline"' in rendered
    item["rows"] = [{"id": "literal", "text": "Two ___ and ___ markers"}]
    assert 'inline-completion' not in quiz_page._form_controls(item)
    item["type"] = "table"
    item["rows"] = [{"id": "literal", "text": "One ___ marker"}]
    assert 'inline-completion' not in quiz_page._form_controls(item)
    item["type"] = "dnd"
    item["rows"] = [{"id": "escaped", "text": '<script> ___ & end'}]
    assert '&lt;script&gt;' in quiz_page._form_controls(item)
    print("F1 inline completion roundtrip: ok")


if __name__ == "__main__":
    main()
