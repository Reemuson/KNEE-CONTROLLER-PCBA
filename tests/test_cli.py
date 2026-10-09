# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
import tomllib
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from boardwright import cli


class CliTests(unittest.TestCase):
    def test_plain_boardwright_opens_tui(self) -> None:
        with patch.object(cli, "_tui", return_value=0) as mocked_tui:
            result = cli.main([])

        self.assertEqual(0, result)
        mocked_tui.assert_called_once_with()

    def test_python_module_entrypoint_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "boardwright", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode)
        self.assertIn("usage: boardwright", completed.stdout)
        self.assertIn("accepted", completed.stdout)
        self.assertIn("adopt", completed.stdout)
        self.assertIn("migrate", completed.stdout)
        self.assertIn("update", completed.stdout)
        self.assertIn("doctor", completed.stdout)
        self.assertIn("review", completed.stdout)
        self.assertIn("testbench", completed.stdout)
        self.assertIn("generate", completed.stdout)
        self.assertIn("outputs", completed.stdout)
        self.assertIn("sheet-title", completed.stdout)
        self.assertIn("worksheet-logo", completed.stdout)
        self.assertIn("source-package", completed.stdout)
        self.assertIn("docker-kibot", completed.stdout)

    def test_outputs_clean_command_prints_summary(self) -> None:
        with patch.object(cli, "clean_generated_outputs", return_value=object()), patch.object(
            cli,
            "format_cleanup_summary",
            return_value="cleanup ok",
        ), redirect_stdout(StringIO()) as stdout:
            result = cli.main(["outputs", "clean"])

        self.assertEqual(0, result)
        self.assertIn("cleanup ok", stdout.getvalue())

    def test_doctor_command_prints_report(self) -> None:
        with patch.object(cli, "load_config", return_value=object()), patch.object(
            cli,
            "run_doctor",
            return_value=(),
        ), patch.object(cli, "format_doctor_report", return_value="Doctor OK"), redirect_stdout(
            StringIO()
        ):
            result = cli.main(["doctor"])

        self.assertEqual(0, result)

    def test_review_command_prints_preview_state(self) -> None:
        state = type("State", (), {"ready": False})()
        with patch.object(cli, "load_config", return_value=object()), patch.object(
            cli,
            "build_preview_state",
            return_value=state,
        ), patch.object(cli, "format_preview_state", return_value="Preview ready"), redirect_stdout(
            StringIO()
        ):
            result = cli.main(["review"])

        self.assertEqual(1, result)

    def test_testbench_plan_command_prints_plan(self) -> None:
        with patch.object(cli, "load_config", return_value=object()), patch.object(
            cli,
            "build_testbench_plan",
            return_value=object(),
        ), patch.object(cli, "format_testbench_plan", return_value="Plan"), redirect_stdout(
            StringIO()
        ):
            result = cli.main(["testbench", "plan"])

        self.assertEqual(0, result)

    def test_worksheet_logo_command_updates_default_worksheet(self) -> None:
        config = type(
            "Config",
            (),
            {
                "root": Path.cwd(),
                "template_sheet_image": "assets/sheet-image.png",
                "worksheet": "Templates/example.kicad_wks",
            },
        )()
        result_obj = type(
            "Result",
            (),
            {
                "worksheet": Path.cwd() / "Templates/example.kicad_wks",
                "logo": Path.cwd() / "assets/sheet-image.png",
                "bitmap_index": 0,
                "png_width": 10,
                "png_height": 5,
            },
        )()
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "embed_logo_in_worksheets",
            return_value=(result_obj,),
        ) as embed, redirect_stdout(StringIO()) as stdout:
            result = cli.main(["worksheet-logo"])

        self.assertEqual(0, result)
        embed.assert_called_once()
        self.assertIn("updated Templates", stdout.getvalue())

    def test_adopt_command_initializes_and_fills_repo_metadata(self) -> None:
        config = type(
            "Config",
            (),
            {
                "root": Path.cwd(),
                "github_repo": "",
                "project": {"project": {"git_url": ""}},
            },
        )()
        with patch.object(cli, "find_project_root", return_value=Path.cwd()), patch.object(
            cli,
            "init_config",
            return_value=[Path.cwd() / ".boardwright" / "project.yaml"],
        ) as init_config, patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "remote_url",
            return_value="https://github.com/owner/repo.git",
        ), patch("boardwright.config.update_project_config", return_value=Path.cwd() / ".boardwright" / "project.yaml") as update, redirect_stdout(
            StringIO()
        ) as stdout:
            result = cli.main(["adopt"])

        self.assertEqual(0, result)
        init_config.assert_called_once()
        update.assert_called_once()
        self.assertIn("Adopted existing project into Boardwright.", stdout.getvalue())

    def test_sheet_title_command_syncs_overrides(self) -> None:
        config = type("Config", (), {"root": Path.cwd()})()
        titles = ("COVER PAGE", "Local Section Title")
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "find_primary_schematic",
            return_value=Path("boardwright.kicad_sch"),
        ), patch.object(
            cli,
            "collect_actual_sheet_titles",
            return_value=titles,
        ), patch.object(
            cli,
            "write_sheet_title_overrides",
            return_value=Path.cwd() / ".boardwright" / "sheet_titles.env",
        ) as write, redirect_stdout(StringIO()) as stdout:
            result = cli.main(["sheet-title", "--sync"])

        self.assertEqual(0, result)
        write.assert_called_once_with(Path.cwd(), titles)
        self.assertIn("sheet_titles.env", stdout.getvalue())

    def test_sheet_title_command_reports_drift(self) -> None:
        config = type("Config", (), {"root": Path.cwd()})()
        titles = ("COVER PAGE", "Local Section Title")
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "find_primary_schematic",
            return_value=Path("boardwright.kicad_sch"),
        ), patch.object(
            cli,
            "collect_actual_sheet_titles",
            return_value=titles,
        ), patch.object(
            cli,
            "read_sheet_title_overrides",
            return_value={1: "COVER PAGE", 2: "Wrong Title"},
        ), redirect_stdout(StringIO()) as stdout:
            result = cli.main(["sheet-title"])

        self.assertEqual(1, result)
        self.assertIn("drift", stdout.getvalue())
        self.assertIn("Wrong Title", stdout.getvalue())

    def test_generate_revision_history_command_writes_output(self) -> None:
        config = type("Config", (), {"root": Path.cwd()})()
        result_obj = type("Result", (), {"path": Path.cwd() / "extra-revision-history.kicad_sch"})()
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "generate_revision_history_sheet",
            return_value=result_obj,
        ) as generate_sheet, redirect_stdout(StringIO()) as stdout:
            result = cli.main([
                "generate",
                "revision-history",
                "--output",
                "extra-revision-history.kicad_sch",
            ])

        self.assertEqual(0, result)
        generate_sheet.assert_called_once()
        self.assertIn("extra-revision-history.kicad_sch", stdout.getvalue())

    def test_generate_sheet_command_adds_child_schematic(self) -> None:
        config = type("Config", (), {"root": Path.cwd()})()
        parent = Path.cwd() / "boardwright.kicad_sch"
        child = Path.cwd() / "subsystem.kicad_sch"
        result_parent = type("Result", (), {"path": parent})()
        result_child = type("Result", (), {"path": child})()
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "find_primary_schematic",
            return_value=parent,
        ), patch.object(
            cli,
            "add_hierarchical_sheet",
            return_value=(result_parent, result_child),
        ) as add_sheet, redirect_stdout(StringIO()) as stdout:
            result = cli.main([
                "generate",
                "sheet",
                "--sheet-name",
                "Subsystem",
                "--child-file",
                "subsystem.kicad_sch",
            ])

        self.assertEqual(0, result)
        add_sheet.assert_called_once()
        self.assertIn("subsystem.kicad_sch", stdout.getvalue())

    def test_source_package_command_writes_archive(self) -> None:
        config = type("Config", (), {"root": Path.cwd()})()
        result_obj = type("Result", (), {"path": Path.cwd() / "boardwright-source.zip", "file_count": 3})()
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli,
            "build_source_package",
            return_value=result_obj,
        ) as build_source, redirect_stdout(StringIO()) as stdout:
            result = cli.main([
                "source-package",
                "--output",
                "boardwright-source.zip",
            ])

        self.assertEqual(0, result)
        build_source.assert_called_once()
        self.assertIn("boardwright-source.zip", stdout.getvalue())

    def test_docker_kibot_command_launches_helper(self) -> None:
        config = type("Config", (), {"root": Path.cwd()})()
        with patch.object(cli, "load_config", return_value=config), patch.object(
            cli.shutil,
            "which",
            return_value="docker",
        ), patch.object(cli.subprocess, "run", return_value=type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()) as run:
            result = cli.main(["docker-kibot", "--version", "9"])

        self.assertEqual(0, result)
        run.assert_called_once()
        command = run.call_args.args[0]
        self.assertTrue(any("docker_kibot" in str(part) for part in command))

    def test_dev_extra_includes_tui_and_templates(self) -> None:
        data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        extras = data["project"]["optional-dependencies"]

        self.assertIn("dev", extras)
        self.assertIn("textual>=0.80", extras["dev"])
        self.assertIn("Jinja2>=3.1", extras["dev"])



if __name__ == "__main__":
    unittest.main()
