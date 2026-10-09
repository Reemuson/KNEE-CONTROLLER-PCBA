# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path
import re
import shutil
from unittest.mock import patch

from boardwright.kicad_tables import prepare_pcb_tables
import boardwright.kicad_tables as kicad_tables


class KiCadTablesTests(unittest.TestCase):
    def test_pcb_worksheet_prefers_pcbnew_layout(self) -> None:
        root = Path("tests/.tmp_kicad_tables_pcb_worksheet")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            (root / "boardwright.kicad_pro").write_text(
                """{
  "schematic": {
    "page_layout_descr_file": "Templates/Schematic.kicad_wks"
  },
  "pcbnew": {
    "page_layout_descr_file": "Templates/Pcb.kicad_wks"
  }
}
""",
                encoding="utf-8",
            )

            self.assertEqual(
                "Templates/Pcb.kicad_wks",
                kicad_tables._pcb_worksheet(root, "Templates/Fallback.kicad_wks"),
            )
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_prepare_pcb_tables_writes_component_count_without_kibot_report(
        self,
    ) -> None:
        root = Path("tests/.tmp_kicad_tables")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            (root / "boardwright.kicad_pro").write_text(
                """{
  "pcbnew": {
    "page_layout_descr_file": "Templates/Boardwright_Template_PCB_A3.kicad_wks"
  }
}
""",
                encoding="utf-8",
            )
            templates = root / "Templates"
            templates.mkdir()
            (templates / "Boardwright_Template_PCB_A3.kicad_wks").write_text(
                '(kicad_wks\n\t(tbtext "${DRAWING_TITLE}"\n)\n\t(tbtext "${DRAWING_NUMBER}"\n)\n\t(tbtext "${DRAWN_BY}"\n)\n\t(tbtext "${DRAWN_DATE}"\n)\n)',
                encoding="utf-8",
            )
            (root / "boardwright.kicad_pcb").write_text(
                """
(kicad_pcb
  (footprint "Resistor_SMD:R_0603" (layer "F.Cu")
    (attr smd)
    (fp_text reference "R1" (at 0 0 0) (layer "F.SilkS")
      (effects (font (face "Arimo") (size 1 1)))))
  (footprint "Capacitor_SMD:C_0603" (layer "B.Cu")
    (attr smd)
    (fp_text reference "C1" (at 0 0 0) (layer "B.SilkS")
      (effects (font (face "Arimo") (size 1 1)))))
  (footprint "Connector_PinHeader:PinHeader_1x02" (layer "F.Cu")
    (attr through_hole)
    (fp_text reference "J1" (at 0 0 0) (layer "F.SilkS")
      (effects (font (face "Arimo") (size 1 1)))))
  (gr_text_box ""
    (start 0 0)
    (end 10 10)
    (uuid "511273fd-c939-4feb-bf05-ae1b43c3644e")
  )
  (gr_rect
    (start 0 0)
    (end 40 16)
    (layer "User.4")
    (uuid "8cb5a7ba-335d-4917-9b0b-efa4a7d38e40")
  )
  (gr_text "IMPEDANCE TABLE"
    (at 0 20 0)
    (layer "User.6")
    (uuid "afcafcfb-b3fc-4338-9b9a-917f96a8ecdc")
  )
  (gr_rect
    (start 0 21)
    (end 40 30)
    (layer "User.6")
    (uuid "9af73f77-a717-4896-ac91-e0684a71d0ea")
  )
  (group "kibot_table_csv_impedance_table"
    (uuid "97c94a25-9c9f-48a5-a72f-6473f597f678")
    (members "9af73f77-a717-4896-ac91-e0684a71d0ea" "afcafcfb-b3fc-4338-9b9a-917f96a8ecdc")
  )
)
""",
                encoding="utf-8",
            )
            (root / "project.kicad_sch").write_text(
                """
(kicad_sch
  (symbol (lib_id "Device:R") (in_bom yes) (on_board yes) (dnp no)
    (property "Reference" "R1") (property "Value" "10k"))
  (symbol (lib_id "Device:R") (in_bom yes) (on_board yes) (dnp no)
    (property "Reference" "R2") (property "Value" "10k"))
  (symbol (lib_id "Device:C") (in_bom yes) (on_board yes) (dnp no)
    (property "Reference" "C1") (property "Value" "100n"))
  (symbol (lib_id "power:GND")
    (property "Reference" "#PWR01") (property "Value" "GND"))
  (symbol (lib_id "Device:LED") (in_bom yes) (on_board yes) (dnp yes)
    (property "Reference" "D1") (property "Value" "LED"))
)
""",
                encoding="utf-8",
            )
            config_dir = root / ".boardwright"
            config_dir.mkdir()
            (config_dir / "project.yaml").write_text(
                """project:
  id: DEMO
  name: Demo Project
  pcba_name: Demo PCBA
  pcb_name: Demo PCB
  board_revision: B
  company: Demo Co
  designer: A. Designer
  git_url: https://github.com/owner/demo.git
release:
  version: v1.2.3
  date: 2026-07-05
documents:
  schematic:
    title: Demo Schematic
    type: SCHEMATIC
    number_source: pcba_name
    revision: C
    revision_scheme: lettered
    drawn_by: RH
    drawn_date: 2026-07-01
  assembly:
    title: Assembly Drawing
    type: ASSEMBLY
    number_source: pcba_name
    revision: C
  fabrication:
    title: Fabrication Drawing
    type: FABRICATION
    number_source: pcb_name
    revision: F
variants:
  dev_default: DRAFT
  preview_default: CHECKED
outputs:
  preview_engine: github-actions
assets:
  logo: assets/logo.png
template:
  sheet_image: assets/sheet-image.png
sheet:
  legal_notice: "PROPERTY OF ${COMPANY}\\nDO NOT COPY."
manufacturing:
  conformal_coating: false
  silkscreen_enabled: false
  manufacturing_standard: IPC-6012 Class 2
  core_material: FR-4
  flammability_rating: UL94V-0
  tg_rating: 170 C
  halogen_free: true
""",
                encoding="utf-8",
            )
            (config_dir / "branches.yaml").write_text(
                "branches:\n  development: dev\n  preview: preview\n  release: main\n",
                encoding="utf-8",
            )
            (config_dir / "legal.yaml").write_text("legal: {}\n", encoding="utf-8")
            (config_dir / "revision_history.yaml").write_text(
                "revision_history: {}\n",
                encoding="utf-8",
            )
            kibot_dir = root / "boardwright_resources" / "kibot" / "yaml"
            kibot_dir.mkdir(parents=True)
            (kibot_dir / "kibot_main.yaml").write_text(
                """definitions:
  PCBA_NAME: PCBA NAME
  PCB_NAME: PCB NAME
  BOARD_REVISION: A
  COMPANY: COMPANY
  DESIGNER: F. LAST
  LOGO: 'assets/logos/logo-wordmark-colour.png'
  TEMPLATE_LOGO: 'assets/logos/logo-block-black.png'
  SHEET_LEGAL_NOTICE: ''
  SHEET_WKS: ${KIPRJMOD}/Templates/Boardwright_Template_PCB_GIT_A4.kicad_wks
  GIT_URL: ''
""",
                encoding="utf-8",
            )

            result = prepare_pcb_tables(root)

            self.assertEqual(result.total, 3)
            self.assertEqual(
                result.rows,
                (("THT", 1, 0, 1), ("SMT", 1, 1, 2), ("Total", 2, 1, 3)),
            )
            self.assertEqual(
                result.csv_path.read_text(encoding="utf-8").replace("\r\n", "\n"),
                "Type,Front Side,Back Side,Total\nTHT,1,0,1\nSMT,1,1,2\nTotal,2,1,3\n",
            )

            pcb = (root / "boardwright.kicad_pcb").read_text(encoding="utf-8")
            self.assertIn('(gr_text "Front Side"', pcb)
            self.assertIn('(gr_text "Back Side"', pcb)
            self.assertIn('(gr_text "THT"', pcb)
            self.assertIn('(gr_text "SMT"', pcb)
            self.assertEqual(4, pcb.count("(gr_line"))
            self.assertIn("(justify left)", pcb)
            self.assertNotIn("(justify center", pcb)
            self.assertIn("(bold yes)", pcb)
            self.assertIn('face "Arimo"', pcb)
            self.assertIn("IMPEDANCE TABLE", pcb)
            self.assertIn("NO IMPEDANCE CONTROLLED TRACES", pcb)
            self.assertIn("kibot_table_csv_impedance_table", pcb)
            fabrication_notes = (
                root
                / "Manufacturing"
                / "Fabrication"
                / "boardwright-fabrication_notes.txt"
            ).read_text(encoding="utf-8")
            fabrication_summary = (
                root
                / "Manufacturing"
                / "Fabrication"
                / "boardwright-fabrication_summary.txt"
            ).read_text(encoding="utf-8")
            component_summary = (
                root
                / "Manufacturing"
                / "Assembly"
                / "boardwright-component_summary.txt"
            ).read_text(encoding="utf-8")
            self.assertNotIn("${bb_w_mm}", fabrication_notes)
            self.assertIn("NO IMPEDANCE", pcb)
            self.assertNotIn("REFER TO IMPEDANCE TABLE", fabrication_notes)
            self.assertNotIn("#?stackup", fabrication_notes)
            note_numbers = [
                int(match.group(1))
                for match in re.finditer(r"^(\d+)\)", fabrication_notes, re.MULTILINE)
            ]
            self.assertEqual(list(range(1, len(note_numbers) + 1)), note_numbers)
            self.assertIn("\n1)", fabrication_notes)
            self.assertNotRegex(fabrication_notes, r"(?m)^\d+\) {2,}")
            self.assertIn("FABRICATE PER IPC-6012 CLASS 2", fabrication_notes)
            self.assertIn("NO SILKSCREEN LEGEND REQUIRED", fabrication_notes)
            self.assertIn("CONFORMAL COATING IS NOT REQUIRED", fabrication_notes)
            self.assertIn("CORE MATERIAL: FR-4", fabrication_notes)
            self.assertIn("UL94V-0 REQUIREMENTS", fabrication_notes)
            self.assertIn("\tBOARD SIZE\t\t\t\t", fabrication_notes)
            self.assertIn("\tMIN. HOLE (PTH)\t\t\t", fabrication_notes)
            self.assertIn("\tMIN. HOLE (NPTH)\t\t", fabrication_notes)
            self.assertIn("\tANNULAR RING\t\t\t", fabrication_notes)
            self.assertIn("\tHOLE TO HOLE\t\t\t", fabrication_notes)
            self.assertIn("FABRICATION SNAPSHOT", fabrication_summary)
            self.assertIn("COMPONENT SNAPSHOT", component_summary)
            self.assertTrue(
                (root / "Manufacturing" / "Assembly" / "boardwright-assembly_notes.txt").is_file()
            )
            kibot_main = (kibot_dir / "kibot_main.yaml").read_text(encoding="utf-8")
            self.assertIn("PCBA_NAME: 'Demo PCBA'", kibot_main)
            self.assertIn("PCB_NAME: 'Demo PCB'", kibot_main)
            self.assertIn("BOARD_REVISION: 'B'", kibot_main)
            self.assertIn("PROJECT_NUMBER: 'Demo Project'", kibot_main)
            self.assertNotIn("PCBA_NUMBER:", kibot_main)
            self.assertNotIn("PCB_NUMBER:", kibot_main)
            self.assertIn("DOCUMENT_TYPE: 'SCHEMATIC'", kibot_main)
            self.assertIn("DRAWING_TITLE: 'DEMO SCHEMATIC'", kibot_main)
            self.assertIn("DRAWING_NUMBER: 'Demo PCBA'", kibot_main)
            self.assertIn("DRAWING_REVISION: 'C'", kibot_main)
            self.assertIn("RELEASE_VERSION: 'v1.2.3'", kibot_main)
            self.assertNotIn("CHECKED_BY:", kibot_main)
            self.assertNotIn("CHECKED_DATE:", kibot_main)
            self.assertIn("DRAWN_DATE: '2026-07-01'", kibot_main)
            self.assertIn("COMPANY: 'Demo Co'", kibot_main)
            self.assertIn("TEMPLATE_LOGO: 'assets/sheet-image.png'", kibot_main)
            self.assertIn(
                "SHEET_LEGAL_NOTICE: 'PROPERTY OF Demo Co\\nDO NOT COPY.'",
                kibot_main,
            )
            self.assertIn(
                "SHEET_WKS: '${KIPRJMOD}/Templates/Boardwright_Template_PCB_A3.kicad_wks'",
                kibot_main,
            )
            self.assertIn("GIT_URL: 'https://github.com/owner/demo.git'", kibot_main)
            fabrication_config = (kibot_dir / "kibot_document_fabrication.generated.yaml").read_text(encoding="utf-8")
            assembly_config = (kibot_dir / "kibot_document_assembly.generated.yaml").read_text(encoding="utf-8")
            self.assertIn("DOCUMENT_TYPE: 'FABRICATION'", fabrication_config)
            self.assertIn("DRAWING_TITLE: 'FABRICATION DRAWING'", fabrication_config)
            self.assertIn("DRAWING_NUMBER: 'Demo PCB'", fabrication_config)
            self.assertIn("DRAWN_BY: 'RH'", fabrication_config)
            self.assertIn("DRAWN_DATE: '2026-07-01'", fabrication_config)
            self.assertIn("DOCUMENT_TYPE: 'ASSEMBLY'", assembly_config)
            self.assertIn("DRAWING_TITLE: 'ASSEMBLY DRAWING'", assembly_config)
            self.assertIn("DRAWING_NUMBER: 'Demo PCBA'", assembly_config)
            self.assertIn("DRAWN_BY: 'RH'", assembly_config)
            self.assertIn("DRAWN_DATE: '2026-07-01'", assembly_config)
            self.assertIn("SHEET_WKS: '${KIPRJMOD}/.boardwright/generated_worksheets/pcb_page_title.kicad_wks'", fabrication_config)
            generated_worksheet = root / ".boardwright" / "generated_worksheets" / "pcb_page_title.kicad_wks"
            generated_worksheet_text = generated_worksheet.read_text(encoding="utf-8")
            self.assertIn("${TITLE}", generated_worksheet_text)
            self.assertNotIn("${DRAWING_TITLE}", generated_worksheet_text)
            self.assertIn("${DRAWN_BY}", generated_worksheet_text)
            badges = (root / ".boardwright" / "readme_badges.txt").read_text(encoding="utf-8")
            self.assertIn("badge.svg?branch=dev", badges)
            self.assertIn("actions/workflows/dev-preview.yaml", badges)
            self.assertIn("actions/workflows/main-outputs.yaml", badges)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_fabrication_notes_omit_blank_manufacturing_requirements_and_wrap_notes(self) -> None:
        template = Path("boardwright_resources/kibot/resources/templates/fabrication_notes.txt").read_text(
            encoding="utf-8"
        )
        long_note = (
            "This fabrication instruction is deliberately long so it should wrap at a "
            "word boundary instead of staying as one hard to read line in the generated notes."
        )
        values = {
            "manufacturing_standard_note": "",
            "pcb_finish_cap": "ENIG",
            "solder_mask_color_text_cap": "GREEN",
            "silkscreen_note": kicad_tables._silkscreen_note(False, "YELLOW"),
            "tented_vias_note": kicad_tables._tented_vias_note(True),
            "rohs_note": kicad_tables._rohs_note(None),
            "material_requirements_block": kicad_tables._material_requirements_block(
                "",
                "",
                "",
                False,
                False,
                "Demo Co",
            ),
            "bb_w_mm": "40.000",
            "bb_h_mm": "16.000",
            "thickness_mm": "1.600",
            "track_mm": "0.200",
            "clearance_mm": "0.200",
            "drill_pth_real_mm": "0.600",
            "drill_npth_real_mm": "0.000",
            "oar_mm": "0.150",
            "c2h_mm": "0.254",
            "c2e_mm": "0.250",
            "h2h_mm": "0.254",
            "conformal_coating_note": kicad_tables._conformal_coating_note(None),
            "fabrication_extra_notes": kicad_tables._extra_note_block(long_note),
        }

        notes = kicad_tables._render_note_template(template, values)
        numbers = [int(match.group(1)) for match in re.finditer(r"^(\d+)\)", notes, re.MULTILINE)]

        self.assertEqual(list(range(1, len(numbers) + 1)), numbers)
        self.assertNotIn("@NOTE@", notes)
        self.assertNotRegex(notes, r"(?m)^\d+\) {2,}")
        self.assertNotIn("FABRICATE PER .", notes)
        self.assertNotIn("PCB MATERIAL REQUIREMENTS", notes)
        self.assertNotIn("CORE MATERIAL:", notes)
        self.assertNotIn("FLAMMABILITY RATING", notes)
        self.assertNotIn("Tg", notes)
        self.assertNotIn("RoHS", notes)
        self.assertNotIn("CONFORMAL COATING", notes)
        self.assertNotIn(long_note, notes)
        self.assertTrue(all(len(line.expandtabs(4)) <= 88 for line in notes.splitlines()))

    def test_prepare_pcb_tables_writes_impedance_table_when_configured(self) -> None:
        root = Path("tests/.tmp_kicad_tables_impedance")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            (root / "boardwright.kicad_pro").write_text(
                """{
  "pcbnew": {
    "page_layout_descr_file": "Templates/Boardwright_Template_PCB_A3.kicad_wks"
  }
}
""",
                encoding="utf-8",
            )
            (root / "boardwright.kicad_pcb").write_text(
                """
(kicad_pcb
  (gr_text_box ""
    (start 0 0)
    (end 10 10)
    (uuid "511273fd-c939-4feb-bf05-ae1b43c3644e")
  )
  (gr_rect
    (start 0 0)
    (end 40 16)
    (layer "User.4")
    (uuid "8cb5a7ba-335d-4917-9b0b-efa4a7d38e40")
  )
  (gr_text "IMPEDANCE TABLE"
    (at 0 20 0)
    (layer "User.6")
    (uuid "afcafcfb-b3fc-4338-9b9a-917f96a8ecdc")
  )
  (gr_rect
    (start 0 21)
    (end 40 30)
    (layer "User.6")
    (uuid "9af73f77-a717-4896-ac91-e0684a71d0ea")
  )
  (group "kibot_table_csv_impedance_table"
    (uuid "97c94a25-9c9f-48a5-a72f-6473f597f678")
    (members "9af73f77-a717-4896-ac91-e0684a71d0ea" "afcafcfb-b3fc-4338-9b9a-917f96a8ecdc")
  )
)
""",
                encoding="utf-8",
            )
            config_dir = root / ".boardwright"
            config_dir.mkdir()
            (config_dir / "project.yaml").write_text(
                """project:
  id: DEMO
  name: Demo Project
  pcba_name: Demo PCBA
  pcb_name: Demo PCB
  board_revision: B
  company: Demo Co
  designer: A. Designer
  git_url: https://github.com/owner/demo.git
release:
  version: v1.2.3
  date: 2026-07-05
documents:
  schematic:
    title: Demo Schematic
    type: SCHEMATIC
    number_source: pcba_name
    revision: C
    revision_scheme: lettered
    drawn_by: RH
    drawn_date: 2026-07-01
  assembly:
    title: Assembly Drawing
    type: ASSEMBLY
    number_source: pcba_name
    revision: C
  fabrication:
    title: Fabrication Drawing
    type: FABRICATION
    number_source: pcb_name
    revision: F
variants:
  dev_default: DRAFT
  preview_default: CHECKED
outputs:
  preview_engine: github-actions
assets:
  logo: assets/logo.png
template:
  sheet_image: assets/sheet-image.png
sheet:
  legal_notice: "PROPERTY OF ${COMPANY}\\nDO NOT COPY."
manufacturing:
  impedance_enabled: true
  impedance_table:
    - transmission_line: Diff Pair A
      impedance_ohms: "90"
      tolerance_ohms: "10"
      layer: F.Cu
      trace_width_mm: "0.15"
      gap_mm: "0.12"
      ref_layers: GND
""",
                encoding="utf-8",
            )
            (config_dir / "branches.yaml").write_text(
                "branches:\n  development: dev\n  preview: preview\n  release: main\n",
                encoding="utf-8",
            )
            (config_dir / "legal.yaml").write_text("legal: {}\n", encoding="utf-8")
            (config_dir / "revision_history.yaml").write_text(
                "revision_history: {}\n",
                encoding="utf-8",
            )
            kibot_dir = root / "boardwright_resources" / "kibot" / "yaml"
            kibot_dir.mkdir(parents=True)
            (kibot_dir / "kibot_main.yaml").write_text(
                """definitions:
  PCBA_NAME: PCBA NAME
  PCB_NAME: PCB NAME
  BOARD_REVISION: A
  COMPANY: COMPANY
  DESIGNER: F. LAST
  LOGO: 'assets/logos/logo-wordmark-colour.png'
  TEMPLATE_LOGO: 'assets/logos/logo-block-black.png'
  SHEET_LEGAL_NOTICE: ''
  SHEET_WKS: ${KIPRJMOD}/Templates/Boardwright_Template_PCB_GIT_A4.kicad_wks
  GIT_URL: ''
""",
                encoding="utf-8",
            )

            prepare_pcb_tables(root)

            csv_path = root / "Manufacturing" / "Fabrication" / "boardwright-impedance_table.csv"
            self.assertTrue(csv_path.is_file())
            self.assertIn("Diff Pair A", csv_path.read_text(encoding="utf-8"))
            fabrication_notes = (
                root
                / "Manufacturing"
                / "Fabrication"
                / "boardwright-fabrication_notes.txt"
            ).read_text(encoding="utf-8")
            self.assertIn("REFER TO IMPEDANCE TABLE", fabrication_notes)
            self.assertIn("CONFIRM TRACE WIDTHS AND SPACINGS", fabrication_notes)
            self.assertNotIn("#?stackup", fabrication_notes)
            pcb = (root / "boardwright.kicad_pcb").read_text(encoding="utf-8")
            self.assertIn("Diff Pair A", pcb)
            self.assertNotIn("NO IMPEDANCE CONTROLLED TRACES", pcb)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_prepare_pcb_tables_leaves_badges_empty_without_github_repo(self) -> None:
        root = Path("tests/.tmp_kicad_tables_no_badges")
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            config = type(
                "Config",
                (),
                {
                    "root": root,
                    "github_repo": "",
                    "dev_branch": "dev",
                    "preview_branch": "preview",
                    "release_branch": "main",
                    "preview_workflow": "dev-preview.yaml",
                    "main_workflow": "main-outputs.yaml",
                    "project": {"project": {"git_url": ""}},
                },
            )()

            from boardwright.kicad_tables import _readme_badges, _write_readme_badges

            with patch.object(kicad_tables, "remote_url", return_value=""):
                _write_readme_badges(root, config)
                badges = (root / ".boardwright" / "readme_badges.txt").read_text(encoding="utf-8")
                self.assertEqual("", _readme_badges(config))
                self.assertEqual("", badges)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
