# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path

import yaml

from boardwright.combined_pdf import (
    prepare_native_combined_outputs,
    _read_combined_sheet_manifest,
    _titles_from_kibot_pages,
    build_combined_pdf_plan,
    read_combined_sheet_title,
    read_combined_sheet_total,
    write_combined_sheet_manifest,
    format_combined_pdf_summary,
)


class CombinedPdfTests(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path("tests") / ".tmp_combined_pdf" / uuid.uuid4().hex
        root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(root.parent, ignore_errors=True))
        return root

    def config(self, root: Path, **outputs):
        return type(
            "Config",
            (),
            {
                "root": root,
                "output_settings": outputs,
            },
        )()

    def test_plan_is_disabled_by_default(self) -> None:
        root = self.make_root()

        plan = build_combined_pdf_plan(self.config(root))

        self.assertFalse(plan.enabled)
        self.assertTrue(plan.toc_enabled)
        self.assertTrue(plan.page_numbers_enabled)
        self.assertEqual(root.resolve() / "Manufacturing" / "boardwright-combined.pdf", plan.output_path)

    def test_plan_discovers_schematic_assembly_and_fabrication_pdfs(self) -> None:
        root = self.make_root()
        for directory, name in (
            ("Schematic", "demo-schematic.pdf"),
            ("Manufacturing/Assembly", "demo-assembly.pdf"),
            ("Manufacturing/Fabrication", "demo-fabrication.pdf"),
        ):
            path = root / directory
            path.mkdir(parents=True)
            (path / name).write_bytes(b"%PDF placeholder")
            (path / name.replace(".pdf", "-1.pdf")).write_bytes(b"%PDF page shard")

        plan = build_combined_pdf_plan(
            self.config(
                root,
                combined_review_pdf=True,
                combined_pdf_name="Manufacturing/ignored.pdf",
                combined_pdf_toc=False,
                combined_pdf_page_numbers=False,
            )
        )

        self.assertTrue(plan.enabled)
        self.assertTrue(plan.toc_enabled)
        self.assertTrue(plan.page_numbers_enabled)
        self.assertEqual(root.resolve() / "Manufacturing" / "boardwright-combined.pdf", plan.output_path)
        self.assertEqual(("Schematic", "Assembly", "Fabrication"), tuple(item.title for item in plan.inputs))
        self.assertTrue(all(not item.path.stem.endswith("-1") for item in plan.inputs))
        self.assertIn("boardwright-combined.pdf", format_combined_pdf_summary(plan))

    def test_manifest_is_enabled_with_combined_review_pdf(self) -> None:
        root = self.make_root()
        (root / "boardwright.kicad_sch").write_text(
            """(kicad_sch
	(title_block
		(title "COVER PAGE")
	)
)
""",
            encoding="utf-8",
        )

        manifest = write_combined_sheet_manifest(
            self.config(root, combined_review_pdf=True)
        )

        self.assertTrue(manifest.enabled)
        self.assertEqual(1, read_combined_sheet_total(root))

    def test_reads_complete_combined_sheet_manifest_for_bookmarks(self) -> None:
        root = self.make_root()
        manifest = root / ".boardwright" / "combined_sheet_titles.env"
        manifest.parent.mkdir()
        manifest.write_text(
            """COMBINED_SHEET_TOTAL=2
SHEET_NAME_1=COVER PAGE
SHEET_SECTION_1=Schematic
SHEET_SOURCE_KIND_1=schematic
SHEET_SOURCE_PAGE_1=1
SHEET_NAME_2=TOP ASSEMBLY
SHEET_SECTION_2=Assembly
SHEET_SOURCE_KIND_2=assembly
SHEET_SOURCE_PAGE_2=1
""",
            encoding="utf-8",
        )

        sheets = _read_combined_sheet_manifest(root)

        self.assertEqual(("COVER PAGE", "TOP ASSEMBLY"), tuple(sheet.title for sheet in sheets))

    def test_disabled_native_combined_outputs_remove_generated_files_and_main_patch(self) -> None:
        root = self.make_root()
        yaml_dir = root / "boardwright_resources" / "kibot" / "yaml"
        yaml_dir.mkdir(parents=True)
        (yaml_dir / "kibot_main.yaml").write_text(
            """groups:

  # Boardwright generated combined native outputs -- start
  - name: combined_native
    outputs:
      - pdf_combined_native_001
  # Boardwright generated combined native outputs -- end

  - name: all_group
    outputs:
      - assembly
      - combined_native

import:
  # Boardwright generated combined native import -- start
  - file: kibot_out_pdf_combined_native.yaml
  # Boardwright generated combined native import -- end

  # Compress fabrication files
""",
            encoding="utf-8",
        )
        native_yaml = yaml_dir / "kibot_out_pdf_combined_native.yaml"
        native_yaml.write_text("outputs: []\n", encoding="utf-8")
        worksheet_dir = root / ".boardwright" / "generated_worksheets"
        worksheet_dir.mkdir(parents=True)
        worksheet = worksheet_dir / "combined_sheet_001.kicad_wks"
        worksheet.write_text("worksheet", encoding="utf-8")
        schematic_worksheet = worksheet_dir / "combined_schematic.kicad_wks"
        schematic_worksheet.write_text("worksheet", encoding="utf-8")

        result = prepare_native_combined_outputs(self.config(root, combined_review_pdf=False))

        self.assertFalse(result.manifest.enabled)
        self.assertFalse(native_yaml.exists())
        self.assertFalse(worksheet.exists())
        self.assertFalse(schematic_worksheet.exists())
        main = (yaml_dir / "kibot_main.yaml").read_text(encoding="utf-8")
        self.assertNotIn("Boardwright generated combined native", main)
        self.assertNotIn("combined_native", main)


    def test_writes_native_combined_sheet_manifest_for_existing_toc(self) -> None:
        root = self.make_root()
        (root / "boardwright.kicad_sch").write_text(
            """(kicad_sch
	(title_block
		(title "COVER PAGE")
	)
	(sheet
		(property "Sheetname" "POWER")
		(property "Sheetfile" "power.kicad_sch")
		(instances
			(project "demo"
				(path "/power"
					(page "2")
				)
			)
		)
	)
)
""",
            encoding="utf-8",
        )
        (root / "boardwright_resources" / "kibot" / "yaml").mkdir(parents=True)
        (root / "boardwright_resources" / "kibot" / "yaml" / "kibot_out_pdf_assembly.yaml").write_text(
            """outputs:
- name: pdf_assembly
  options:
    pages:
      - title: 'TOP ASSEMBLY'
""",
            encoding="utf-8",
        )
        (root / "boardwright_resources" / "kibot" / "yaml" / "kibot_out_pdf_fabrication.yaml").write_text(
            """outputs:
- name: pdf_fabrication
  options:
    pages:
      - title: 'L1-L2 DRILL MAP'
      - title: 'L1 COPPER'
""",
            encoding="utf-8",
        )

        manifest = write_combined_sheet_manifest(
            self.config(root, combined_review_pdf=True)
        )

        self.assertTrue(manifest.enabled)
        self.assertEqual(5, read_combined_sheet_total(root))
        self.assertEqual("COVER PAGE", read_combined_sheet_title(root, 1))
        self.assertEqual("POWER", read_combined_sheet_title(root, 2))
        self.assertEqual("TOP ASSEMBLY", read_combined_sheet_title(root, 3))
        self.assertEqual("L1-L2 DRILL MAP", read_combined_sheet_title(root, 4))
        self.assertEqual("L1 COPPER", read_combined_sheet_title(root, 5))


    def test_prepares_native_pcb_outputs_and_numbered_worksheets(self) -> None:
        root = self.make_root()
        templates = root / "Templates"
        templates.mkdir()
        (templates / "Boardwright_Template_PCB_GIT_A4.kicad_wks").write_text(
            '(kicad_wks\n\t(tbtext "${DRAWING_TITLE}"\n)\n\t(tbtext "${DRAWING_NUMBER}"\n)\n\t(tbtext "${#} OF ${##}"\n)\n)',
            encoding="utf-8",
        )
        (templates / "Schematic.kicad_wks").write_text(
            '(kicad_wks\n\t(tbtext "SHEET ${#} OF ${##}"\n)\n)',
            encoding="utf-8",
        )
        (root / "demo.kicad_pro").write_text(
            json.dumps({"schematic": {"page_layout_descr_file": "Templates/Schematic.kicad_wks"}}),
            encoding="utf-8",
        )
        yaml_dir = root / "boardwright_resources" / "kibot" / "yaml"
        yaml_dir.mkdir(parents=True)
        (yaml_dir / "kibot_main.yaml").write_text(
            """groups:

  - name: all_group
    outputs:
      - assembly

  - name: all_group_k9
    outputs:
      - assembly

import:

  # Compress fabrication files

definitions:
  SHEET_WKS: ${KIPRJMOD}/Templates/Boardwright_Template_PCB_GIT_A4.kicad_wks
  COLOR_THEME: KiCad_Theme
  PCBA_NAME: Demo PCBA
  PCB_NAME: Demo PCB
  ASSEMBLY_SCALING: 1.0
  FAB_SCALING: 1.0
""",
            encoding="utf-8",
        )
        (yaml_dir / "kibot_document_assembly.generated.yaml").write_text(
            """definitions:
  DOCUMENT_TYPE: 'ASSEMBLY'
  DRAWING_TITLE: 'ASSEMBLY DRAWING'
  DRAWING_NUMBER: 'Demo PCBA'
""",
            encoding="utf-8",
        )
        (yaml_dir / "kibot_document_fabrication.generated.yaml").write_text(
            """definitions:
  DOCUMENT_TYPE: 'FABRICATION'
  DRAWING_TITLE: 'FABRICATION DRAWING'
  DRAWING_NUMBER: 'Demo PCB'
""",
            encoding="utf-8",
        )
        (yaml_dir / "kibot_out_pdf_assembly.yaml").write_text(
            """outputs:
- name: pdf_assembly
  type: pcb_print
  options:
    output: '%f-assembly%I%v.%x'
    format: 'PDF'
    title: 'ASSEMBLY DOCUMENT'
    sheet_reference_layout: '@SHEET_WKS@'
    pages:
      - scaling: @SCALING@
        title: 'TOP ASSEMBLY'
        sheet: TOP ASSEMBLY
""",
            encoding="utf-8",
        )
        (yaml_dir / "kibot_out_pdf_fabrication.yaml").write_text(
            """outputs:
- name: pdf_fabrication
  type: pcb_print
  options:
    output: '%f-fabrication%I%v.%x'
    format: 'PDF'
    title: 'FABRICATION DOCUMENT'
    sheet_reference_layout: '@SHEET_WKS@'
    drill:
      unify_pth_and_npth: '@PTH_NPTH@'
      group_slots_and_round_holes: '@GROUP_ROUND_SLOTS@'
    pages:
      - scaling: @SCALING@
        title: 'L1 COPPER'
        sheet: L1 COPPER
""",
            encoding="utf-8",
        )

        result = prepare_native_combined_outputs(
            self.config(root, combined_review_pdf=True)
        )

        self.assertEqual(("pdf_combined_native_002", "pdf_combined_native_003"), result.output_names)
        self.assertIn("2 OF 3", result.worksheets[0].read_text(encoding="utf-8"))
        self.assertIn("3 OF 3", result.worksheets[1].read_text(encoding="utf-8"))
        assembly_worksheet = result.worksheets[0].read_text(encoding="utf-8")
        fabrication_worksheet = result.worksheets[1].read_text(encoding="utf-8")
        self.assertIn("TOP ASSEMBLY", assembly_worksheet)
        self.assertIn("Demo PCBA", assembly_worksheet)
        self.assertIn("L1 COPPER", fabrication_worksheet)
        self.assertIn("Demo PCB", fabrication_worksheet)
        generated_schematic = root / ".boardwright" / "generated_worksheets" / "combined_schematic.kicad_wks"
        self.assertIn(
            "SHEET ${#} OF ${COMBINED_SHEET_TOTAL}",
            generated_schematic.read_text(encoding="utf-8"),
        )
        project = json.loads((root / "demo.kicad_pro").read_text(encoding="utf-8"))
        self.assertEqual(
            "${KIPRJMOD}/.boardwright/generated_worksheets/combined_schematic.kicad_wks",
            project["schematic"]["page_layout_descr_file"],
        )
        generated = result.yaml_path.read_text(encoding="utf-8")
        self.assertIn("pdf_combined_native_002", generated)
        self.assertIn("combined-002-top-assembly", generated)
        parsed = yaml.safe_load(generated)
        self.assertEqual("pdf_combined_native_002", parsed["outputs"][0]["name"])
        self.assertIn("pages", parsed["outputs"][0]["options"])
        self.assertEqual("yes", parsed["outputs"][1]["options"]["drill"]["unify_pth_and_npth"])
        main = (yaml_dir / "kibot_main.yaml").read_text(encoding="utf-8")
        self.assertIn("combined_native", main)
        self.assertIn("kibot_out_pdf_combined_native.yaml", main)

    def test_plan_uses_native_combined_page_shards(self) -> None:
        root = self.make_root()
        (root / "Schematic").mkdir()
        (root / "Schematic" / "demo-schematic.pdf").write_bytes(b"%PDF placeholder")
        combined = root / "Manufacturing" / "CombinedSources"
        combined.mkdir(parents=True)
        (combined / "demo-combined-003-top-assembly-1.pdf").write_bytes(b"%PDF placeholder")
        (combined / "demo-combined-004-l1-copper-1.pdf").write_bytes(b"%PDF placeholder")
        (root / "Manufacturing" / "Assembly").mkdir(parents=True)
        (root / "Manufacturing" / "Assembly" / "demo-assembly.pdf").write_bytes(b"%PDF placeholder")

        plan = build_combined_pdf_plan(self.config(root, combined_review_pdf=True))

        self.assertEqual(
            ("Schematic", "TOP ASSEMBLY", "L1 COPPER"),
            tuple(item.title for item in plan.inputs),
        )
        self.assertTrue(all("CombinedSources" in str(item.path) for item in plan.inputs[1:]))

    def test_extracts_expanded_kibot_page_titles(self) -> None:
        root = self.make_root()
        yaml = root / "kibot_pages.yaml"
        yaml.write_text(
            """outputs:
- name: pdf_fabrication
  options:
    title: 'FABRICATION DOCUMENT'
    pages:
      - title: 'TOP FABRICATION'
      - title: 'L1-L2 DRILL MAP'
      - title: 'L1 COPPER'
definitions:
  DOC_TITLE: FABRICATION
""",
            encoding="utf-8",
        )

        self.assertEqual(
            ("TOP FABRICATION", "L1-L2 DRILL MAP", "L1 COPPER"),
            _titles_from_kibot_pages(yaml),
        )


if __name__ == "__main__":
    unittest.main()
