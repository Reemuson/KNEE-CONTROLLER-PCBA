# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

from __future__ import annotations

import shutil
import subprocess
import unittest
import uuid
from pathlib import Path

from boardwright.config import init_config, load_config
from boardwright.git_ops import remote_url
from boardwright.project_setup import normalize_remote_url, setup_project_repository


class ProjectSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("tests") / ".tmp_project_setup" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(self.root.parent, ignore_errors=True))

    def test_init_config_can_start_in_plain_directory(self) -> None:
        written = init_config(root=self.root, workflows=False)

        self.assertTrue((self.root / ".boardwright" / "project.yaml").exists())
        self.assertIn((self.root / ".boardwright" / "project.yaml").resolve(), written)

    def test_setup_initializes_git_origin_and_metadata(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        init_config(root=self.root, workflows=False)
        config = load_config(self.root)

        result = setup_project_repository(config, "owner/repo")
        updated = load_config(self.root)

        self.assertTrue((self.root / ".git").exists())
        self.assertEqual("https://github.com/owner/repo.git", remote_url(self.root))
        self.assertEqual("https://github.com/owner/repo.git", updated.project["project"]["git_url"])
        self.assertNotIn("github_repo", updated.project["project"])
        self.assertEqual("owner/repo", updated.github_repo)
        self.assertTrue(result.initialized_git)
        self.assertTrue(result.configured_origin)

    def test_setup_without_git_only_updates_metadata(self) -> None:
        init_config(root=self.root, workflows=False)

        result = setup_project_repository(load_config(self.root), "owner/repo", git=False)
        updated = load_config(self.root)

        self.assertFalse((self.root / ".git").exists())
        self.assertEqual("https://github.com/owner/repo.git", updated.project["project"]["git_url"])
        self.assertNotIn("github_repo", updated.project["project"])
        self.assertEqual("owner/repo", updated.github_repo)
        self.assertFalse(result.initialized_git)
        self.assertFalse(result.configured_origin)
    def test_setup_updates_existing_origin_url(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not installed")
        init_config(root=self.root, workflows=False)
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/old/repo.git"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )

        setup_project_repository(load_config(self.root), "https://github.com/new/repo.git")

        self.assertEqual("https://github.com/new/repo.git", remote_url(self.root))
        self.assertEqual("new/repo", load_config(self.root).github_repo)

    def test_normalize_remote_url_accepts_slug_or_url(self) -> None:
        self.assertEqual("https://github.com/owner/repo.git", normalize_remote_url("owner/repo"))
        self.assertEqual(
            "git@github.com:owner/repo.git",
            normalize_remote_url("git@github.com:owner/repo.git"),
        )


if __name__ == "__main__":
    unittest.main()
