<p align="center">
  <img src="assets/logos/logo-block-colour.png" alt="Boardwright" width="520">
</p>

# Boardwright

Boardwright is a KiCad and KiBot project template with a command-line interface and a text user interface.

It provides a controlled workflow for design review, manufacturing outputs, and releases. GitHub Actions generates the project outputs.

Boardwright does not replace KiCad, KiBot, Git, or GitHub Actions. It defines how these tools pass project state between each workflow stage.

```text
edit -> record changes -> commit and push -> generate preview
     -> review outputs -> accept to main -> create release
```

## Current Status

Boardwright supports these functions:

- Project status, validation, and local environment checks.
- Changelog entries and controlled drawing revision history.
- Preview generation and output review.
- Promotion of reviewed source to `main`.
- Release preparation and publication.
- Project metadata, worksheet, legal notice, and variant settings.
- Schematic and hierarchical sheet generation.
- Migration from the Nguyen hierarchical template.
- Version-aware updates for Boardwright-managed files.

The project still requires work in these areas:

- External review of the licence and provenance model.
- Worksheet consolidation.
- More Project Info fields.
- More detailed generated project READMEs.

See [docs/ROADMAP.md](docs/ROADMAP.md) for planned work.

## Repository Contents

| Path | Content |
| --- | --- |
| `.boardwright/` | Project metadata and managed-file state. |
| `.github/workflows/` | Preview, accepted-output, and release workflows. |
| `assets/` | Project logos and generated image locations. |
| `boardwright_resources/` | KiBot configuration, scripts, fonts, and report templates. |
| `docs/` | Product contracts, references, plans, and test procedures. |
| `scripts/` | Installation and local helper scripts. |
| `src/boardwright/` | The Boardwright Python package. |
| `Templates/` | KiCad worksheet templates. |
| `tests/` | Python regression tests. |

CI generates `Manufacturing/`, `Schematic/`, `Reports/`, `HTML/`, `KiRI/`, and `Testing/`. Do not store these directories on normal source branches.

## Install Boardwright

From the repository root, run:

```powershell
.\scripts\install_boardwright.ps1
boardwright
```

The installer installs the bundled Arimo and Tinos fonts for the current user. Restart KiCad after the font installation.

Use `-NoFonts` if you do not want the installer to install fonts:

```powershell
.\scripts\install_boardwright.ps1 -NoFonts
```

For a project-local installation, run:

```powershell
.\scripts\install_boardwright.ps1 -Scope Project
.\boardwright.ps1
```

This installation uses the Boardwright version stored in the project.

To make the global command prefer a project-local installation, run:

```powershell
.\scripts\install_boardwright.ps1 -Scope Project -InstallProfileCommand
```

For Boardwright development, install the development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

The `boardwright` command starts the text user interface. Without Textual, the command shows a console status view and an installation hint.

## Normal Project Workflow

1. Make design changes on the `dev` branch.

2. Start Boardwright:

   ```powershell
   boardwright
   ```

3. Record the project change.

4. Commit and push the `dev` branch.

5. Generate a preview for the required variant.

6. Download and review the preview output.

7. Accept the reviewed source commit to `main`.

8. Create a draft, prerelease, or release.

The text user interface provides these main actions:

- Record Changes
- Commit and Push
- Generate Preview
- Review Outputs
- Accept to Main
- Create Release
- Project Info
- Refresh

Refresh synchronises project text variables before it updates the dashboard. Close KiCad first to prevent it from overwriting external project-file changes.

## Migrate a Nguyen Project

Use this workflow only for descendants of Nguyen Vincent's hierarchical KiCad and KiBot template.

Migration keeps these items:

- KiCad source filenames and hierarchy.
- Git commits, branches, tags, and remotes.
- Changelog history.
- The project licence.
- Referenced custom logos.

Migration replaces recognised legacy KiBot resources, KDT worksheets, launchers, and the single legacy CI workflow.

### Migration Procedure

1. Close KiCad.

2. Create a migration branch:

   ```powershell
   git switch -c migrate/boardwright
   ```

3. Make sure that the working tree is clean:

   ```powershell
   git status --short
   ```

4. Create the migration plan:

   ```powershell
   boardwright migrate plan --output migration.yaml
   ```

5. If the repository has multiple root projects, select one:

   ```powershell
   boardwright migrate plan --project FIC-100A.kicad_pro --output migration.yaml
   ```

6. Review `migration.yaml`.

7. Set each unresolved value in the `resolutions` section.

8. Apply the plan:

   ```powershell
   boardwright migrate apply migration.yaml
   ```

9. Validate the migrated project:

   ```powershell
   boardwright validate
   ```

10. Review and commit the changes.

Migration does not create a commit. It also does not change remote branches, tags, or GitHub releases.

The migration replaces legacy `${REVISION}` schematic references with `${DRAWING_REVISION}`. Boardwright keeps drawing revisions separate from board revisions and release versions.

## Update a Boardwright Project

Boardwright records managed files in `.boardwright/state.yaml`. It uses this record to classify local and upstream changes.

An update does not replace these user-owned files:

- KiCad design sources.
- Project metadata values.
- Licences and notices.
- Changelog history.
- User assets.

### Update Procedure

1. Check the installed state:

   ```powershell
   boardwright update status
   ```

2. Create an update plan:

   ```powershell
   boardwright update plan --output update.yaml
   ```

3. Review `update.yaml`.

4. Resolve each reported conflict.

5. Apply the plan:

   ```powershell
   boardwright update apply update.yaml
   ```

6. Validate and review the project changes.

Boardwright replaces unchanged managed files. It uses a three-way merge for customised text files.

Boardwright stops when changes overlap. It also stops for customised binary files or files without a known base.

## Branch and Release Model

| Git reference | Purpose |
| --- | --- |
| `dev` | Normal design and source work. |
| `preview` | Disposable generated preview content. |
| `main` | Reviewed and accepted project state. |
| Version tag | Immutable release source and package point. |

Preview CI does not change `dev`.

The accepted-output workflow builds the reviewed `dev` source commit. It can add the generated README and board images to `main`.

Release preparation updates the changelog and release metadata. It then creates the release commit and version tag.

The tag workflow publishes release files. It does not push branch commits.

## Variants

Boardwright uses these KiBot variants:

| Variant | Intended use |
| --- | --- |
| `DRAFT` | Early design output. |
| `PRELIMINARY` | Review output before final checks. |
| `CHECKED` | Reviewed output that includes ERC and DRC. |
| `RELEASED` | Official production release output. |

Project defaults are in `.boardwright/project.yaml`. You can edit them through Project Info.

## Useful Commands

```powershell
python -m boardwright status
python -m boardwright validate
python -m boardwright doctor
python -m boardwright revision-history
python -m boardwright migrate --help
python -m boardwright update status
python -m boardwright review
python -m boardwright accepted
python -m boardwright source-package --output boardwright-source.zip
python -m boardwright docker-kibot --version 9
```

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

See [docs/TESTBENCH.md](docs/TESTBENCH.md) for the isolated live CI test procedure.

## Generated Project README

This README describes Boardwright.

Boardwright generates downstream project READMEs from:

```text
boardwright_resources/kibot/resources/templates/readme.txt
```

The generated README can show board images, project identity, revisions, dimensions, and release links.

## Licensing and Provenance

Boardwright derives from Nguyen Vincent's `KDT_Hierarchical_KiBot` template. Nguyen published the original work under the MIT Licence.

The preserved licence text is in [LICENSES/Nguyen-MIT.txt](LICENSES/Nguyen-MIT.txt).

The root [LICENSE](LICENSE) applies to Boardwright-specific tooling, workflows, documentation, metadata, and template changes.

The Boardwright Hardware Output Exception excludes downstream hardware designs and generated hardware outputs from the Boardwright tooling licence.

Copied Boardwright template material and third-party notices keep their applicable terms.

Boardwright does not provide legal advice. Review the licensing, branding, safety, and regulatory requirements for each downstream project.

Use these files for legal and provenance information:

- [LICENSE](LICENSE)
- [NOTICE.md](NOTICE.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [LICENSES/README.md](LICENSES/README.md)
- [docs/PROVENANCE.md](docs/PROVENANCE.md)

## Documentation

Start with [docs/README.md](docs/README.md).

The documentation index identifies the source for product behaviour, fields, provenance, plans, and test procedures.

## Credits

- Nguyen Vincent created the original hierarchical KiCad and KiBot template.
- KiBot provides the KiCad automation engine.
- KiCad provides the electronic design automation platform.
