#!/usr/bin/env python3
"""The Phase 16C shared synthetic corpus: four fictional subjects every later
16C plan consumes for notes, strategies, claims, the trio, and the legacy
upgrade.

Every string in this file is fictional, invented for fixtures, and no line
derives from any real course, book, learner, exam, or textbook. Banks are
written only to caller-supplied directories, never into the repository tree,
so nothing this module produces can reach a commit. `itembank guard` is the
mechanical backstop for that promise, not this docstring.

These banks are note and strategy fixtures, not authored courseware. They are
built to PARSE: `model.load` returns at least two items, `parse_lesson`
returns at least four headings, and `parse_terms` returns at least four terms.
They are deliberately NOT required to pass `itembank lint`, whose distractor,
position-skew, and confidence rules belong to the authoring skill and would
make every fixture edit an authoring exercise. A reviewer who wants
lint-clean corpus banks is asking for a fixture-quality upgrade with its own
plan, not for a defect fix here.

Determinism is a contract: building twice into two directories produces
byte-identical files, because the content is literal and `SEED` seeds every
`random.Random` use. Plan 16C-06 and the trio depend on that.

Naming, per D-16C-6: strategy-action states are learner task states
(lowercase activity); the Activity view (capitalized) is the 16B IA jobs area
and is not this module's subject.
"""
import os
import random


SEED = 1603

SUBJECTS = ("emt_respiratory", "math_linear_system", "cs_loop_invariant",
            "history_conflicting_accounts")


# One record per subject. `headings` is a list of (title, body) pairs; the
# body carries at least one [[term]] reference so the trio's concept-map
# edges have real refs to read (D-16C-7). `terms` is a list of
# (canonical, definition) pairs. `items` is the literal question block.
_TITLES = {
    "emt_respiratory":
        "# Fictional respiratory assessment drill (synthetic fixture)",
    "math_linear_system":
        "# Fictional two-variable linear system drill (synthetic fixture)",
    "cs_loop_invariant":
        "# Fictional loop invariant walkthrough (synthetic fixture)",
    "history_conflicting_accounts":
        "# Fictional conflicting-accounts reading (synthetic fixture)",
}

_PREAMBLE = ("Invented teaching content for the Phase 16C note and strategy "
             "fixtures. It is not derived from any real course, exam, or "
             "textbook, and every name in it is made up.")

_HEADINGS = {
    "emt_respiratory": [
        ("Counting the breaths",
         "The first measurement in this fictional drill is the [[respiratory "
         "rate]], counted for a full thirty seconds and doubled. A learner "
         "who counts for ten seconds and multiplies by six inherits the "
         "error of every pause. The count is taken before the learner asks "
         "the patient anything, because a person who knows they are being "
         "counted breathes differently."),
        ("Reading the effort",
         "Rate alone decides nothing. The invented protocol pairs it with "
         "[[work of breathing]]: whether the shoulders lift, whether speech "
         "arrives in whole sentences or in three-word fragments, and whether "
         "the chest rises evenly. A normal rate with heavy effort is the "
         "case this drill exists to teach."),
        ("The two sounds that change the plan",
         "Two invented sounds separate the branches. A high whistle on the "
         "way in points at the upper airway and at [[positioning]]. A coarse "
         "rattle spread through both fields points lower and does not "
         "improve with positioning at all. Naming the sound before choosing "
         "the action is the whole discipline here."),
        ("When the numbers disagree",
         "The drill closes on a disagreement: a fast rate, easy effort, and "
         "a calm patient. The fictional guidance is to trust the effort over "
         "the number, record both, and recount. A recorded disagreement is "
         "evidence; a silently discarded number is not."),
    ],
    "math_linear_system": [
        ("Two lines, one question",
         "A [[linear system]] in this fictional unit asks where two lines "
         "meet. The answer is a point, a whole line, or nothing at all, and "
         "the three cases are told apart before any arithmetic starts. "
         "Learners who begin by solving lose the habit of asking which case "
         "they are in."),
        ("Substitution, carefully",
         "The invented worked path isolates one variable and substitutes it "
         "into the other equation. The step that goes wrong most often in "
         "this drill is the sign carried through the [[substitution]], "
         "because the isolated expression is negative and the parentheses "
         "are dropped."),
        ("Elimination and the scaling trap",
         "The second path scales one equation so a variable cancels. The "
         "trap invented here is scaling only one side, which changes the "
         "line rather than its representation. [[elimination]] is a "
         "rewriting move, and a rewriting move that changes the solution set "
         "is a mistake, not a shortcut."),
        ("Checking is part of the method",
         "Both paths end by putting the candidate point back into both "
         "original equations. In this unit the check is not optional "
         "etiquette; it is the only step that distinguishes a solved system "
         "from a plausible one, and it catches the [[sign error]] that the "
         "substitution step invites."),
    ],
    "cs_loop_invariant": [
        ("What an invariant claims",
         "A [[loop invariant]] is a statement true before the loop starts "
         "and true after every pass. In this fictional walkthrough the "
         "invariant is that everything left of the cursor is already sorted. "
         "The claim is about the state between passes, never about the "
         "state halfway through one."),
        ("The off-by-one this unit is about",
         "The invented code walks indices one through the length of the "
         "list, and the list is indexed from zero. The final pass therefore "
         "reads one past the end. The [[boundary condition]] is the whole "
         "lesson: the invariant holds on every pass that runs, and the bug "
         "is in which passes run at all."),
        ("Tracing three passes by hand",
         "The walkthrough traces a four-element list by hand and stops after "
         "three passes. Two learners in this fixture disagree about whether "
         "the third pass is the last one, and the disagreement is left "
         "standing on purpose so a [[trace table]] has something to settle."),
        ("Fixing it two ways",
         "The invented fix is either to stop one index earlier or to index "
         "from zero throughout. Both are correct and they are not "
         "equivalent: one changes the loop, the other changes the "
         "convention. Recording which was chosen is what makes the next "
         "reader of this fictional code able to follow it."),
    ],
    "history_conflicting_accounts": [
        ("Two diarists, one afternoon",
         "Two invented diarists, Marek Sowa and Ilse Brandt, both write "
         "about the same fictional harbour afternoon. Their accounts agree "
         "on the weather and disagree on almost everything else. A "
         "[[primary account]] is evidence of what its writer believed, "
         "which is not the same as evidence of what happened."),
        ("Where the accounts split",
         "Sowa writes that the crowd gathered before the announcement; "
         "Brandt writes that the announcement drew it. The [[order of "
         "events]] is the contested fact, and it matters because one order "
         "makes the crowd a cause and the other makes it a consequence."),
        ("Reading for interest, not for honesty",
         "Neither invented diarist is lying in this exercise. Sowa stood to "
         "lose a contract if the crowd was blamed, and Brandt wrote for a "
         "readership that expected order. [[interest]] explains a shaped "
         "account better than dishonesty does, and it is the reading this "
         "unit practices."),
        ("What a careful reader may claim",
         "The fictional conclusion is narrow: the announcement and the crowd "
         "both happened that afternoon, and the order is unresolved from "
         "these two sources alone. A [[warranted claim]] states its own "
         "limits, and this unit grades the limits rather than the "
         "confidence."),
    ],
}

_TERMS = {
    "emt_respiratory": [
        ("respiratory rate", "Breaths counted over a full timed window."),
        ("work of breathing", "How hard the invented patient works to move "
                              "air, read from posture and speech."),
        ("positioning", "Changing head and jaw position to open the upper "
                        "airway in this fictional protocol."),
        ("adventitious sound", "Any breath sound this drill treats as added "
                               "to normal air movement."),
    ],
    "math_linear_system": [
        ("linear system", "Two or more linear equations asked about "
                          "together."),
        ("substitution", "Isolating one variable and putting its expression "
                         "into the other equation."),
        ("elimination", "Scaling equations so that adding them removes a "
                        "variable."),
        ("sign error", "A dropped or flipped negative, the error this unit "
                       "is built around."),
    ],
    "cs_loop_invariant": [
        ("loop invariant", "A claim true before the loop and after every "
                           "pass."),
        ("boundary condition", "The first and last values an index takes."),
        ("trace table", "A hand-written table of state after each pass."),
        ("off-by-one", "An error of exactly one position in a boundary."),
    ],
    "history_conflicting_accounts": [
        ("primary account", "A record written by someone present."),
        ("order of events", "Which invented event this reading places "
                            "first."),
        ("interest", "What a writer stood to gain or lose."),
        ("warranted claim", "A claim stating the limits of its own "
                            "evidence."),
    ],
}

# Two parseable items per subject, one `mc` and one `short`. Stems and options
# are invented and are not required to satisfy the authoring linter.
_ITEMS = {
    "emt_respiratory": [
        ("Which finding should change the plan first in this fictional "
         "drill?",
         ("A normal rate with heavy effort",
          "A fast rate with easy effort",
          "A calm patient with even chest rise",
          "A recorded count taken twice"),
         "A",
         "Effort is the finding this invented protocol trusts over the "
         "number."),
        ("Explain why the count is taken before the learner speaks to the "
         "patient, and name one finding that would make you recount.",
         "The count is taken first because a person who knows they are "
         "being counted changes how they breathe. A disagreement between a "
         "fast rate and easy effort is the finding that makes this drill "
         "recount and record both numbers."),
    ],
    "math_linear_system": [
        ("Which step most often introduces the error this unit is about?",
         ("Dropping parentheses around a negative substituted expression",
          "Writing the system in a different order",
          "Checking the candidate point in both equations",
          "Naming which of the three cases applies"),
         "A",
         "The invented worked path loses the sign at the substitution."),
        ("Explain why scaling only one side of an equation is a mistake "
         "rather than a shortcut, and say what it changes.",
         "Scaling one side changes which points satisfy the equation, so it "
         "changes the line itself rather than its representation. "
         "Elimination is a rewriting move, and a rewriting move must leave "
         "the solution set alone."),
    ],
    "cs_loop_invariant": [
        ("In this fictional walkthrough, where is the bug?",
         ("In which passes run, not in the invariant",
          "In the invariant, which is false after the second pass",
          "In the trace table, which counts from one",
          "In the list, which is indexed from one"),
         "A",
         "The invariant holds on every pass that runs; the boundary decides "
         "which run."),
        ("Name the two fixes this walkthrough offers and say why they are "
         "not equivalent.",
         "Stopping one index earlier changes the loop; indexing from zero "
         "throughout changes the convention. Both remove the off-by-one, and "
         "recording which was chosen is what lets the next reader follow the "
         "code."),
    ],
    "history_conflicting_accounts": [
        ("What may a careful reader claim from these two invented diaries "
         "alone?",
         ("That both the announcement and the crowd happened, order "
          "unresolved",
          "That the announcement drew the crowd",
          "That the crowd gathered before the announcement",
          "That one diarist is lying"),
         "A",
         "The unit grades the limits a claim states, not its confidence."),
        ("Explain why interest is a better reading of a shaped account than "
         "dishonesty, using one of the two invented diarists.",
         "Sowa stood to lose a contract if the crowd was blamed, so his "
         "account shapes toward an order that removes the blame without any "
         "need for him to lie. Interest explains the shape and leaves the "
         "account usable as evidence of what he believed."),
    ],
}

# Explicit typed relation data for the trio (D-16C-7): no inline grammar, and
# no relation type outside this closed set.
RELATION_TYPES = ("part_of", "causes", "contrasts_with", "requires")

_RELATIONS = {
    "emt_respiratory": [
        ("counting-the-breaths", "part_of", "reading-the-effort"),
        ("reading-the-effort", "causes", "when-the-numbers-disagree"),
        ("the-two-sounds-that-change-the-plan", "contrasts_with",
         "reading-the-effort"),
        ("when-the-numbers-disagree", "requires", "counting-the-breaths"),
    ],
    "math_linear_system": [
        ("two-lines-one-question", "part_of", "substitution-carefully"),
        ("substitution-carefully", "contrasts_with",
         "elimination-and-the-scaling-trap"),
        ("elimination-and-the-scaling-trap", "causes",
         "checking-is-part-of-the-method"),
        ("checking-is-part-of-the-method", "requires",
         "two-lines-one-question"),
    ],
    "cs_loop_invariant": [
        ("what-an-invariant-claims", "part_of",
         "the-off-by-one-this-unit-is-about"),
        ("the-off-by-one-this-unit-is-about", "causes",
         "tracing-three-passes-by-hand"),
        ("tracing-three-passes-by-hand", "requires",
         "what-an-invariant-claims"),
        ("fixing-it-two-ways", "contrasts_with",
         "the-off-by-one-this-unit-is-about"),
    ],
    "history_conflicting_accounts": [
        ("two-diarists-one-afternoon", "part_of", "where-the-accounts-split"),
        ("where-the-accounts-split", "causes",
         "reading-for-interest-not-for-honesty"),
        ("reading-for-interest-not-for-honesty", "requires",
         "two-diarists-one-afternoon"),
        ("what-a-careful-reader-may-claim", "contrasts_with",
         "where-the-accounts-split"),
    ],
}

# The replacement heading `revise_lesson` writes in, per subject. Both its
# title and its body differ from the original, so its slug and its
# quoted-context hash both change: that is the NOTE-01 anchor-invalidation
# fixture.
_REVISIONS = {
    "emt_respiratory": (
        "Recording what disagreed",
        "The revised fictional section drops the disagreement discussion and "
        "asks instead what the learner wrote down. A number recorded once is "
        "a measurement; two numbers recorded with the reason they differ is "
        "an observation."),
    "math_linear_system": (
        "Writing the check down",
        "The revised fictional section asks for the check to be written out "
        "rather than performed mentally, because a mental check that passes "
        "and a mental check that was skipped look identical afterwards."),
    "cs_loop_invariant": (
        "Choosing a convention and saying so",
        "The revised fictional section drops the two-fixes comparison and "
        "asks only that the chosen convention be stated at the top of the "
        "invented file, where the next reader will look first."),
    "history_conflicting_accounts": (
        "Stating the limits first",
        "The revised fictional section asks the learner to write the limits "
        "of the claim before the claim itself, so the hedge is a structural "
        "part of the sentence rather than an apology appended to it."),
}

_ROLE_CYCLE = ("quote", "learner_claim", "learner_question",
               "learner_example", "calculation")

_WORDINGS = {
    "quote": "The invented text says the %s section is where this is "
             "settled.",
    "learner_claim": "I think %s is the part that actually decides the "
                     "answer here.",
    "learner_question": "Why does %s matter more than the number itself?",
    "learner_example": "My own example for %s: the case where both readings "
                       "look fine and still disagree.",
    "calculation": "Working for %s: two counts, thirty seconds each, "
                   "recorded separately.",
}


def _terms_block(subject):
    """The `## TERMS` rows in the shipped shape: `canonical | definition`,
    one per line, no header row and no separator row.

    A header row would parse as a glossary entry named "Term", because the
    section's boundary rule counts any two-cell row as a term. The shipped
    fixtures carry no header for exactly that reason.
    """
    return "\n".join("%s | %s" % (canonical, definition)
                     for canonical, definition in _TERMS[subject])


def _lesson_block(subject):
    out = []
    for title, body in _HEADINGS[subject]:
        out.append("### %s\n\n%s\n" % (title, body))
    return "\n".join(out)


def _items_block(subject):
    mc, short = _ITEMS[subject]
    stem, options, correct, why = mc
    letters = "ABCD"
    lines = ["Q1. %s   (difficulty: application)" % stem,
             "[OBJECTIVE: %s.obj.1]" % subject, ""]
    for i, opt in enumerate(options):
        lines.append("%s) %s" % (letters[i], opt))
    lines += ["", "CORRECT: %s" % correct, "",
              "WHY BEST: %s" % why, "",
              "KEY DISCRIMINATOR: The finding this fictional unit says to "
              "trust when two readings disagree.", "",
              "DISTRACTOR ANALYSIS:"]
    for i, opt in enumerate(options):
        if letters[i] == correct:
            lines.append("- %s) Correct: %s" % (letters[i], why))
        else:
            lines.append("- %s) %s is plausible here; it would be correct if "
                         "the question asked which finding is normal."
                         % (letters[i], opt))
    lines += ["", "TRAP: Answering from the number alone.", "",
              "CONFIDENCE: high", ""]

    stem2, model_answer = short
    lines += ["Q2. %s   (difficulty: analysis)" % stem2,
              "[TYPE: short]",
              "[OBJECTIVE: %s.obj.2]" % subject, "",
              "MODEL: %s" % model_answer, "",
              "RUBRIC:",
              "- Names the reason the fictional unit gives",
              "- States the second half of the question explicitly",
              "- Stays inside what the invented material supports", "",
              "TRAP: Answering only the first half of the question.", "",
              "CONFIDENCE: high", ""]
    return "\n".join(lines)


def build_subject_bank(subject, dest_dir):
    """Write `<dest_dir>/<subject>_bank.md` and return its path.

    Writes only where the caller says. Nothing in this module ever targets
    the repository tree.
    """
    if subject not in SUBJECTS:
        raise ValueError("unknown subject: %r" % (subject,))
    text = "\n".join([
        _TITLES[subject], "", _PREAMBLE, "",
        "## LESSON", "",
        _lesson_block(subject),
        "## TERMS", "",
        _terms_block(subject), "",
        _items_block(subject),
    ])
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, "%s_bank.md" % subject)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def build_all(dest_dir):
    """Build all four banks and return `{subject: path}`."""
    return dict((s, build_subject_bank(s, dest_dir)) for s in SUBJECTS)


def typed_relations(subject):
    """The subject's declared typed concept edges as
    `(source_slug, relation_type, target_slug)` tuples.

    Explicit fixture data per D-16C-7: the trio reads relations from here and
    from `[[term]]` refs, and no new inline grammar exists to parse.
    """
    if subject not in SUBJECTS:
        raise ValueError("unknown subject: %r" % (subject,))
    return list(_RELATIONS[subject])


def build_note_set(subject, headings):
    """Five synthetic learner notes for `subject`, anchored to `headings`
    (the list `model.parse_lesson` returns).

    Every note names an epistemic role from the seven-role vocabulary, an
    invented wording, an anchor heading slug, and one objective id. Roles
    `quote`, `learner_claim`, and `learner_question` each appear at least
    once. Note ids are drawn from `random.Random(SEED)` so two builds produce
    identical sets.
    """
    if subject not in SUBJECTS:
        raise ValueError("unknown subject: %r" % (subject,))
    if not headings:
        raise ValueError("no headings to anchor to for %r" % (subject,))
    rng = random.Random(SEED)
    notes = []
    for i, role in enumerate(_ROLE_CYCLE):
        heading = headings[i % len(headings)]
        notes.append({
            "fixture_note_id": "%016x" % rng.getrandbits(64),
            "epistemic_role": role,
            "learner_wording": _WORDINGS[role] % heading["text"].lower(),
            "anchor_slug": heading["slug"],
            "objective_id": "%s.obj.%d" % (subject, (i % 2) + 1),
        })
    return notes


def revise_lesson(dest_dir, subject):
    """Rewrite one already-built bank so exactly one lesson heading's title
    and body are replaced with different invented text, and return the
    REPLACED heading's original slug.

    Both the slug and the content change, so a note anchored to that heading
    can no longer resolve. This is the NOTE-01 anchor-invalidation fixture:
    what the note must do about it is `notes.resolve_anchor`'s business, not
    this builder's.
    """
    if subject not in SUBJECTS:
        raise ValueError("unknown subject: %r" % (subject,))
    path = os.path.join(dest_dir, "%s_bank.md" % subject)
    text = open(path, encoding="utf-8").read()
    old_title, old_body = _HEADINGS[subject][-1]
    new_title, new_body = _REVISIONS[subject]
    old_block = "### %s\n\n%s\n" % (old_title, old_body)
    if old_block not in text:
        raise ValueError("bank for %r is not in its built form" % (subject,))
    text = text.replace(old_block, "### %s\n\n%s\n" % (new_title, new_body))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    # The slug is computed the one way the parser computes it.
    import model
    return model.lesson_slug(old_title)


def broken_trio_fixtures(dest_dir):
    """One good content instance and three deliberately broken ones, for
    plan 16C-07's validator proof.

    Each break is the smallest one that makes exactly one mode unable to
    render honestly, so a validator that fires on the wrong fixture is
    caught rather than credited:

    - `cornell`: a heading nothing is anchored to, which is a cue with no
      matching notes.
    - `concept_map`: one edge carrying the relation type `related`, which is
      outside the closed vocabulary.
    - `notebook`: a note anchored to a heading whose title and body were
      then replaced, so the anchor points at a block that moved.

    Returns `{"bank": path, "good": {...}, "cornell": {...},
    "concept_map": {...}, "notebook": {...}}` where each inner dict carries
    the `notes`, `relations`, and `headings` a caller composes into a
    content instance. Building the instance itself is the caller's job,
    because this module imports no projection.
    """
    import model
    import notes as notes_mod

    subject = "emt_respiratory"
    path = build_subject_bank(subject, dest_dir)
    lesson = model.parse_lesson(path)
    headings = lesson["headings"]

    def anchored_note(heading, role, wording):
        digest = notes_mod.hash_quoted_context(heading["body"])
        target = notes_mod.target_record(
            "lesson_step", heading["slug"], digest,
            "heading:%s" % heading["slug"], digest)
        return notes_mod.note_record(
            "course-%s" % subject, ["%s.obj.1" % subject], role, wording,
            [target])

    good_notes = [
        anchored_note(headings[0], "learner_question",
                      "Why is the count taken before speaking?"),
        anchored_note(headings[1], "learner_claim",
                      "Effort decides the plan more than the number does."),
        anchored_note(headings[2], "quote",
                      "The invented text calls the whistle an upper-airway "
                      "sign."),
        anchored_note(headings[3], "learner_example",
                      "My own case: a fast rate with easy effort."),
    ]
    relations = typed_relations(subject)

    good = {"notes": good_notes, "relations": relations,
            "headings": headings}

    # Cornell: drop the note anchored to the last heading, leaving that
    # heading a cue with nothing beneath it.
    cornell = {"notes": good_notes[:-1], "relations": relations,
               "headings": headings}

    # Concept map: one untyped edge.
    concept_map = {"notes": good_notes,
                   "relations": relations + [(headings[0]["slug"], "related",
                                              headings[3]["slug"])],
                   "headings": headings}

    # Notebook: the anchored heading is replaced under the note's feet.
    moved_dir = os.path.join(dest_dir, "moved")
    os.makedirs(moved_dir, exist_ok=True)
    build_subject_bank(subject, moved_dir)
    revise_lesson(moved_dir, subject)
    moved_headings = model.parse_lesson(
        os.path.join(moved_dir, "%s_bank.md" % subject))["headings"]
    notebook = {"notes": good_notes, "relations": relations,
                "headings": moved_headings}

    return {"bank": path, "good": good, "cornell": cornell,
            "concept_map": concept_map, "notebook": notebook}
