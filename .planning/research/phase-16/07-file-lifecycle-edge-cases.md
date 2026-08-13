# Stream 07: file lifecycle, interoperability, and edge cases

**Research date and source access date:** 2026-08-13

**Status:** research input, not an accepted product contract

**Scope boundary:** discovery, linking, identity, paths, permissions, external
edits, executable documents, conflicts, moves, deletion, storage edge cases,
migrations, recovery, diagnostics, and user explanations. Curriculum hierarchy,
progress, onboarding, app information architecture, and visual design are out of
scope except where they directly constrain a file operation.

## 1. Scope and research questions

1. How should itembank find previous work across user-approved roots without
   moving, copying, rewriting, or claiming ownership of it?
2. What identity survives renames, moves, external edits, removable media,
   cloud placeholders, and restore operations?
3. How should link, edit in place, import, copy, convert, move, supersede,
   detach, and delete remain distinct and understandable?
4. How should external edits, concurrent writes, conflicts, and broken links be
   detected and reconciled without content loss?
5. When should mixed prose, code, output, data, and interactive documents be
   linked, rendered, imported, converted, executed, or left external?
6. What path, permission, migration, backup, recovery, and diagnostic contracts
   must hold in the packaged app and CLI?

### Evidence labels

- **Fact:** directly observed in the repository or a cited source.
- **Inference:** conclusion drawn from facts.
- **Recommendation:** proposed direction for later synthesis.
- **Open question:** requires user choice, policy, or prototype evidence.

No protected content or assets are copied. External sources were accessed
2026-08-13.

## 2. Sources

### 2.1 Existing itembank research and shipped behavior reviewed

| Source | Type | Relevant finding |
|---|---|---|
| `AGENTS.md` | Binding instruction | Discovery is read-only by default; approved roots; find before create; distinguish link, import, copy, move, and supersede; preserve identity and provenance |
| `.planning/SOURCE-TO-COURSE.md` | Binding product contract | Search several approved roots, fingerprint artifacts, retain locators, link adequate existing work, keep mutations reviewable and recoverable |
| `.planning/PLANNING-DIRECTIVES.md` and `.planning/ROADMAP.md` | Planning direction | Course workspace direction, shipped phase status, desktop and authoring boundaries |
| `.planning/research/phase-16/README.md` | Research index | Research structure and synthesis-only contract update rule |
| `.planning/research/2026-08-09-packaging.md` | Prior research | `.pyz` and Tauri packaging analysis; useful path and updater concerns, but some pre-Phase-13 assumptions are stale |
| Phase 2.1 plans, verification, tests, `update.py`, `resources.py` | Shipped behavior | Side-by-side verified `.pyz` updates, disclosure before network use, checkout/archive resource resolution |
| Phase 3 plans, verification, `model.py`, lesson tests | Shipped behavior | `[LESSON-SRC:]`, bank-relative containment, shared Markdown lesson, broken-source degraded state |
| Phase 11 plans, verification, audit modules and tests | Shipped behavior | Source normalization, locators, stale fingerprints, read-only audit, atomic writes, preflight, Git or shadow manifests, stale-safe undo |
| Phase 13 plans, verification, `src-tauri/`, packaging tests | Shipped behavior | Tauri shell and Python sidecar packaging path, packaged resource and process constraints |
| Phase 999.5 summaries, `README.md`, CLI help checks | Shipped behavior | User-facing command documentation and a README-to-command drift gate |
| `evidence.py`, schemas, migration tests | Shipped behavior | Immutable events, rebuildable projections, explicit migration reconciliation |

### 2.2 Current external sources

| Source | Type | Facts used |
|---|---|---|
| [Jupyter Notebook format](https://nbformat.readthedocs.io/en/stable/format_description.html) | Primary specification | Ordered cells, unique cell ids, code, kernel metadata, execution counts, rich MIME outputs, attachments, and metadata are distinct notebook content |
| [Jupyter Book execution](https://jupyterbook.org/stable/execution/) | Primary documentation | Build execution, cached/static outputs, widgets, browser execution, and external launch are separate modes |
| [MyST Markdown notebooks](https://jupyterbook.org/v1/file-types/myst-notebooks.html) | Primary documentation | Text-based notebooks can preserve executable structure and improve version-control ergonomics |
| [Quarto execution options](https://quarto.org/docs/computations/execution-options.html) and [project freeze](https://quarto.org/docs/projects/code-execution.html#freeze) | Primary documentation | Execution, cache, output, kernel, and frozen-result policies are explicit and affect meaning |
| [nbdime](https://nbdime.readthedocs.io/en/latest/) | Primary documentation | Notebook-aware diff and merge operate structurally rather than as raw JSON line changes |
| [Tauri capabilities](https://v2.tauri.app/security/capabilities/) | Primary documentation | Permissions and scopes are granted per window or webview; overlapping capabilities merge authority |
| [Tauri filesystem plugin](https://v2.tauri.app/plugin/file-system/) | Primary documentation | Filesystem operations have separate permissions; installed resources are not generally writable on macOS or Linux and can require elevation on Windows |
| [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/) | Primary standard | Config, durable data, state, cache, and runtime files have different locations and lifetimes |
| [Python pathlib](https://docs.python.org/3/library/pathlib.html) | Primary documentation | Resolution, metadata, directory creation, rename, replace, and move are platform filesystem primitives |
| [Windows `FILE_ID_INFO`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info) | Primary platform documentation | Volume serial plus file id can identify an open file on one computer |
| [OneDrive Files On-Demand](https://support.microsoft.com/en-us/office/save-disk-space-with-onedrive-files-on-demand-for-windows-0e6860d3-d9f3-4971-b321-7092438fb38e) | Primary product documentation | Online-only paths may be visible without local bytes; opening downloads them; deleting propagates across devices; moving outside OneDrive downloads and removes the cloud item |
| [Windows automatic file downloads](https://support.microsoft.com/en-us/windows/automatic-file-download-notifications-in-windows) | Primary platform documentation | Apps can trigger visible hydration of online-only files and users can block an app |
| [Apple Time Machine backup](https://support.apple.com/guide/mac-help/back-up-files-mh35860/mac) | Primary platform documentation | User files and older versions can be restored; local snapshots are bounded; external backup remains recommended |
| [Git documentation on ignore and attributes](https://git-scm.com/docs/gitattributes) | Primary project documentation | File attributes can select text, binary, diff, and merge behavior, but Git does not understand every external format automatically |

## 3. Existing research and behavior: valid findings and stale assumptions

### 3.1 Valid foundations to reuse

**Fact.** itembank already has several narrow, well-tested file-lifecycle
primitives:

- lesson source resolution refuses missing and out-of-tree relative paths and
  gives a useful degraded reader state;
- source audit records byte locators and content fingerprints and refuses to
  claim stale material as covered;
- Phase 11 writing uses preflight hashes, atomic replacement, operation
  manifests, Git or shadow recovery, and refuses stale undo;
- evidence projections can be rebuilt from durable event files;
- packaging resolves resources in both checkout and `.pyz` contexts;
- updates land side by side rather than overwriting a running artifact;
- CLI and app routes reuse runtime behavior rather than creating new authority.

**Inference.** These are suitable implementation seeds. They are not yet a
general artifact registry, multi-root identity system, move transaction, cloud
placeholder policy, or external-edit conflict model.

### 3.2 Stale or incomplete assumptions

| Assumption | Assessment | Reason |
|---|---|---|
| A bank-relative path is sufficient identity | **Incomplete** | It cannot survive renames, cross-root moves, removable-drive mount changes, or reuse from another course |
| Exact hash means “same artifact” | **Incomplete** | It proves identical bytes, not ownership or intended identity; edited versions necessarily have different hashes |
| Similar filename means moved file | **Reject** | Names are weak evidence and can collide routinely |
| Scan result authorizes edits | **Reject** | Root discovery permission and file mutation authority are distinct |
| A normal-looking path has readable local bytes | **Stale** | Cloud placeholders can appear in the directory while remaining online-only |
| A filesystem move is always one atomic rename | **Stale** | Cross-volume moves may become copy then delete; cloud moves may hydrate or propagate remotely |
| An app undo is a backup | **Reject** | Undo covers a known transaction; backup covers broader loss and independent failure domains |
| Flattening `.ipynb` to Markdown preserves it | **Reject** | Cell ids, outputs, attachments, metadata, environment, and active MIME behavior can be lost |
| The `.pyz` directory is the final place for user data | **Reject** | Installed resources are not reliable writable storage and Phase 13 adds a separate desktop shell |

## 4. Lifecycle and operation model

### 4.1 Default: no move, no copy, no rewrite

**Recommendation.** Discovery registers metadata only. The normal reuse path is
to link the file where it already lives. A course can use files from several
approved roots. Folder layout is not curriculum identity and need not be
normalized.

The default no-move rule protects:

- external editors and user habits;
- Obsidian or other vault links;
- Git repositories and collaboration;
- application-specific project structure;
- cloud-provider sharing and sync configuration;
- file ownership and licensing boundaries;
- existing backup inclusion;
- paths referenced by tools itembank cannot inspect.

A move is appropriate only when the user explicitly chooses organization or a
required destination, understands broken-link risk, and receives a preview and
rollback plan.

### 4.2 User-language operation vocabulary

| Operation | Promise to the user | Bytes changed | Identity rule | Default authority |
|---|---|---|---|---|
| Find | “Look in this folder and list relevant material.” | None | Candidate metadata only | Read root |
| Link in place | “Use this file where it is. itembank will not copy it.” | None | Keep external ownership and locator | Read root |
| Edit in place | “Change this original file at its current location.” | Original changes atomically | Same intended artifact, new revision and hash | Exact approval or bounded write root |
| Import copy | “Make a course-owned copy. Future edits do not update the original.” | New file | New artifact id, `derived_from` original | Explicit destination |
| Convert | “Create another format and report what may be lost.” | New derivative | New id and converter provenance | Explicit destination |
| Move | “Relocate the original and update links itembank knows how to update.” | Location changes, possibly copy/delete | Same intended artifact only after verification | Transaction approval |
| Supersede | “Prefer this newer artifact while retaining the old one.” | None required | Typed relation, both remain addressable | Explicit choice |
| Detach | “Stop using this file; do not delete it.” | None | Disable relation | Safe default removal |
| Delete generated copy | “Remove the course-owned derivative.” | Derivative removed | Tombstone and manifest retained | Exact target confirmation |
| Delete original | “Remove your original file, possibly across synced devices.” | Original removed | Exceptional destructive action | Separate high-friction confirmation |

Avoid “add,” “sync,” and “organize” as mutation verbs unless the confirmation
explains the exact underlying operation.

### 4.3 Proposed artifact registry

The registry is metadata, not a hidden content library:

```text
artifact_id          opaque stable itembank id
kind                 source, syllabus, lesson, notebook, bank, data, media, package
root_id              approved root grant
relative_path        portable locator within that root
canonical_path_cache local optimization, never portable identity
content_fingerprint  hash of bytes actually read
native_identity      format id, cell ids, file id, or repository id when available
owner                learner, institution, publisher, generated, unknown
provenance           source and operation manifest links
format_version       parser or native format version
availability         present, online_only, offline, permission_lost, missing, ambiguous
write_policy         read_only, propose, bounded_write
last_observed        metadata snapshot and timestamp
last_verified        bytes and verifier version
```

**Recommendation.** Registry export must be inspectable and portable. A
disposable search index may be rebuilt from it and the roots. User content must
not be stored in the index.

## 5. Identity and paths

### 5.1 Layered identity, not one magic key

| Signal | Strength | Limitation |
|---|---|---|
| Embedded itembank artifact id | Strong | External formats may not permit metadata; copies duplicate the id unless import handles it |
| Format-native stable id, such as notebook cell ids plus document provenance | Strong within format | May be absent or rewritten by exporters |
| Exact content fingerprint | Strong evidence of identical bytes | Identical copies are not necessarily the same intended artifact |
| OS file id plus volume id | Strong on one mounted filesystem | Not portable across copy, restore, cloud rehydration, or some filesystems |
| Git repository plus tracked path and blob/history | Useful provenance | Not all roots use Git; renames are inferred, not stored as immutable identity |
| Root-relative prior path and metadata | Moderate | Fails on moves and metadata normalization |
| Filename, size, or semantic similarity | Weak | Requires review; never sufficient for mutation |

**Recommendation.** Keep stable application identity separate from every
locator. Use several signals to propose a moved candidate. Auto-relink only
when policy defines a strong match, normally embedded/native id or exact hash
plus unambiguous lineage. Never infer identity from a filename alone.

### 5.2 Path contract

- Store `root_id + relative_path` as the normal portable locator.
- Resolve and validate the real path at operation time, including symlink and
  junction containment.
- Preserve the user's spelling only for display where useful; compare using
  platform-aware normalization without rewriting names silently.
- Treat case-only renames as a special transaction on case-insensitive roots.
- Treat Unicode normalization differences as possible collisions.
- Reject traversal and reserved-device paths before any write.
- Do not follow new symlinks discovered during a write unless the approved root
  policy explicitly allows the resolved target.
- Record path length, illegal-name, and filename-loss issues before cross-OS
  export or move.
- Never commit machine-specific absolute paths into portable course files.

### 5.3 Approved root grants

Each root needs:

- human label and canonical locator;
- read, propose, or bounded-write authority;
- included and excluded file kinds or paths;
- size and recursion limits;
- whether network hydration is allowed during scans;
- whether execution may read it;
- availability and last successful authorization;
- device or provider hints for diagnostics, not identity.

Discovery across a read root does not authorize editing any found file. Write
approval can be per operation, exact artifact, or an explicit bounded write
root. External model or executor access is another capability.

## 6. Discovery and linking in place

### 6.1 Read-only inventory pipeline

1. Resolve approved roots and report unavailable ones.
2. Enumerate metadata without opening unsupported or online-only content where
   the platform permits.
3. Apply ignore, size, recursion, and file-count limits.
4. Classify likely formats by content and extension without executing them.
5. Hash locally available candidate bytes incrementally.
6. Extract only safe metadata and stable locators.
7. Group exact duplicates, moved candidates, edited relatives, unsupported
   files, and conflicts.
8. Present findings. Do not import, convert, rename, or create folders.
9. Save disposable index state and durable registry decisions separately.

**Recommendation.** A scan must be pausable and resumable. Repeated scans should
use metadata to avoid rereading unchanged large files, while periodic or
explicit verification catches unreliable metadata. Hashing must not silently
hydrate a cloud tree or spin up a sleeping removable disk without explanation.

### 6.2 Link behavior

A link records artifact identity, root-relative locator, last verified
fingerprint, provenance, and relation to the consuming artifact. Opening it:

- verifies availability and permission;
- detects changed bytes before relying on derived claims;
- renders through the correct safe reader;
- marks cached metadata stale rather than pretending old content is current;
- offers locate, inspect candidate, relink, detach, or leave unresolved when
  broken.

Linking never means itembank will keep a private up-to-date copy. Any cached
render is labeled with its source fingerprint and invalidated on change.

## 7. External edits, concurrency, and conflicts

### 7.1 External edit states

| Observed state | Interpretation | Safe response |
|---|---|---|
| Same locator, new hash | Externally edited revision | Reparse, mark derived mappings stale, show diff if supported |
| Old locator missing, one exact-hash candidate | Likely move or copy | Propose relink; distinguish whether old location still exists |
| Old missing, several exact copies | Ambiguous identity | Ask which is authoritative or keep all as duplicates |
| Same embedded id at two edited files | Divergent copies or merge conflict | Do not auto-merge; compare provenance and ask |
| File changes during scan | Unstable read | Discard result and retry later with bounded attempts |
| File changes after preview but before write | Stale preflight | Refuse write and regenerate proposal from new bytes |
| External deletion | Missing, not proof of intent | Keep tombstone; do not delete derived artifacts automatically |

### 7.2 Optimistic concurrency contract

Reuse Phase 11's exact preflight:

1. preview records before fingerprint and intended locator;
2. immediately before mutation, reopen safely and compare identity and hash;
3. acquire a narrow per-artifact or per-operation lock for itembank writers;
4. write a sibling temporary file on the same filesystem;
5. flush as appropriate, validate full candidate, and replace atomically where
   supported;
6. record after fingerprint and manifest;
7. never assume the app lock controls external editors.

An external edit during the transaction leads to refusal or conflict output,
not last-writer-wins. For plain text, a three-way merge may be offered only when
a recorded base exists. Assessment files must pass full parsing and lint after
merge, and semantic/key changes require explicit review. For notebooks, use a
structure-aware comparison such as nbdime concepts; raw JSON conflict markers
are not a safe merge result.

### 7.3 File watching

File watchers are hints, not correctness authority. Events can coalesce, drop,
reorder, report temporary-save renames, or disappear while a drive is offline.
Use them to schedule verification. Hash and preflight decide current state.
Periodic reconciliation remains necessary.

## 8. Move, rename, copy, and folder operations

### 8.1 Move transaction

1. Resolve exact source and destination with no broad glob.
2. Verify source identity, current hash, authority, free-space class, and root
   availability.
3. Inventory known inbound references and list external references itembank
   cannot update.
4. Detect collision, case-only rename, normalization collision, cross-volume
   boundary, cloud-provider boundary, and removable destination.
5. Preview every file, directory, and known link to change in user language.
6. Prefer atomic same-filesystem rename when safe.
7. Otherwise copy to a temporary destination, verify bytes and structure, then
   publish destination.
8. Update supported links through their parser, never blind text replacement.
9. Validate every changed artifact.
10. Delete source only after destination and links verify, and only within the
    approved transaction.
11. Record a manifest, old-locator tombstone, and recovery state.

Default to no move when a link suffices. A folder move must inventory nested
artifacts and references but remain one journaled operation with per-file
results. Partial success is visible and resumable.

### 8.2 Cross-volume and remote moves

**Inference.** A high-level `move` API can conceal copy/delete behavior. The
product contract must not. Across volumes, network shares, providers, or
filesystems:

- verify capacity before copy where possible;
- preserve content, not promise unsupported permissions, timestamps, extended
  attributes, or sparse-file semantics;
- report metadata loss;
- verify the destination by content hash;
- keep the source until publication and link rewrite complete;
- never claim atomicity;
- make interruption recovery able to classify temp, complete destination,
  duplicated source, and partially copied state.

### 8.3 Folder creation

Creating a course folder is a write operation with a preview. Show the exact
destination, directories, collision policy, and permissions. Never reorganize
an existing root to fit a preferred template. On rollback, remove only empty
directories created by the transaction.

## 9. Deletion and destructive edge cases

### 9.1 Deletion hierarchy

Prefer, in order:

1. detach the link;
2. archive itembank metadata or course-owned derivative;
3. move a course-owned file to platform trash when reliable;
4. permanent delete only by exact confirmation and explicit scope.

Deleting an original source is never implied by deleting a course, objective
link, imported derivative, registry entry, or cached render.

### 9.2 Cloud deletion warning

**Fact.** OneDrive documents that deleting an online-only file from the device
deletes it from OneDrive across devices, subject to recycle-bin recovery.

**Recommendation.** When a root appears sync-managed, say: “This removes the
original from this synced folder and may remove it on other devices. Detach
keeps the file.” Do not promise provider recovery duration because account and
provider policies vary. The operation manifest records the provider hint and
whether platform trash was used, but a provider recycle bin is not an itembank
undo mechanism.

### 9.3 Secure deletion

Do not offer “secure erase.” SSDs, copy-on-write filesystems, cloud history,
backups, and synced replicas make that promise unreliable. Say “permanently
delete from this filesystem location” and disclose known sync implications.

## 10. Cloud, network, removable, and unusual storage

### 10.1 State model

| State | Meaning | Allowed behavior |
|---|---|---|
| Local and verified | Bytes read and hashed | Normal render and approved writes |
| Online-only placeholder | Path exists, bytes absent | Metadata listing; explicit hydration before content scan or use |
| Hydrating | Provider is downloading bytes | Show progress or pending; do not parse partial content |
| Provider conflict copy | Several divergent replicas | Register separately; do not choose newest timestamp automatically |
| Root offline | Network or device unavailable | Keep link and last-known metadata marked stale; no write |
| Permission lost | Path may exist but grant is invalid | Reauthorize; do not broaden scope automatically |
| Read-only media | Source readable, not writable | Link and render; edits require import copy or new destination |
| Unstable removable media | Mount may vanish mid-operation | Read retry; mutation journal and source-preserving copy protocol |

### 10.2 Cloud placeholders

**Fact.** OneDrive online-only files appear in Explorer but cannot be opened
offline; opening downloads them. Apps can trigger automatic download notices,
and users can block the app.

**Recommendation.** Discovery should avoid unbounded hydration. Before hashing
or rendering a placeholder, say what will download, approximate known size, and
whether the action requires network access. Offer metadata-only registration,
download this file, or mark a chosen root for explicit offline availability.
Never turn an entire cloud root local merely to inventory it.

### 10.3 Sync races and provider behavior

- Do not infer latest truth from modification time alone.
- A provider-created conflict copy is a first-class divergent artifact.
- Wait for a stable readable file before hashing, but do not wait indefinitely.
- Atomic local replace may sync as provider-specific operations; the manifest
  promises local verification, not immediate remote convergence.
- Renaming only letter case may not converge uniformly across clients.
- Excluding temporary and lock files from sync reduces clutter, but durable
  manifests and content must not live only in an evictable cache.
- Provider roots can be institution-controlled, read-only, retention-managed,
  or revoked. Do not promise ownership or deletion recovery.

### 10.4 Removable and network storage

Use a persistent root id plus remembered device hints, not the mount point as
identity. A different device mounted at the same path must not inherit trust.
Verify volume and expected sentinel or artifact evidence before writes.

On disconnect:

- cancel or journal the in-flight operation;
- retain source if deletion has not safely occurred;
- mark root offline, not missing-everything;
- avoid a flood of broken-link notifications;
- reconcile when the same device returns.

Network shares add latency, weak locking, permission changes, and server-side
rename semantics. Use local temp only for derived processing; final atomicity
must be assessed on the destination share. If safe replace cannot be
established, restrict the root to read or import-to-local.

### 10.5 Symlinks, junctions, aliases, and hard links

- Resolve symlink and junction targets for scope checks.
- Record the user-facing locator and resolved target separately.
- Refuse a write when resolution changes since preview.
- Treat hard-linked paths as the same underlying bytes locally but separate
  user locators; editing one changes all links and must be disclosed.
- Platform shortcuts or aliases are not automatically content links. Resolve
  them only through an explicit supported adapter.
- Detect symlink loops during traversal.

## 11. Executable notebooks and mixed documents

### 11.1 Observed facts

**Fact.** A Jupyter notebook contains more than readable text. Code cells,
outputs, cell ids, execution counts, attachments, MIME bundles, kernel
metadata, and arbitrary metadata may affect meaning. Rich outputs can contain
active content. Notebook ecosystems distinguish execution, caching, frozen
results, widgets, browser-backed execution, and external launch.

**Inference.** “Open,” “render,” “trust output,” and “execute” require separate
permissions and provenance. A historic output is evidence of a past run, not
proof that current code, data, and dependencies reproduce it.

### 11.2 Decision matrix

| Artifact | Default | Render | Import | Convert | Execute |
|---|---|---|---|---|---|
| `.ipynb` with important code, outputs, or widgets | Link native in place | Sanitized static cell view with output provenance | Only as intact course-owned copy | Optional derivative with explicit loss report | Explicit executor profile only |
| `.ipynb` used as static reading | Link | Strong option | Optional | Static HTML or Markdown derivative if verified | Usually unnecessary |
| MyST notebook | Link native text | Render text and known outputs | Optional project-aware copy | Avoid needless conversion | Explicit environment only |
| Quarto `.qmd` or R Markdown project | Link project root | Prefer existing frozen output with fingerprint | Import whole required project, not orphan page | Export derivative only | Leave to native environment unless adapter is deliberately supported |
| Plain script plus data | Link both and relate them | Source and recorded outputs are separate | Optional project copy | Lesson may cite excerpts, not replace source | Constrained runner with explicit data roots |
| Hosted executable document | Link external | Safe snapshot or external open | Official user-owned export only | No scraping into false native representation | Leave external |
| H5P or QTI package | Preserve intact | Adapter or sandbox if fidelity tested | Package-aware import | Convert supported constructs only and fail loudly | Interaction sandbox; assessment authority remains runtime-owned |
| PDF with code and figures | Link | Safe reader | Optional owned copy | OCR/Markdown is a derivative with uncertainty | Never infer executable source |

### 11.3 Render manifest

For any executable or derived render, record:

- source fingerprint and native format version;
- stable cell or block ids;
- kernel language and environment reference, or `unknown`;
- output origin: embedded historic, executed by itembank, or external;
- execution time, executor version, dependency-lock fingerprint, working
  directory and data input policy where known;
- MIME sanitation result and omissions;
- converter version, warnings, and source backlinks.

Never execute during discovery, preview, import, conversion preview, or lesson
open. Network, filesystem roots, subprocesses, secrets, time, memory, and output
size are distinct capabilities. Unknown environments remain render-only.

### 11.4 Conversion rules

Conversion creates a derivative and never overwrites the native source by
default. A conversion report must classify:

- preserved content;
- omitted outputs or metadata;
- flattened interaction;
- attachment handling;
- code language and environment uncertainty;
- locator mapping from derivative blocks to native cells;
- whether a reverse conversion is unsupported.

The source remains authoritative unless the user explicitly adopts the
derivative as a new artifact. “Exported successfully” is false if unsupported
content was silently dropped.

## 12. Import, export, and interoperability policy

### 12.1 Native-first rule

Link and render before importing. Import when the user wants a managed copy,
offline guarantee, immutable assessment package, or independent editing.
Convert only when a supported downstream format is required or native
rendering is impossible and loss is acceptable.

### 12.2 Format adapter contract

Every adapter declares:

- recognized versions and profiles;
- readable and writable features;
- identity preservation;
- attachment and path policy;
- unsupported constructs and whether they block or warn;
- round-trip guarantees, if any;
- accessibility effects;
- provenance fields;
- deterministic fixtures from real specifications, using synthetic content.

Assessment conversion must fail loudly by item or interaction when meaning,
scoring, feedback, accessibility, or disclosure cannot be preserved. It must
never introduce a second scorer.

### 12.3 External tools and edits

Opening in a native editor is a link operation plus an external-process action,
not a handoff of authority. After return, itembank rechecks bytes and invalidates
stale derivatives. It should not watch keystrokes or claim to save another
application's file.

If an external tool creates auxiliary folders, checkpoints, caches, or lock
files, classify them through adapter ignore rules. Do not delete them as
“clutter” unless that tool's documented lifecycle and user approval allow it.

## 13. Packaged paths and permissions

### 13.1 Path roles

**Recommendation.** Maintain separate roles:

| Role | Contents | Durability |
|---|---|---|
| Installed resources | App code, bundled sample, schemas, static assets | Immutable, replaced by app update |
| Config | Preferences and root grant references | Durable, small, portable where safe |
| User data | Registry, evidence, accepted manifests | Durable and backed up |
| State | Migration journal, operation journal, logs | Durable enough for recovery, not user content |
| Cache | Search index, sanitized renders, thumbnails | Rebuildable and freely deletable |
| Runtime | Sockets, lock coordination, process handshake | Session lifetime |
| Approved roots | Learner or institution files | External ownership and policy |
| Export or snapshot destination | User-selected portable recovery artifact | Explicitly managed |

The XDG specification provides the Linux distinction. Windows and macOS should
map the same roles to platform conventions. Tauri's installed resource
directory must not hold learner content or mutable state.

### 13.2 Least authority

The webview should not receive broad filesystem authority. The sidecar/runtime
performs scoped operations after validating root grants and exact targets.
Tauri capabilities constrain shell APIs, but the Python sidecar still needs its
own authoritative checks. A compromised frontend must not turn a read root into
a recursive write capability.

## 14. Migrations and long-term compatibility

### 14.1 Migration classes

| Class | Example | Safe approach |
|---|---|---|
| Rebuildable projection | Search index or cached render | Delete and rebuild from durable inputs |
| Additive metadata | New availability state | Versioned backfill with defaults and provenance |
| Registry identity change | New root-relative locator model | Dual-read, reconcile, validate, then switch |
| Content schema change | Lesson or bank format | Preserve original; additive parser or explicit derivative migration |
| Evidence projection change | New report state | Replay immutable events with versioned projector |
| External format change | New notebook or QTI version | Adapter version gate; leave unsupported source untouched |
| Path-role relocation | Move app state out of install directory | Copy, verify, atomic pointer switch, retain old until health check |

### 14.2 Migration transaction

1. Inspect app and data versions without mutation.
2. Refuse unsupported future versions in write mode.
3. Verify or create a restorable snapshot of affected durable app data.
4. Run one version step at a time with an idempotent journal.
5. Never mutate linked external originals merely to upgrade app metadata.
6. Reconcile counts, ids, fingerprints, paths, provenance, and assessment
   authority after each step.
7. Atomically switch the active version or pointer.
8. Keep old data until packaged health checks and user-visible validation pass.
9. On failure, preserve evidence and originals and open recovery diagnostics.

Downgrade is not implied. An old app facing newer data should open read-only
when safely possible or refuse with export and upgrade guidance.

### 14.3 Stale-source detection

Staleness is a relation between a derived claim and the source fingerprint it
used. A changed source does not automatically invalidate every derivative, but
it requires revalidation. Report exact affected locators and why they are
stale. Do not overwrite accepted lessons or assessments during refresh.

## 15. Recovery, backup, and diagnostics

### 15.1 Operation manifest

Extend Phase 11's manifest to every mutation:

```text
operation_id and type
actor and authority mode
previewed targets and root grants
before locators, identities, hashes, and existence
temporary and final paths
created directories
rewritten references
converter or migrator versions
after hashes and validation
commit, trash, provider, or shadow recovery information
status: prepared, copied, published, links_updated, source_removed, complete
```

Undo verifies the recorded after-state. If bytes changed, it refuses and offers
reconciliation. Recovery after interruption examines the journal and actual
filesystem rather than replaying blindly.

### 15.2 Backup boundary

App undo, Git history, provider versioning, trash, and OS backup are different:

| Mechanism | Protects | Does not guarantee |
|---|---|---|
| Transaction undo | Known recent itembank mutation | External edits or disk loss |
| Git | Tracked committed files | Untracked data, large binaries, remote backup |
| Cloud versioning/recycle bin | Provider-managed history | Offline access, account retention, independent backup |
| Platform trash | Recoverable local deletion on supported targets | Synced remote semantics or permanent retention |
| Time Machine or other backup | Broader versioned recovery | Current inclusion, successful completion, or restore validity unless tested |
| itembank portable snapshot | Registry, manifests, evidence, selected owned artifacts | Copyrighted linked sources not included by policy |

**Recommendation.** Provide a portable snapshot manifest and restore drill.
External linked sources are normally referenced, not copied. The restore report
lists found, missing, changed, permission-lost, and ambiguous roots and asks for
relink decisions.

### 15.3 Diagnostics

Diagnostics should report locally and export with paths and secrets redacted by
default:

- app, shell, sidecar, schema, registry, and migration versions;
- path roles, writability, free-space class, and cache rebuildability;
- approved roots, authority, online/offline/placeholder/permission state, and
  last successful verification;
- counts of stale, missing, ambiguous, conflicting, and unsupported artifacts;
- incomplete operation and migration journals;
- evidence log integrity and projection rebuild status;
- notebook renderer, sanitizer, executor profile, and missing environment state;
- update channel and last verified result;
- last itembank snapshot and restore drill, without claiming an OS or provider
  backup is healthy;
- exact next safe actions.

Do not send diagnostics automatically. Do not include file contents, API keys,
full usernames, or unredacted absolute paths in a support bundle by default.

### 15.4 User explanations for common failures

| Condition | Explanation | Safe choices |
|---|---|---|
| Root offline | “The folder is registered but its drive or server is not available. Your link is kept.” | Retry, work with other files, detach |
| Online-only file | “The file is listed here but its contents are not on this device.” | Download this file, metadata only, cancel |
| Permission lost | “itembank no longer has permission to read this folder.” | Reauthorize exact folder, detach |
| Changed externally | “This file changed after the preview. Nothing was overwritten.” | Review new diff, rebuild proposal, cancel |
| Ambiguous move | “Several files could be the one previously linked. itembank will not guess.” | Compare, select, keep unresolved |
| Move partly complete | “The verified copy exists, but the original was kept because the operation stopped before cleanup.” | Resume, keep both, roll back |
| Unsupported conversion | “These constructs cannot be represented in the target format.” | Keep linked original, export supported subset only with explicit consent, cancel |
| Missing notebook kernel | “The notebook can be read, but its code cannot be reproduced in the current environment.” | Static render, configure environment, open externally |

## 16. Pattern inventory

| Pattern | Benefit | Weakness | Applicability |
|---|---|---|---|
| Link in place by default | Preserves ownership and existing workflows | Roots may be offline or permissions revoked | Core default |
| Approved roots and metadata-only discovery | Privacy and bounded scans | More setup and incomplete global search | Core safety |
| Layered identity | Survives more real-world changes | Requires uncertainty and review states | Core |
| Root-relative locators | Portable when a whole root moves | Not enough for cross-root moves | Core with stable ids |
| Hash preflight and atomic replace | Prevents stale overwrite | External formats and remote filesystems vary | Core for supported writes |
| Transaction journal | Interruption recovery | Every mutation path must participate | Core |
| Native artifact plus derived render | Preserves interoperability | Cache invalidation and sanitation burden | Core for mixed documents |
| Format-aware diff and merge | Reduces JSON or binary corruption | Adapter cost and unresolved semantic conflicts | Prototype by format |
| Cloud metadata-only scan | Avoids mass download | Provider state detection is platform-specific | Accept with conservative fallback |
| Automatic filename relink | Low-friction appearance | High wrong-link risk | Reject |
| Central hidden content library | Easy indexing | Breaks ownership, provenance, and storage expectations | Reject |

## 17. Cross-cutting effects

### 17.1 Accessibility

File operations need semantic, keyboard-operable confirmation and status text.
Do not communicate online-only, conflict, destructive scope, or stale state by
icon or color alone. Notebook renders need text alternatives for meaningful
outputs and explicit omission notices for unsafe or inaccessible MIME content.

### 17.2 Portability

Plain authored files remain primary. Stable ids, root-relative paths, portable
registry export, versioned manifests, and native-first adapters avoid locking
content to one machine. Absolute paths and OS file ids are local hints only.

### 17.3 Privacy

No root scan before approval. No silent cloud hydration. No automatic upload,
telemetry, or support bundle. Least-privilege read and write grants, content-free
indexes, and redacted diagnostics are required.

### 17.4 Provenance

Every import, conversion, move, relink, external edit, migration, and generated
derivative carries before and after identity, source links, tool version, loss
report, and acceptance state.

### 17.5 Authorability

Users can keep editing Markdown and notebooks in their preferred tools.
itembank should add sidecar metadata when embedding ids would harm the native
format or external workflow. Conflicts are surfaced as files and relations the
user can inspect, not silently resolved database records.

### 17.6 Agent skills and legacy upgrades

Agents receive registry queries and explicit operation plans, not broad path
access. Course skills must search all approved roots before drafting and return
link/import/convert proposals separately. A notebook skill defaults to inspect
and safe render. Legacy upgrade skills preserve original identity, show a
format-aware diff and render, validate, and use the same manifest and undo path.

## 18. Accept, reject, defer, prototype, and open

### 18.1 Accept

| Decision | Reason | Verification |
|---|---|---|
| Default link in place and no move | Preserves user ownership and external workflows | Multi-root course works with no copied content |
| Artifact registry over approved roots | Enables discovery and reconciliation without hidden copies | Rebuild, export, restore, offline-root tests |
| Separate operations and user-language promises | Prevents ambiguous destructive behavior | CLI and app produce same manifest and explanation |
| Layered identity with uncertain state | Avoids filename guesses | Rename, copy, edit, restore, duplicate, and device-swap fixtures |
| Exact preflight, atomic local write, manifest, stale-safe undo | Reuses proven authoring safety | Concurrent external edit and interruption tests |
| Native-first executable document policy | Preserves code, output, metadata, and provenance | Notebook corpus and conversion loss tests |
| Explicit cloud placeholder and hydration state | Prevents surprising downloads | Offline and blocked-download tests on supported OS |
| Separate path roles and least authority | Required by packaged permissions | Frozen and installed package tests |
| Journaled schema and path migrations | Preserves recoverability | Every supported version upgrade and interrupted step |
| Redacted local diagnostics and restore drill | Makes edge cases supportable without telemetry | Secret/path leak fixtures and clean-install restore |

### 18.2 Reject

| Rejected behavior | Reason |
|---|---|
| Home-directory scan on launch | Unbounded and privacy-invasive |
| Move or copy discovered files automatically | Discovery is not mutation authority |
| Force user files into one course folder | Breaks external organization and provenance |
| Filename-only duplicate merge or relink | Identity evidence is insufficient |
| Silent cloud hydration | Can consume bandwidth, storage, and disclose content access |
| Flatten notebooks by default | Loses semantics and reproducibility |
| Execute on open, preview, import, or scan | Unsafe and surprising |
| Blind textual reference rewriting | Can corrupt code, prose, and assessment content |
| Permanent delete as normal removal | Detach or trash is safer |
| “Secure erase” promise | Unreliable across modern storage, cloud, and backups |
| Learner data under installed resources | Not reliably writable or update-safe |
| Last-writer-wins external conflict handling | Risks silent content loss |

### 18.3 Defer

| Item | Until |
|---|---|
| General notebook execution | Safe renderer and explicit executor prototype pass |
| Full QTI and H5P round trip | Profiles and scorer boundary are selected and tested |
| Provider-specific cloud APIs | Conservative filesystem behavior proves insufficient |
| Real-time collaborative editing | Single-user external conflict model is reliable |
| Automatic cross-tool link rewriting | Each native format has an approved parser and reversible adapter |
| OS backup integration | Portable snapshot and restore drill are proven |

### 18.4 Prototype

| Prototype | Question | Pass condition |
|---|---|---|
| Multi-root registry and reconciler | Can links survive realistic edits and moves? | Strong matches relink, weak matches stop, discovery never mutates |
| Cross-volume move state machine | Can interruption occur at every step without loss? | Original or verified destination always recoverable; journal explains state |
| Cloud placeholder inventory | Can scan avoid implicit hydration? | Metadata-only scan, explicit one-file hydration, blocked/offline degradation |
| External-editor concurrency | Can stale proposals never overwrite newer bytes? | Deterministic preflight refusal and format-aware comparison |
| Notebook safe renderer | What can render without execution? | Cells, attachments, safe MIME and provenance work; active content omitted or sandboxed |
| Registry snapshot and restore | Can a clean install reconnect external roots honestly? | Found, missing, changed, permission-lost, and ambiguous results are distinct |
| Packaged path migration | Can old state move out of legacy location safely? | Idempotent copy, verification, pointer swap, rollback, no source mutation |

### 18.5 Open questions

| Question | Evidence needed |
|---|---|
| Should portable registry metadata live per course, globally, or as a hybrid? | Multi-course reuse, restore, privacy, and concurrent-editor prototype |
| Which formats may embed an itembank id without harming native workflows? | Round-trip tests per format |
| What exact evidence permits automatic relink after an edited move? | False-positive corpus and user review |
| Which cloud placeholder APIs are stable across supported targets? | Packaged OS prototypes |
| Is platform trash reliable enough for every supported root type? | Local, network, removable, and provider tests |
| Which notebook MIME types are safe and accessible? | Security sanitizer and assistive-technology corpus |
| What migration window and downgrade behavior are supportable? | Release policy and storage-cost decision |
| May agents request new root grants, or only operate within user-created grants? | Threat model and capability UX decision |

## 19. Concrete recommendations and risks

### 19.1 Recommendations for synthesis

1. Establish artifact identity, approved roots, and path roles before adding
   automated source organization.
2. Make link in place the default and require an explicit transaction for move,
   import, conversion, or deletion.
3. Generalize Phase 11's preflight, manifest, atomic write, and undo patterns to
   every mutating operation.
4. Treat watchers, metadata, OS file ids, and filenames as hints. Current bytes
   and validated preconditions remain authoritative.
5. Make cloud placeholder, offline root, removable device, permission loss,
   and ambiguous identity first-class states.
6. Preserve executable documents natively, render safely, convert as a
   derivative with a loss report, and execute only through explicit capabilities.
7. Separate app update, data migration, cache rebuild, source refresh, and
   external content upgrade.
8. Ship diagnostics, transaction recovery, portable snapshot, and restore drill
   with the file model, not after it.

### 19.2 Principal risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Wrong auto-relink | Course uses the wrong source or assessment | Strong-only automation, uncertainty and review |
| Cross-volume or cloud move interrupted | Duplicate, missing, or partially copied data | Source-preserving journaled state machine |
| External editor races app | Lost work | Exact preflight and no last-writer-wins |
| Hidden cloud hydration | Bandwidth, storage, privacy surprise | Metadata-only scan and explicit hydration |
| Provider deletion propagation | Original disappears on several devices | Detach default and sync-aware warning |
| Registry becomes hidden content store | Ownership and portability erode | Metadata only, inspectable export, rebuildable index |
| Notebook active output executes | Local compromise or data disclosure | Sanitation, CSP, MIME allowlist, no execution on open |
| Migration changes originals | Irreversible content damage | Migrate app metadata and derivatives, preserve linked sources |
| Diagnostics leak paths or content | Privacy breach | Local-only, redacted export, leak tests |
| App claims backup health falsely | False confidence | Report only itembank snapshot and restore evidence |

## 20. Implementation-readiness audit for accepted file-lifecycle research

After synthesis accepts decisions, map each accepted item to:

```text
decision id
artifact or operation contract
owner layer: registry, runtime, server, surface, shell, adapter, migration, docs
phase and plan
dependencies
platforms and root types
data migration class
security and permission boundary
automated and packaged verification gates
interruption points and rollback
user explanation and diagnostic code
maintenance trigger
```

The audit must fail on duplicate registries or writers, alternate path
authority in the webview, mutation without a manifest, adapters without loss
policy, migration without rollback, or a consumer scheduled before identity and
permission foundations.

Proposed order, subject to synthesis:

```text
terminology and operation contract
  -> path roles and approved root grants
  -> artifact registry and layered identity
  -> read-only discovery and reconciliation prototype
  -> mutation manifest and recovery state machine
  -> external edit and conflict handling
  -> cloud, removable, and network storage gates
  -> notebook safe renderer and adapter contract
  -> migrations, diagnostics, portable snapshot, restore drill
  -> bounded agent operations and legacy upgrades
  -> packaged cross-platform edge-case audit
```

Trigger the next readiness audit after any accepted change to stable identity,
write authority, root scope, move semantics, notebook execution, migration
window, packaged path roles, or deletion policy, and before any release that
migrates learner data.

## 21. Conclusion

**Inference.** The core file-lifecycle problem is maintaining truthful identity
and user authority while paths, bytes, devices, providers, formats, and app
versions change.

**Recommendation.** Keep learner files in place by default. Register them
through explicit roots, treat paths as locators rather than identity, preserve
native formats, and make every mutation a validated, journaled, recoverable
transaction. Model external edits, placeholders, offline media, ambiguity, and
permission loss as normal states. Explain each operation in terms of what
happens to the original bytes.

This direction reuses shipped lesson containment, fingerprinting, atomic
authoring, undo, evidence migration, resource resolution, updates, packaging,
and help checks while identifying the general contracts still missing. It does
not alter product contracts or implementation before synthesis.
