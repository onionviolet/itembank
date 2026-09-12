/* Draft authoring only. The existing runtime owns parsing and scoring. */
(() => {
  "use strict";

  const sourceTitle = "Figure 2. Water moving through a local landscape";
  const sourceLocator = "figures.md#source-figure-2";
  const locations = [
    {
      id: "evaporation", label: "Evaporation", location: "Location 1",
      context: "upward arrow leaving the lake",
      distinction: "water leaving the lake and rising",
      confusion: "falling water",
    },
    {
      id: "condensation", label: "Condensation", location: "Location 2",
      context: "cloud formation area",
      distinction: "cloud formation",
      confusion: "water falling away from the cloud",
    },
    {
      id: "precipitation", label: "Precipitation", location: "Location 3",
      context: "downward arrow from cloud to land",
      distinction: "water falling from cloud to land",
      confusion: "water crossing land",
    },
    {
      id: "runoff", label: "Runoff", location: "Location 4",
      context: "arrow crossing land toward the stream and lake",
      distinction: "water crossing land toward the stream and lake",
      confusion: "water rising from the lake",
    },
  ];
  const suppliedLabels = [...locations].sort((a, b) =>
    a.label < b.label ? -1 : a.label > b.label ? 1 : 0);

  // JSON preserves exact author strings without introducing Markdown fields.
  function metadata(value) {
    if (Array.isArray(value)) return "[" + value.map(metadata).join(",") + "]";
    return JSON.stringify(value).replace(/[<>&`\[\]#|\u0085\u2028\u2029\u202a-\u202e\u2066-\u2069]/g,
      character => "\\u" + character.charCodeAt(0).toString(16).padStart(4, "0"));
  }

  function requireText(value, name) {
    if (typeof value !== "string" || !value.trim()) {
      throw new Error(`${name} must contain text.`);
    }
  }

  function create(draft) {
    if (!draft || typeof draft !== "object" || Array.isArray(draft)) {
      throw new Error("Choose a figure placement draft to export.");
    }
    const { source, format, selectedIds, instruction, purpose, wordBank } = draft;
    if (source !== "figure" || format !== "placement") {
      throw new Error("Export supports figure label placement only.");
    }
    if (wordBank !== true) {
      throw new Error("Keep the supplied word bank visible for placement export.");
    }
    if (!Array.isArray(selectedIds) || selectedIds.length === 0) {
      throw new Error("Select at least one figure location to export.");
    }
    const selected = new Set(selectedIds);
    if (selected.size !== selectedIds.length || Array.from(selectedIds).some(id =>
      !locations.some(location => location.id === id))) {
      throw new Error("Selected locations must be unique known figure labels.");
    }
    requireText(instruction, "Instruction");
    requireText(purpose, "Purpose");
    // This is an input restriction, not an alternate bank parser. Preserve the
    // caller's wording or refuse it instead of rewriting structural characters.
    if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069\[\]`#<>|]/u.test(instruction) ||
        /(?:^|\s)Q\d+\.|\b(?:TYPE|SCORING|CORRECT|WHY BEST|KEY DISCRIMINATOR|SECOND-BEST|DISTRACTOR ANALYSIS|TRAP|CONFIDENCE|MODEL|RUBRIC)\s*:|\(difficulty\s*:/iu.test(instruction)) {
      throw new Error("Use a plain-text instruction without question markers, Markdown fields, headings, code, or control characters.");
    }
    // Lone surrogates cannot survive a UTF-8 download unchanged.
    if (/[\ud800-\udbff](?![\udc00-\udfff])|(?<![\ud800-\udbff])[\udc00-\udfff]/u.test(instruction)) {
      throw new Error("Instruction contains an invalid Unicode character.");
    }

    const targets = locations.filter(location => selected.has(location.id));
    const unusedCount = locations.length - targets.length;
    const categories = targets.map(target => target.location);
    if (unusedCount) categories.push("Not used");
    const targetText = targets.map(target => `${target.location}: ${target.context}.`).join(" ");
    const placementRule = "Each selected location takes exactly one label. Use every supplied label once." +
      (unusedCount ? " Put all remaining labels in Not used." : "");
    // Exact user punctuation remains in metadata. Escaping an em dash here
    // keeps authored question prose within the repository's prose convention.
    const joinedInstruction = instruction.replace(/\s+/gu, " ").trim();
    const instructionNormalized = joinedInstruction !== instruction;
    const publicInstruction = joinedInstruction.replace(/\u2014/g, "&#8212;");
    const rationale = targets.map(target =>
      `${target.label} matches ${target.location}, the ${target.context}.`).join(" ") +
      (unusedCount ? " Labels whose source locations were not selected belong in Not used." : "");
    const distractors = suppliedLabels.map(label => selected.has(label.id)
      ? `- ${label.label} would be correct at another location only if it showed ${label.distinction}. Here ${label.location} shows that context, not ${label.confusion}.`
      : `- ${label.label} would be correct at ${label.location} if that source location were selected. It describes ${label.distinction}, not ${label.confusion}. That target is absent here, so this label belongs in Not used.`);

    const text = [
      "# Synthetic water-process label placement draft",
      "",
      "Status: original synthetic draft. Key review is pending and deferred. Product acceptance is deferred.",
      "Role: exploratory learning practice. This is not a grade-bearing assessment or an EMT examination item.",
      "The supplied source-derived key and rationales are authored synthesis pending review. No accepted item ID has been assigned.",
      "",
      "## Author context",
      "",
      "Instruction and purpose below are exact JSON-encoded author text. Decode JSON escapes to recover the original wording.",
      `Author instruction (JSON): ${metadata(instruction)}`,
      `Author purpose (JSON): ${metadata(purpose)}`,
      ...(instructionNormalized ? ["Public instruction: whitespace was joined into one line. The exact original wording remains in the JSON metadata above."] : []),
      `Selected source labels (JSON): ${metadata(selectedIds)}`,
      "Supplied word bank: visible. All four source labels are retained in alphabetical order.",
      "Tested demand: match supplied labels to the selected source contexts. Author purpose does not change this response format or its scoring rule.",
      "Source reproduction and presentation are user choices. This downloaded draft includes the original synthetic source for author review.",
      "The author context contains the labeled source and key material. Use the runtime's public item for a learner sitting.",
      "",
      "## SOURCES",
      "",
      `synthetic-figure-2 | ${sourceLocator}, ${sourceTitle}. Original synthetic specimen created for this prototype.`,
      "",
      "## Original synthetic source specimen",
      "",
      sourceTitle,
      "",
      "Source identity: original synthetic specimen created for this prototype. There is no book source, external URL, source binding, or rights grant to infer.",
      "",
      "```text",
      "             [Condensation]",
      "                   cloud",
      "                     |",
      "                     | [Precipitation]",
      "     [Evaporation]   v",
      " lake  ^              hill ---- [Runoff] ----> stream ----> lake",
      "       |",
      "```",
      "",
      "The figure names four movements of water in the illustrated watershed:",
      "evaporation rises from the lake, condensation names cloud formation,",
      "precipitation falls from the cloud, and runoff moves across land toward the",
      "stream and lake.",
      "",
      "## Static practice representation",
      "",
      `Supplied labels: ${suppliedLabels.map(label => label.label).join(", ")}.`,
      targetText,
      placementRule,
      "",
      `Q1. ${publicInstruction} Match each supplied water-process label to a selected location in synthetic Figure 2. ${targetText} ${placementRule} Source: ${sourceLocator}, Figure 2.   (difficulty: application)`,
      "[OBJECTIVE: synthetic:water-cycle.label-location]",
      "[TYPE: dnd]",
      "[SRC: synthetic-figure-2 Figure 2]",
      `[CATEGORIES: ${categories.join(" | ")}]`,
      "",
      ...suppliedLabels.map(label => `ITEM) ${label.label} :: ${selected.has(label.id) ? label.location : "Not used"}`),
      "",
      `WHY BEST: ${rationale}`,
      "",
      "KEY DISCRIMINATOR: Distinguish rising water, cloud formation, falling water, and water crossing land. Match only the selected locations.",
      "",
      "SECOND-BEST: Assigning a different process to a selected location would work only if that location showed the other process. The named movement or change in the source decides the match.",
      "",
      "DISTRACTOR ANALYSIS:",
      ...distractors,
      "",
      "TRAP: Assigning labels by closeness to the cloud or option order instead of the specific movement or change at a selected location.",
      "",
      "CONFIDENCE: low",
      "",
    ].join("\n");
    return { text, filename: "water-cycle-placement-draft.md", selectedCount: targets.length, unusedCount, instructionNormalized };
  }

  globalThis.ItembankPlacementExport = Object.freeze({ create });
})();
