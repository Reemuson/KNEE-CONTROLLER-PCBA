# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path

from boardwright.config import BoardwrightConfig
from boardwright.validation import (
    _find_known_local_branding,
    _has_edge_cuts_geometry,
    _validate_deprecated_schematic_variables,
    validate_project,
)


class ValidationTests(unittest.TestCase):
    def test_validates_variant_values(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={
                "project": {
                    "id": "TEST",
                    "name": "Test",
                    "company": "Company",
                    "designer": "Designer",
                },
                "variants": {
                    "dev_default": "FAST",
                    "preview_default": "CHECKED",
                    "main_default": "CHECKED",
                    "release_default": "RELEASED",
                },
                "outputs": {"preview_engine": "github-actions"},
            },
            branches={"branches": {}},
            legal={"legal": {}},
            revision_history={"revision_history": {}},
        )

        issues = validate_project(config)

        self.assertTrue(
            any("Unsupported variants.dev_default" in issue.message for issue in issues)
        )

    def test_warns_when_pcb_has_no_edge_cuts_geometry(self) -> None:
        self.assertFalse(_has_edge_cuts_geometry(Path("boardwright.kicad_pcb")))

    def test_accepts_edge_cuts_geometry(self) -> None:
        path = Path("tests/fixtures_edge_cuts_geometry.kicad_pcb")
        try:
            path.write_text(
                '(kicad_pcb (gr_rect (start 0 0) (end 1 1) (layer "Edge.Cuts")))',
                encoding="utf-8",
            )
            self.assertTrue(_has_edge_cuts_geometry(path))
        finally:
            if path.exists():
                path.unlink()

    def test_finds_known_local_branding_in_active_template_files(self) -> None:
        root = Path("tests/.tmp_branding_validation")
        path = root / "Templates" / "example.kicad_wks"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Logo: assets/logos/rd-logo.png", encoding="utf-8")

            hits = _find_known_local_branding(root)

            self.assertEqual(1, len(hits))
            self.assertTrue(hits[0][0].replace("\\", "/").endswith("Templates/example.kicad_wks"))
            self.assertEqual("assets/logos/rd-logo.png", hits[0][1])
        finally:
            if path.exists():
                path.unlink()
            if path.parent.exists():
                path.parent.rmdir()
            if root.exists():
                root.rmdir()

    def test_rejects_legacy_revision_variable_in_schematic(self) -> None:
        root = Path("tests/.tmp_deprecated_schematic_variable")
        path = root / "example.kicad_sch"
        try:
            root.mkdir(parents=True, exist_ok=True)
            path.write_text(
                '(kicad_sch (title_block (rev "${REVISION}")))',
                encoding="utf-8",
            )
            issues = []

            _validate_deprecated_schematic_variables(root, issues)

            self.assertEqual(1, len(issues))
            self.assertEqual("error", issues[0].level)
            self.assertIn("DRAWING_REVISION", issues[0].message)
        finally:
            if path.exists():
                path.unlink()
            if root.exists():
                root.rmdir()


    def test_validates_document_scheme_and_signoff_dates(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={
                "project": {
                    "id": "TEST",
                    "name": "Test",
                    "company": "Company",
                    "designer": "Designer",
                },
                "documents": {
                    "schematic": {
                        "revision_scheme": "roman",
                        "drawn_date": "05/07/2026",
                    }
                },
                "variants": {
                    "dev_default": "DRAFT",
                    "preview_default": "CHECKED",
                    "main_default": "CHECKED",
                    "release_default": "RELEASED",
                },
                "outputs": {"preview_engine": "github-actions"},
            },
            branches={"branches": {}},
            legal={"legal": {}},
            revision_history={"revision_history": {}},
        )

        issues = validate_project(config)

        self.assertTrue(any("Unsupported documents.schematic.revision_scheme" in issue.message for issue in issues))
        self.assertTrue(any(issue.level == "warning" and "documents.schematic.drawn_date" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
