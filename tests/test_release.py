# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
import shutil
import subprocess
from pathlib import Path

from boardwright.errors import BoardwrightError
from boardwright.config import BoardwrightConfig
from boardwright.config import load_config
from boardwright.release import _validate_version, prepare_release, validate_release_plan, build_release_plan


class ReleaseTests(unittest.TestCase):
    def test_validates_semver(self) -> None:
        _validate_version("0.1.0")
        with self.assertRaises(BoardwrightError):
            _validate_version("v0.1.0")

    def test_release_plan_allows_empty_unreleased_changelog(self) -> None:
        root = Path.cwd() / ".test_release_prepare_workspace"
        shutil.rmtree(root, ignore_errors=True)
        try:
            root.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [Unreleased]\n",
                encoding="utf-8",
            )
            config = BoardwrightConfig(
                root=root,
                project={"project": {}, "variants": {}, "outputs": {}, "assets": {}},
                branches={"branches": {"release": "main"}},
                legal={},
                revision_history={"revision_history": {}},
            )

            plan = build_release_plan(config, "0.1.0", check_remote=False)
            problems = validate_release_plan(plan, allow_dirty=True)

            self.assertFalse(plan.has_unreleased_changes)
            self.assertNotIn("CHANGELOG.md has no unreleased changes.", problems)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_prepare_release_writes_no_change_note_when_changelog_is_empty(self) -> None:
        root = Path.cwd() / ".test_release_workspace"
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)
        try:
            root.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            (root / ".boardwright").mkdir()
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [Unreleased]\n",
                encoding="utf-8",
            )
            (root / ".boardwright" / "project.yaml").write_text(
                "project:\n  id: TEST\n  name: Test\ndocuments:\n  schematic:\n    title: Schematic\n    type: SCHEMATIC\n    number_source: pcba_name\n    revision: A\n    drawn_by: RH\n",
                encoding="utf-8",
            )
            (root / ".boardwright" / "branches.yaml").write_text("branches:\n  release: main\n", encoding="utf-8")
            (root / ".boardwright" / "legal.yaml").write_text("boardwright: {}\n", encoding="utf-8")
            (root / ".boardwright" / "revision_history.yaml").write_text("revision_history:\n  slots: 1\n", encoding="utf-8")
            (root / ".boardwright" / "document_revisions.yaml").write_text("document_revisions:\n  schematic:\n    rows: []\n", encoding="utf-8")
            config = load_config(root)

            prepare_release(
                config,
                "0.1.0",
                allow_dirty=True,
                dry_run=False,
                drawing_revision="B",
                revision_description="Initial controlled release",
            )

            changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            project_yaml = (root / ".boardwright" / "project.yaml").read_text(encoding="utf-8")
            document_revisions = (root / ".boardwright" / "document_revisions.yaml").read_text(encoding="utf-8")
            revision_vars = (root / ".boardwright" / "revision_history_variables.env").read_text(encoding="utf-8")
            self.assertIn("## [0.1.0] - ", changelog)
            self.assertIn("No changelog entries recorded", changelog)
            self.assertIn("revision: B", project_yaml)
            self.assertIn("revision: B", document_revisions)
            self.assertIn("description: Initial controlled release", document_revisions)
            self.assertIn("drawn_by: RH", document_revisions)
            self.assertIn('REVTABLE_1_REV="B"', revision_vars)
            self.assertIn('REVTABLE_1_DESC="Initial controlled release"', revision_vars)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_prepare_release_requires_controlled_revision_row(self) -> None:
        root = Path.cwd() / ".test_release_requires_revision_workspace"
        shutil.rmtree(root, ignore_errors=True)
        try:
            root.mkdir()
            subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
            (root / ".boardwright").mkdir()
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n", encoding="utf-8")
            config = BoardwrightConfig(
                root=root,
                project={"project": {}, "variants": {}, "outputs": {}, "assets": {}},
                branches={"branches": {"release": "main"}},
                legal={},
                revision_history={"revision_history": {"slots": 1}},
            )

            with self.assertRaises(BoardwrightError):
                prepare_release(config, "0.1.0", allow_dirty=True, dry_run=False)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
