"""Source attribution and paraphrase passes behind the model facade."""
import hashlib, os, re


# ---- plan 03.2-04: winnowing paraphrase lint (D-13) -----------------------
# stdlib-only winnowing over k-gram fingerprints. The window size is the
# executor's discretion (03.2-CONTEXT "Claude's discretion"): the selection
# below is the standard min-hash-per-window winnowing (Schleimer et al.), and
# the shipped default window is 1 -- the deterministic end of the family,
# where every k-gram is its own window minimum. A larger window would thin
# the fingerprint set but loses the exactness the copy-run measurement needs,
# so the default trades memory for determinism: the stage-4 gate (D-08) must
# be deterministic, and the source text itself is read transiently, reduced
# to hashes, and never stored or echoed (T-032-12).

PARAPHRASE_DEFAULTS = {"winnow_threshold": 8, "jaccard_threshold": 0.25}
_PARAPHRASE_K = 4           # word k-gram size
_PARAPHRASE_WINDOW = 1      # winnowing window: min-hash per window; 1 = no thinning

_SPECIFIC_FACT_RE = re.compile(
    r"(?:\d+(?:\.\d+)?\s*(?:mg|mcg|µg|mcg/kg|mg/kg|g|kg|mL|ml|L|cm|mm|m|IU|"
    r"mEq|mmol|units?|U|drops?|gtts?|bpm|mmHg|mm\s?Hg|min|hrs?|sec|%))"
    r"|\d+\.\d+",
    re.I)



def _fingerprint_tokens(text):
    """The word tokens a paraphrase fingerprint is built from: lowercase
    alphanumeric runs, so case and punctuation never create false distinct
    k-grams."""
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _gram_hash(gram):
    """A stable, process-independent hash of one k-gram (stdlib sha1), so the
    fingerprint is identical across runs -- the deterministic stage-4 gate
    must never vary with PYTHONHASHSEED."""
    return int.from_bytes(
        hashlib.sha1(" ".join(gram).encode("utf-8")).digest()[:8], "big")


def _kgram_hashes(text, k=_PARAPHRASE_K):
    """The k-gram hash list of `text`: hash(words[i:i+k]) for each position."""
    words = _fingerprint_tokens(text)
    return [_gram_hash(words[i:i + k]) for i in range(len(words) - k + 1)]


def _winnow_positions(hashes, window=_PARAPHRASE_WINDOW):
    """Winnowing (Schleimer et al.): the minimum hash in each sliding window
    of `window` consecutive k-grams is selected, rightmost on a tie. Returns
    the selected positions. With the default window 1 every k-gram is its own
    minimum -- the full fingerprint, kept for run-exactness."""
    out = set()
    if not hashes:
        return out
    w = max(1, int(window))
    for i in range(len(hashes) - w + 1):
        chunk = hashes[i:i + w]
        j = i + max(idx for idx, h in enumerate(chunk)
                    if h == min(chunk))
        out.add(j)
    return out


def _winnow_set(hashes, window=_PARAPHRASE_WINDOW):
    return {hashes[i] for i in _winnow_positions(hashes, window)}


def paraphrase_check(candidate_text, source_text, winnow_threshold=8,
                     jaccard_threshold=0.25):
    """The winnowing-based paraphrase comparison (D-13, SEED-05). Both texts
    are reduced to k-gram hashes -- fingerprints only, the source text is
    never stored. Returns a dict:
        copy_words -- the longest run of consecutive candidate words that
            appear verbatim in the source (matching k-gram run + k - 1)
        jaccard    -- |candidate fp & source fp| / |candidate fp | source fp|
        copy       -- copy_words >= winnow_threshold
        overlap    -- jaccard > jaccard_threshold
    """
    c_hashes = _kgram_hashes(candidate_text)
    s_set = set(_kgram_hashes(source_text))
    run = best = 0
    for h in c_hashes:
        if h in s_set:
            run += 1
            best = max(best, run)
        else:
            run = 0
    copy_words = best + _PARAPHRASE_K - 1 if best else 0
    c_win = _winnow_set(c_hashes)
    s_win = _winnow_set(_kgram_hashes(source_text))
    union = c_win | s_win
    jaccard = len(c_win & s_win) / len(union) if union else 0.0
    return {"copy_words": copy_words, "jaccard": jaccard,
            "copy": copy_words >= winnow_threshold,
            "overlap": jaccard > jaccard_threshold}


def _read_source_text(base_dir, locators):
    """Read one source's text transiently for fingerprinting. A locator's
    first whitespace token is taken as a path relative to the bank's
    directory. When it cannot be read -- a prose locator, or a corpus that
    lives outside the repo (D-17) -- the check degrades gracefully to None,
    never an error, and never a stored byte."""
    if not locators or not locators.strip():
        return None
    first = locators.strip().split()[0]
    path = os.path.join(base_dir or ".", first)
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _item_text(q):
    """The full author-written text surface of a parsed item (stem, options,
    rationale fields, table rows, build steps) -- what the paraphrase and
    unsourced-specific checks scan."""
    import model
    parts = []
    if q.get("stem"):
        parts.append(q["stem"])
    for letter in sorted(q.get("opts") or {}):
        v = q["opts"].get(letter)
        if v:
            parts.append(v)
    for _, t in model._rationale_texts(q):
        parts.append(t)
    for row in q.get("rows") or []:
        parts.append(row.get("text", ""))
    for step in q.get("steps") or []:
        parts.append(step)
    return "\n".join(p for p in parts if p)


def paraphrase_findings(candidate_text, sources, thresholds=None,
                        item_tag=None, subject="the text"):
    """Paraphrase findings for `candidate_text` against every source its
    [SRC:] directives resolve to (D-13). With `item_tag`, only directives
    carried by that item are compared (the bank-lint case); without it, every
    directive in `sources` is used (the seeding-draft case, where the draft's
    own [SRC:]s are resolved by the caller). Returns (code, message) pairs;
    the source text is read transiently and reduced to hashes, and the
    messages name only the source id and file -- never its content."""
    th = dict(PARAPHRASE_DEFAULTS)
    if thresholds:
        th.update(thresholds or {})
    out = []
    if not sources:
        return out
    known = sources.get("sources") or {}
    path = sources.get("path") or ""
    fname = os.path.basename(path) if path else "the bank"
    base_dir = os.path.dirname(os.path.abspath(path)) if path else "."
    seen = set()
    for d in sources.get("srcs") or []:
        if item_tag is not None and d.get("item") != item_tag:
            continue
        sid = d.get("id") or ""
        if sid not in known or sid in seen:
            continue
        seen.add(sid)
        locators = (d.get("locators") or "").strip() or (known[sid] or "")
        text = _read_source_text(base_dir, locators)
        if text is None:
            continue
        r = paraphrase_check(candidate_text, text,
                             th["winnow_threshold"], th["jaccard_threshold"])
        if r["copy"]:
            out.append(("prov.paraphrase_copy",
                        "%d consecutive words of %s match source '%s' of %s "
                        "verbatim -- rewrite, or this is transcription"
                        % (r["copy_words"], subject, sid, fname)))
        elif r["overlap"]:
            out.append(("prov.paraphrase_overlap",
                        "%s shares fingerprint overlap %.2f with source '%s' "
                        "of %s -- paraphrase more freely"
                        % (subject, r["jaccard"], sid, fname)))
    return out


def unsourced_specific_findings(q, sources, item_tag):
    """style.unsourced_specific (D-14): numerals, units and doses in an item's
    text with no resolved [SRC:] are a structural error -- a seeded specific
    must name the source it came from. Structural regex, never a model
    judgement (D-14); a resolved [SRC:] on the item satisfies it."""
    import model
    if not sources:
        return []
    known = sources.get("sources") or {}
    path = sources.get("path") or ""
    fname = os.path.basename(path) if path else "the bank"
    has_src = any(d.get("item") == item_tag and d.get("id") in known
                  for d in sources.get("srcs") or [])
    if has_src:
        return []
    m = _SPECIFIC_FACT_RE.search(_item_text(q))
    if not m:
        return []
    return [model.LintError("style.unsourced_specific", "src", item_tag,
                      "item carries the specific fact %r with no resolved "
                      "[SRC:] -- cite the source it came from in %s"
                      % (m.group(0).strip(), fname))]


