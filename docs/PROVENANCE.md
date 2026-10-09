<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# Boardwright Provenance

This file is the public source-of-truth for where Boardwright came from, which
parts are inherited, which parts are Boardwright-authored, and which bundled
assets still need licensing confirmation.

It is an engineering inventory, not legal advice.

## Baseline

Boardwright derives from Nguyen Vincent's KiCad/KiBot template work,
`KDT_Hierarchical_KiBot`, published under the MIT License.

The inherited MIT license text is preserved in:

```text
LICENSES/Nguyen-MIT.txt
```

Important local history points:

```text
59e7267  2025-01-19  Vincent Nguyen initial template import
079a4ec  2025-12-14  latest Nguyen-authored baseline / merge-base
c139657  2026-02-18  Reemuson Ryan Dynamics template fork
e41bf10  2026-04-25  Reemuson Boardwright conversion
```

The archived local audit notes contain the detailed git-history comparison.
This public file records the resulting classification at repository level.

## Licensing Model

The root `LICENSE` applies to Boardwright-specific work:

```text
Apache-2.0 with Commons Clause
Boardwright Hardware Output Exception
```

Nguyen-derived material keeps Nguyen MIT attribution. Boardwright-specific
changes and additions use the root Boardwright license unless a file states a
different license.

Using Boardwright to make a hardware project does not force the Boardwright
tooling license onto that downstream hardware design, project files,
manufacturing outputs, release artifacts, or project-specific documentation,
except where Boardwright template material or third-party notices are copied
into that downstream project.

## Classification Rules

Use these rules when adding SPDX headers or reviewing files:

- Unchanged or mostly renamed Nguyen files keep Nguyen MIT attribution.
- Files that are still structurally Nguyen-derived, even after Boardwright
  edits, are treated as derivative and should preserve Nguyen MIT attribution.
- Boardwright-authored Python tooling, workflows, tests, metadata, and docs use
  `LicenseRef-Boardwright-Source-Available`.
- Mixed files descended from Nguyen's work keep the Nguyen MIT SPDX header and
  add a Boardwright modification line. Use this even when the current file is
  mostly Boardwright work, if git history shows the file descends from Nguyen's
  template.
- Bundled third-party assets need their own source/license records.
- Generated downstream hardware outputs are not Boardwright source code.

## Inherited Or Derivative Areas

Treat these areas as Nguyen-inherited or Nguyen-derived unless a file-level
review says otherwise:

```text
Templates/*.kicad_wks
boardwright.kicad_pro
boardwright.kicad_sch
boardwright.kicad_pcb
boardwright.kicad_dru
boardwright_resources/kibot/yaml/
boardwright_resources/kibot/resources/templates/
boardwright_resources/kibot/resources/scripts/legacy or adapted scripts
boardwright_resources/kibot/resources/colors/
scripts/kibot_launch.sh
```

These areas include the KiCad/KiBot template structure, output groups, layer
conventions, worksheet layout, report-template patterns, and manufacturing
document conventions inherited from `KDT_Hierarchical_KiBot`.

Renamed files are still inherited when the file content came from Nguyen's
template. A path rename from `KDT_*` to `Boardwright_*` does not by itself make
the file Boardwright-original.

## Boardwright-Authored Or Heavily Reworked Areas

Treat these areas as Boardwright-authored unless a file-level review finds
substantial inherited content:

```text
src/boardwright/
tests/
.boardwright/*.yaml
.github/workflows/dev-preview.yaml
.github/workflows/main-outputs.yaml
.github/workflows/prepare-release.yaml
.github/workflows/release.yaml
docs/SPEC.md
docs/TODO.md
docs/ROADMAP.md
docs/TESTBENCH.md
docs/PROVENANCE.md
README.md
CONTRIBUTING.md
```

These areas implement the Boardwright CLI/TUI, workflow-state model, GitHub
Actions promotion/release system, project metadata model, testbench flow,
documentation model, and public repository policy.

## Mixed Or Review-Required Areas

These areas need careful file-level review because they combine inherited
template material with Boardwright changes:

```text
boardwright_resources/kibot/yaml/
boardwright_resources/kibot/resources/templates/
boardwright_resources/kibot/resources/scripts/
Templates/
boardwright.kicad_*
scripts/
```

Default policy for mixed files: keep inherited attribution unless the file has
been fully rewritten and no meaningful inherited expression remains. The
standard header for Nguyen-derived modified files is:

```text
SPDX-License-Identifier: MIT
Original template material copyright Nguyen Vincent.
Modified for Boardwright by Ryan Hicks.
```

## Bundled Third-Party Assets

### Fonts

Current bundled fonts:

```text
boardwright_resources/kibot/resources/fonts/Arimo-*.ttf
boardwright_resources/kibot/resources/fonts/Tinos-*.ttf
```

Arimo and Tinos are Steve Matteson font families distributed under the SIL Open
Font License. The OFL text is included in `LICENSES/OFL-1.1.txt`. They replace
the earlier Arial/Times New Roman rendering dependency so CI-generated PDFs can
keep stable typography without bundling proprietary system fonts.

The PowerShell installer installs the bundled fonts for the current user by
default so local KiCad rendering matches CI. Users can opt out with `-NoFonts`.

### Color Themes

Current bundled color themes:

```text
boardwright_resources/kibot/resources/colors/Altium_Theme.json
boardwright_resources/kibot/resources/colors/KiCad_Theme.json
```

These need source/license confirmation or replacement with Boardwright-authored
theme files.

### Logos And Branding

Current Boardwright logo assets live under:

```text
assets/logos/
meta/
```

Boardwright logo/wordmark assets are project branding. Affinity Designer and
Spline source files are ignored locally and are not intended to be committed to
the public template repository.

## KiCad Worksheets And Title Blocks

The worksheet files were inherited from the original `KDT_Template...` files
and renamed to `Boardwright_Template...`.

Current policy:

- Worksheet selection comes from the KiCad project file.
- Sheet logo artwork is configured through Boardwright Project Info and
  embedded into all worksheet templates by tooling.
- Sheet legal text is configured through Boardwright project metadata.
- The default public template should stay Boardwright-neutral.
- Downstream projects can replace branding and legal notice text without
  manually editing every worksheet.

Known follow-up:

- keep checking worksheet files for residual local-business branding
- add validation warnings for known-local branding strings
- keep inherited attribution where worksheet layout remains Nguyen-derived

## Generated Outputs

Full KiBot output trees are CI products, not normal source-branch content:

```text
Manufacturing/
Schematic/
Reports/
HTML/
KiRI/
Testing/
```

Preview outputs may be published to the disposable `preview` branch. Preview,
accepted-output, and release outputs are uploaded as artifacts. Accepted and
release workflows may commit lightweight snapshot files such as generated
README/renders, depending on project configuration.

Generated downstream hardware outputs are governed by the downstream project,
subject to copied template material and preserved third-party notices.

## Files That Define The Licensing Record

```text
LICENSE
LICENSES/README.md
LICENSES/Apache-2.0.txt
LICENSES/Commons-Clause.txt
LICENSES/Nguyen-MIT.txt
NOTICE.md
THIRD_PARTY_NOTICES.md
CONTRIBUTING.md
.boardwright/legal.yaml
docs/PROVENANCE.md
```

Keep these files aligned whenever licensing, attribution, bundled assets, or
downstream output policy changes.

## Open Review Items

- Confirm or replace bundled color theme files.
- Finish applying the mixed-file SPDX/header policy for Nguyen/Boardwright
  derivative files.
- Add validation for residual local/business branding in worksheets and config.
- Get the implemented license stack reviewed by qualified legal counsel.
