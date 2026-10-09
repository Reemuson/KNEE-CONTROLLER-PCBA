<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# Boardwright Roadmap

This roadmap tracks the product sequence. `TODO.md` is the tactical work queue.
`SPEC.md` defines the desired behavior and current product contract.

## Current Position

Boardwright has a working local tooling foundation, a usable TUI workflow
cockpit, and split GitHub Actions workflows for preview, accepted outputs,
release preparation, and tag publishing. A full live run through preview,
review, accept to main, and release has succeeded. The critical path is now
productization: external legal review, worksheet consolidation, richer project
metadata editing, and generated README/output polish.

The current branch is expected to be `main` for accepted template work. Normal
Boardwright project usage still expects design changes on `dev`.

## Critical Path

Do these before treating Boardwright as a clean public/template release:

1. Legal and provenance review: maintain the implemented source-available
   Boardwright license stack, identify Nguyen-derived files, confirm bundled
   third-party assets/fonts/scripts, keep notices accurate, and obtain qualified
   legal review.
2. Worksheet consolidation: retain configurable identity and legal text while
   reducing transitional worksheet variants after combined-PDF behavior is
   stable.
3. Project Info 2.0: expand the existing project, template, sheet, variant, and
   asset sections to cover fabrication metadata, assembly notes, controlled
   impedance, and output/README policy.
4. Generated README polish: make project READMEs useful hardware front pages
   without broken badges or stale placeholders.
5. Project generation polish: refine the implemented revision-history,
   one-sheet, hierarchy, and TUI-assisted sheet-generation helpers.

## Milestone 1: Local Project Control

Status: implemented.

Delivered:

- `.boardwright/` config
- CLI package and console entry point
- validation
- changelog recording
- revision-history variable generation
- legal/notice generation
- optional Textual TUI with console fallback
- safe git status, commit, and push helpers
- user/global and project-local install helper
- developer/test extra via `pip install -e ".[dev]"`
- unit tests for core local behavior

## Milestone 2: Preview Loop

Status: implemented and live-tested.

Delivered:

- `dev-preview.yaml`
- manual preview dispatch path
- dedicated review/preview dispatch path, instead of previewing every push
- variant-aware preview planning/dispatch
- disposable preview branch publishing
- preview artifact upload
- TUI/CLI preview status and artifact fetch helpers
- expected output path summary, including `assets/renders` and `assets/3d`
- preview run model with source branch, source SHA, run id, creation time,
  status, conclusion, and artifact name
- freshness comparison against latest pushed `origin/dev`
- local review marker for the exact downloaded run/SHA/artifact

Remaining:

- keep tuning review/download UX after real project use
- add artifact folder/README open shortcuts after downloads

## Milestone 3: Accepted Main Outputs

Status: implemented and live-tested.

Delivered:

- `main-outputs.yaml`
- `boardwright promote`
- TUI `Accept to Main`
- variant selection
- optional commit of generated README/render snapshot assets
- policy that wholesale generated output folders are not committed to `main`
- freshness/review gate before TUI dispatch

Remaining:

- keep accepted-output evidence concise in the TUI while preserving enough
  detail for troubleshooting

## Milestone 4: CI-Owned Release Tagging

Status: implemented and live-tested for prerelease/full release paths.

Delivered:

- `prepare-release.yaml`
- `boardwright release --dispatch`
- release kind support: draft, prerelease, release
- release variant support
- changelog promotion in CI
- `.boardwright/release.env`
- accepted release-state commit to `main`
- CI-created tag
- tag workflow that publishes artifacts without branch mutation
- release notes with side-by-side board renders when available

Remaining:

- live retest draft release
- measure whether CI runtime needs further optimization

## Milestone 5: Project README, Legal Review, And Usable Dashboard

Status: active.

Delivered:

- README template has Boardwright-specific structure
- revision, variant, dimensions
- side-by-side board renders
- legal notes
- TUI status bar, grouped action rail, compact workflow map, sectioned
  Now/Evidence/Release inspector, validation panel, and changed-file panel
- shared TUI workflow-state model for timeline, next action, and action locks
- shared action gates for visible buttons and keyboard shortcuts
- dedicated Review Artifacts screen
- Create Release readiness checklist before dispatch
- `boardwright doctor` readiness checks for Git, remotes, workflow dispatch
  shape, GitHub CLI/auth hints, Textual, and validation
- `boardwright review` for scriptable preview artifact state/fetch
- `boardwright testbench plan/init` plus `docs/TESTBENCH.md` for isolated live
  CI testing in a separate repository
- compact CI status with readable phase names: Preview, Accept, Release
- latest semantic release/prerelease tag display in the TUI status strip
- root README replaced with a Boardwright-native product/template README
- initial provenance inventory in `docs/PROVENANCE.md`
- detailed Nguyen git-history provenance audit captured in local archived notes
- licensing options/recommendation captured in local archived notes
- detailed three-layer reconciliation captured in local archived notes
- inherited Nguyen MIT text moved to `LICENSES/Nguyen-MIT.txt`
- root `LICENSE` replaced with the Boardwright source-available license/index:
  Apache-2.0 with Commons Clause, plus the Boardwright Hardware Output
  Exception
- `LICENSES/Apache-2.0.txt` and `LICENSES/Commons-Clause.txt` added
- `LICENSES/OFL-1.1.txt` added for bundled Arimo/Tinos fonts
- `CONTRIBUTING.md` added
- `.boardwright/legal.yaml` restructured as downstream hardware-project
  defaults instead of repository licensing
- `NOTICE.md` and `THIRD_PARTY_NOTICES.md` updated to reflect the implemented
  license split
- first-pass file-level provenance/SPDX policy completed for Boardwright,
  Nguyen-derived, and mixed files
- worksheet/title-block branding made project-configurable, with validation for
  known local branding markers
- controlled-impedance table output now comes from project config when enabled,
  with an explicit no-traces fallback when projects do not opt in
- generated README legal references confirmed for `LICENSE`, `NOTICE.md`, and
  `THIRD_PARTY_NOTICES.md`
- generated README now includes optional CI status badges when repository URL
  metadata is trustworthy enough to avoid broken links
- bundled KiCad color theme references now point at the repo-managed KiCad_Theme
  resources instead of local ad hoc files
- next-action labels now use more explicit action wording for validation,
  changelog, preview, and editing states

Remaining:

- keep `SPEC.md`, `TODO.md`, and this roadmap as the source of truth after live
  workflow changes
- get the implemented license stack reviewed by qualified legal counsel
- table the full worksheet consolidation until the current combined-PDF work is
  stable, then reduce each project/brand to one active worksheet template. CME
  can serve as the branded example; Boardwright-native templates should be
  refreshed into standardized AS 1100, ISO, and ANSI-style families.
- add latest release/package links to generated README
- add stackup/fabrication summary if KiBot variables are available
- add component count summary if KiBot output data supports it

Success criteria:

- root `README.md` clearly describes Boardwright itself
- legal files make inherited/original/third-party provenance clear enough for a
  public template repository
- default KiCad sheets no longer require manually editing every title block to
  remove one business's branding
- generated `README.md` is useful as the front page of a hardware repo
- TUI shows enough state that normal users rarely need to open GitHub Actions
- Accept to Main is based on fresh reviewed preview evidence
- generated README includes release, workflow, fabrication, and component snapshots

## Milestone 6: Project Metadata Editing And Onboarding

Status: planned, with identity/variant editing, adopt support, and schematic
generation helpers started.

Delivered:

- `boardwright adopt` for existing KiCad projects
- `boardwright generate` helpers for revision-history sheets, one-sheet
  schematics, hierarchical skeletons, and TUI-driven sheet insertion
- named downstream legal profiles for public-hardware, compatibility-friendly,
  and internal-prototype project defaults
- curated source-package support for release archives when requested by the
  project config
- local KiBot/Docker runner surfaced as a helper command after the CI-first
  flow proved stable

Scope:

- first-run setup when `.boardwright/` is missing or incomplete
- edit/view project metadata from the TUI
- set GitHub repository, branch names, variants, logo/assets paths, and legal
  metadata without hand-editing YAML
- configure KiCad title-block/worksheet identity values without manually
  editing each sheet
- select from Boardwright-native worksheet standards such as AS 1100, ISO, and
  ANSI once the single-template-per-project model replaces permanent `_PCB`
  variants
- generate extra revision-history worksheets/schematic sheets when the default
  fixed set is not enough
- create new one-sheet or hierarchical project structures from the TUI
- edit fabrication metadata, assembly notes, testpoint policy, and controlled
  impedance data without hand-editing KiBot templates
- detect missing GitHub CLI authentication and show exact fallback commands

Success criteria:

- a new board repo can be initialized and configured mostly through Boardwright
- users can keep working in KiCad and Boardwright without memorizing config
  file paths

## Later

- first-class local Docker output generation matching the CI pipeline
- multi-board or assembly variants once KiCad/KiBot variant support is stable
- richer artifact browser if the small cockpit proves insufficient

## Planned Local Docker Output Engine

Boardwright should grow a first-class local Docker output engine alongside the
current GitHub Actions flow. The target user experience is a non-interactive
local command such as `boardwright preview --local` or
`boardwright outputs generate --engine docker --variant PRELIMINARY` that
mirrors the CI pipeline without requiring the user to remember KiBot groups or
helper scripts.

The local engine should:

- detect Docker and report a clear doctor/setup action when it is missing or
  not running
- use the KiCad 9 KiBot image, currently
  `ghcr.io/inti-cmnb/kicad9_auto_full:dev`
- mount the project directory read/write and keep generated files project-local
- install bundled fonts inside the container before generation
- run `prepare_pcb_tables.py`, KiBot `table_sources`, `prune_pdf_pages.py`, the
  selected KiBot output group, and `clean_generated_outputs.py` in the same
  order as CI
- write reviewable preview files to `boardwright-preview/` for local review
  workflows
- support a project setting such as `outputs.preview_engine: docker` while
  keeping GitHub Actions available for shared/release workflows

Installing Docker Desktop itself should remain guided rather than silent:
Windows/macOS installs may need admin approval, WSL2 setup, service startup,
license prompts, or reboot. Boardwright can offer `boardwright local setup` to
validate Docker and pull the image, but it should not make hidden system-level
changes.
