# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

from __future__ import annotations

import shutil
import unittest
import uuid
from pathlib import Path

from boardwright.kibot_pdf_pages import (
    format_pdf_page_prune_summary,
    prune_empty_testpoint_pdf_pages,
)


class KiBotPdfPageTests(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path("tests") / ".tmp_kibot_pdf_pages" / uuid.uuid4().hex
        root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(root.parent, ignore_errors=True))
        return root

    def write_fabrication_yaml(self, root: Path) -> Path:
        config = root / "boardwright_resources" / "kibot" / "yaml"
        config.mkdir(parents=True)
        path = config / "kibot_out_pdf_fabrication.yaml"
        path.write_text(
            """
outputs:
- name: pdf_fabrication
  options:
    pages:
      - scaling: 1
        sheet: 'TOP TEST POINTS (SCALE 1:1)'
        layers:
          - layer: F.TestPointList
      - scaling: 1
        sheet: 'BOTTOM TEST POINTS (SCALE 1:1)'
        layers:
          - layer: B.TestPointList
      - scaling: 1
        sheet: '%ln (SCALE 1:1)'
        layers:
          - layer: F.Cu
...
""",
            encoding="utf-8",
        )
        return path

    def test_prunes_only_empty_testpoint_side_pages(self) -> None:
        root = self.make_root()
        config = self.write_fabrication_yaml(root)
        testpoints = root / "Testing" / "Testpoints"
        testpoints.mkdir(parents=True)
        (testpoints / "board-testpoints-top.csv").write_text(
            "Ref.,Net,X [mm],Y [mm]\nTP1,+3V3,1,2\n",
            encoding="utf-8",
        )
        (testpoints / "board-testpoints-bottom.csv").write_text(
            "Ref.,Net,X [mm],Y [mm]\n",
            encoding="utf-8",
        )

        result = prune_empty_testpoint_pdf_pages(root)
        text = config.read_text(encoding="utf-8")

        self.assertEqual(("BOTTOM TEST POINTS",), result.removed_pages)
        self.assertIn("TOP TEST POINTS", text)
        self.assertNotIn("BOTTOM TEST POINTS", text)
        self.assertIn("%ln", text)
        self.assertIn("BOTTOM TEST POINTS", format_pdf_page_prune_summary(result))

    def test_prunes_both_testpoint_pages_when_no_side_has_rows(self) -> None:
        root = self.make_root()
        config = self.write_fabrication_yaml(root)
        testpoints = root / "Testing" / "Testpoints"
        testpoints.mkdir(parents=True)
        (testpoints / "board-testpoints-top.csv").write_text("Ref.,Net\n", encoding="utf-8")
        (testpoints / "board-testpoints-bottom.csv").write_text("Ref.,Net\n", encoding="utf-8")

        result = prune_empty_testpoint_pdf_pages(root)
        text = config.read_text(encoding="utf-8")

        self.assertEqual(("TOP TEST POINTS", "BOTTOM TEST POINTS"), result.removed_pages)
        self.assertNotIn("TOP TEST POINTS", text)
        self.assertNotIn("BOTTOM TEST POINTS", text)


    def test_expands_repeated_layer_pages_to_literal_titles(self) -> None:
        root = self.make_root()
        config = self.write_fabrication_yaml(root)
        (root / "demo.kicad_pro").write_text("{}\n", encoding="utf-8")
        (root / "demo.kicad_pcb").write_text(
            """
(kicad_pcb
  (layers
    (0 "F.Cu" signal "L1")
    (31 "B.Cu" signal "L2")
  )
)
""",
            encoding="utf-8",
        )
        config.write_text(
            """
outputs:
- name: pdf_fabrication
  options:
    pages:
      - scaling: 1
        title: '%lp DRILL MAP'
        sheet: 'DRILL DRAWING (%lp)'
        layer_var: 'DRILL DRAWING %lp (SCALE 1:1)'
        repeat_for_layer: '@LAYER_DRILL_MAP@'
        repeat_layers: 'drill_pairs'
        layers:
          - layer: '@LAYER_DRILL_MAP@'
      - scaling: 1
        sheet: '%ln (SCALE 1:1)'
        layer_var: '%ln (SCALE 1:1)'
        title: '%ln COPPER'
        repeat_for_layer: 'F.Cu'
        repeat_layers: 'copper'
        layers:
          - layer: 'F.Cu'
...
""",
            encoding="utf-8",
        )

        result = prune_empty_testpoint_pdf_pages(root)
        text = config.read_text(encoding="utf-8")

        self.assertEqual(("L1-L2 DRILL MAP", "L1 COPPER", "L2 COPPER"), result.expanded_pages)
        self.assertIn("title: 'L1-L2 DRILL MAP'", text)
        self.assertIn("title: 'L1 COPPER'", text)
        self.assertIn("title: 'L2 COPPER'", text)
        self.assertIn("layer: 'F.Cu'", text)
        self.assertIn("layer: 'B.Cu'", text)
        self.assertNotIn("%lp", text)
        self.assertNotIn("%ln", text)
        self.assertIn("repeat_for_layer: '@LAYER_DRILL_MAP@'", text)
        self.assertIn("repeat_layers: 'drill_pairs'", text)
        self.assertNotIn("repeat_layers: 'copper'", text)

if __name__ == "__main__":
    unittest.main()

