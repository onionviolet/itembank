"""Identity splicing behind the model facade."""
import hashlib, re


def _key_content_hash(block_lines):
    """The change-detection digest of one `> [!KEY]` block's content --
    title and body lines only, never its `[ID:]`/`[HASH:]` directive lines,
    so minting an id never reads as content drift and editing the body
    always does."""
    parts = []
    for line in block_lines:
        stripped = re.sub(r"^>\s?", "", line).strip()
        if re.match(r"^\[(ID|HASH):", stripped):
            continue
        if stripped:
            parts.append(stripped)
    return "sha256:" + hashlib.sha256(
        ("\n".join(parts)).encode("utf-8")).hexdigest()[:16]


def _assign_key_ids(chunk, taken, changes, key_count):
    """Mint `[ID:]`/`[HASH:]` into every `> [!KEY]` block of one preamble
    chunk, using the exact `new_item_id()`/taken-set path items use -- there
    is no separate key id namespace (research Pitfall 5). Returns the
    rewritten chunk text. `key_count` is a one-element list so the K-tags
    stay sequential across chunks."""
    import model
    lines = chunk.split("\n")
    out = []
    i = 0
    while i < len(lines):
        m = model._KEY_MARK_RE.match(lines[i])
        if m is None:
            out.append(lines[i])
            i += 1
            continue
        start = i
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            i += 1
        block_lines = lines[start:i]
        raw = "\n".join(block_lines)
        key_count[0] += 1
        tag = "K%d" % key_count[0]

        had_id = model.grab(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", raw)
        item_id = had_id
        id_action = "kept"
        if not item_id:
            item_id = model.new_item_id()
            while item_id in taken:
                item_id = model.new_item_id()
            id_action = "assigned"
        taken.add(item_id)

        old_hash = model.grab(r"(?m)^>\s*\[HASH:\s*(\S+)\s*\]", raw)
        new_hash = _key_content_hash(block_lines)
        if not old_hash:
            hash_action = "recorded"
        elif old_hash != new_hash:
            hash_action = "updated"
        else:
            hash_action = "unchanged"

        changes.append({"item": tag, "item_id": item_id,
                        "action": id_action, "hash_action": hash_action,
                        "old_hash": old_hash, "new_hash": new_hash})

        if id_action == "kept" and hash_action == "unchanged":
            out.extend(block_lines)
            continue

        new_lines = []
        inserted_id = False
        inserted_hash = False
        for line in block_lines:
            if re.match(r"^>\s*\[ID:", line):
                if had_id:
                    new_lines.append("> [ID: %s]" % item_id)
                    inserted_id = True
                continue
            if re.match(r"^>\s*\[HASH:", line):
                if old_hash:
                    new_lines.append("> [HASH: %s]" % new_hash)
                    inserted_hash = True
                continue
            new_lines.append(line)
        pos = 1
        if not inserted_id:
            new_lines.insert(pos, "> [ID: %s]" % item_id)
            pos += 1
        if not inserted_hash:
            new_lines.insert(pos, "> [HASH: %s]" % new_hash)
        out.extend(new_lines)
    return "\n".join(out)


def assign_ids(text, taken=None):
    """Pure text transform: mint a missing `[ID:]` and record or refresh
    `[HASH:]` for every question block in `text`. Returns `(new_text,
    changes)` and touches no file -- `surfaces/evidence_cli.py:cmd_id_assign`
    is the only writer, so `lint` stays read-only (D-03).

    `taken` is a set of ids already claimed elsewhere -- a caller assigning
    across several banks in one pass adds each minted id to it, so D-05's
    global uniqueness holds across the whole pass, not just within one bank.

    A block whose id and hash are both already current is passed through
    unchanged, so a no-change run returns `new_text == text` byte for byte: a
    transform that reformats a file it did not need to touch is a transform
    nobody will run on a real bank.
    """
    import model
    if taken is None:
        taken = set()
    # Prepass: every existing [ID:] in the bank -- item and key alike --
    # joins the claimed set before anything is minted, so a key can never
    # collide with an item id that already exists in this bank (Pitfall 5).
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if re.match(r"Q\d+\.", ch.strip()):
            q = model.parse_question(ch)
            if q and q.get("item_id"):
                taken.add(q["item_id"])
        else:
            for km in re.finditer(r"(?m)^>\s*\[ID:\s*(\S+)\s*\]", ch):
                taken.add(km.group(1))
    changes = []
    out_chunks = []
    idx = 0
    key_count = [0]
    for ch in re.split(r"(?m)^(?=Q\d+\.)", text):
        if not re.match(r"Q\d+\.", ch.strip()):
            out_chunks.append(_assign_key_ids(ch, taken, changes, key_count))
            continue
        q = model.parse_question(ch)
        if q is None:
            out_chunks.append(ch)
            continue
        idx += 1
        tag = "Q%d" % idx

        had_id = q.get("item_id", "")
        item_id = had_id
        id_action = "kept"
        if not item_id:
            item_id = model.new_item_id()
            while item_id in taken:
                item_id = model.new_item_id()
            id_action = "assigned"
        taken.add(item_id)

        old_hash = q.get("content_hash", "")
        new_hash = model.content_fingerprint(q)
        if not old_hash:
            hash_action = "recorded"
        elif old_hash != new_hash:
            hash_action = "updated"
        else:
            hash_action = "unchanged"

        changes.append({"item": tag, "item_id": item_id, "action": id_action,
                        "hash_action": hash_action, "old_hash": old_hash,
                        "new_hash": new_hash})

        if id_action == "kept" and hash_action == "unchanged":
            out_chunks.append(ch)
            continue

        chunk = ch
        if had_id:
            chunk = re.sub(r"(?m)^\[ID:\s*\S+\s*\]", "[ID: %s]" % item_id, chunk, count=1)
        if old_hash:
            chunk = re.sub(r"(?m)^\[HASH:\s*\S+\s*\]", "[HASH: %s]" % new_hash, chunk, count=1)

        to_insert = []
        if not had_id:
            to_insert.append("[ID: %s]" % item_id)
        if not old_hash:
            to_insert.append("[HASH: %s]" % new_hash)
        if to_insert:
            insert_text = "\n".join(to_insert) + "\n"
            m = model.TERMINATOR.search(chunk)
            if m:
                chunk = chunk[:m.start()] + insert_text + chunk[m.start():]
            else:
                if not chunk.endswith("\n"):
                    chunk += "\n"
                chunk += insert_text

        out_chunks.append(chunk)
    new_text = "".join(out_chunks)
    return new_text, changes

# The one honest-limits sentence for a check item, worded once and reused
# verbatim: SPEC ends its check section with it, and plan 05-05 substitutes
# the same constant into the browser copy beside the editor (D-10). Two
# readers, one source.
