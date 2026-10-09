# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import base64
import shutil
import unittest
from pathlib import Path

from boardwright.errors import BoardwrightError
from boardwright.worksheet_logo import (
    embed_logo_in_worksheet,
    format_bitmap_data,
    png_dimensions,
)


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/l6gK0wAAAABJRU5ErkJggg=="
)
PNG_2X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAYAAAD0In+KAAAADUlEQVR42mP8z8BQDwAFgwJ/l6gK0wAAAABJRU5ErkJggg=="
)


class WorksheetLogoTests(unittest.TestCase):
    def test_png_dimensions_reads_ihdr(self) -> None:
        self.assertEqual((1, 1), png_dimensions(PNG_1X1))

    def test_png_dimensions_rejects_non_png(self) -> None:
        with self.assertRaises(BoardwrightError):
            png_dimensions(b"not a png")

    def test_format_bitmap_data_chunks_base64(self) -> None:
        data = format_bitmap_data(PNG_1X1, indent="\t\t", chunk_size=12)

        self.assertTrue(data.startswith('\t\t(data "iVBORw0KGgoA"'))
        self.assertIn('\n\t\t\t"', data)
        self.assertTrue(data.endswith("\n\t\t)"))

    def test_embed_logo_replaces_only_bitmap_data(self) -> None:
        root = Path("tests/.tmp_worksheet_logo")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            logo = root / "logo.png"
            logo.write_bytes(PNG_2X1)
            worksheet = root / "test.kicad_wks"
            worksheet.write_text(
                """(kicad_wks
    (bitmap
        (name "")
        (pos 10 20)
        (scale 0.5)
        (data "old")
    )
)""",
                encoding="utf-8",
            )

            result = embed_logo_in_worksheet(worksheet, logo)

            text = worksheet.read_text(encoding="utf-8")
            self.assertEqual((2, 1), (result.png_width, result.png_height))
            self.assertIn("(pos 10 20)", text)
            self.assertIn("(scale 0.5)", text)
            self.assertNotIn('"old"', text)
            self.assertIn(base64.b64encode(PNG_2X1).decode("ascii")[:40], text)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_embed_logo_normalizes_excessive_data_indent(self) -> None:
        root = Path("tests/.tmp_worksheet_logo")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            logo = root / "logo.png"
            logo.write_bytes(PNG_1X1)
            worksheet = root / "test.kicad_wks"
            excessive_indent = "\t" * 2000
            worksheet.write_text(
                f"""(kicad_wks
    (bitmap
        (name "")
        (pos 10 20)
        (scale 0.5)
{excessive_indent}(data "old")
    )
)""",
                encoding="utf-8",
            )

            embed_logo_in_worksheet(worksheet, logo)

            text = worksheet.read_text(encoding="utf-8")
            self.assertLess(worksheet.stat().st_size, 5000)
            self.assertIn('\n\t\t(data "', text)
            self.assertNotIn(excessive_indent, text)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
