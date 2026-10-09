<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# Contributing

Contributions to Boardwright are welcome when they fit the project direction
and preserve the licensing/provenance boundaries in this repository.

## License Of Contributions

By contributing to Boardwright, you agree that your contribution is licensed
under the same license terms as the part of Boardwright you contribute to.

For Boardwright-specific tooling/template work, that means the terms described
in the root `LICENSE`: Apache License, Version 2.0 as modified by Commons
Clause, plus the Boardwright Hardware Output Exception.

Do not contribute code, documentation, fonts, images, worksheets, KiCad assets,
or other material unless you have the rights needed to contribute it under the
applicable terms.

## Provenance

When a contribution copies or adapts third-party material, include the source,
author, copyright notice, and license details in the relevant file or in
`THIRD_PARTY_NOTICES.md`.

Do not include secrets, customer files, private hardware designs, proprietary
datasheets, or confidential project material.

## Tests

Run the Python tests before submitting changes:

```powershell
python -m unittest discover -s tests -v
```

For a convenient local development install with the TUI and template helpers,
use:

```powershell
python -m pip install -e ".[dev]"
```

For workflow changes, also validate the template state:

```powershell
python -m boardwright validate
```

Validation may report hardware-template issues, such as missing Edge.Cuts in
the template PCB, that are tracked separately from Python test failures.
