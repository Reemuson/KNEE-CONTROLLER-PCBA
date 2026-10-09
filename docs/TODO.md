<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# Boardwright TODO

This is the actionable tracker. Product rules live in `SPEC.md`; sequencing
lives in `ROADMAP.md`.

## Recently Completed: Productization Foundation

This section records the completed foundation for a clean template product.
Current open work starts in the next section.

- [x] Add plan/apply migration for Nguyen hierarchical-template descendants,
      preserving KiCad design sources, Git/release history, changelog, and
      project licensing while replacing recognized legacy infrastructure.
- [x] Add manifest-backed Boardwright project updates with configuration schema
      additions, three-way text merges, conflict blocking, validation, and
      rollback.
- [x] Replace compact CI abbreviations with readable phase names in the TUI
      status strip and evidence panel.
- [x] Make the dashboard tag display use the latest semantic release tag, with
      prerelease fallback when no stable release tags exist.
- [x] Document the latest-tag rule in `SPEC.md`.
- [x] Add legal/provenance and configurable KiCad sheet/title-block requirements
      to `SPEC.md`.
- [x] Do one more TUI happy-path pass after the latest status-strip changes.
- [x] Replace root `README.md` with a Boardwright-native README.
- [x] Complete first-pass file-level legal/provenance review for Nguyen-derived
      files, Boardwright-original code/docs, bundled fonts/assets, helper
      scripts, and generated-output notices.
- [x] Replace hardcoded local business title-block/worksheet legal text with
      Boardwright-neutral defaults and project-configured variables.
- [x] Add project config fields for sheet/title-block legal notice, logo,
      embedded sheet image, and organization metadata.
- [x] Collapse worksheet branding to one sheet image field; keep README logo
      and project images separate.
- [x] Re-embed the configured sheet image into all worksheet templates when
      Project Info is saved from the TUI.
- [x] Replace embedded worksheet bitmap image data from project-configured
      `template.sheet_image` paths with `boardwright worksheet-logo`.
- [x] Capture known live CI/release findings in this tracker.

## Next: Worksheets, Legal Review, And Template Polish

- [ ] Defer full worksheet consolidation until combined PDF output stabilizes:
      keep the normal GIT worksheet as the intended single Boardwright template,
      keep the CME worksheet as the worked branded example, and retire permanent
      `_PCB` templates once standalone assembly/fabrication numbering no longer
      needs them.
- [ ] Design Boardwright-native standardized worksheet families after the
      consolidation decision: AS 1100, ISO, and ANSI-style layouts, all driven
      by project config/text variables rather than hardcoded business fields.
- [ ] Keep the simplified drawing identity model aligned: project name, PCBA
      name, PCB name, board revision/spin, drawing revision, and configurable
      drawing revision scheme. Keep Git release/package version separate.
- [ ] Keep drawn-by/date as generated document metadata and checked/approved as
      post-generation signature areas.
- [ ] Extend revision-history variables/sheets to support controlled-document
      rows with revision, date, description, and drawn-by fields.
- [x] Audit root README draft notes and decide what moves into
      the real root README.
- [x] Add a clear section explaining the difference between the Boardwright
      template README and generated board-project READMEs.
- [x] Review `LICENSE`, `NOTICE.md`, and `THIRD_PARTY_NOTICES.md` for current
      accuracy.
- [x] Create a provenance inventory for inherited Nguyen files/patterns,
      Boardwright original work, bundled fonts, logos/assets, and scripts.
- [x] Rewrite public provenance as a source-of-truth engineering inventory
      rather than narrative legal notes.
- [x] Add git-history-based Nguyen provenance audit in archived local notes.
- [x] Add a licensing review covering Nguyen MIT inheritance, Ryan Hicks
      ownership goals, source-available options, and downstream hardware output
      carve-out.
- [x] Capture detailed three-layer licensing reconciliation in archived local
      notes.
- [x] Decide Ryan Hicks licensing policy: Apache-2.0 with Commons Clause,
      plus the Boardwright Hardware Output Exception.
- [x] Move inherited Nguyen MIT text into `LICENSES/Nguyen-MIT.txt`.
- [x] Replace root `LICENSE` with the selected Boardwright/Ryan Hicks
      source-available license/index.
- [x] Add `LICENSES/Apache-2.0.txt` and `LICENSES/Commons-Clause.txt`.
- [x] Drop standalone trademark policy; keep branding restrictions in
      `LICENSE` and `NOTICE.md` because there is no registered trademark.
- [x] Add `CONTRIBUTING.md` with inbound-equals-outbound contribution terms.
- [x] Restructure `.boardwright/legal.yaml` so it clearly describes downstream
      hardware-project defaults rather than the Boardwright repository license.
- [ ] Get the implemented license stack reviewed by qualified legal counsel.
- [x] Add SPDX/file headers to safe Boardwright-authored and inherited
      Nguyen-unchanged text/code files.
- [x] Decide SPDX/header policy for mixed Nguyen/Boardwright derivative files:
      keep Nguyen MIT SPDX attribution and add a Boardwright modification line.
- [x] Use the archived Nguyen provenance audit as the source map for SPDX/header
      classification.
- [x] Decide default public-template legal/title-block wording.
- [x] Make KiCad worksheet/title-block legal text configurable without editing
      every sheet manually; worksheet selection now follows the KiCad project
      file.
- [x] Make worksheet embedded logo artwork configurable without editing every
      worksheet manually.
- [x] Add validation warnings for known-local hardcoded branding once neutral
      defaults are in place.
- [x] Confirm or replace bundled KiCad color theme files.

## Done: Fresh Preview Acceptance

Goal: make `Review Artifacts` and `Accept to Main` trustworthy.

- [x] Add a preview run/artifact model in `src/boardwright/preview.py`.
- [x] Query recent preview runs with enough metadata to know source branch,
      head SHA, status, conclusion, run id, and creation time.
- [x] Add a git helper for the latest pushed `origin/dev` SHA.
- [x] Mark preview state as `missing`, `running`, `failed`, `stale`, or
      `ready`.
- [x] Teach `fetch_latest_preview_artifact()` to require a successful fresh run
      for the requested variant.
- [x] Update TUI Review Artifacts to show branch, SHA, artifact name, creation
      time, and freshness.
- [x] Write a local review marker after fetching a fresh preview artifact.
- [x] Gate `Accept to Main` when the latest preview is
      missing, failed, stale, or unreviewed.
- [x] Add tests for ready/stale/failed/running preview-state decisions.
- [x] Add live GitHub CLI/manual fallback copy for missing `gh` or auth failure.

## Done: TUI Workflow State

Goal: make the TUI render from shared project state instead of local ad hoc
rules.

- [x] Add shared workflow-state model with stage, next action, reason, timeline
      steps, and primary action enablement.
- [x] Wire TUI timeline and Next Action panel to the shared model.
- [x] Lock/unlock primary TUI actions from the shared model.
- [x] Expose current stage and next action in `boardwright status`.
- [x] Add tests for key stages: validation blocked, needs changelog, ready to
      commit, needs push, stale preview, fresh reviewed preview, release ready.

## Near: Review Artifacts Screen

- [x] Add dedicated TUI screen/modal for preview artifact evidence.
- [x] Show run id, branch, source SHA, expected SHA, variant, artifact name,
      created time, state, and reviewed marker.
- [x] Provide fetch/review action from the screen.
- [x] Show manual GitHub fallback instructions in the screen.
- [x] Add richer artifact open/browse shortcuts after download.

## Done: Accepted Main And Release Readiness

- [x] Track/report latest accepted main-output workflow state.
- [x] Show accepted main-output source SHA where available.
- [x] Poll and summarize preview, accepted-main, and release CI status in the
      TUI.
- [x] Add CLI `accepted` command for accepted main-output state.
- [x] Block Create Release unless accepted main outputs are fresh for
      the latest pushed `origin/dev` source SHA.
- [x] Add Create Release checklist before dispatch.
- [x] Add CLI `review` command for preview artifact state.
- [x] Add CLI `doctor` command for environment/integration checks.
- [x] Add live-testbench plan/init command and `docs/TESTBENCH.md`.

## Near: CI Retest And Output Polish

Goal: prove workflows still work after moving visible generated media under
`assets/`.

- [x] Record live-test finding: standalone KiBot `notes` target is unsafe for
      this template; notes should be generated through the normal output group.
- [x] Record live-test finding: use `PRELIMINARY` for template harness testing
      because the template PCB intentionally lacks a fabrication-ready outline.
- [x] Clean generated packages after KiBot so preview/release artifacts do not
      include numbered PDF page shards or empty generated CSV tables.
- [x] Stop generating the placeholder impedance CSV by default until there is a
      reliable project data source for controlled-impedance traces.
- [x] Make TUI preview artifact fetch non-blocking and simplify the review
      evidence display.
- [x] Remove global `include_table` preflight after live CI proved it runs
      before the CSV reports it needs.
- [x] Restore output-level `pcb_print.include_table` for movable drill,
      and testpoint placeholders.
- [x] Replace assembly component-count table with a non-recursive source; KiBot
      `report`-based component-count output recurses when used by
      `pcb_print.include_table` in the same run.
- [x] Prune empty top/bottom testpoint PDF pages after side-specific testpoint
      CSVs are generated.
- [x] Restore full default fabrication and assembly notes for PDF text-variable
      fallback.
- [x] Replace the impedance table body with "No impedance controlled traces"
      when no controlled-impedance entries are configured.
- [x] Add a controlled-impedance data model and restore impedance table output
      when projects explicitly opt in.
- [x] Replace Arial/Times New Roman CI rendering dependency with bundled
      Arimo/Tinos OFL fonts.
- [x] Add `LICENSES/OFL-1.1.txt` for bundled Arimo/Tinos fonts.
- [x] Install bundled Arimo/Tinos fonts from the PowerShell installer for
      local KiCad rendering, with `-NoFonts` opt-out.
- [x] Decide how Boardwright should model/edit fabrication notes,
      assembly notes, testpoint policy, and controlled-impedance requirements
      from the TUI.
- [x] Add a TUI project-information editor for project name, company, author,
      GitHub repository, assets, and variant defaults.
- [x] Extend the TUI project-information editor to fabrication notes, assembly
      notes, and other project-specific manufacturing metadata.
- [x] Review stackup legend layer colors against the original template.
- [x] Preview workflow uses `assets/renders` and `assets/3d` correctly.
- [x] Preview artifact includes `README.md`, `assets/`, and expected output
      folders.
- [x] Preview branch publishes only disposable generated review content.
- [x] Main-output workflow builds from the reviewed source SHA, verifies that
      SHA, and pushes the accepted source plus `README.md` and
      `assets/renders/*.png` to `main` when `commit_outputs` is true.
- [x] Main-output workflow still pushes the reviewed source merge when the
      README/render snapshot is unchanged.
- [x] Prepare-release can create a release section with a generated no-change
      note when `CHANGELOG.md` has no unreleased entries.
- [x] Prepare-release workflow commits `CHANGELOG.md`,
      `.boardwright/revision_history_variables.env`, `.boardwright/release.env`,
      `README.md`, and `assets/renders/*.png`.
- [x] Release workflow packages `assets/` and attaches board render PNGs to the
      GitHub Release.
- [x] Record any live CI findings back into this tracker.

## Next: Generated README

Goal: make the generated README a useful hardware project front page.

- [x] Add Boardwright-specific README structure.
- [x] Keep the generated project README separate from the root product README.
- [x] Add CI status badges only when repository URL metadata is reliable and
      generated README links will not be broken.
- [x] Keep `${RELEASE_VERSION}` as package metadata and add `${BOARD_REVISION}` for
      A/B/C board spins.
- [ ] Keep controlled drawing revision separate from semantic release/package version
      in title blocks, generated README, release metadata, and revision-history
      generation.
- [x] Add board dimensions.
- [x] Keep board images side by side in README and release markdown.
- [x] Add latest release/package links.
- [x] Add brief stackup/fabrication summary if KiBot exposes reliable variables.
- [x] Add component count summary if KiBot output data supports it.
- [x] Remove or reword placeholder text that will look stale in real projects.
- [x] Confirm generated README still mentions `LICENSE`, `NOTICE.md`, and
      `THIRD_PARTY_NOTICES.md`.

## Near: CLI And Packaging Polish

- [x] Add `src/boardwright/__main__.py` so `python -m boardwright` works.
- [x] Update `boardwright release --prepare` output so it no longer suggests
      the old local tag/push sequence as the primary release path.
- [x] Decide whether to add a dev/test optional dependency group.
- [x] Make bare test instructions explicit in contributor docs:
      `python -m unittest discover -s tests -v`.
- [x] Add/refresh root README installation and contributor instructions.

## Near: TUI Polish

- [x] Show exact manual fallback commands when GitHub CLI is unavailable.
- [x] Add direct GitHub Actions URLs after repository metadata is configured.
- [x] Make Generate Preview a direct TUI action instead of hiding dispatch in
      CLI-only/manual fallback flows.
- [x] Rebalance primary/secondary action layout now that Generate Preview and
      Project Info are first-class TUI actions.
- [x] Compact the main workflow map so long per-step explanations live in the
      inspector or modal screens instead.
- [x] Add a sectioned Now/Evidence/Release inspector instead of a raw status
      dump.
- [x] Make the TUI adapt to shorter terminals and turn Project Info into
      cleaner labeled sections with lighter helper text.
- [x] Make TUI keybindings use the same action gates as disabled/enabled
      buttons.
- [x] Tune next-action labels after more full-path live use.
- [x] Verify the TUI can drive the full happy path after CI retest.

## Verification Targets

- [x] Local validation passes.
- [x] Python unittest suite passes.
- [x] Dummy repo can generate preview outputs.
- [x] Dummy repo can publish a tag release.
- [x] Revision history populates on generated schematic.
- [x] Revision variable populates on generated schematic.
- [x] Cover ToC includes nested sheets.
- [x] Prepare-release workflow can create a prerelease tag from `main`.
- [x] Prepare-release workflow can create a draft tag from `main`.
- [x] Prepare-release workflow can create a full release tag from `main`.
- [x] TUI can drive record -> commit/push -> review -> accept -> release.
- [ ] Measure CI time after switching caches to `actions/cache@v4`; decide
      whether accepted outputs need a later artifact-promotion fast path.

## Done

- [x] Split planning into `SPEC.md`, `ROADMAP.md`, and `TODO.md`.
- [x] Add `.boardwright/` project config.
- [x] Scaffold Python package and CLI.
- [x] Add `boardwright init`, `status`, `change`, `validate`, `legal`,
      `revision-history`, `preview`, `promote`, and `release`.
- [x] Add changelog parser/writer and release promotion.
- [x] Add legal/notice generation.
- [x] Add README template validation.
- [x] Add optional Textual TUI with console fallback.
- [x] Make plain `boardwright` open the TUI.
- [x] Add user/global and project-local install helper for the `boardwright`
      command.
- [x] Add TUI changelog-entry form.
- [x] Add safe git status and dry-run commit helpers.
- [x] Add GitHub Actions preview workflow.
- [x] Add GitHub Actions main-output workflow.
- [x] Add prepare-release workflow.
- [x] Add tag publish workflow.
- [x] Add shared action layer used by CLI and TUI.
- [x] Commit `.boardwright/release.env` during release preparation.
- [x] Make tag workflow read release metadata for variant and release kind.
- [x] Let Boardwright dispatch CI-owned tag creation.
- [x] Add TUI commit and push controls for the normal dev loop.
- [x] Add workflow status polling where GitHub CLI is available.
- [x] Add preview artifact download/fetch helper.
- [x] Consolidate visible project media under `assets/`.
- [x] Make schematic ToC recurse through nested KiCad sheets.
- [x] Add KiBot revision-history variables with newest release first.
- [x] Populate `${RELEASE_VERSION}` from release metadata or git tags during release builds.
- [x] Attach generated README and board images to GitHub Releases.

## Later

- [x] Add `boardwright adopt` for existing projects.
- [x] Add worksheet/schematic generation tools:
      generate extra revision-history sheets, create one-sheet projects, create
      hierarchical-sheet project skeletons, and add new hierarchical schematic
      sheets from the TUI.
- [x] Add a sheet-title sync/check tool:
      read KiCad hierarchical `Sheetname` values, update local
      `SHEET_NAME_1..40` placeholder text variables for interactive editing,
      and warn when visible navigation labels drift from actual sheet names.
- [x] Add richer legal/licence profiles after the initial provenance pass.
- [x] Add curated source package support if needed.
- [x] Add local KiBot/Docker runner support after CI-first flow is solid.
- [ ] Revisit multi-board or assembly variants after KiCad/KiBot variant support
      settles.
