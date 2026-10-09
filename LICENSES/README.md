<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# License Structure

This repository uses a layered license structure.

## Boardwright Tooling And Template Work

Boardwright-specific source code, workflows, documentation, configuration,
metadata, tests, and template changes are covered by the root `LICENSE` unless
a file states otherwise.

The root `LICENSE` applies the Apache License, Version 2.0 as modified by the
Commons Clause License Condition v1.0, plus the Boardwright Hardware Output
Exception.

Supporting license texts:

```text
LICENSES/Apache-2.0.txt
LICENSES/Commons-Clause.txt
LICENSES/OFL-1.1.txt
```

## Inherited Nguyen/KDT Template Material

Material inherited from or derived from Nguyen Vincent's
`KDT_Hierarchical_KiBot` template remains under the preserved MIT notice in:

```text
LICENSES/Nguyen-MIT.txt
```

## Third-Party Material

Third-party assets, fonts, color themes, scripts, and other externally sourced
material are listed in:

```text
THIRD_PARTY_NOTICES.md
```

Some bundled assets still require source/license confirmation or replacement
before public/template release.

The bundled Arimo and Tinos font files are distributed under the SIL Open Font
License. The OFL text is included in `LICENSES/OFL-1.1.txt`.

## Downstream Hardware Projects

Using Boardwright to generate or manage a hardware project does not impose the
Boardwright tooling/template license on the downstream hardware design,
manufacturing outputs, release packages, or project-specific documentation,
except for Boardwright template material copied into those outputs.

Downstream hardware-project license defaults are project metadata and live in:

```text
.boardwright/legal.yaml
```

That file does not define the license of the Boardwright repository itself.
