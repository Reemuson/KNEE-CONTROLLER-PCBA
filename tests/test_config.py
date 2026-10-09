# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
import shutil
from pathlib import Path

from boardwright.config import BoardwrightConfig, _read_simple_yaml, load_config, update_project_config


class ConfigTests(unittest.TestCase):
    def test_simple_yaml_reads_folded_text(self) -> None:
        parsed = _read_simple_yaml(
            """legal:
  safety_notice: >
    Verify isolation, creepage, and clearance.
    Confirm regulatory compliance.
"""
        )

        self.assertEqual(
            "Verify isolation, creepage, and clearance. Confirm regulatory compliance.",
            parsed["legal"]["safety_notice"],
        )

    def test_update_project_config_edits_metadata_and_variants(self) -> None:
        root = Path.cwd() / ".test_config_workspace"
        if root.exists():
            shutil.rmtree(root)
        try:
            root.mkdir()
            config_dir = root / ".boardwright"
            config_dir.mkdir()
            (config_dir / "project.yaml").write_text(
                """project:
  name: Old Project
  pcba_name: Old PCBA
  pcb_name: Old PCB
  board_revision: A
  company: Old Co
  designer: Old Designer
  git_url: ""
variants:
  dev_default: DRAFT
  preview_default: PRELIMINARY
  main_default: CHECKED
  release_default: RELEASED
outputs:
  preview_engine: github-actions
  commit_generated_outputs_to_main: false
  use_preview_branch: true
  release_include_source_archive: false
assets:
  logo: old.png
  product_image: ""
template:
  sheet_image: old-image.png
sheet:
  legal_notice: "OLD\\nNOTICE"
manufacturing:
  rohs_pb_free: true
  conformal_coating: false
  tented_vias: true
  impedance_enabled: false
  silkscreen_enabled: true
  manufacturing_standard: IPC-6012 Class 2
  core_material: FR-4
  flammability_rating: UL94V-0
  tg_rating: 170 C
  halogen_free: true
  fabrication_notes: "Old fab"
  assembly_notes: "Old assembly"
  testpoint_policy: "Old testpoint"
  impedance_notes: "Old impedance"
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
            (config_dir / "legal.yaml").write_text(
                """boardwright:
  tooling_license: LicenseRef-Boardwright-Source-Available
  inherited_notice_file: LICENSES/Nguyen-MIT.txt
  third_party_notice_file: THIRD_PARTY_NOTICES.md
  default_profile: public-hardware
legal_profiles:
  public-hardware:
    hardware_design_license: CERN-OHL-W-2.0
    compatibility:
      enabled: false
      wording: ""
      trademark_owner: ""
    branding_reserved: true
    safety_notice: "Safe by default"
  compatibility-friendly:
    hardware_design_license: CERN-OHL-S-2.0
    compatibility:
      enabled: true
      wording: compatible with selected instruments
      trademark_owner: the original manufacturer
    branding_reserved: true
    safety_notice: "Compatibility-safe"
downstream_project_defaults:
  profile: public-hardware
  hardware_design_license: CERN-OHL-W-2.0
  copyright_holder: Old Co
  notice_file: OLD_NOTICE.md
  third_party_notice_file: OLD_THIRD_PARTY.md
  safety_notice: "Old safety"
""",
                encoding="utf-8",
            )
            (config_dir / "revision_history.yaml").write_text(
                "revision_history:\n  slots: 4\n  preflight_slots: 12\n",
                encoding="utf-8",
            )
            (root / "Templates").mkdir()
            (root / "Templates" / "Boardwright_Template_PCB_A4.kicad_wks").write_text(
                "",
                encoding="utf-8",
            )
            (root / "Templates" / "CME_Template_A3.kicad_wks").write_text(
                "",
                encoding="utf-8",
            )
            (root / "boardwright.kicad_pro").write_text(
                """{
  "pcbnew": {
    "page_layout_descr_file": "Templates/Boardwright_Template_PCB_A4.kicad_wks"
  },
  "schematic": {
    "page_layout_descr_file": "kicad-embed://CME_Template_A3.kicad_wks"
  }
}
""",
                encoding="utf-8",
            )
            (config_dir / "branches.yaml").write_text("branches:\n  development: dev\n", encoding="utf-8")
            (config_dir / "legal.yaml").write_text("legal: {}\n", encoding="utf-8")
            (config_dir / "revision_history.yaml").write_text(
                "revision_history: {}\n",
                encoding="utf-8",
            )
            config = BoardwrightConfig(
                root=root,
                project=load_config(root).project,
                branches=load_config(root).branches,
                legal=load_config(root).legal,
                revision_history=load_config(root).revision_history,
            )

            update_project_config(
                config,
                project_fields={
                    "name": "New Project",
                    "git_url": "https://github.com/owner/repo.git",
                },
                variant_fields={"preview_default": "checked"},
                asset_fields={"logo": "assets/logo.png"},
                template_fields={
                    "sheet_image": "assets/sheet-image.png",
                },
                sheet_fields={"legal_notice": "NEW\nNOTICE"},
                branch_fields={"development": "develop"},
                output_fields={"commit_generated_outputs_to_main": "true"},
                legal_fields={
                    "profile": "compatibility-friendly",
                    "hardware_design_license": "CERN-OHL-S-2.0",
                    "copyright_holder": "New Co",
                    "notice_file": "NOTICE.md",
                    "safety_notice": "Updated safety",
                },
                manufacturing_fields={
                    "silkscreen_enabled": "false",
                    "manufacturing_standard": "IPC-A-600 Class 2",
                    "core_material": "FR-4",
                    "flammability_rating": "UL94V-0",
                    "tg_rating": "150 C",
                    "halogen_free": "true",
                    "fabrication_notes": "New fab",
                    "assembly_notes": "New assembly",
                    "impedance_table": [
                        {
                            "transmission_line": "Diff Pair A",
                            "impedance_ohms": "90",
                            "tolerance_ohms": "10",
                            "layer": "F.Cu",
                            "trace_width_mm": "0.15",
                            "gap_mm": "0.12",
                            "ref_layers": "GND",
                        }
                    ],
                },
            )

            updated = load_config(root)
            self.assertEqual("New Project", updated.project_id)
            self.assertEqual("New Project", updated.project_name)
            self.assertEqual("Old PCBA", updated.pcba_name)
            self.assertEqual("Old PCB", updated.pcb_name)
            self.assertEqual("A", updated.board_revision)
            self.assertEqual("owner/repo", updated.github_repo)
            updated.project["project"].pop("git_url")
            updated.project["project"]["github_repo"] = "https://github.com/Reemuson/7-087598-700.git"
            self.assertEqual("Reemuson/7-087598-700", updated.github_repo)

            self.assertEqual("CHECKED", updated.preview_variant)
            self.assertEqual("assets/logo.png", updated.assets["logo"])
            self.assertEqual("Templates/CME_Template_A3.kicad_wks", updated.worksheet)
            updated.project["template"]["worksheet"] = "Templates/Explicit_Template.kicad_wks"
            self.assertEqual("Templates/Explicit_Template.kicad_wks", updated.worksheet)
            updated.project["template"].pop("worksheet")
            self.assertEqual("assets/sheet-image.png", updated.template_sheet_image)
            self.assertEqual("assets/sheet-image.png", updated.template_logo)
            self.assertEqual("NEW\nNOTICE", updated.sheet_legal_notice)
            self.assertEqual("develop", updated.dev_branch)
            self.assertTrue(updated.commit_generated_outputs_to_main)
            self.assertEqual("compatibility-friendly", updated.legal_profile)
            self.assertEqual("CERN-OHL-S-2.0", updated.hardware_design_license)
            self.assertEqual("NOTICE.md", updated.notice_file)
            self.assertEqual("New Co", updated.copyright_holder)
            self.assertEqual("Updated safety", updated.safety_notice)
            self.assertEqual("New fab", updated.manufacturing["fabrication_notes"])
            self.assertFalse(updated.manufacturing["silkscreen_enabled"])
            self.assertEqual("IPC-A-600 Class 2", updated.manufacturing["manufacturing_standard"])
            self.assertEqual(1, len(updated.impedance_entries))
            self.assertEqual("Diff Pair A", updated.impedance_entries[0]["transmission_line"])
        finally:
            if root.exists():
                shutil.rmtree(root)


    def test_defaults_include_document_control_fields(self) -> None:
        root = Path.cwd() / ".test_config_defaults_workspace"
        if root.exists():
            shutil.rmtree(root)
        try:
            from boardwright.config import init_config

            root.mkdir()
            init_config(root, workflows=False)
            config = load_config(root)

            self.assertEqual("A", config.document_settings("schematic")["revision"])
            self.assertEqual("lettered", config.document_settings("schematic")["revision_scheme"])
            self.assertEqual("Boardwright KiCad/KiBot Template", config.project_name)
            self.assertEqual("Boardwright KiCad/KiBot Template", config.pcba_name)
            self.assertEqual("Boardwright KiCad/KiBot Template PCB", config.pcb_name)
            self.assertEqual("SCHEMATIC", config.document_settings("schematic")["type"])
            self.assertEqual("pcba_name", config.document_settings("assembly")["number_source"])
            self.assertEqual("pcb_name", config.document_settings("fabrication")["number_source"])
            self.assertEqual(
                {
                    "document_revisions": {
                        "schematic": {"rows": []},
                        "assembly": {"rows": []},
                        "fabrication": {"rows": []},
                    }
                },
                config.document_revisions,
            )
        finally:
            if root.exists():
                shutil.rmtree(root)


    def test_resolves_document_specific_drawing_variables(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={
                "project": {
                    "name": "Example Project",
                    "pcba_name": "Example Board Assembly",
                    "pcb_name": "Example Bare PCB",
                    "company": "Example Co",
                    "designer": "RH",
                    "board_revision": "C",
                },
                "release": {"version": "v9.9.9", "date": "2026-07-05"},
                "documents": {
                    "schematic": {
                        "title": "Schematic",
                        "type": "SCHEMATIC",
                        "number_source": "pcba_name",
                        "revision": "A",
                        "drawn_by": "RH",
                        "drawn_date": "2026-07-01",
                    },
                    "assembly": {
                        "title": "Assembly Drawing",
                        "type": "ASSEMBLY",
                        "number_source": "pcba_name",
                        "revision": "B",
                    },
                    "fabrication": {
                        "title": "PCB Fabrication Drawing",
                        "type": "FABRICATION",
                        "number_source": "pcb_name",
                        "revision": "D",
                    },
                },
            },
            branches={"branches": {}},
            legal={"legal": {}},
            revision_history={"revision_history": {}},
        )

        schematic = config.drawing_variables("schematic")
        assembly = config.drawing_variables("assembly")
        fabrication = config.drawing_variables("fabrication")

        self.assertEqual("Example Project", schematic["PROJECT_NUMBER"] )
        self.assertEqual("Example Board Assembly", schematic["PCBA_NAME"])
        self.assertEqual("Example Bare PCB", schematic["PCB_NAME"])
        self.assertEqual("SCHEMATIC", schematic["DRAWING_TITLE"])
        self.assertEqual("ASSEMBLY DRAWING", assembly["DRAWING_TITLE"])
        self.assertEqual("PCB FABRICATION DRAWING", fabrication["DRAWING_TITLE"])
        self.assertEqual("Example Board Assembly", schematic["DRAWING_NUMBER"])
        self.assertEqual("Example Board Assembly", assembly["DRAWING_NUMBER"])
        self.assertEqual("Example Bare PCB", fabrication["DRAWING_NUMBER"])
        self.assertEqual("A", schematic["DRAWING_REVISION"])
        self.assertEqual("D", fabrication["DRAWING_REVISION"])
        self.assertEqual("C", fabrication["BOARD_REVISION"])
        self.assertEqual("v9.9.9", fabrication["RELEASE_VERSION"])
        self.assertEqual("RH", assembly["DRAWN_BY"])
        self.assertEqual("2026-07-01", fabrication["DRAWN_DATE"])
        self.assertNotIn("CHECKED_BY", schematic)
        self.assertNotIn("CHECKED_DATE", schematic)
        self.assertNotEqual(fabrication["DRAWING_REVISION"], fabrication["BOARD_REVISION"])
        self.assertNotEqual(fabrication["DRAWING_REVISION"], fabrication["RELEASE_VERSION"])


if __name__ == "__main__":
    unittest.main()
