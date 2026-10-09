# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
import uuid
from unittest.mock import patch

import yaml

from boardwright.errors import BoardwrightError
from boardwright.managed_project import (
    BASE_PATH,
    STATE_PATH,
    PayloadFile,
    _file_hash,
    apply_update_plan,
    build_update_plan,
    update_status,
    write_plan,
)
from boardwright.migration import (
    apply_migration_plan,
    build_migration_plan,
    looks_like_nguyen_project,
)
from boardwright.validation import ValidationIssue


class NguyenMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("tests/.tmp_migration_update") / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.addCleanup(_remove_test_tree, self.root.parent)

    def test_rejects_arbitrary_kicad_repository(self) -> None:
        (self.root / "example.kicad_pro").write_text("{}", encoding="utf-8")
        (self.root / "example.kicad_sch").write_text("(kicad_sch)", encoding="utf-8")
        (self.root / "example.kicad_pcb").write_text("(kicad_pcb)", encoding="utf-8")

        self.assertFalse(looks_like_nguyen_project(self.root))
        with self.assertRaisesRegex(BoardwrightError, "does not match"):
            build_migration_plan(self.root)

    def test_plan_requires_primary_project_when_ambiguous(self) -> None:
        self._write_legacy_fixture()
        shutil.copy2(self.root / "legacy.kicad_pro", self.root / "other.kicad_pro")

        with self.assertRaisesRegex(BoardwrightError, "Multiple KiCad projects"):
            build_migration_plan(self.root)

        plan = build_migration_plan(self.root, Path("legacy.kicad_pro"))
        self.assertEqual("legacy.kicad_pro", plan["project"])

    def test_migration_preserves_design_history_and_license(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        self._write_legacy_fixture()
        self._initialize_git()
        original_schematic = (self.root / "legacy.kicad_sch").read_bytes()
        original_license = (self.root / "LICENSE").read_bytes()
        original_tag = self._git("rev-parse", "legacy-1.2.3")

        plan = build_migration_plan(self.root)
        plan["resolutions"]["pcba_name"] = "Example Assembly"
        plan["resolutions"]["pcb_name"] = "Example PCB"
        plan_path = write_plan(self.root / "migration.yaml", plan)

        apply_migration_plan(plan_path)

        migrated_schematic = (self.root / "legacy.kicad_sch").read_bytes()
        self.assertEqual(
            original_schematic.replace(b"${REVISION}", b"${DRAWING_REVISION}"),
            migrated_schematic,
        )
        self.assertEqual(original_license, (self.root / "LICENSE").read_bytes())
        self.assertEqual(original_tag, self._git("rev-parse", "legacy-1.2.3"))
        self.assertFalse((self.root / "kibot_yaml").exists())
        self.assertFalse((self.root / "kibot_resources").exists())
        self.assertFalse((self.root / ".github/workflows/ci.yaml").exists())
        self.assertTrue((self.root / ".github/workflows/dev-preview.yaml").exists())
        self.assertTrue((self.root / ".boardwright/state.yaml").exists())
        self.assertTrue((self.root / "assets/logos/custom-logo.png").exists())

        project = json.loads((self.root / "legacy.kicad_pro").read_text(encoding="utf-8"))
        self.assertEqual(
            "Templates/Boardwright_Template_GIT.kicad_wks",
            project["schematic"]["page_layout_descr_file"],
        )
        self.assertEqual(
            "Templates/Boardwright_Template_PCB_GIT_A4.kicad_wks",
            project["pcbnew"]["page_layout_descr_file"],
        )
        self.assertNotIn("KDT_Hierarchical_KiBot", json.dumps(project))
        config = yaml.safe_load(
            (self.root / ".boardwright/project.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("Example Assembly", config["project"]["pcba_name"])
        self.assertEqual("Example PCB", config["project"]["pcb_name"])
        self.assertEqual("", config["release"]["version"])
        legal = yaml.safe_load(
            (self.root / ".boardwright/legal.yaml").read_text(encoding="utf-8")
        )
        self.assertIn("migrated-project", legal["legal_profiles"])
        self.assertEqual(
            "migrated-project",
            legal["downstream_project_defaults"]["profile"],
        )
        self.assertIn("## [Unreleased]", (self.root / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertTrue(self._git("status", "--porcelain"))

    def _write_legacy_fixture(self) -> None:
        (self.root / "kibot_yaml").mkdir()
        (self.root / "kibot_resources/templates").mkdir(parents=True)
        (self.root / "kibot_resources").joinpath("custom-logo.png").write_bytes(b"logo")
        (self.root / "Templates").mkdir()
        (self.root / ".github/workflows").mkdir(parents=True)
        project = {
            "pcbnew": {
                "page_layout_descr_file": "Templates/KDT_Template_PCB_GIT_A4.kicad_wks"
            },
            "schematic": {
                "page_layout_descr_file": "Templates/KDT_Template_GIT.kicad_wks"
            },
            "text_variables": {
                "PROJECT_NAME": "Example Project",
                "BOARD_NAME": "Example Board",
                "COMPANY": "Example Company",
                "DESIGNER": "E. Designer",
                "GIT_URL": "https://github.com/example/board.git",
                "LOGO": "kibot_resources/custom-logo.png",
            },
            "meta": {"filename": "KDT_Hierarchical_KiBot.kicad_pro"},
            "cvpcb": {"netlist": "KDT_Hierarchical_KiBot.net"},
        }
        (self.root / "legacy.kicad_pro").write_text(
            json.dumps(project), encoding="utf-8"
        )
        (self.root / "legacy.kicad_sch").write_text(
            '(kicad_sch (title_block (rev "${REVISION}")) '
            '(sheet (property "Sheetname" "Child") '
            '(property "Sheetfile" "child.kicad_sch")))',
            encoding="utf-8",
        )
        (self.root / "child.kicad_sch").write_text(
            '(kicad_sch (title_block (rev "${REVISION}")))',
            encoding="utf-8",
        )
        (self.root / "legacy.kicad_pcb").write_text(
            '(kicad_pcb (gr_rect (start 0 0) (end 1 1) (layer "Edge.Cuts")))',
            encoding="utf-8",
        )
        (self.root / "Templates/KDT_Template_GIT.kicad_wks").write_text(
            "(kicad_wks)", encoding="utf-8"
        )
        (self.root / "Templates/KDT_Template_PCB_GIT_A4.kicad_wks").write_text(
            "(kicad_wks)", encoding="utf-8"
        )
        (self.root / ".github/workflows/ci.yaml").write_text(
            "name: CI\n", encoding="utf-8"
        )
        (self.root / "kibot_resources/templates/readme.txt").write_text(
            "legacy", encoding="utf-8"
        )
        (self.root / "kibot_yaml/kibot_main.yaml").write_text(
            """# KDT_Hierarchical KiBot template
import:
  - file: kibot_out_pdf_schematic.yaml
definitions:
  PROJECT_NAME: 'Example Project'
  BOARD_NAME: 'Example Board'
  COMPANY: 'Example Company'
  DESIGNER: 'E. Designer'
  GIT_URL: 'https://github.com/example/board.git'
  LOGO: 'kibot_resources/custom-logo.png'
  RESOURCES_DIR: kibot_resources
  SHEET_WKS: ${KIPRJMOD}/Templates/KDT_Template_PCB_GIT_A4.kicad_wks
""",
            encoding="utf-8",
        )
        (self.root / "README.md").write_text("# Example\n", encoding="utf-8")
        (self.root / "LICENSE").write_text("Legacy MIT licence\n", encoding="utf-8")
        (self.root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [1.2.3] - 2025-01-01\n\n- Legacy release\n",
            encoding="utf-8",
        )

    def _initialize_git(self) -> None:
        self._git("init", "-b", "migration")
        self._git("config", "user.email", "tests@example.com")
        self._git("config", "user.name", "Boardwright Tests")
        self._git("add", "-A")
        self._git("commit", "-m", "legacy project")
        self._git("tag", "legacy-1.2.3")

    def _git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        return completed.stdout.strip()


class ManagedUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("tests/.tmp_migration_update") / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.addCleanup(_remove_test_tree, self.root.parent)
        (self.root / ".boardwright/managed-base").mkdir(parents=True)
        (self.root / "managed.txt").write_text("alpha\nbeta\nomega\n", encoding="utf-8")
        base = (self.root / "managed.txt").read_bytes()
        digest = __import__("hashlib").sha256(base).hexdigest()
        (self.root / BASE_PATH / digest).write_bytes(base)
        self.state = {
            "schema_version": 1,
            "template_version": "0.0.9",
            "origin": "boardwright",
            "managed_files": {
                "managed.txt": {
                    "sha256": digest,
                    "strategy": "merge",
                    "base": (BASE_PATH / digest).as_posix(),
                }
            },
        }
        (self.root / STATE_PATH).write_text(
            yaml.safe_dump(self.state, sort_keys=False), encoding="utf-8"
        )
        self.incoming = self.root / "incoming.txt"

    def test_status_reports_modified_and_missing_files(self) -> None:
        (self.root / "managed.txt").write_text("custom\n", encoding="utf-8")
        self.state["managed_files"]["missing.txt"] = {
            "sha256": "missing",
            "strategy": "merge",
        }
        (self.root / STATE_PATH).write_text(
            yaml.safe_dump(self.state, sort_keys=False), encoding="utf-8"
        )

        status = update_status(self.root)

        self.assertEqual(["managed.txt"], status["modified"])
        self.assertEqual(["missing.txt"], status["missing"])

    def test_three_way_update_merges_non_overlapping_changes(self) -> None:
        self.incoming.write_text("alpha\nbeta\nOMEGA UPSTREAM\n", encoding="utf-8")
        (self.root / "managed.txt").write_text("ALPHA LOCAL\nbeta\nomega\n", encoding="utf-8")
        payload = self._payload()

        with patch("boardwright.managed_project.collect_payload", return_value=payload):
            plan = build_update_plan(self.root)
            self.assertEqual("merge", plan["operations"][0]["action"])
            plan_path = write_plan(self.root / "update.yaml", plan)
            with patch("boardwright.config.load_config", return_value=object()), patch(
                "boardwright.validation.validate_project", return_value=[]
            ):
                apply_update_plan(plan_path)

        self.assertEqual(
            "ALPHA LOCAL\nbeta\nOMEGA UPSTREAM\n",
            (self.root / "managed.txt").read_text(encoding="utf-8"),
        )

    def test_update_blocks_overlapping_changes(self) -> None:
        self.incoming.write_text("ALPHA UPSTREAM\nbeta\nomega\n", encoding="utf-8")
        (self.root / "managed.txt").write_text("ALPHA LOCAL\nbeta\nomega\n", encoding="utf-8")

        with patch("boardwright.managed_project.collect_payload", return_value=self._payload()):
            plan = build_update_plan(self.root)

        self.assertEqual(["managed.txt"], plan["blockers"])
        self.assertEqual("conflict", plan["operations"][0]["action"])

    def test_validation_failure_rolls_back_file_and_state(self) -> None:
        self.incoming.write_text("alpha\nBETA UPSTREAM\nomega\n", encoding="utf-8")
        original_state = (self.root / STATE_PATH).read_bytes()
        payload = self._payload()

        with patch("boardwright.managed_project.collect_payload", return_value=payload):
            plan_path = write_plan(self.root / "update.yaml", build_update_plan(self.root))
            with patch("boardwright.config.load_config", return_value=object()), patch(
                "boardwright.validation.validate_project",
                return_value=(ValidationIssue("error", "injected failure"),),
            ):
                with self.assertRaisesRegex(BoardwrightError, "injected failure"):
                    apply_update_plan(plan_path)

        self.assertEqual(
            "alpha\nbeta\nomega\n",
            (self.root / "managed.txt").read_text(encoding="utf-8"),
        )
        self.assertEqual(original_state, (self.root / STATE_PATH).read_bytes())

    def _payload(self) -> dict[str, PayloadFile]:
        return {
            "managed.txt": PayloadFile(
                path=Path("managed.txt"),
                source=self.incoming,
                sha256=_file_hash(self.incoming),
                strategy="merge",
            )
        }


def _remove_test_tree(path: Path) -> None:
    def retry(function, target, _error) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    if path.exists():
        shutil.rmtree(path, onexc=retry)


if __name__ == "__main__":
    unittest.main()
