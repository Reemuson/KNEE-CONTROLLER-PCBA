# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import shutil
import unittest
import zipfile
from pathlib import Path

from boardwright.source_package import build_source_package


class SourcePackageTests(unittest.TestCase):
    def test_build_source_package_excludes_generated_outputs(self) -> None:
        root = Path.cwd() / ".test_source_package"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            (root / "src").mkdir()
            (root / "src" / "module.py").write_text("print('hello')\n", encoding="utf-8")
            (root / "README.md").write_text("# Readme\n", encoding="utf-8")
            (root / "Manufacturing").mkdir()
            (root / "Manufacturing" / "fabrication.pdf").write_text("skip\n", encoding="utf-8")
            (root / "assets").mkdir()
            (root / "assets" / "renders").mkdir(parents=True, exist_ok=True)
            (root / "assets" / "renders" / "board.png").write_text("skip\n", encoding="utf-8")

            output = root / "boardwright-source.zip"
            result = build_source_package(root, output, prefix="boardwright-source", force=True)

            self.assertEqual(output, result.path)
            self.assertEqual(2, result.file_count)
            with zipfile.ZipFile(output) as archive:
                names = sorted(archive.namelist())
            self.assertIn("boardwright-source/README.md", names)
            self.assertIn("boardwright-source/src/module.py", names)
            self.assertNotIn("boardwright-source/Manufacturing/fabrication.pdf", names)
            self.assertNotIn("boardwright-source/assets/renders/board.png", names)
        finally:
            if root.exists():
                shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
