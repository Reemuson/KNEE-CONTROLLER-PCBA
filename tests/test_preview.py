# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path
from unittest import mock

from boardwright.config import BoardwrightConfig
from boardwright.errors import BoardwrightError
from boardwright.preview import (
    PreviewArtifact,
    PreviewRun,
    build_preview_plan,
    build_preview_state,
    evaluate_preview_state,
    fetch_latest_preview_artifact,
    format_preview_state,
    latest_preview_variant,
    mark_preview_reviewed,
    parse_preview_runs,
    parse_run_artifacts,
    preview_variant_from_title,
    preview_manual_fallback,
    preview_reviewed,
    dispatch_preview,
)
from boardwright.variants import normalize_variant


class PreviewTests(unittest.TestCase):
    def test_normalize_variant(self) -> None:
        self.assertEqual("CHECKED", normalize_variant("checked"))
        with self.assertRaises(BoardwrightError):
            normalize_variant("FAST")

    def test_build_preview_plan_uses_config_defaults(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={
                "project": {"id": "TEST", "name": "Test", "github_repo": "owner/private"},
                "variants": {"dev_default": "DRAFT", "preview_default": "PRELIMINARY"},
                "outputs": {
                    "preview_engine": "github-actions",
                    "preview_workflow": "ci.yaml",
                },
            },
            branches={"branches": {}},
            legal={"legal": {}},
            revision_history={"revision_history": {}},
        )

        plan = build_preview_plan(config)

        self.assertEqual("PRELIMINARY", plan.variant)
        self.assertEqual("github-actions", plan.engine)
        self.assertEqual("preview", plan.preview_branch)
        self.assertTrue(plan.source_label)
        self.assertIn(Path("Schematic"), plan.output_paths)
        self.assertIn(Path("assets/renders"), plan.output_paths)
        self.assertIn("Manual fallback", preview_manual_fallback(plan))
        self.assertIn("variant=PRELIMINARY", preview_manual_fallback(plan))
        self.assertEqual("owner/private", plan.repo)
        self.assertIn("source_label=", preview_manual_fallback(plan))
        self.assertIn("--repo owner/private", preview_manual_fallback(plan))

    def test_dispatch_preview_passes_configured_repo(self) -> None:
        plan = build_preview_plan(_config())
        completed = subprocess_result(0, "", "")

        with mock.patch("boardwright.preview._gh_command", return_value="gh"), mock.patch(
            "pathlib.Path.exists",
            return_value=True,
        ), mock.patch("subprocess.run", return_value=completed) as mocked_run:
            dispatch_preview(plan, Path("."))

        command = mocked_run.call_args.args[0]
        self.assertIn("--repo", command)
        self.assertIn("owner/private", command)

    def test_fetch_preview_requires_gh(self) -> None:
        config = BoardwrightConfig(
            root=Path("."),
            project={
                "project": {"id": "TEST", "name": "Test", "github_repo": "owner/private"},
                "variants": {"preview_default": "PRELIMINARY"},
                "outputs": {"preview_workflow": "ci.yaml"},
            },
            branches={"branches": {}},
            legal={"legal": {}},
            revision_history={"revision_history": {}},
        )

        with self.assertRaises(BoardwrightError):
            with mock.patch("boardwright.preview._gh_command", return_value=None):
                fetch_latest_preview_artifact(config)

    def test_parse_preview_runs(self) -> None:
        runs = parse_preview_runs(
            """
            [
              {
                "databaseId": 123,
                "status": "completed",
                "conclusion": "success",
                "headBranch": "dev",
                "headSha": "abc123",
                "createdAt": "2026-05-23T00:00:00Z",
                "displayTitle": "preview"
              }
            ]
            """
        )

        self.assertEqual(1, len(runs))
        self.assertEqual("123", runs[0].database_id)
        self.assertEqual("abc123", runs[0].head_sha)

    def test_parse_run_artifacts(self) -> None:
        artifacts = parse_run_artifacts(
            """
            {
              "artifacts": [
                {"name": "boardwright-preview-CHECKED", "sizeInBytes": 1234}
              ]
            }
            """
        )

        self.assertEqual((PreviewArtifact("boardwright-preview-CHECKED", 1234, False),), artifacts)

    def test_preview_state_ready(self) -> None:
        run = _preview_run("7", "completed", "success", "abcdef123456")

        state = evaluate_preview_state((run,), "abcdef123456", "preliminary")

        self.assertEqual("ready", state.state)
        self.assertTrue(state.ready)
        self.assertIn("boardwright-preview-PRELIMINARY", format_preview_state(state))

    def test_preview_state_stale(self) -> None:
        run = _preview_run("7", "completed", "success", "oldsha")

        state = evaluate_preview_state((run,), "newsha", "CHECKED")

        self.assertEqual("stale", state.state)
        self.assertFalse(state.ready)

    def test_preview_state_failed(self) -> None:
        run = _preview_run("7", "completed", "failure", "abcdef")

        state = evaluate_preview_state((run,), "abcdef", "CHECKED")

        self.assertEqual("failed", state.state)

    def test_preview_state_running_takes_priority(self) -> None:
        run = _preview_run("8", "in_progress", "", "abcdef")

        state = evaluate_preview_state((run,), "abcdef", "CHECKED")

        self.assertEqual("running", state.state)

    def test_preview_state_filters_variant_from_run_title(self) -> None:
        checked = _preview_run(
            "8",
            "in_progress",
            "",
            "abcdef",
            title="Preview CHECKED from dev@abcdef",
        )
        preliminary = _preview_run(
            "7",
            "completed",
            "success",
            "abcdef",
            title="Preview PRELIMINARY from dev@abcdef",
        )

        checked_state = evaluate_preview_state((checked, preliminary), "abcdef", "CHECKED")
        preliminary_state = evaluate_preview_state((checked, preliminary), "abcdef", "PRELIMINARY")

        self.assertEqual("running", checked_state.state)
        self.assertEqual("ready", preliminary_state.state)
        self.assertIn("boardwright-preview-CHECKED", format_preview_state(checked_state))
        self.assertIn("boardwright-preview-PRELIMINARY", format_preview_state(preliminary_state))

    def test_preview_state_reports_missing_requested_variant_when_titles_are_known(self) -> None:
        preliminary = _preview_run(
            "7",
            "completed",
            "success",
            "abcdef",
            title="Preview PRELIMINARY from dev@abcdef",
        )

        state = evaluate_preview_state((preliminary,), "abcdef", "CHECKED")

        self.assertEqual("missing", state.state)
        self.assertIn("No CHECKED preview workflow runs", state.message)

    def test_latest_preview_variant_uses_run_title(self) -> None:
        run = _preview_run(
            "8",
            "in_progress",
            "",
            "abcdef",
            title="Preview CHECKED from dev@abcdef",
        )

        self.assertEqual("CHECKED", latest_preview_variant((run,), "PRELIMINARY"))
        self.assertEqual("PRELIMINARY", latest_preview_variant((), "PRELIMINARY"))
        self.assertEqual("CHECKED", preview_variant_from_title("Preview CHECKED from dev@abc"))

    def test_preview_state_missing_without_origin_dev(self) -> None:
        state = evaluate_preview_state((), "", "CHECKED")

        self.assertEqual("missing", state.state)
        self.assertIn("origin/dev", state.message)

    def test_preview_review_marker_matches_exact_run(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")
        state = evaluate_preview_state((run,), "abcdef", "CHECKED")
        marker_json = """
        {
          "artifact_name": "boardwright-preview-CHECKED",
          "run_id": "9",
          "head_sha": "abcdef",
          "expected_sha": "abcdef"
        }
        """

        with mock.patch("pathlib.Path.exists", return_value=False):
            self.assertFalse(preview_reviewed(config, state))
        with mock.patch("pathlib.Path.exists", return_value=True), mock.patch(
            "pathlib.Path.read_text",
            return_value=marker_json,
        ):
            self.assertTrue(preview_reviewed(config, state))

        stale_state = evaluate_preview_state((run,), "newsha", "CHECKED")
        with mock.patch("pathlib.Path.exists", return_value=True), mock.patch(
            "pathlib.Path.read_text",
            return_value=marker_json,
        ):
            self.assertFalse(preview_reviewed(config, stale_state))

    def test_build_preview_state_includes_review_marker(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")

        with mock.patch("boardwright.preview.latest_pushed_dev_sha", return_value="abcdef"), mock.patch(
            "boardwright.preview.preview_reviewed",
            return_value=True,
        ):
            reviewed_state = build_preview_state(config, runs=(run,))

        self.assertTrue(reviewed_state.reviewed)
        self.assertIn("Reviewed: yes", format_preview_state(reviewed_state))

    def test_mark_preview_reviewed_writes_marker(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")
        state = evaluate_preview_state((run,), "abcdef", "CHECKED")

        with mock.patch("pathlib.Path.mkdir") as mocked_mkdir, mock.patch(
            "pathlib.Path.write_text"
        ) as mocked_write:
            mark_preview_reviewed(config, state)

        mocked_mkdir.assert_called()
        mocked_write.assert_called()

    def test_fetch_preview_rejects_empty_download(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")
        state = evaluate_preview_state((run,), "abcdef", "CHECKED")
        completed = subprocess_result(0, "downloaded", "")

        with mock.patch("boardwright.preview._gh_command", return_value="gh"), mock.patch(
            "boardwright.preview.build_preview_state",
            return_value=state,
        ), mock.patch("subprocess.run", return_value=completed), mock.patch(
            "boardwright.preview.list_run_artifacts",
            return_value=(PreviewArtifact("boardwright-preview-CHECKED"),),
        ), mock.patch(
            "pathlib.Path.mkdir"
        ), mock.patch(
            "boardwright.preview._downloaded_files",
            return_value=(),
        ):
            with self.assertRaises(BoardwrightError) as raised:
                fetch_latest_preview_artifact(config)

        self.assertIn("but boardwright-preview is empty", str(raised.exception))
        self.assertIn("gh run download", str(raised.exception))

    def test_fetch_preview_download_error_lists_available_artifacts(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")
        state = evaluate_preview_state((run,), "abcdef", "PRELIMINARY")
        completed = subprocess_result(1, "", "no artifact matches any of the names")

        with mock.patch("boardwright.preview._gh_command", return_value="gh"), mock.patch(
            "boardwright.preview.build_preview_state",
            return_value=state,
        ), mock.patch("subprocess.run", return_value=completed), mock.patch(
            "boardwright.preview.list_run_artifacts",
            return_value=(PreviewArtifact("boardwright-preview-CHECKED"),),
        ), mock.patch("pathlib.Path.mkdir"):
            with self.assertRaises(BoardwrightError) as raised:
                fetch_latest_preview_artifact(config, "PRELIMINARY")

        self.assertIn("Artifacts on run: boardwright-preview-CHECKED", str(raised.exception))

    def test_fetch_preview_reports_downloaded_files(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")
        state = evaluate_preview_state((run,), "abcdef", "CHECKED")
        completed = subprocess_result(0, "downloaded", "")

        with mock.patch("boardwright.preview._gh_command", return_value="gh"), mock.patch(
            "boardwright.preview.build_preview_state",
            return_value=state,
        ), mock.patch("subprocess.run", return_value=completed), mock.patch(
            "boardwright.preview._prepare_preview_destination"
        ), mock.patch(
            "boardwright.preview._downloaded_files",
            return_value=(Path("boardwright-preview/MANIFEST.txt"),),
        ), mock.patch(
            "boardwright.preview.mark_preview_reviewed"
        ):
            result = fetch_latest_preview_artifact(config)

        self.assertIn("Files: MANIFEST.txt", result)

    def test_fetch_preview_replaces_existing_destination(self) -> None:
        config = _config()
        run = _preview_run("9", "completed", "success", "abcdef")
        state = evaluate_preview_state((run,), "abcdef", "CHECKED")
        completed = subprocess_result(0, "downloaded", "")

        with mock.patch("boardwright.preview._gh_command", return_value="gh"), mock.patch(
            "boardwright.preview.build_preview_state",
            return_value=state,
        ), mock.patch("subprocess.run", return_value=completed), mock.patch(
            "boardwright.preview._prepare_preview_destination"
        ) as prepare, mock.patch(
            "boardwright.preview._downloaded_files",
            return_value=(Path("boardwright-preview/MANIFEST.txt"),),
        ), mock.patch(
            "boardwright.preview.mark_preview_reviewed"
        ):
            fetch_latest_preview_artifact(config)

        prepare.assert_called_once_with(Path("boardwright-preview"))


def _config() -> BoardwrightConfig:
    return BoardwrightConfig(
        root=Path("."),
        project={
            "project": {"id": "TEST", "name": "Test", "github_repo": "owner/private"},
            "variants": {"preview_default": "CHECKED"},
            "outputs": {"preview_workflow": "ci.yaml"},
        },
        branches={"branches": {"development": "dev"}},
        legal={"legal": {}},
        revision_history={"revision_history": {}},
    )


def _preview_run(
    database_id: str,
    status: str,
    conclusion: str,
    head_sha: str,
    title: str = "preview",
) -> PreviewRun:
    return PreviewRun(
        database_id=database_id,
        status=status,
        conclusion=conclusion,
        branch="dev",
        head_sha=head_sha,
        created_at="2026-05-23T00:00:00Z",
        title=title,
    )


def subprocess_result(returncode: int, stdout: str, stderr: str) -> object:
    return type(
        "Completed",
        (),
        {"returncode": returncode, "stdout": stdout, "stderr": stderr},
    )()


if __name__ == "__main__":
    unittest.main()
