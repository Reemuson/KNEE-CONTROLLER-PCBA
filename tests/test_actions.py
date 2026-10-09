# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path

from boardwright.actions import (
    build_preview_action,
    build_prepare_release_action,
    build_promote_action,
)
from boardwright.config import BoardwrightConfig
from boardwright.errors import BoardwrightError


def _config() -> BoardwrightConfig:
    return BoardwrightConfig(
        root=Path("."),
        project={
            "project": {
                "id": "TEST",
                "name": "Test",
                "github_repo": "owner/repo",
            },
            "variants": {"dev_default": "DRAFT", "preview_default": "PRELIMINARY"},
            "outputs": {
                "main_workflow": "main-outputs.yaml",
                "prepare_release_workflow": "prepare-release.yaml",
            },
        },
        branches={"branches": {"development": "dev", "release": "main"}},
        legal={"legal": {}},
        revision_history={"revision_history": {}},
    )


class ActionTests(unittest.TestCase):
    def test_build_preview_action_uses_preview_default(self) -> None:
        action = build_preview_action(_config())

        self.assertEqual("preview", action.name)
        self.assertIn(("variant", "PRELIMINARY"), action.fields)
        self.assertTrue(any(key == "source_label" for key, _ in action.fields))

    def test_build_promote_action(self) -> None:
        action = build_promote_action(_config(), "checked")

        self.assertEqual("promote", action.name)
        self.assertEqual("main-outputs.yaml", action.workflow)
        self.assertEqual("dev", action.ref)
        self.assertIn(("variant", "CHECKED"), action.fields)
        self.assertIn(("commit_outputs", "true"), action.fields)
        self.assertIn(("source_ref", "dev"), action.fields)
        self.assertIn(("target_branch", "main"), action.fields)
        self.assertTrue(any(key == "source_label" for key, _ in action.fields))
        self.assertIn("--repo", action.command)
        self.assertIn("owner/repo", action.command)
        self.assertIn("Manual fallback", action.manual_fallback)
        self.assertIn("main-outputs.yaml", action.manual_fallback)
        self.assertIn("variant: CHECKED", action.manual_fallback)

    def test_build_promote_action_can_pin_reviewed_source_sha(self) -> None:
        action = build_promote_action(
            _config(),
            "preliminary",
            source_ref="dev",
            source_sha="abc123",
        )

        self.assertIn(("variant", "PRELIMINARY"), action.fields)
        self.assertIn(("source_ref", "dev"), action.fields)
        self.assertIn(("source_sha", "abc123"), action.fields)
        self.assertIn(("source_label", "dev@abc123"), action.fields)

    def test_build_prepare_release_action(self) -> None:
        action = build_prepare_release_action(
            _config(),
            "0.1.2",
            "preliminary",
            "prerelease",
            "B",
            "Release connector update",
        )

        self.assertEqual("prepare-release.yaml", action.workflow)
        self.assertIn(("version", "0.1.2"), action.fields)
        self.assertIn(("variant", "PRELIMINARY"), action.fields)
        self.assertIn(("release_kind", "prerelease"), action.fields)
        self.assertIn(("drawing_revision", "B"), action.fields)
        self.assertIn(("revision_description", "Release connector update"), action.fields)

    def test_build_prepare_release_action_supports_draft(self) -> None:
        action = build_prepare_release_action(
            _config(),
            "0.1.2",
            "checked",
            "draft",
            "A",
            "Initial controlled release",
        )

        self.assertIn(("release_kind", "draft"), action.fields)
        self.assertEqual("prepare-release.yaml", action.workflow)

    def test_rejects_bad_release_kind(self) -> None:
        with self.assertRaises(BoardwrightError):
            build_prepare_release_action(_config(), "0.1.2", "CHECKED", "weird", "A", "Initial")


if __name__ == "__main__":
    unittest.main()


class PrepareReleaseRevisionInputTests(unittest.TestCase):
    def test_requires_drawing_revision_inputs(self) -> None:
        with self.assertRaises(BoardwrightError):
            build_prepare_release_action(_config(), "0.1.2", "CHECKED", "release", "", "Initial")
        with self.assertRaises(BoardwrightError):
            build_prepare_release_action(_config(), "0.1.2", "CHECKED", "release", "A", "")
        with self.assertRaises(BoardwrightError):
            build_prepare_release_action(_config(), "0.1.2", "CHECKED", "release", "A", "x" * 61)
