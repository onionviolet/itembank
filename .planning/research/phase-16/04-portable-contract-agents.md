# Portable lesson contract and agents

**Research stream:** 04

**Research date and source access date:** 2026-08-13

**Status:** research input, not an accepted product contract

## 1. Scope and research questions

This stream asks how a lesson can remain useful as a readable Markdown or
Obsidian file while itembank adds semantic presentation, accessible interaction,
media, validation, discovery, and agent-assisted upgrades.

The questions are:

1. Which open formats provide a durable base without creating a second document
   model?
2. Which semantics belong in the authored file, and which state or behavior
   should be derived by the app?
3. How should files, sections, sources, media, and derived assets retain stable
   identity and provenance across edits and moves?
4. How can rich interactions degrade to coherent prose, images, tables, or
   worked steps and remain accessible?
5. What descriptions and validation loop let agents author and upgrade lessons
   safely?
6. What evidence would justify a proprietary file type?

The scope is document architecture and authoring operations. It does not select
the Phase 17 visual language, define assessment scoring, or authorize migration
of existing lessons.

## 2. Existing itembank research reviewed

On receipt of the added inventory direction, this stream reviewed the existing
`.planning/research/` corpus and the prior lesson and UI audits most relevant to
portability. The following findings were reused where they remain supported, and
the remaining standards checks were focused on documented gaps:

| Existing artifact | Still-valid finding reused | Date-sensitive or superseded claim |
|---|---|---|
| [`2026-08-09-lesson-display-editor.md`](../2026-08-09-lesson-display-editor.md) | A durable Markdown source, the project renderer as preview, graceful script failure, visible figure captions, alt-text validation, and focus-equivalent hover content remain sound. Its rejection of a rich-text document model also supports keeping one canonical parse model. | Product comparisons and bundle-size estimates were snapshots dated 2026-08-09. This stream does not reuse those current-product or cost claims without new verification. Its proposed syntax and phase assignments are prior recommendations, not accepted Phase 16 decisions. |
| [`2026-08-09-visual-design.md`](../2026-08-09-visual-design.md) | Semantic structure should precede decoration; generated content needs visible labeling; reading measure, source visibility, and calm degradation remain relevant. | The product screenshots, trend claims, font sizes, and vendor-specific visual observations were dated 2026-08-09 and several are explicitly marked assumed. Phase 16 separates capability and flow from visual-system selection, so this stream does not carry forward its named visual direction or token proposals. |
| [`2026-08-09-landscape-widening.md`](../2026-08-09-landscape-widening.md) | Chat should not become the primary learning surface; generated work needs lint, provenance, and review; open-standard adoption must be justified by the product's actual interchange need. | Its statements about 2025 to 2026 product behavior, adoption percentages, competitive novelty, and trend categories are date-sensitive. Its blanket rejection of QTI as a "second parser" overstates the current directive, which allows additive growth to the one parser and permits export mappings. This stream evaluates formats on semantic fit, portability, and total cost instead. |
| [`2026-08-10-constraint-audit.md`](../2026-08-10-constraint-audit.md) | The binding rules are one parser and scorer, additive compatibility, runtime assessment authority, local evidence, and the named accessibility gates. Dependencies and JavaScript are not generally prohibited, but lesson-authored JavaScript is. Supply-chain claims require pinned versions, checksums, and license review. | The audit describes corpus state on 2026-08-10. Its general rule corrections remain reflected in current `PLANNING-DIRECTIVES.md`; individual line references or claims about files being edited then may be stale. |
| [`2026-08-10-lesson-item-coupling.md`](../2026-08-10-lesson-item-coupling.md) | Stable identity must survive moves, copying must not duplicate IDs, shared external lessons require whole-root validation, filename similarity is not identity, and authoring should pass the resolved lesson section rather than merely a path. The audit, propose, diff, validate loop remains valuable. | Its verified parser details describe the code on 2026-08-10 and its default separate-versus-inline lesson ruling predates the course-centered product reframe. Phase 16 should preserve both readable layouts through one model rather than inherit subject defaults without revalidation. |
| [`2026-08-10-style-registry-mechanics.md`](../2026-08-10-style-registry-mechanics.md) | Pagination and margin presentation belong to render modes rather than authored layout grammar. Semantic roles should name pedagogical purpose, and the same content should support continuous, guided, and nonvisual readings. | Its proposed block count, grammar-cost estimates, phase ownership, and statement that any additional classifier branch is a second parser are planning-era conclusions, not current constraints. The present directive explicitly says additive branches inside the one parser are allowed. |
| [`UI-SPEC.md`](../../UI-SPEC.md) | The nine accessibility gates remain binding: no hover-only narrow-screen controls, semantic controls and headings, full keyboard operation, no hidden keyed content, equivalent visual control paths, accessible math fallback, restrained announcements, AA contrast, and readable degraded lessons. | Visual tokens, layout, and pre-Phase-16 component choices are inputs rather than conclusions for this research stream. Phase 17 owns the new visual system. |

This inventory exposed gaps that justified new browsing: a standards-based
provenance model, robust selectors for source and media fragments, formal media
attribution and derivative records, integrity versus authentication, current
Obsidian portability boundaries, current JSON Schema status, accessible disclosure
and hover behavior, and portable agent-skill descriptions. New browsing was focused
on those gaps. No external product visual audit was repeated because it would not
answer this stream's semantic-contract question.

## 3. Sources

All sources below were accessed 2026-08-13. Product behavior is documented from
official documentation. Standards sources are normative specifications or the
standards body's official guidance.

| Source | Source type | Relevance |
|---|---|---|
| [CommonMark Specification 0.31.2](https://spec.commonmark.org/0.31.2/) | Open specification | Portable Markdown baseline, blocks, links, images, fenced code, and HTML extension behavior. |
| [Obsidian Properties](https://obsidian.md/help/properties) | Official product documentation | YAML properties, typed values, lists, URLs, and internal links. |
| [Obsidian Internal links](https://obsidian.md/help/links) | Official product documentation | Markdown links, wikilinks, heading links, aliases, and explicit warning that block references are Obsidian-specific. |
| [Obsidian Callouts](https://obsidian.md/help/callouts) | Official product documentation | Semantic-looking callout syntax built on Markdown blockquotes. |
| [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) | Open specification | Versioned validation vocabulary and machine-readable schema contract. |
| [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/) | W3C Recommendation | Bodies, targets, selectors, lifecycle, agents, rights, and target-state patterns for source bindings. |
| [W3C PROV-O](https://www.w3.org/TR/prov-o/) | W3C Recommendation | General entity, activity, and agent provenance model. |
| [W3C Media Fragments URI 1.0](https://www.w3.org/TR/media-frags/) | W3C Recommendation | Portable spatial and temporal fragments for media locators. |
| [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/) | Open community specification | Attributed compound media, ordered views, structure, annotations, and interoperable rich viewers. |
| [Creative Commons, Reusing CC-Licensed Content](https://creativecommons.org/reusing-cc-licensed-content/) | Official license guidance | Title, author, source, and license attribution practice, including public-domain guidance. |
| [C2PA Technical Specification 2.4](https://spec.c2pa.org/specifications/specifications/2.4/) | Open technical specification | Signed provenance manifests for supported digital media. |
| [RFC 9530, Digest Fields](https://www.rfc-editor.org/rfc/rfc9530.html) | IETF Proposed Standard | Distinction between byte integrity and authentication, useful when defining fingerprints. |
| [WCAG 2.2, Content on Hover or Focus](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) | W3C accessibility guidance | Dismissible, hoverable, and persistent requirements for additional content. |
| [WAI-ARIA APG Disclosure Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) | W3C implementation guidance | Keyboard and state contract for show and hide controls. |
| [Agent Skills, Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/agents/skills) | Official implementation documentation for an open skill convention | Portable `SKILL.md` packages, descriptions, resources, scripts, and progressive disclosure. |

## 4. Observed facts, inference, and recommendation

### 4.1 Observed facts

- CommonMark specifies familiar text structures, including headings, links,
  images, blockquotes, fenced code, and raw HTML. YAML front matter, callout
  roles, wikilinks, and interactive lesson semantics are not part of CommonMark.
- Obsidian properties use YAML front matter and support scalar and list values.
  Obsidian supports both standard Markdown links and wikilinks. Its documentation
  explicitly states that block references are specific to Obsidian and do not
  work outside it.
- Obsidian callouts encode a type token in the first line of a blockquote. A
  renderer that ignores this extension still exposes the blockquoted content.
- JSON Schema 2020-12 supplies a declared dialect, validation vocabularies,
  references, and structured validation results for JSON-shaped data.
- The Web Annotation model represents an annotation as bodies associated with
  targets. It defines selectors for fragments, text quotes, text positions,
  spatial regions, and ranges, plus lifecycle, rights, creator, and generator
  metadata.
- PROV-O defines an interoperable model for entities, activities, and agents.
  It can be specialized, so adopting its concepts does not require serializing
  every lesson as RDF.
- Media Fragments defines URI syntax for temporal and spatial portions of media.
  IIIF Presentation defines manifests for structured and attributed image,
  audio, video, and compound objects and uses Web Annotation concepts.
- Creative Commons recommends title, author, source, and license attribution,
  commonly called TASL, and recommends provenance information even for public
  domain material when reasonable.
- C2PA binds signed provenance assertions to supported media. RFC 9530 states
  that a digest provides integrity but does not itself provide authentication,
  authorization, or privacy.
- WCAG 2.2 requires author-controlled hover or focus content to be dismissible,
  hoverable, and persistent. The ARIA disclosure pattern uses an activatable
  button, `aria-expanded`, and Enter or Space keyboard operation.
- The cited Agent Skills documentation describes a skill as a directory with a
  required Markdown instruction file and optional scripts, references, and
  assets. Its description is used for discovery, and detailed resources can be
  loaded only when relevant.

### 4.2 Inferences

- A CommonMark-compatible document can carry the lesson's essential explanation
  and fallback, but it cannot by itself express every semantic teaching role or
  interaction contract. A small, documented profile is necessary.
- Syntax that remains valid and intelligible Markdown when ignored has a lower
  lock-in cost than opaque directives or required embedded HTML. Blockquote-based
  roles are promising for block semantics. Inline definitions need a similarly
  readable explicit representation, such as a glossary section plus ordinary
  links, rather than tooltip-only text.
- Stable identity and content fingerprints solve different problems. Identity
  should survive a move or ordinary revision. A fingerprint should change when
  relevant content changes. Neither a path nor a hash should serve both roles.
- Source anchoring is more robust when it stores more than one locator where
  feasible, for example source identity plus page or heading and an exact text
  quote. This is a practical subset of the Web Annotation selector model.
- Rich behavior is safer when lessons declare semantic intent and the trusted app
  selects a registered renderer. Letting lesson authors supply executable code
  makes portability, security review, accessibility, and deterministic validation
  materially harder.
- A generated derivative is not automatically a trustworthy source. It needs a
  relationship to its input, the transformation activity or tool, time, review
  state, and integrity value. C2PA may preserve signed media history when present,
  but cannot replace the lesson's own source and rights record.
- Agent authoring becomes reliable when the capability vocabulary, examples,
  linter codes, render checks, permissions, and upgrade protocol are discoverable
  as one product interface rather than scattered prose.

### 4.3 Recommendations

1. Use UTF-8 Markdown as the canonical lesson artifact, with a constrained YAML
   metadata header and a versioned, additive semantic profile.
2. Keep essential meaning in ordinary Markdown. Enrich blocks through
   blockquote-compatible semantic markers and enrich terms through visible links
   to definitions. Treat rich rendering as a projection, never the only copy.
3. Parse the profile into one canonical lesson document model. Generate indexes,
   HTML, search data, thumbnails, simulation state, and accessibility views from
   that model. Do not make sidecars a competing authored truth.
4. Give every lesson and addressable authored component an opaque stable ID.
   Store a separately computed content fingerprint and explicit revision and
   profile versions.
5. Use a compact provenance record inspired by PROV and Web Annotation rather
   than requiring full RDF. Preserve source entity, locator or selector,
   creator, generator, activity, timestamp, rights, review state, and derivation
   relationship.
6. Permit only registered, trusted interaction types with validated data. Reject
   lesson-authored JavaScript. Every interaction must declare a useful static
   fallback and an accessible control and state model.
7. Publish an agent-facing capability catalog and schema, scaffold commands,
   validator, render verifier, discovery rules, and audit-first upgrade skill.
8. Do not create a proprietary file type now. Revisit only against the explicit
   decision criteria in section 8.

## 5. Pattern inventory

| Pattern | Benefits | Weaknesses | Applicability to itembank |
|---|---|---|---|
| CommonMark core plus constrained profile | Human-readable diffs, broad editor support, graceful unknown-syntax behavior, easy agent authoring. | Markdown has ambiguities and no native semantic lesson vocabulary. | **High.** Use as the durable source layer with one parser and strict linting. |
| YAML metadata header | Familiar, searchable identity and document metadata; Obsidian reads it. | YAML scalar typing and quoting can surprise authors; large nested graphs become hard to edit. | **High for shallow metadata.** Keep keys bounded and forbid complex arbitrary nesting. |
| Blockquote-compatible semantic blocks | Plain readers retain the content; Obsidian already recognizes a related callout pattern. | Type tokens are an extension and visual meaning can be lost outside a supporting renderer. | **High.** Standardize teaching roles, require meaningful titles and prose, and never rely on color or icon alone. |
| Visible glossary definitions plus enhanced term triggers | Plain files preserve definitions; UI can add hover, focus, touch, and navigation. | Repeated terms can create clutter; ambiguous surface forms require explicit binding. | **High.** Define once by stable term ID, link deliberately, and let the renderer enhance. |
| Semantic interaction declaration plus static fallback | Separates pedagogy from implementation; trusted renderers can improve over time. | Requires a capability registry, validation, and fallback authoring effort. | **High.** Appropriate for prediction, staged reveal, comparison, diagram, and simulation primitives. |
| Embedded lesson-authored HTML or JavaScript | Maximum local expressiveness and rapid prototypes. | Poor portability, unsafe execution, difficult accessibility review, renderer coupling, and agent-generated attack surface. | **Reject for accepted lessons.** Prototype behavior in trusted product code instead. |
| Opaque proprietary binary or package as source | Could bundle assets and state and enforce a specialized editor. | Weak diffs and recovery, tool lock-in, poor Obsidian use, costly agent inspection, and duplicate truth risk. | **Reject now.** A package may later be an export or transport, not the canonical authored source. |
| Stable opaque IDs plus independent fingerprints | Survives moves and ordinary revisions while detecting change. | Requires ID collision checks, normalization rules, and reconciliation UX. | **High.** Apply to lessons, semantic blocks, objectives, source bindings, and media records where links depend on them. |
| Multi-selector source binding | Page, heading, quote, time, or region locators can corroborate one another and recover from edits. | Selector drift remains possible; some source formats lack stable pagination. | **High.** Store source ID, human locator, machine selector, quote context, and source fingerprint when lawful. |
| PROV-inspired compact provenance | Captures who or what derived an artifact and from which source without forcing RDF authoring. | A custom subset needs mapping documentation and validation. | **High.** Define explicit mappings and allow export to a standard representation later. |
| Attributed media manifest | Separates media identity, rights, accessibility text, renditions, and derivations from presentation. | More metadata and review work; remote sources may disappear. | **High.** Keep a visible caption and credit in Markdown, with richer records in constrained metadata. |
| Disposable derived index | Fast discovery across multiple roots without moving user files. | Staleness and false duplicate matches if treated as authoritative. | **High.** Rebuild from canonical files, record scan scope and time, and require review for uncertain identity. |
| Audit, propose, validate upgrade | Preserves identity and intent; supports reviewable diffs and rollback. | Slower than bulk rewriting and requires baseline captures. | **Required.** Particularly important for assessment artifacts and source-derived lessons. |
| Agent skill with progressive disclosure | Keeps triggering instructions concise while exposing detailed capability and validation references on demand. | Agents may skip references unless triggers and required steps are explicit. | **High.** Pair descriptions with deterministic tools and completion evidence. |

## 6. Cross-cutting effects

### 6.1 Accessibility

- The plain file must carry headings, explanatory prose, captions, alt text or a
  long description, table headers, link purpose, and the full static fallback.
- A definition trigger cannot be hover-only. The rich UI should support pointer
  hover, keyboard focus, touch activation, dismissal, persistence, and navigation
  to the full glossary entry. Inline expansion or a glossary link remains an
  equivalent path.
- A collapsed hint, answer step, or optional detail should use a disclosure
  control with an accessible name and exposed state. Reading order must remain
  sensible when all content is expanded or scripts fail.
- Diagrams and simulations need a textual model or structured data summary that
  communicates the teaching point. A screenshot is not an equivalent fallback.
- Semantic roles must not depend on color, placement, animation, or iconography.
  Motion and time-based activities need product-level controls and alternatives.
- Validation should distinguish presence from adequacy. `alt` existing is a
  syntactic fact; whether it explains the relevant concept is a review judgment.

### 6.2 Portability

- The compatibility floor should be CommonMark-like reading, not identical
  rendering in every Markdown implementation.
- Standard Markdown links should be canonical. Wikilinks may be accepted as an
  import or author convenience only if normalized or validated with a portable
  equivalent. Obsidian block references must not be required for course meaning.
- Relative asset paths are appropriate within an approved course root. External
  URLs need a cached or explicit unavailable fallback only when licensing and
  ownership permit it. Missing remote media must not erase the explanation.
- Derived output should carry the source lesson ID, profile version, source
  fingerprint, generator version, and build time, so staleness is detectable.

### 6.3 Privacy and security

- A lesson is data, not executable authority. Accept only registered semantic
  capabilities, sanitize rendered Markdown and media metadata, and prohibit
  authored scripts, event handlers, and untrusted active embeds.
- Remote images, fonts, video players, and scripts can disclose viewing activity.
  The renderer should default to local or explicitly fetched assets and clearly
  mark network-dependent content.
- Provenance fields can contain personal identities or private source paths.
  Separate local operational locations from portable display credits, minimize
  exported personal data, and never publish an approved-root inventory by
  default.
- A digest detects byte changes, not ownership or truth. Signature status and
  human review state must be represented separately.

### 6.4 Provenance and media

Minimum media metadata should include:

- stable media ID and lesson relationship;
- canonical source URL or local source identity;
- creator or credited institution when known;
- title when supplied;
- rights or license identifier and license URL;
- required attribution text and a flag or note for modifications;
- retrieval date and source fingerprint where available;
- media type, dimensions or duration, and language where relevant;
- caption, concise alternative, and long-description or transcript reference;
- derivation relation, generator or transformation, parameters sufficient to
  understand the change, creation time, and review state;
- optional C2PA verification result and manifest reference, without treating its
  absence as proof of inauthenticity.

The Markdown view should display a useful caption and compact credit next to the
asset. Detailed machine fields may live in constrained front matter when small,
or in a course media registry referenced by stable ID when repetition becomes
unmanageable. That registry composes the lesson contract and must not contain the
only caption or explanation.

### 6.5 Authorability

- Prefer a small vocabulary of pedagogical roles over visual component names.
  For example, `misconception`, `worked-example`, and `prediction` communicate
  purpose; `purple-card` does not.
- Require one canonical example and one misuse example per capability, along with
  plain-file, rich-render, narrow-screen, keyboard, touch, and screen-reader
  expectations.
- Error messages should identify the file, stable block ID, line, rule code,
  consequence, and a repair suggestion. Warnings should distinguish uncertain
  pedagogy or provenance from invalid syntax.
- Keep frequently edited author fields near their content. Avoid asking an agent
  to coordinate large positional arrays or duplicate prose in metadata.

## 7. Implications

### 7.1 Learner flow

The same parsed lesson can support continuous reader and guided modes. A guided
mode may sequence semantic blocks, persist learner progress separately, and
activate trusted interactions. Reader mode presents the complete authored order.
Switching modes must not fork content or hide the fallback. Source links should
open at a stored locator when available and still expose a human-readable
citation when the source cannot be opened.

Learner responses, disclosure state, progress, and assessment evidence do not
belong in the lesson file. They are runtime or per-learner state keyed to stable
lesson and component IDs. This prevents a reusable lesson from becoming a mixed
content and evidence store.

### 7.2 Semantic content contract

A candidate layered contract is:

1. **Portable source:** UTF-8 Markdown containing the complete explanation,
   headings, ordinary links, media fallback, definitions, captions, citations,
   and static form of every activity.
2. **Document metadata:** a shallow YAML header with lesson ID, profile version,
   document revision, title, language, objective links, status, ownership,
   provenance summary, and optional registry references.
3. **Semantic blocks:** a constrained additive grammar for teaching roles and
   registered interactions. Each block has a stable ID, purpose, content, and
   any validated parameters.
4. **Canonical parse model:** the only in-memory document model produced by the
   project parser. All surfaces consume this model.
5. **Derived products:** disposable indexes, rendered HTML, thumbnails, cached
   derivatives, link graphs, and build manifests. Each records the source ID,
   source fingerprint, profile version, and generator version.
6. **Separate learner state:** runtime-owned progress, responses, evidence, and
   disclosure authority, referenced by stable IDs but never embedded into the
   canonical lesson.

Version fields should have distinct meanings:

- `profile_version`: grammar and semantic contract understood by tooling;
- `revision`: author-controlled artifact evolution or accepted revision ID;
- `fingerprint`: tool-computed change detection over normalized relevant bytes;
- `generator_version`: renderer, indexer, or transformation implementation;
- `source_version`: edition or retrieved source state when known.

Compatibility policy should follow semantic versioning principles for the
profile: additive optional roles are minor changes; incompatible syntax or
meaning requires a major version and an explicit migrator. Unknown optional
roles render as their Markdown fallback and emit a warning. Unknown required
behavior fails validation rather than silently discarding meaning.

### 7.3 Agent skills and authoring descriptions

The product should expose two complementary descriptions:

1. A machine-readable profile and capability catalog, including field types,
   constraints, fallback requirements, accessibility obligations, examples,
   version availability, and validator codes.
2. Agent skills that explain when and why to use capabilities, source and write
   boundaries, discovery and identity reconciliation, the authoring loop, media
   clearance, review criteria, and safe upgrade behavior.

The authoring skill should require this loop:

1. Read the course objective, approved sources, profile version, capability
   catalog, and write scope.
2. Discover existing artifacts and identities before creating anything.
3. Select the treatment and semantic roles based on teaching purpose.
4. Scaffold stable IDs through a tool, not invented ad hoc by the model.
5. Draft complete portable content and then add optional enhancement declarations.
6. Record citations, media rights, generated synthesis, derivations, and
   uncertainty.
7. Parse and schema-validate, lint semantics, render plain and rich views, check
   links and media, and run accessibility checks.
8. Present the bounded diff, validation results, known uncertainty, and undo path.

Skill descriptions should contain clear triggers such as "author or revise an
itembank lesson," "bind existing lessons across approved roots," and "upgrade a
legacy lesson for registered UI capabilities." Detailed capability references
should load only for applicable work, but the required validation and authority
boundaries must be in the main skill instructions.

### 7.4 Discovery and linking

Discovery should index explicit read roots without mutating them. Each candidate
record should contain path, stable artifact ID if present, fingerprint, type,
title, objective links, source bindings, ownership, status, and validation state.
Reconciliation should use multiple signals and report confidence:

- exact stable ID with changed path suggests a move;
- same fingerprint with different IDs suggests a duplicate or copy;
- same ID with divergent content suggests a conflict or branch;
- name similarity alone is only a search hint;
- an artifact without an ID is a legacy candidate, not permission to assign one.

Link, import, copy, move, derive, and supersede must be distinct operations.
Links retain the external artifact's identity and ownership. Imports create an
owned snapshot with provenance. Copies require a new identity and a derivation
relation. Moves preserve identity. Supersession preserves both artifacts and an
explicit relationship.

### 7.5 Audit-first legacy upgrades

An upgrade skill should never begin with transformation. It should:

1. Inventory the file, parser result, identity, fingerprint, objective and source
   links, keyed assessment boundaries, ownership, citations, media, and current
   validation state.
2. Capture a plain-reader baseline and rich-render baseline when one exists.
3. Identify a concrete learning problem or accessibility gap. Cosmetic novelty
   alone is insufficient.
4. Propose the smallest semantic enhancement, including its portable fallback,
   provenance changes, expected benefit, risks, and reversibility.
5. Preserve stable identity and source history. Create new IDs only for genuinely
   new addressable components.
6. Show a bounded diff and require the operation's configured approval level.
7. Re-run parse, lint, link, media, plain-file, rich-render, narrow-screen,
   keyboard, touch, and screen-reader verification as applicable.
8. For questions or exams, prove assessment meaning, keyed content, difficulty,
   objective alignment, and scoring behavior did not change unless an explicitly
   reviewed assessment revision intended that change.

## 8. Decision table

| Disposition | Candidate | Rationale or decision criteria |
|---|---|---|
| Accept | UTF-8 Markdown as canonical lesson source | Best current fit for inspectability, Obsidian use, agent authoring, diffs, and graceful degradation. |
| Accept | Constrained YAML metadata and additive semantic profile | Supplies missing identity and semantics without replacing the readable document. Keep it shallow and versioned. |
| Accept | One canonical parse model with disposable derived products | Prevents renderer-specific interpretations and a second source of truth. |
| Accept | Stable opaque IDs separate from fingerprints and paths | Supports moves, revisions, reconciliation, evidence references, and change detection correctly. |
| Accept | Compact PROV and Web Annotation-inspired source and derivation records | Covers lifecycle, selectors, agents, rights, and derivation while remaining authorable. |
| Accept | Registered interactions with complete static fallbacks | Enables progressive enhancement while keeping execution trusted and portable meaning intact. |
| Accept | Media credit, rights, accessibility, integrity, and derivation fields | Necessary for lawful reuse, learner understanding, offline resilience, and auditability. |
| Accept | Agent capability catalog plus write, lint, render, and upgrade skills | Makes the semantic contract operable across compatible agents. |
| Reject | Accepted lessons containing author-provided JavaScript or event handlers | Creates unacceptable security, accessibility, validation, and portability costs. Semantic data should invoke trusted components. |
| Reject | Obsidian block references or wikilinks as the only stable linkage | Official documentation identifies a portability limit for block references; standard links and stable IDs are safer canonical forms. |
| Reject | Hashes used as durable identity | Any edit changes the hash, so it cannot preserve identity across revision. |
| Reject | Derived index, rendered HTML, or media cache as canonical content | These can be stale or regenerated and must not become the only readable lesson. |
| Reject now | Proprietary canonical file type | Current needs are representable as readable Markdown plus a constrained profile. Lock-in and dual-model costs are not justified. |
| Defer | Full RDF or JSON-LD serialization in every lesson | Standards mapping is useful, but full graph syntax would burden authors. Add export only when an interoperability consumer exists. |
| Defer | C2PA signing or verification as a required media gate | Useful when credentials exist, but format support, tooling, and source coverage vary. Preserve optional results first. |
| Defer | IIIF manifest authoring for all local media | Valuable for compound cultural objects and remote institutions, excessive for a single ordinary diagram. Support binding when a source already provides IIIF. |
| Prototype | Blockquote-based semantic roles and glossary-backed term links | Verify plain Markdown, Obsidian, parser determinism, line-addressable lint, and accessible rich rendering. |
| Prototype | Multi-selector source binding and drift recovery | Test page or heading plus exact quote, time fragment, or spatial region across source changes. |
| Prototype | Trusted simulation declaration with structured static fallback | Verify a real teaching benefit, no authored execution, keyboard and touch parity, screen-reader alternative, and offline behavior. |
| Prototype | Legacy upgrade audit and diff | Exercise one lesson and one assessment artifact without changing identity or assessment meaning. |
| Open question | Metadata placement threshold | Determine when repeated media or provenance fields should move from lesson front matter to a referenced course registry. |
| Open question | Component-level ID granularity | Measure whether IDs on all semantic blocks create authoring noise; require them at least where links, state, evidence, or upgrades depend on identity. |
| Open question | Markdown extension syntax | Compare Obsidian-compatible callouts with another block directive syntax using round-trip and plain-reader tests before fixing grammar. |
| Open question | Canonical normalization for fingerprints | Specify line endings, front-matter ordering, volatile fields, and whether fingerprints cover raw bytes or normalized semantic content. |

### Proprietary format decision criteria

A proprietary canonical format is justified only if a prototype demonstrates all
of the following, not merely one:

1. A required learning capability cannot be represented as Markdown semantics,
   validated data, external assets, and trusted derived behavior without losing
   essential meaning.
2. The limitation affects common accepted lessons, not an unusual optional edge
   case.
3. An open package or existing standard such as EPUB, HTML, IIIF, or a directory
   bundle cannot satisfy the need.
4. The benefit is material to learning quality, accessibility, integrity, or
   authoring reliability and exceeds migration, lock-in, tooling, and security
   costs.
5. Agents and humans can still inspect, diff, validate, migrate, and recover the
   content with documented open tooling.
6. A lossless export preserves essential text, structure, citations, media
   credits, and static interaction fallbacks.
7. One authoritative parser and document model remains possible. The new form
   does not coexist as a second truth with Markdown.
8. Version negotiation, forward-compatible unknown content, migration, and
   rollback are specified and tested before adoption.

No evidence reviewed in this stream meets these criteria.

## 9. Concrete recommendations and risks

### 9.1 Concrete recommendations for Phase 16 synthesis

1. Specify a `lesson_profile` version and a deliberately small metadata table.
   Reserve extension keys and state how unknown optional and required semantics
   behave.
2. Define stable IDs, fingerprints, revision fields, and normalization rules as
   separate contracts. Add collision, move, duplicate, conflict, and stale-build
   tests.
3. Select semantic roles by teaching purpose. Require for each role: portable
   syntax, plain rendering, rich rendering, accessibility behavior, misuse
   warning, author example, and linter rule.
4. Make the first interaction registry data-only. Include no arbitrary executable
   payload. Each entry names a trusted component version and contains a complete
   static fallback.
5. Define a compact source binding with source ID, edition or source version,
   human locator, optional machine selectors, exact quote where lawful, source
   fingerprint, attribution, and review state.
6. Define a media record with TASL-compatible credit, rights, modification,
   accessibility, origin, derivation, integrity, availability, and review fields.
   Show compact credit beside media in the plain file.
7. Publish a JSON Schema or equivalent generated schema for metadata and
   interaction data, but validate the whole Markdown document through the single
   project parser so schema validation does not become a second parser.
8. Require four authoring proofs for the representative unit: coherent raw
   Markdown, Obsidian reading, rich UI interaction, and degraded offline or
   script-disabled rendering. Add keyboard, touch, and screen-reader checks.
9. Write separate agent playbooks for discovery and binding, lesson authoring,
   media intake, and audit-first legacy upgrade. Make all of them call the same
   deterministic validation tools.
10. Keep a proprietary format off the roadmap unless a documented prototype
    passes every decision criterion above.

### 9.2 Risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| Semantic profile expands into a programming language | Complex parser, unsafe behavior, weak portability. | Keep declarations data-only, register trusted components, and require static fallbacks. |
| Different renderers interpret extensions differently | Lesson meaning or order drifts. | One canonical parse model, conformance fixtures, and snapshot comparison of semantic output. |
| YAML becomes an unreviewable database | Author errors and duplicated truth. | Keep metadata shallow, content-adjacent semantics in Markdown, and course-scale repetition in referenced registries. |
| Stable IDs are regenerated during editing | Broken links, state, evidence, and provenance. | Mint IDs only through tooling, lint duplicates and replacements, and preserve IDs through moves and revisions. |
| Fingerprints imply authenticity | False confidence in ownership or truth. | Label fingerprints as integrity and change detection; record signatures, provenance, and review separately. |
| Remote media disappears or tracks learners | Broken instruction and privacy leakage. | Preserve a text fallback, declare network dependence, and cache only with rights and user-approved policy. |
| Generated images obscure their derivation | Misleading provenance or license ambiguity. | Record generator, inputs or source relations, date, modification status, review, and optional credentials. |
| Tooltip enhancements exclude touch or keyboard users | Definitions become inaccessible. | Make visible glossary links canonical and implement hover, focus, touch, dismissal, persistence, and inline navigation. |
| Agent bulk upgrade changes learning or assessment meaning | Silent quality regression. | Audit first, require a purpose and bounded diff, preserve identity, validate both views, and separately guard keyed assessment semantics. |
| Obsidian compatibility becomes vendor dependence | Non-Obsidian readers lose structure. | Treat Obsidian as a compatibility target, keep CommonMark fallbacks, and avoid proprietary references as canonical links. |
| A sidecar registry becomes the only understandable record | Lesson is no longer portable. | Keep essential prose, captions, citations, and fallback in Markdown; sidecars may deduplicate detail but not meaning. |

## Conclusion

The evidence favors an open itembank lesson profile, not a proprietary lesson
file. The durable artifact should be readable Markdown with a small versioned
semantic layer, stable identity, explicit provenance, and complete fallbacks.
The app may derive much richer behavior, but only from validated data and through
trusted accessible components. Agents should operate this contract through
discoverable skills and deterministic tools, with audit-first upgrades and
reviewable diffs. A proprietary canonical type should remain rejected unless a
future prototype proves that an essential, common learning requirement cannot be
met by this layered design and passes the full portability and migration gate.
