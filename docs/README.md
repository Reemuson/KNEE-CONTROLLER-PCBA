<!-- SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available -->
<!-- Copyright (c) Ryan Hicks -->

# Boardwright Documentation

Use this index to find the correct document for each task.

| Document | Content |
| --- | --- |
| [`../README.md`](../README.md) | Product overview, installation, migration, updates, and normal use. |
| [`SPEC.md`](SPEC.md) | Product contract and design rules. |
| [`FIELDS.md`](FIELDS.md) | Project fields and KiCad or KiBot variable meanings. |
| [`ROADMAP.md`](ROADMAP.md) | Product milestones and planned sequence. |
| [`TODO.md`](TODO.md) | Open work and completed tasks. |
| [`TESTBENCH.md`](TESTBENCH.md) | Isolated GitHub Actions test procedure. |
| [`PROVENANCE.md`](PROVENANCE.md) | File origins, attribution, and licence boundaries. |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | Contribution and verification requirements. |

Use `../LICENSE`, `../NOTICE.md`, `../THIRD_PARTY_NOTICES.md`, and `../LICENSES/` for legal terms and notices.

## Maintenance Rules

- Update the document that owns the information.
- Link to detailed information instead of copying it.
- Keep implemented behaviour separate from planned behaviour.
- Record open work in `TODO.md`.
- Record milestones and sequence in `ROADMAP.md`.
- Update `FIELDS.md` when a project field or worksheet variable changes.
- Check each example command against `python -m boardwright --help`.
