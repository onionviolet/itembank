/* Synthetic draft serializer only. Parsing, disclosure and scoring belong to the runtime. */
(() => {
  'use strict';
  const instruction = 'Describe how Gauge B compares with Gauge A and explain why the intervals matter for this comparison.';
  const purpose = 'Explain the difference between Monday rainfall readings over equal collection intervals.';
  function plain(value, name) {
    if (typeof value !== 'string' || !value.trim()) throw new Error(`${name} must contain text.`);
    if (/[\u0000-\u001f\u007f-\u009f\u2028-\u202e\u2066-\u2069\[\]`#<>|]/u.test(value) ||
        /(?:^|\s)Q\d+\.|\b(?:TYPE|SCORING|CORRECT|WHY BEST|KEY DISCRIMINATOR|SECOND-BEST|DISTRACTOR ANALYSIS|TRAP|CONFIDENCE|MODEL|RUBRIC)\s*:|\(difficulty\s*:/iu.test(value) ||
        /[\ud800-\udbff](?![\udc00-\udfff])|(?<![\ud800-\udbff])[\udc00-\udfff]/u.test(value)) {
      throw new Error(`${name} must be a single plain-text line without bank fields, Markdown structure, code, or control characters.`);
    }
  }
  function create(draft) {
    if (!draft || draft.source !== 'table' || draft.format !== 'comparison') throw new Error('Choose the Monday comparison treatment to export.');
    if (!Array.isArray(draft.selectedIds) || draft.selectedIds.length !== 2 || new Set(draft.selectedIds).size !== 2 || !draft.selectedIds.includes('0-1') || !draft.selectedIds.includes('0-2')) throw new Error('Comparison export requires both Monday readings.');
    plain(draft.instruction, 'Instruction');
    plain(draft.purpose, 'Purpose');
    const text = [
      '# Synthetic rainfall comparison draft', '',
      'Status: original synthetic draft. Model answer and rubric are proposed synthesis pending human review. Product acceptance is deferred.',
      'Role: exploratory learning practice, not a grade-bearing assessment or an EMT examination item.',
      'No accepted item ID, points, penalties, pass threshold, or official grading policy is assigned.', '',
      '## Author context', '',
      `Author instruction (JSON): ${JSON.stringify(draft.instruction)}`,
      `Author purpose (JSON): ${JSON.stringify(draft.purpose)}`,
      'Tested demand: explain the Monday comparison and equal collection intervals. An author note does not change the response type or review policy.',
      'Source selection: Table 1, Monday row, Gauge A and Gauge B, with Collection interval. Both readings remain visible.',
      'Trial responses are temporary and never used as a model answer or rubric.', '',
      '## SOURCES', '',
      'synthetic-table-1 | figures.md#source-table-1, Table 1, Monday row, Gauge A, Gauge B, and Collection interval. Original synthetic specimen.', '',
      '## Static source excerpt', '',
      '| Day | Gauge A | Gauge B | Collection interval |',
      '| --- | ---: | ---: | --- |',
      '| Monday | 12 mm | 18 mm | 24 hours |', '',
      'This embedded excerpt preserves the selected source context outside the studio. The locator identifies the original synthetic specimen, not an external source binding or rights grant.', '',
      '## Review policy', '',
      'Equivalent mathematical or verbal explanations are acceptable proposals. Ambiguous gauge direction, missing units, or unsupported intervals require human review. All prose remains pending until approved marking.', '',
      `Q1. ${draft.instruction} Table 1 records Monday rainfall: Gauge A = 12 mm, Gauge B = 18 mm, and both collection intervals = 24 hours. Source: figures.md#source-table-1, Table 1, Monday row.   (difficulty: application)`,
      '[OBJECTIVE: synthetic:rainfall.equal-interval-comparison]', '[TYPE: short]', '[SRC: synthetic-table-1 Table 1 Monday row]', '',
      "MODEL: Gauge B collected 6 mm more than Gauge A, since 18 mm minus 12 mm is 6 mm. Both readings cover 24 hours, so the depth comparison uses the same duration.\n\nRUBRIC:\n- Identifies Gauge B as the larger reading and states the difference as 6 mm, or gives an equivalent calculation with units and clear direction.\n- Explains that both readings cover the same 24-hour interval, so a longer collection time is not the reason for the difference.\n\nTRAP: Reporting the size of the difference without saying which gauge is larger, or assuming unequal collection times despite the source row.\n\nCONFIDENCE: low\n"
    ].join('\n');
    return {text, filename:'rainfall-comparison-draft.md'};
  }
  globalThis.ItembankTableExport = Object.freeze({create, instruction, purpose});
})();
