# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path

from boardwright.accepted import AcceptedRun, evaluate_accepted_state
from boardwright.config import BoardwrightConfig
from boardwright.preview import PreviewRun, evaluate_preview_state
from boardwright.status import ProjectStatus
from boardwright.validation import ValidationIssue
from boardwright.workflow_state import action_state, build_workflow_state


class WorkflowStateTests(unittest.TestCase):
    def test_validation_blocked(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(),
            (ValidationIssue("error", "Broken"),),
            "ready for dry-run",
        )

        self.assertEqual("validation_blocked", workflow.stage)
        self.assertEqual("Fix validation", workflow.next_action)
        self.assertFalse(action_state(workflow, "Commit").enabled)

    def test_needs_changelog(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(dirty_count=1, unreleased_changes=False),
            (),
            "ready for dry-run",
        )

        self.assertEqual("needs_changelog", workflow.stage)
        self.assertEqual("Add changelog", workflow.next_action)

    def test_ready_to_commit(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(dirty_count=1, unreleased_changes=True),
            (),
            "ready for dry-run",
        )

        self.assertEqual("ready_to_commit", workflow.stage)
        self.assertTrue(action_state(workflow, "Commit").enabled)

    def test_needs_push(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(ahead=1, unreleased_changes=True),
            (),
            "ready for dry-run",
        )

        self.assertEqual("needs_push", workflow.stage)
        self.assertTrue(action_state(workflow, "Commit").enabled)

    def test_stale_preview(self) -> None:
        run = PreviewRun(
            database_id="1",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="old",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview = evaluate_preview_state((run,), "new", "CHECKED")
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
            preview,
        )

        self.assertEqual("preview_stale", workflow.stage)
        self.assertFalse(action_state(workflow, "Accept").enabled)

    def test_preview_missing_prompts_generation(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
            type(
                "Preview",
                (),
                {
                    "state": "missing",
                    "message": "No fresh preview run found.",
                    "ready": False,
                },
            )(),
        )

        self.assertEqual("preview_missing", workflow.stage)
        self.assertEqual("Preview", workflow.next_action)
        self.assertEqual("No fresh preview run found.", workflow.reason)

    def test_unreleased_changes_prompt_preview(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
        )

        self.assertEqual("preview_missing", workflow.stage)
        self.assertEqual("Preview", workflow.next_action)
        self.assertEqual("Run preview.", workflow.reason)

    def test_preview_ready_prompts_fetch(self) -> None:
        run = PreviewRun(
            database_id="1",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview = evaluate_preview_state((run,), "same", "CHECKED")
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
            preview,
        )

        self.assertEqual("preview_ready", workflow.stage)
        self.assertEqual("Fetch", workflow.next_action)
        self.assertEqual("Preview is ready.", workflow.reason)

    def test_reviewed_preview_enables_accept(self) -> None:
        run = PreviewRun(
            database_id="1",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview = evaluate_preview_state((run,), "same", "CHECKED")
        preview = type(preview)(**{**preview.__dict__, "reviewed": True})
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "not ready yet",
            preview,
        )

        self.assertEqual("preview_reviewed", workflow.stage)
        self.assertTrue(action_state(workflow, "Accept").enabled)

    def test_release_ready(self) -> None:
        run = PreviewRun(
            database_id="1",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview = evaluate_preview_state((run,), "same", "CHECKED")
        preview = type(preview)(**{**preview.__dict__, "reviewed": True})
        accepted_run = AcceptedRun(
            database_id="2",
            status="completed",
            conclusion="success",
            branch="main",
            head_sha="mainsha",
            created_at="2026-05-23T00:00:00Z",
            title="accepted",
        )
        accepted = evaluate_accepted_state((accepted_run,), "mainsha", "main-outputs.yaml")
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
            preview,
            accepted,
        )

        self.assertEqual("release_ready", workflow.stage)
        self.assertTrue(action_state(workflow, "Release").enabled)

    def test_clean_pushed_state_allows_opening_release_checklist(self) -> None:
        run = PreviewRun(
            database_id="1",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview = evaluate_preview_state((run,), "same", "CHECKED")
        preview = type(preview)(**{**preview.__dict__, "reviewed": True})
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
            preview,
        )

        self.assertEqual("preview_reviewed", workflow.stage)
        release_action = action_state(workflow, "Release")
        self.assertTrue(release_action.enabled)
        self.assertIn("checklist", release_action.reason)

    def test_generate_preview_enabled_only_after_clean_push(self) -> None:
        workflow = build_workflow_state(
            _config(),
            _status(unreleased_changes=True),
            (),
            "ready for dry-run",
        )

        self.assertTrue(action_state(workflow, "Preview").enabled)
        self.assertEqual("Run a preview.", action_state(workflow, "Preview").reason)

        dirty = build_workflow_state(
            _config(),
            _status(dirty_count=1, unreleased_changes=True),
            (),
            "ready for dry-run",
        )

        self.assertFalse(action_state(dirty, "Preview").enabled)


def _config() -> BoardwrightConfig:
    return BoardwrightConfig(
        root=Path("."),
        project={
            "project": {"id": "TEST", "name": "Test"},
            "variants": {"dev_default": "DRAFT", "main_default": "CHECKED"},
            "outputs": {"main_workflow": "main-outputs.yaml"},
        },
        branches={"branches": {"development": "dev", "release": "main"}},
        legal={"legal": {}},
        revision_history={"revision_history": {}},
    )


def _status(
    dirty_count: int = 0,
    ahead: int = 0,
    behind: int = 0,
    unreleased_changes: bool = False,
    branch: str = "dev",
) -> ProjectStatus:
    return ProjectStatus(
        project_id="TEST",
        project_name="Test",
        branch=branch,
        dirty_count=dirty_count,
        ahead=ahead,
        behind=behind,
        latest_tag=None,
        unreleased_changes=unreleased_changes,
        variant="DRAFT",
    )


if __name__ == "__main__":
    unittest.main()
