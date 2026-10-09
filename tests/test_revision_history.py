# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import json
import shutil
import unittest
from pathlib import Path

from boardwright.config import BoardwrightConfig
from boardwright.revision_history import (
    build_revision_slots,
    build_revision_slots_from_text,
    write_document_revision_rows,
    write_full_revision_history,
    write_revision_variables,
)


class RevisionHistoryTests(unittest.TestCase):
    def test_builds_changelog_slots_for_legacy_parser_tests(self) -> None:
        text = (
            "# Changelog\n\n"
            "## [Unreleased]\n\n### Added\n\n- Current work\n\n"
            "## [0.1.0] - 2026-04-25\n\n### Fixed\n\n- First release\n"
        )

        slots = build_revision_slots_from_text(text, slot_count=3)

        self.assertEqual(3, len(slots))
        self.assertEqual("Unreleased", slots[0].version)
        self.assertEqual("0.1.0", slots[1].version)
        self.assertEqual("", slots[2].version)

    def test_previous_changelog_releases_shift_down(self) -> None:
        text = (
            "# Changelog\n\n"
            "## [Unreleased]\n\n"
            "## [0.3.0] - 2026-04-25\n\n### Added\n\n- Third\n\n"
            "## [0.2.0] - 2026-04-20\n\n### Changed\n\n- Second\n\n"
            "## [0.1.0] - 2026-04-10\n\n### Fixed\n\n- First\n"
        )

        slots = build_revision_slots_from_text(
            text,
            slot_count=4,
            include_unreleased=False,
        )

        self.assertEqual("0.3.0", slots[0].version)
        self.assertEqual("0.2.0", slots[1].version)
        self.assertEqual("0.1.0", slots[2].version)
        self.assertEqual("", slots[3].version)
        self.assertEqual("0.3.0 - 2026-04-25", slots[0].title)
        self.assertEqual("Changed:\n  - Second", slots[1].body)

    def test_document_rows_generate_latest_six_table_variables_and_note(self) -> None:
        root = Path("tests/.tmp_revision_history_document_rows")
        shutil.rmtree(root, ignore_errors=True)
        try:
            (root / ".boardwright").mkdir(parents=True)
            rows = []
            for index, revision in enumerate("HGFEDCBA", start=1):
                rows.append(
                    {
                        "revision": revision,
                        "description": f"Revision {revision}",
                        "date": f"2026-08-{index:02d}",
                        "drawn_by": "RH",
                    }
                )
            config = BoardwrightConfig(
                root=root,
                project={"project": {}},
                branches={"branches": {}},
                legal={"legal": {}},
                revision_history={"revision_history": {}},
                document_revisions={"document_revisions": {"schematic": {"rows": rows}}},
            )

            slots = build_revision_slots(config)
            output = write_revision_variables(config).read_text(encoding="utf-8")
            full = write_full_revision_history(config).read_text(encoding="utf-8").replace("\r\n", "\n")

            self.assertEqual("C", slots[0].revision)
            self.assertEqual("H", slots[5].revision)
            self.assertIn('REVTABLE_1_REV="C"', output)
            self.assertIn('REVTABLE_1_DATE="2026-08-06"', output)
            self.assertIn('REVTABLE_1_DESC="Revision C"', output)
            self.assertIn('REVTABLE_1_DRAWN="RH"', output)
            self.assertNotIn('REVTABLE_1_CHECKED', output)
            self.assertIn('REVTABLE_6_REV="H"', output)
            self.assertIn('REVTABLE_NOTE="Latest 6 revisions shown. See full revision history."', output)
            self.assertIn("REV,DATE,DESCRIPTION,DRAWN\n", full)
            self.assertIn("B,2026-08-07,Revision B,RH\n", full)
            self.assertIn("A,2026-08-08,Revision A,RH\n", full)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_unused_title_block_rows_emit_blank_values(self) -> None:
        root = Path("tests/.tmp_revision_history_blank_rows")
        shutil.rmtree(root, ignore_errors=True)
        try:
            (root / ".boardwright").mkdir(parents=True)
            config = BoardwrightConfig(
                root=root,
                project={"project": {}},
                branches={"branches": {}},
                legal={"legal": {}},
                revision_history={"revision_history": {}},
                document_revisions={
                    "document_revisions": {
                        "fabrication": {
                            "rows": [
                                {
                                    "revision": "A",
                                    "date": "2026-07-05",
                                    "description": "Initial release",
                                }
                            ]
                        }
                    }
                },
            )

            output = write_revision_variables(config, "fabrication").read_text(encoding="utf-8")

            self.assertIn('REVTABLE_1_REV="A"', output)
            self.assertIn('REVTABLE_2_REV=""', output)
            self.assertNotIn('REVTABLE_6_CHECKED', output)
            self.assertIn('REVTABLE_NOTE=""', output)
        finally:
            shutil.rmtree(root, ignore_errors=True)


    def test_write_document_revision_rows_persists_newest_first_yaml(self) -> None:
        root = Path("tests/.tmp_revision_history_editor_rows")
        shutil.rmtree(root, ignore_errors=True)
        try:
            (root / ".boardwright").mkdir(parents=True)
            config = BoardwrightConfig(
                root=root,
                project={"project": {}},
                branches={"branches": {}},
                legal={"legal": {}},
                revision_history={"revision_history": {}},
                document_revisions={},
            )

            write_document_revision_rows(
                config,
                [
                    {
                        "revision": "B",
                        "date": "2026-08-01",
                        "description": "Updated connector callouts",
                        "drawn_by": "RH",
                    },
                    {
                        "revision": "A",
                        "date": "2026-07-05",
                        "description": "Initial release",
                        "drawn_by": "RH",
                    },
                ],
            )
            loaded = BoardwrightConfig(
                root=root,
                project={"project": {}},
                branches={"branches": {}},
                legal={"legal": {}},
                revision_history={"revision_history": {}},
                document_revisions={
                    "document_revisions": {
                        "schematic": {
                            "rows": [
                                {"revision": "B", "date": "2026-08-01", "description": "Updated connector callouts", "drawn_by": "RH"},
                                {"revision": "A", "date": "2026-07-05", "description": "Initial release", "drawn_by": "RH"},
                            ]
                        }
                    }
                },
            )
            output = write_revision_variables(loaded).read_text(encoding="utf-8")
            saved = (root / ".boardwright" / "document_revisions.yaml").read_text(encoding="utf-8")

            self.assertIn("revision: B", saved)
            self.assertIn("description: Updated connector callouts", saved)
            self.assertIn('REVTABLE_1_REV="A"', output)
            self.assertIn('REVTABLE_2_REV="B"', output)
        finally:
            shutil.rmtree(root, ignore_errors=True)


    def test_write_revision_variables_syncs_kicad_project_text_variables(self) -> None:
        root = Path("tests/.tmp_revision_history_kicad_project")
        shutil.rmtree(root, ignore_errors=True)
        try:
            (root / ".boardwright").mkdir(parents=True)
            (root / "demo.kicad_pro").write_text(
                json.dumps({"text_variables": {"EXISTING": "keep", "PROJECT_NAME": "stale", "PROJECT_ID": "stale"}}, indent=2) + "\n",
                encoding="utf-8",
            )
            config = BoardwrightConfig(
                root=root,
                project={
                    "project": {
                        "name": "Demo Project",
                        "pcba_name": "Demo PCBA",
                        "pcb_name": "Demo PCB",
                        "company": "Demo Co",
                        "designer": "RH",
                        "board_revision": "B",
                    },
                    "documents": {
                        "schematic": {
                            "title": "Schematic",
                            "type": "SCHEMATIC",
                            "number_source": "pcba_name",
                            "revision": "C",
                        }
                    },
                },
                branches={"branches": {}},
                legal={"legal": {}},
                revision_history={"revision_history": {}},
                document_revisions={
                    "document_revisions": {
                        "schematic": {
                            "rows": [
                                {
                                    "revision": "C",
                                    "date": "2026-07-07",
                                    "description": "Updated title block",
                                    "drawn_by": "RH",
                                }
                            ]
                        }
                    }
                },
            )

            write_revision_variables(config)

            variables = json.loads((root / "demo.kicad_pro").read_text(encoding="utf-8"))["text_variables"]
            self.assertEqual("keep", variables["EXISTING"])
            self.assertNotIn("PROJECT_NAME", variables)
            self.assertNotIn("PROJECT_ID", variables)
            self.assertEqual("Demo Project", variables["PROJECT_NUMBER"])
            self.assertEqual("Demo PCBA", variables["PCBA_NAME"])
            self.assertEqual("Demo PCBA", variables["DRAWING_NUMBER"])
            self.assertEqual("C", variables["DRAWING_REVISION"])
            self.assertEqual("C", variables["REVTABLE_1_REV"])
            self.assertEqual("Updated title block", variables["REVTABLE_1_DESC"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_empty_yaml_history_does_not_fall_back_to_changelog_exports(self) -> None:
        root = Path("tests/.tmp_revision_history_no_changelog_fallback")
        shutil.rmtree(root, ignore_errors=True)
        try:
            (root / ".boardwright").mkdir(parents=True)
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [0.1.0] - 2026-04-25\n\n### Added\n\n- First\n",
                encoding="utf-8",
            )
            config = BoardwrightConfig(
                root=root,
                project={"project": {}},
                branches={"branches": {}},
                legal={"legal": {}},
                revision_history={"revision_history": {"slots": 1}},
                document_revisions={},
            )

            output = write_revision_variables(config).read_text(encoding="utf-8")

            self.assertIn('REVTABLE_1_REV=""', output)
            self.assertNotIn("REVHIST_", output)
            self.assertNotIn("0.1.0", output)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
