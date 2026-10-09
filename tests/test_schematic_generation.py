# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import shutil
import unittest
from pathlib import Path

from boardwright.schematic_generation import (
    add_hierarchical_sheet,
    generate_hierarchical_project,
    generate_one_sheet_schematic,
    generate_revision_history_sheet,
)


class SchematicGenerationTests(unittest.TestCase):
    def test_generate_revision_history_sheet_updates_title(self) -> None:
        root = Path.cwd() / ".test_schematic_generation"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            (root / "revision-history.kicad_sch").write_text(
                """(kicad_sch
\t(title_block
\t\t(title "REVISION HISTORY")
\t)
)
""",
                encoding="utf-8",
            )
            output = root / "extra-revision-history.kicad_sch"

            result = generate_revision_history_sheet(root, output, title="EXTRA HISTORY")

            self.assertEqual(output, result.path)
            self.assertIn('(title "EXTRA HISTORY")', output.read_text(encoding="utf-8"))
        finally:
            if root.exists():
                shutil.rmtree(root)

    def test_generate_one_sheet_schematic_writes_skeleton(self) -> None:
        root = Path.cwd() / ".test_schematic_generation"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            output = root / "project.kicad_sch"

            result = generate_one_sheet_schematic(
                output,
                title="Demo Board",
                company="Acme",
                revision="A",
                date_text="2025-01-12",
            )

            self.assertEqual(output, result.path)
            text = output.read_text(encoding="utf-8")
            self.assertIn('(title "Demo Board")', text)
            self.assertIn('One-sheet schematic skeleton', text)
        finally:
            if root.exists():
                shutil.rmtree(root)

    def test_generate_hierarchical_project_writes_parent_and_child(self) -> None:
        root = Path.cwd() / ".test_schematic_generation"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:

            parent, child = generate_hierarchical_project(
                root,
                project_name="Demo Board",
                company="Acme",
                revision="B",
                sheet_name="POWER",
                child_filename="power-stage.kicad_sch",
                date_text="2025-01-12",
            )

            self.assertTrue(parent.path.exists())
            self.assertTrue(child.path.exists())
            parent_text = parent.path.read_text(encoding="utf-8")
            child_text = child.path.read_text(encoding="utf-8")
            self.assertIn('(property "Sheetname" "POWER"', parent_text)
            self.assertIn('(property "Sheetfile" "power-stage.kicad_sch"', parent_text)
            self.assertIn('Child sheet skeleton', child_text)
        finally:
            if root.exists():
                shutil.rmtree(root)

    def test_add_hierarchical_sheet_appends_to_existing_parent(self) -> None:
        root = Path.cwd() / ".test_schematic_generation"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            parent = root / "boardwright.kicad_sch"
            parent.write_text(
                """(kicad_sch
\t(version 20250114)
\t(generator "eeschema")
\t(generator_version "9.0")
\t(uuid "parent")
\t(paper "A4")
\t(title_block
\t\t(title "Boardwright")
\t)
\t(lib_symbols)
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
""",
                encoding="utf-8",
            )
            child = root / "subsystem.kicad_sch"

            result_parent, result_child = add_hierarchical_sheet(
                parent,
                child,
                sheet_name="Subsystem",
                child_title="Subsystem",
            )

            self.assertEqual(parent, result_parent.path)
            self.assertEqual(child, result_child.path)
            parent_text = parent.read_text(encoding="utf-8")
            self.assertIn('(property "Sheetname" "Subsystem"', parent_text)
            self.assertIn('(property "Sheetfile" "subsystem.kicad_sch"', parent_text)
            self.assertTrue(child.exists())
        finally:
            if root.exists():
                shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
