<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# Boardwright Product Specification

Boardwright is a KiCad/KiBot hardware project template plus a small workflow
tool. Its job is to make the normal PCB loop predictable:

```text
edit in KiCad -> record changes -> commit + push -> review artifacts
-> accept to main -> create release
```

The user should not need to remember KiBot groups, GitHub Actions inputs, tag
rituals, or revision-history plumbing during normal design work.

## Current Codebase

The repository currently contains three coupled parts:

- KiCad template files at the repository root, with worksheets in `Templates/`.
- Boardwright Python tooling in `src/boardwright/`.
- KiBot/GitHub Actions build resources in `boardwright_resources/` and
  `.github/workflows/`.

The Python package provides:

- project config loading from `.boardwright/`
- validation of required config, KiCad, KiBot, README, licence, and asset files
- changelog parsing, writing, and release promotion
- revision-history variable generation for KiBot/KiCad text variables
- legal/notice file generation
- CLI commands for status, validation, change recording, preview planning,
  promotion planning, release preparation, and git commit dry-runs
- shared workflow action builders used by CLI and TUI
- optional Textual TUI with a console fallback
- GitHub CLI integration for workflow dispatch, CI polling, and preview artifact
  download when `gh` is available

The current tests are Python `unittest` tests under `tests/`. Run them with:

```powershell
python -m unittest discover -s tests -v
```

`python -m boardwright ...` and `python -m boardwright.cli ...` both work for
local module execution. The installed console script is `boardwright`.

## Core Rules

- `dev` is the normal KiCad/source development branch.
- CI must not mutate `dev`.
- `preview` is disposable and may be force-updated.
- `main` is the accepted state.
- `main` may contain source files plus accepted generated README/render snapshot
  assets, but not wholesale manufacturing output folders.
- Tags are immutable published package points.
- Tag workflows publish artifacts only; they do not commit back to branches.
- Release-affecting operations require explicit user intent.
- CLI and TUI should share action logic instead of duplicating workflow rules.

## Branch And Release Model

```text
dev      = normal design/source work
preview  = disposable generated preview branch/artifacts
main     = reviewed and accepted project state
tags     = immutable published release package points
```

Normal work happens on `dev`. Preview CI is explicitly dispatched when the user
is ready to review generated outputs. Preview CI generates reviewable artifacts
and can publish the disposable `preview` branch, but must not commit to `dev`.

`main` represents a reviewed state. The `Accept` action dispatches the
main-output workflow from the exact reviewed `dev` source SHA, with a selected
variant. CI verifies that source SHA before generation. When requested, that
workflow pushes the reviewed source plus an accepted `README.md` and render
snapshot under `assets/renders/` to `main`.

Release preparation is CI-owned. Boardwright dispatches `prepare-release.yaml`;
that workflow promotes the changelog, writes release metadata, generates
accepted outputs, commits the accepted release state to `main`, creates the tag,
and dispatches the tag workflow. The tag workflow publishes the release package
without mutating `main`.

## Variants

Supported variants are:

```text
DRAFT
PRELIMINARY
CHECKED
RELEASED
```

Variant intent:

| Stage | Variant | Typical release state |
| --- | --- | --- |
| early schematic/design | `DRAFT` | draft or prerelease |
| schematic mostly complete | `PRELIMINARY` | prerelease |
| fabrication package ready | `CHECKED` | prerelease or release candidate |
| official production release | `RELEASED` | full release |

Defaults live in `.boardwright/project.yaml`:

- `variants.dev_default`
- `variants.preview_default`
- `variants.main_default`
- `variants.release_default`

Variant defaults are not the same thing as a CI run's selected output variant:

- `dev_default` is the source project's normal design-stage label and is what
  the TUI status strip calls `dev`.
- `preview_default`, `main_default`, and `release_default` seed the selector
  values for their respective actions.
- Dispatching preview, accepting to main, or preparing a release must not
  silently rewrite `.boardwright/project.yaml` on `dev`. Those actions are CI
  output selections and are recorded in run names, artifacts, job summaries,
  accepted-main evidence, and `.boardwright/release.env` for releases.
- If the project has genuinely moved from `DRAFT` to `PRELIMINARY` or
  `CHECKED`, the user should change `dev_default` deliberately in Info
  and commit that source-state change.

## Project Config

Boardwright config lives in `.boardwright/`:

```text
.boardwright/
  project.yaml
  branches.yaml
  legal.yaml
  revision_history.yaml
  revision_history_variables.env
  release.env
```

`project.yaml` holds project identity, drawing identifiers, GitHub
repository settings, variant defaults, workflow filenames, output policy, and
visible asset paths.

`branches.yaml` maps the development, preview, and release branches. The
current default is:

```text
development: dev
preview: preview
release: main
```

`release.env` is written and committed by release preparation so the tag
workflow can read:

```text
RELEASE_VERSION=0.1.0
RELEASE_VARIANT=CHECKED
RELEASE_KIND=prerelease
```

KiCad text-variable naming:

- `${RELEASE_VERSION}` is the semantic package/release value, normally
  sourced from `.boardwright/release.env` during release preparation or from
  git tags as a fallback. It is not the controlled drawing revision.
- `${BOARD_REVISION}` is the hardware board spin such as `A`, `B`, `C`, `1`,
  `2`, or `3`, sourced from `project.board_revision`.
- `${PROJECT_NUMBER}` is the configured project name from `project.name`.
- `${DRAWING_NUMBER}` is resolved per output context from the configured
  document name source. Schematic and assembly use the PCBA name;
  fabrication uses the PCB name.
- `${DRAWING_REVISION}` is the controlled drawing revision for the current
  document. Its scheme can be semantic, lettered, or numeric per
  document/customer requirements.

Numbering and revision model:

Boardwright should distinguish four related but separate concepts:

| Concept | Examples | Intended use |
| --- | --- | --- |
| Project name | `GRICE-PSW-0028` | User/customer/job/program identity printed via `${PROJECT_NUMBER}` |
| PCBA name | `7-087598-700` | Schematic and assembly drawing identity |
| PCB name | `7-087598-701` | Fabrication drawing and board marking identity |
| Board revision / spin | `A`, `B`, `C`, `1`, `2`, `3` | Hardware design spin for the PCB/PCBA |
| Drawing revision | `A`, `B`, `C`, `0.1.0`, `1.2.0` | Controlled drawing revision shown in title blocks and revision history |

Projects may use the same value for some of these fields, especially small or
early-stage designs, but Boardwright should not force that coupling. The data
model should make the distinction explicit so a CME-style project can show a
PCBA name, a different bare PCB name, a board revision, and a separately
controlled drawing revision without abusing `${TITLE}` or `${RELEASE_VERSION}`.

Drawing revision schemes should be configurable. Supported schemes should
include at least semantic, lettered, and numeric. Git tags can remain semantic
for automation and package publishing while the drawing revision shown on
controlled sheets is lettered or numeric.

Drawing authorship and signoff metadata:

Controlled drawings should emit drawn-by and drawn-date metadata independent of
Git commit metadata. Checked and approved fields are physical/electronic
signature areas applied after generation, not Boardwright text variables.
Revision-history rows should include revision, date, description, and drawn-by
metadata. Git commit hashes and release tags remain useful traceability
evidence, but they should not be the only representation of controlled-document
authorship.

Dashboard tag display:

- The status bar's tag value is the latest semantic release tag in the
  repository, not the nearest tag reachable from the current branch tip.
- Stable semantic-version tags such as `0.1.3` or `v0.1.3` win over
  prerelease tags.
- If there are no stable release tags, the latest semantic prerelease tag such
  as `0.1.3-rc.1` is shown.
- If there are no semantic release/prerelease tags, the dashboard shows `none`.

## Project Information And Manufacturing Metadata

Boardwright should treat project-specific manufacturing text as structured
project data, not as hardcoded KiBot YAML. The TUI should expose this as a
`Info` screen with compact tabs or sections:

- Identity: project name, PCBA name, PCB name,
  board revision, document revision, document revision scheme, company,
  designer/author, logo path, repository URL, development branch, preview
  branch, release branch.
- Variants: dev, preview, accepted-main, and release default variants.
- Fabrication: surface finish, soldermask color, silkscreen color, material
  requirements, IPC class, RoHS/Pb-free policy, tented-via policy, controlled
  impedance enabled/disabled, and editable fabrication notes.
- Assembly: DNP policy, BOM precedence policy, conformal coating requirement,
  pin-1/orientation note, and editable assembly notes.
- Tables: component-count behavior, testpoint policy, impedance table entries,
  and whether empty side-specific pages should be omitted.
- Outputs: README/render snapshot policy, release package contents, and
  generated output cleanup policy.

The first implementation should avoid a raw YAML editor. It should show fields
as normal form controls:

- text inputs for names, part numbers, document revisions, signoff names,
  signoff dates, repository URL, colors, material notes, and freeform note
  bodies
- selects for variant defaults, document revision scheme, IPC class, surface
  finish, soldermask color, silkscreen color, and release kind defaults
- checkboxes for RoHS/Pb-free, conformal coating, tented vias, controlled
  impedance, and side-specific testpoint pages
- a small editable impedance table with columns:
  `Transmission Line`, `Impedance [ohms]`, `Tolerance [ohms]`, `Layer`,
  `Trace Width [mm]`, `Gap [mm]`, and `Ref. Layers`

The manufacturing-note templates remain parameterized. Boardwright should
eventually render them from project metadata before KiBot runs, so the KiCad
text variables receive complete notes even when the report outputs have not
yet been generated. Freeform edits should be stored as project-local data under
`.boardwright/`, while the repository template keeps sane defaults.

Controlled impedance is opt-in. When no impedance entries exist, Boardwright
must render a short note in the impedance-table placeholder that says there are
no impedance controlled traces. When entries exist, Boardwright should generate
the CSV/table from the structured project data and leave the KiCad placeholder
movable.

## KiCad Sheets And Title Blocks

The default KiCad worksheets and sheet title blocks must be Boardwright-neutral
and project-configurable. They should not be hardcoded to any one business,
consultancy, customer, logo, or legal notice.

Target behavior:

- Project identity fields such as company, designer, board name, board
  revision, release version, repository URL, and legal notice should come from
  `.boardwright/project.yaml` and KiCad/KiBot text variables.
- Template worksheets may carry Boardwright visual identity as a neutral
  default, but project branding should be easy to override from Info.
- Users should not need to edit every schematic sheet or PCB worksheet by hand
  to change title-block ownership, branding, logo, or legal copy.
- Legal notice copy on sheets should be generated from Boardwright legal
  metadata, with conservative defaults while the project-level legal review is
  ongoing.
- Business-specific defaults from local/internal use belong in project config
  or downstream project repos, not in the public template defaults.

Implementation direction:

- keep worksheet assets under `Templates/` but make visible identity text
  variable-driven wherever KiCad supports it
- converge toward one active worksheet template per project/brand rather than
  separate schematic and `_PCB` worksheet families. The normal Boardwright
  template should use the standard `Boardwright_Template_GIT.kicad_wks` path;
  downstream branded examples such as CME should likewise have one active CME
  worksheet when their title-block fields can carry the context that formerly
  required PCB-specific worksheets.
- treat the existing `_PCB` worksheet templates as transitional compatibility
  assets while standalone assembly/fabrication outputs still depend on native
  KiCad sheet numbering behavior. Combined review output may generate
  temporary numbered worksheets or bake page text for its own shards, so it
  should not require permanent duplicate PCB templates.
- develop Boardwright-native worksheet families for common drawing standards
  after the single-template model is proven. Initial targets are AS 1100, ISO,
  and ANSI-style layouts, with project branding, legal notice, logo artwork,
  release metadata, and title fields still driven by config/text variables.
- expose title-block/legal fields in Info, grouped into project,
  template, sheet, variant, and asset sections
- read worksheet selection from the KiCad project file
  (`*.kicad_pro` `pcbnew.page_layout_descr_file`) so KiCad remains the source
  of truth for the active page layout
- store embedded sheet-image intent in the `template` section of
  `.boardwright/project.yaml`
- store the embedded worksheet bitmap source as `template.sheet_image`; by
  default it can match the main brand logo, but it is the only image field for
  worksheet/title-block bitmap artwork
- store sheet legal copy in the `sheet` section of `.boardwright/project.yaml`;
  the default may use project placeholders such as `${COMPANY}` and should be
  expanded into the `SHEET_LEGAL_NOTICE` KiCad/KiBot text variable
- group downstream legal defaults into named profiles in `legal.yaml`, so
  projects can start from a public-hardware, compatibility-friendly, or
  internal-prototype stance without rewriting every legal field by hand
- document which fields are source project metadata and which are generated
  release metadata
- add validation warnings for hardcoded known-local branding in default
  template sheets once the neutral replacements exist

Current implementation note:

- Legal title-block text is variable-driven through `${SHEET_LEGAL_NOTICE}` in
  the worksheet files.
- Combined-review sheet totals use `${COMBINED_SHEET_TOTAL}` for schematic
  worksheets so the schematic ToC/title block can refer to the whole combined
  document. Native `${##}` remains valid for standalone KiCad/PCB print outputs
  until those paths also use generated per-output worksheets.
- The worksheet path is read from the KiCad project and feeds KiBot's
  `SHEET_WKS` definition. The TUI shows this as project context rather than an
  editable Boardwright field.
- Schematic sheet titles should use the KiCad hierarchical sheet `Sheetname`
  property as the source of truth. The `SHEET_NAME_1..40` text variables exist
  only as local placeholder values for the cover/navigation sheet; KiBot
  overwrites them during CI from the actual schematic sheet names. Locally,
  `boardwright sheet-title --sync` writes `.boardwright/sheet_titles.env` so
  the helper can keep editable placeholder names aligned with the schematic
  hierarchy when working offline.
- The README/main brand image lives under `assets.logo`. Project/render images
  live under asset/project-image fields. Worksheet/title-block artwork lives
  under `template.sheet_image`.
- The sheet-image path is captured in config and the TUI. The
  `boardwright worksheet-logo` command embeds `template.sheet_image` by default
  into worksheet bitmap data while preserving each worksheet's existing
  position and scale.
- Saving Info in the TUI should re-embed `template.sheet_image` into
  all worksheet templates so changes are visible without running a separate
  command.

## Legal, Licensing, And Provenance

Boardwright must make provenance clear before a public/template release. The
repository includes original Boardwright work, Nguyen-derived KiCad/KiBot
template work, bundled third-party assets/fonts, and generated-output
templates. These should be documented in a way that is useful to downstream
hardware projects.

Required source-of-truth files:

```text
LICENSE
LICENSES/README.md
LICENSES/Apache-2.0.txt
LICENSES/Commons-Clause.txt
LICENSES/Nguyen-MIT.txt
NOTICE.md
THIRD_PARTY_NOTICES.md
CONTRIBUTING.md
docs/PROVENANCE.md
```

Legal/provenance goals:

- Preserve the inherited Nguyen template license and attribution for files or
  patterns that remain derivative.
- Keep a git-evidence-based Nguyen provenance audit so future file moves do
  not erase attribution history.
- Clearly state which parts are Boardwright-original and covered by the
  Boardwright source-available license stack.
- List bundled third-party assets, fonts, helper scripts, and their license
  obligations.
- Explain that generated hardware project outputs may include Boardwright
  template text/assets and therefore may carry notices into downstream repos or
  release packages.
- Avoid putting one business's legal language into the public default title
  blocks or generated README.
- Keep the legal metadata editable at the project level so downstream projects
  can set company-specific notices without patching templates.
- Keep the Boardwright tooling/template license separate from downstream
  hardware-design licensing. Using Boardwright must not force a user's hardware
  design or generated manufacturing artifacts under the Boardwright tool
  license, except for copied Boardwright template material.
- Preserve the root `LICENSE` policy of Apache-2.0 with Commons Clause, plus
  the Boardwright Hardware Output Exception, unless external legal review
  changes that policy.
- Keep `.boardwright/legal.yaml` scoped to downstream project defaults. It must
  not be treated as the Boardwright repository/tooling license.

The legal tooling should remain practical rather than pretending to be legal
advice. It should generate/check notice files, highlight missing provenance,
and make review work visible in the TUI/CLI.

## Changelog And Revision History

`CHANGELOG.md` remains the human/Git release narrative. Commit messages and
recorded changes stay with Git and release notes. Controlled drawing revision
history is a separate YAML-backed table: when preparing an actual release, the
operator supplies a drawing revision and a short revision-table description.
Boardwright writes that row to `.boardwright/document_revisions.yaml`, updates
the current document drawing revision, and regenerates fixed `REVTABLE_*`
variables.

Supported changelog sections are:

```text
Added
Changed
Fixed
Removed
Notes
Status
```

The TUI exposes the everyday sections:

```text
Added
Changed
Fixed
Removed
Notes
```

Release preparation no longer fails solely because `Unreleased` is empty. If a
release is otherwise valid and no changelog entries are waiting, Boardwright
creates the version heading with a generated note:

```text
No changelog entries recorded for this release.
```

This keeps release packages traceable while still allowing the TUI to show the
missing changelog entry as a warning. The controlled revision table row is not
derived from the changelog body; it uses the release-time drawing revision and
short description instead.

KiCad sheets consume fixed text-variable slots:

```text
${REVTABLE_1_REV}
${REVTABLE_1_DESC}
```

Boardwright writes every configured slot to
`.boardwright/revision_history_variables.env`. Newest visible release content
fills slot 1, and unused slots are written as blank values. The KiBot preflight
defines a larger ceiling than the default visible slot count so projects can
expand their revision-history sheets later.

Revision-history generation supports controlled-document rows from YAML:

```text
Revision | Date | Description | Drawn
```

Checked and approved signoffs are handled as signature areas after generation,
so Boardwright does not export checked/approved text variables.

## CI/CD Workflows

Boardwright-native workflows:

```text
.github/workflows/dev-preview.yaml
.github/workflows/main-outputs.yaml
.github/workflows/prepare-release.yaml
.github/workflows/release.yaml
```

Workflow run names should be human-readable in the GitHub Actions list. They
should include the user decision and short source label where practical, for
example `Preview PRELIMINARY from dev@a9cf86e1d223` and
`Accept CHECKED from dev@a9cf86e1d223 to main`. Full source SHAs belong in the
job summary as clickable commit links rather than in long run titles.

`dev-preview.yaml`

- runs on manual dispatch for the selected source ref
- selects a KiBot generation mode from the variant
- generates preview outputs
- cleans generated output packages before upload
- uploads `boardwright-preview-<VARIANT>` artifacts
- uploads KiBot logs
- publishes the disposable `preview` branch from `dev`
- does not mutate `dev`

`main-outputs.yaml`

- runs on manual dispatch
- checks out and verifies the reviewed source ref/SHA
- generates accepted outputs from that reviewed source
- intentionally regenerates outputs rather than copying the preview artifact.
  Preview artifacts are review evidence; accepted outputs are a reproducible CI
  build from the reviewed source SHA.
- cleans generated output packages before upload
- uploads generated outputs as artifacts
- discards generated source/config side effects, including temporary KiBot
  metadata injected into `boardwright_resources/kibot/yaml/kibot_main.yaml`,
  before switching to the accepted branch
- optionally pushes the reviewed source plus `README.md` and
  `assets/renders/*.png` to the target accepted branch
- when committing the accepted snapshot, merges the reviewed source SHA onto the
  current target branch first, then reapplies the generated README/render
  snapshot. This avoids non-fast-forward failures after earlier CI snapshot
  commits on `main`.
- always pushes the reviewed-source merge to the target branch, even when the
  generated README/render snapshot is unchanged. This keeps accepted source
  changes such as `CHANGELOG.md` from being stranded in the CI runner.

`prepare-release.yaml`

- runs on manual dispatch from `main`
- installs Boardwright
- promotes `CHANGELOG.md`
- writes `.boardwright/release.env`
- generates accepted outputs/README
- cleans generated output packages before commit/tag
- discards generated source/config side effects before committing release state
- commits accepted release state to `main`
- creates and pushes the tag
- dispatches `release.yaml` for the tag

`release.yaml`

- runs on semantic-version tags or manual dispatch against a tag
- reads `.boardwright/release.env`
- generates release outputs
- cleans generated output packages before packaging
- creates release notes from changelog content and board renders
- packages release assets
- publishes the GitHub Release
- does not push branch commits

CI cache policy:

- Use pinned official `actions/cache@v4` cache steps for Boardwright-owned
  caches, with restore keys.
- Treat GitHub cache-save outages as non-fatal infrastructure warnings. The
  build should still succeed without a cache write.
- Cache 3D model downloads by runner OS and KiCad major version only. This
  cache is a best-effort speedup and must not depend on fragile `hashFiles`
  expressions that can block workflow parsing.
- Cache Python package downloads where Boardwright is installed in CI.

## CLI

Core commands:

```text
boardwright
boardwright init
boardwright status
boardwright change
boardwright suggest-commit
boardwright validate
boardwright revision-history
boardwright preview
boardwright promote
boardwright accepted
boardwright review
boardwright release
boardwright doctor
boardwright migrate
boardwright update
boardwright testbench
boardwright generate
boardwright source-package
boardwright outputs clean
boardwright legal
boardwright git-status
boardwright commit
boardwright tui
```

Plain `boardwright` opens the TUI. If Textual is not installed, it prints a
console status view and an install hint.

The CLI remains scriptable and useful in CI. The TUI is the intended everyday
interface for designers.

Planned CLI additions:

- `boardwright config show`: read-only project configuration summary.

Implemented onboarding helper:

- `boardwright adopt`: adopts an existing KiCad project by initializing the
  Boardwright config files and filling repository URL metadata when possible.
  Recognized Nguyen hierarchical-template descendants are directed to the
  migration workflow instead of being adopted as generic projects.

Implemented migration and managed-update support:

- `boardwright migrate plan`: recognizes the Nguyen hierarchical KiCad/KiBot
  template family, selects one root KiCad project, collects metadata candidates,
  fingerprints migration inputs, and writes a reviewable YAML plan.
- `boardwright migrate apply`: requires a clean non-release branch and resolved
  metadata, rechecks fingerprints, preserves KiCad design sources and repository
  history, replaces legacy infrastructure, rewrites worksheet references,
  validates, and leaves the result uncommitted.
- `boardwright update status`: compares managed files with the installed
  `.boardwright/state.yaml` payload record.
- `boardwright update plan` and `boardwright update apply`: update untouched
  managed files, three-way merge non-overlapping text customizations, block on
  conflicting or binary changes, migrate missing configuration keys without
  replacing user values, and roll back when validation fails.
- `.boardwright/state.yaml` records schema/template versions, migration origin,
  managed-file hashes, strategies, and managed text bases. KiCad design files,
  project metadata, changelog history, licences, and user assets are user-owned.

Implemented schematic generation support:

- `boardwright generate revision-history`: copies the revision-history schematic
  template to a new file.
- `boardwright generate one-sheet`: writes a minimal one-sheet schematic
  skeleton from the configured project metadata.
- `boardwright generate hierarchy`: writes a small hierarchical project
  skeleton with a child schematic.
- `boardwright generate sheet`: adds a new hierarchical child schematic to an
  existing schematic, and the TUI exposes the same helper through a one-step
  "Generate Sheet" action.

Implemented curated source-package support:

- `boardwright source-package`: creates a curated archive of the repository
  checkout, omitting generated manufacturing/output folders and other obvious
  release noise. The release workflow can include that archive in the release
  package when `release_include_source_archive` is enabled in project config.

Implemented local KiBot runner support:

- `boardwright docker-kibot`: launches the bundled Docker helper script for a
  local KiBot session, using the repo-managed KiBot image selection helpers
  already present in `boardwright_resources/kibot/resources/scripts/`.

Implemented accepted-output CLI support:

- `boardwright accepted`: shows latest accepted main-output workflow evidence,
  including run id, branch, source SHA, expected reviewed `origin/dev` SHA,
  status, and freshness.

Implemented environment-readiness CLI support:

- `boardwright doctor`: checks local Git/repository state, configured branches
  and remotes, workflow dispatch shape, GitHub CLI/auth hints, Textual
  availability, and base project validation. It exits nonzero only for blocking
  errors; warnings are advisory readiness notes.

Implemented scriptable review/testbench support:

- `boardwright review`: shows preview artifact freshness, run evidence,
  expected `origin/dev` SHA, and local reviewed-marker state. With `--fetch`,
  it downloads the fresh preview artifact and marks that exact run/SHA/artifact
  as reviewed.
- `boardwright testbench plan`: prints a live-test command sequence for a
  separate repository.
- `boardwright testbench init`: copies the template into a separate local
  testbench repo, excludes generated/local artifacts, optionally sets
  `project.git_url`, and initializes local `main`/`dev` branches. The GitHub repo slug is derived from `git_url`.
- `boardwright outputs clean`: removes KiBot packaging noise after generation.
  It drops numbered PDF page shards when a combined PDF exists and removes empty
  generated CSV tables for component-count, testpoint, and impedance-style
  outputs. CI workflows run the same cleanup before upload, commit, tag, or
  release packaging.

## TUI

The TUI is a small workflow cockpit, not a full git client or KiBot editor.
It should answer:

1. What state is the project in?
2. What should I do next?
3. What artifacts or release outputs are ready to review?

Primary actions:

```text
Record
Commit
Preview
Review
Folder
README
New Sheet
Accept
Release
Info
Refresh
```

Target main-screen layout:

- Top status strip: one concise line with project id, branch, git state,
  variant, latest semantic release/prerelease tag, compact CI summary, and
  validation summary. CI phases should be named with words (`Preview`,
  `Accept`, `Release`) rather than single-letter abbreviations. Detailed run
  ids, titles, and evidence belong in the inspector or action modals, not in
  the top strip. The strip should scroll horizontally if the terminal is
  narrow instead of truncating important fields. The header/subtitle should
  carry the current project identity plus stage and next action, and a
  lightweight help shortcut should be discoverable from the top chrome.
- Left action rail: grouped by intent rather than shown as one flat button
  pack. On short terminals, the rail should keep readable labels and preserve
  the action column instead of collapsing the whole cockpit into a narrow
  stack. The rail should favor a single readable column of buttons over a
  cramped multi-column layout.
  - Work: Record, Commit.
  - Artifacts: Preview, Review, Folder, README.
  - Schematics: New Sheet.
  - Release: Release.
  - Setup: Info, Refresh.
- Center workflow map: a compact seven-step progress map with one line per
  step. It should show state with simple markers and color, but not repeat long
  explanatory paragraphs.
- Right inspector: a structured readout with `Now`, `Evidence`, and `Release`
  sections. `Now` states the next action and blocker in plain language.
  `Evidence` has separate preview, review, accept, and release rows so mixed
  CI states do not collapse into one noisy sentence. `Release` summarizes
  readiness. Raw workflow evidence belongs in the action modal or review
  screen, not permanently in the main readout.
- Bottom panels: validation and changed files, both scrollable when needed.
  Validation stays compact on the dashboard and expands into a separate drill
  down when the operator wants the full checklist. On very short terminals,
  the TUI keeps the workflow and inspector visible first and lets the lower
  detail panels fall away instead of overflowing the screen.

Button and keybind behavior must be identical. Every visible action and every
keyboard shortcut must pass through the same shared `action_state` gate before
opening a modal or dispatching work. Disabled actions should explain the lock
reason in a notification.

`Release` opens the release checklist once the local dev state is clean
and pushed. The checklist, not the main button, gates the actual
`prepare-release.yaml` dispatch against accepted-main evidence, release inputs,
changelog readiness, and tag availability. This keeps the release path
discoverable without allowing an accidental publish.

Routine plumbing should be automatic, CLI-only, or advanced/fallback:

```text
Validate
Write Revision History
Legal
Raw Git Status
Raw Workflow Dispatch
```

Current implemented TUI behavior:

- status bar shows project id, branch, dirty state, remote ahead/behind,
  variant, latest tag, CI summary, and validation summary
- workflow timeline shows edit, record, commit/push, preview, review, accept,
  and release steps as a compact progress map
- inspector is sectioned into Now, Evidence, and Release instead of showing a
  raw status dump
- the top chrome is a branded title and tagline, while the detailed project
  identity and current stage live in the status strip
- the responsive layout uses a very short terminal mode to protect readable
  actions and the main narrative panels, while keeping the lower detail panels
  as the screen allows
- in very short terminals, validation and changed-file summaries are shortened
  further so the inspector and workflow remain readable before the supporting
  panels
- in very short terminals, the project summary trims secondary metadata such
  as preview defaults and remote counts so the status strip and workflow stay
  readable first
- the changed-files panel includes a small badge legend in normal width so the
  file status colors remain self-explanatory
- in very short terminals, the top status line drops secondary metadata like
  branch and remote counts so the most important state words stay visible
- top chrome shows the project identity, current stage, next action, and a
  lightweight help affordance
- the footer is contextual and mirrors the current screen plus the most useful
  shortcuts, rather than dumping every binding all the time
- action buttons use readable single-line labels so the rail remains readable
  at a glance on narrow terminals
- Record updates `CHANGELOG.md`, writes revision-history variables, validates,
  and suggests a commit message
- Commit requires the configured `dev` branch, requires a changelog entry for
  dirty work, validates, writes revision-history variables, commits, and pushes
  `origin/dev`
- Preview dispatches `dev-preview.yaml` for a selected variant after the
  configured `dev` branch is clean and pushed. It does not run implicitly on
  every push.
- Review polls recent workflow runs and downloads the latest preview artifact
  evidence when `gh` is available. It opens a dedicated review screen showing
  run id, branch, source SHA, expected SHA, artifact name, created time,
  status, freshness, selected variant, and reviewed marker. The default variant
  comes from `variants.preview_default`; the operator can override it for
  manual workflow runs. During fetch, the TUI shows artifact download progress.
  A successful fetch writes a local review marker under `boardwright-preview/`
  for the exact artifact, run id, and SHA.
- Accept dispatches `main-outputs.yaml` only when the selected variant has a
  fresh preview artifact for the latest pushed `origin/dev` SHA and that exact
  artifact has been reviewed locally. The dispatch pins that reviewed source
  SHA and tells CI to push the accepted state to `main`.
- Release opens a release readiness checklist before dispatching
  `prepare-release.yaml`. The release modal collects semantic release version,
  variant, release kind, controlled drawing revision, and a short revision-table
  description. The checklist shows accepted-main evidence, release inputs, the
  controlled revision row, unreleased changelog readiness, local tag
  availability, and dispatch target. Preview is disabled while any checklist
  item is blocking.
- primary action buttons lock/unlock from the shared workflow-state model
- keybindings use the same action gates as the visible buttons
- Info edits project id, name, company, designer, Git URL, GitHub repo, logo
  path, product image path, and the dev/preview/main/release variant defaults
  stored in `.boardwright/project.yaml`. Those defaults live in the Workflow
  section, not a separate variants tab.
- Refresh checks accepted-main evidence when GitHub CLI is available. Release
  is blocked unless accepted main outputs are fresh for the latest
  pushed `origin/dev` source SHA.
- CI polling summarizes all three active CI phases in the top status and
  inspector: preview, accepted-main outputs, and release preparation/publish
  runs. Preview polling infers the latest variant from the workflow run title
  instead of always using `variants.preview_default`.
- The compact CI summary uses human-readable phase names, for example
  `Preview:CHECKED ready | Accept:ready | Release:prepare running`. Color
  priority is failure/error first, then running/queued/stale/review-needed
  states, then ready/success states.
- Validation on the dashboard is intentionally compact. The inline summary
  surfaces blockers first, then a short warning list, while `v` opens the full
  validation detail screen and `boardwright doctor` remains the broad
  readiness check.

The TUI renders from a shared workflow-state model rather than keeping its own
private timeline rules. That model provides:

- current stage
- next action
- human-readable reason
- ordered timeline steps
- primary action enablement and lock reasons

Initial workflow stages:

```text
validation_blocked
needs_changelog
ready_to_commit
needs_push
behind_remote
preview_missing
preview_running
preview_failed
preview_stale
preview_ready
preview_reviewed
accepted_missing
accepted_running
release_ready
editing
```

Important missing TUI behavior:

- first-run metadata editing/onboarding is not implemented
- project-information editing for identity, fabrication metadata, assembly
  notes, and controlled-impedance requirements is not implemented

## README And Assets

Boardwright has two README surfaces:

- The root repository `README.md` describes Boardwright itself: what the
  template/tool is, how to install/use it, the workflow model, legal/provenance
  status, and how to create or adopt projects.
- The generated project README is produced for downstream board projects from
  the KiBot report template below.

The root README must not be overwritten by generated board-project content
during normal template development. CI may generate project README snapshots
for downstream/template-test repos, but the source repository needs a stable
human-authored product README.

The generated project README is produced from:

```text
boardwright_resources/kibot/resources/templates/readme.txt
```

The current template includes project logo, board renders, board revision,
release version, variant, dimensions, generated-output guidance, and legal
notes. Workflow badges are deferred until repository URL metadata is reliable
enough to avoid broken relative links in generated project READMEs.

The target README should also include, where KiBot data makes it practical:

- latest release/package links
- stackup/fabrication summary
- component counts, including SMT/THT if available
- clearer links to generated manufacturing outputs

Visible project media belongs under:

```text
assets/logos/
assets/renders/
assets/3d/
```

`assets/renders/` may be committed to `main` as the accepted README snapshot.
`assets/3d/` is packaged into release artifacts but is not normally committed
as source state.

## Validation Contract

Validation currently checks:

- required `.boardwright/` config files
- required root files: `CHANGELOG.md`, `LICENSE`, `README.md`
- variant values
- supported preview engine
- configured workflow files
- changelog structure and duplicate releases
- revision-history slot settings
- presence of KiCad project/schematic/PCB files
- warns when PCB files have no `Edge.Cuts` outline geometry, because
  `CHECKED`/`RELEASED` CI runs may fail DRC without a real board outline
- presence of the KiBot main config
- configured asset paths
- README template mentions legal files
- known local branding markers in active template/config files

Validation should remain fast and local. CI/runtime output freshness and GitHub
authentication checks belong in status/review actions rather than base project
validation.

## Known Product Gaps

These are the important gaps between the current code and the intended product:

1. Legal/provenance: the first-pass source map, license stack, font
   replacement, and mixed-file SPDX policy are in place. Remaining risk is
   external legal review plus confirming or replacing bundled KiCad color theme
   files.
2. KiCad sheet branding: worksheet path, sheet logo, and legal text are now
   project-configurable. Remaining work is polish around project generation and
   deeper metadata editing.
3. Info depth: the TUI now exposes the project metadata in sectioned
   tabs with lighter helper text; remaining work is only live-use ergonomic
   tuning.
4. TUI full-path polish: the main screen now stays usable on shorter terminals
   without collapsing the action rail, and the Info modal is grouped
   more logically, but the full record -> commit -> preview -> review ->
   accept -> release loop still benefits from repeated live use to tune labels,
   lock reasons, and modal density.
5. README richness: the generated README template is partly refreshed but still
   lacks stackup/component/latest-release sections.
6. Onboarding and generation: new/adopted project setup is better, and the
   basic schematic-generation helpers now exist. Remaining work is deeper
   metadata editing and any future generator polish.
7. GitHub fallback UX can still be refined with direct URLs after repository
   metadata is configured.

## Out Of Scope For The Current Build

Do not prioritize these until the normal workflow is reliable:

- full YAML editor
- full git client
- full GitHub Actions browser
- KiCad file browser
- local KiBot/Docker runner as the primary flow
- multi-board management
- complete metadata editor
