# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
import shutil
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from boardwright_resources.kibot.resources.scripts.get_sheet_title import (
    _title_from_schematic,
    get_sheet_title,
)
from boardwright.sheet_titles import collect_actual_sheet_titles


class SheetTitleTests(unittest.TestCase):
    def test_falls_back_to_kicad_schematic(self) -> None:
        title = _title_from_schematic(Path("boardwright.kicad_sch"), 6, 8)

        self.assertEqual("POWER SEQUENCE", title)

    def test_missing_sheet_returns_dots(self) -> None:
        title = _title_from_schematic(Path("boardwright.kicad_sch"), 99, 8)

        self.assertEqual("........", title)

    def test_finds_nested_sheet_a(self) -> None:
        title = _title_from_schematic(Path("boardwright.kicad_sch"), 4, 8)

        self.assertEqual("Section A - Title A", title)

    def test_finds_nested_sheet_b(self) -> None:
        title = _title_from_schematic(Path("boardwright.kicad_sch"), 5, 8)

        self.assertEqual("Section B - Title B", title)

    def test_get_sheet_title_accepts_kicad_sch(self) -> None:
        # Smoke test: should not require an intermediate XML file.
        get_sheet_title("boardwright.kicad_sch", 6, 8)

    def test_collect_actual_sheet_titles_reads_hierarchy(self) -> None:
        titles = collect_actual_sheet_titles(Path("."))

        self.assertEqual("COVER PAGE", titles[0])
        self.assertEqual("Section A - Title A", titles[3])
        self.assertEqual("Section B - Title B", titles[4])

    def test_local_sheet_title_override_file_takes_precedence(self) -> None:
        root = Path("tests/.tmp_sheet_title_overrides")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            config_dir = root / ".boardwright"
            config_dir.mkdir()
            (config_dir / "sheet_titles.env").write_text(
                "SHEET_NAME_2=Local Section Title\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                get_sheet_title(root / "boardwright.kicad_sch", 2, 8)

            self.assertEqual("Local Section Title", stdout.getvalue().strip())
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
