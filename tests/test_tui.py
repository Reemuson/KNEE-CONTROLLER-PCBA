# SPDX-License-Identifier: LicenseRef-Boardwright-Source-Available
# Copyright (c) Ryan Hicks

import unittest
from pathlib import Path
from unittest.mock import patch

from boardwright.accepted import AcceptedMainState, AcceptedRun, evaluate_accepted_state, format_accepted_state
from boardwright.actions import WorkflowRunStatus
from boardwright import tui
from boardwright.config import load_config
from boardwright.preview import PreviewRun, evaluate_preview_state
from boardwright.status import ProjectStatus
from boardwright.validation import ValidationIssue
from boardwright.workflow_state import build_workflow_state


class TuiTests(unittest.TestCase):
    def test_textual_is_optional(self) -> None:
        self.assertIsInstance(tui.textual_available(), bool)
        self.assertIn("pip install", tui.INSTALL_HINT)

    def test_legal_profile_options_include_unknown_selected_profile(self) -> None:
        options = tui._legal_profile_options(
            {"public-hardware": {}},
            "migrated-project",
        )

        self.assertIn(("migrated-project", "migrated-project"), options)
        self.assertIn(("public-hardware", "public-hardware"), options)

    @patch("boardwright.tui.write_revision_variables")
    @patch("boardwright.tui.load_config")
    def test_refresh_project_text_variables_syncs_schematic_metadata(
        self,
        mock_load_config,
        mock_write_revision_variables,
    ) -> None:
        config = object()
        expected = Path(".boardwright/revision_history_variables.env")
        mock_load_config.return_value = config
        mock_write_revision_variables.return_value = expected

        result = tui._refresh_project_text_variables()

        self.assertEqual(expected, result)
        mock_write_revision_variables.assert_called_once_with(config, "schematic")

    def test_responsive_layout_mode_switches_for_short_terminals(self) -> None:
        self.assertEqual("compact", tui._responsive_layout_mode(120, 40))
        self.assertEqual("tiny", tui._responsive_layout_mode(195, 32))
        self.assertEqual("short", tui._responsive_layout_mode(195, 40))
        self.assertEqual("wide", tui._responsive_layout_mode(200, 48))
        self.assertEqual("wide", tui._responsive_layout_mode(180, 60))

    def test_semantic_palette_styles(self) -> None:
        self.assertEqual(f"bold {tui.STATUS_ERROR}", tui._semantic_style("error"))
        self.assertEqual(f"bold {tui.STATUS_WARNING}", tui._semantic_style("warning"))
        self.assertEqual(f"bold {tui.STATUS_SUCCESS}", tui._semantic_style("loaded"))
        self.assertEqual(f"bold {tui.STATUS_LOADING}", tui._semantic_style("loading"))
        self.assertEqual(f"bold {tui.STATUS_UNSET}", tui._semantic_style("unset"))
        self.assertEqual(f"bold {tui.STATUS_LOADING}", tui._ci_status_style("Preview:CHECKED running"))
        self.assertEqual(f"bold {tui.STATUS_SUCCESS}", tui._ci_status_style("Preview:CHECKED ready"))
        self.assertEqual(f"bold {tui.STATUS_UNSET}", tui._ci_status_style("Preview:CHECKED missing"))
        self.assertEqual(f"bold {tui.STATUS_ERROR}", tui._ci_status_style("Preview:CHECKED failed"))
        self.assertEqual("Record", tui._action_button_labels("compact")["record_change"])
        self.assertEqual("Folder", tui._action_button_labels("compact")["open_preview_folder"])
        self.assertEqual("README", tui._action_button_labels("compact")["open_preview_readme"])
        self.assertEqual("Preview", tui._action_button_labels("wide")["generate_preview"])
        self.assertEqual("New Sheet", tui._action_button_labels("wide")["generate_sheet"])
        self.assertEqual("Record", tui._action_button_labels("tiny")["record_change"])
        self.assertEqual("Folder", tui._action_button_labels("tiny")["open_preview_folder"])
        self.assertEqual("README", tui._action_button_labels("tiny")["open_preview_readme"])
        self.assertEqual("Record", tui._action_button_labels("short")["record_change"])
        self.assertEqual("Folder", tui._action_button_labels("short")["open_preview_folder"])
        self.assertEqual("README", tui._action_button_labels("short")["open_preview_readme"])
        self.assertEqual("Record", tui._action_button_labels("wide")["record_change"])


    def test_project_info_exposes_document_control_fields(self) -> None:
        source = Path("src/boardwright/tui.py").read_text(encoding="utf-8")

        self.assertIn("Project name (${PROJECT_NUMBER})", source)
        self.assertIn("PCBA name (${PCBA_NAME})", source)
        self.assertIn("PCB name (${PCB_NAME})", source)
        self.assertNotIn("project_project_number", source)
        self.assertNotIn("project_pcba_number", source)
        self.assertNotIn("project_pcb_number", source)
        self.assertIn("Drawing revision", source)
        self.assertIn("project_document_revision", source)
        self.assertIn('document_fields=result["documents"]', source)
        self.assertIn("lettered", source)
        self.assertIn("numeric", source)
        self.assertIn("semantic", source)
        self.assertIn("YYYY-MM-DD", source)
        self.assertIn("document_revision_rows", source)
        for section in ("project", "drawing", "revisions", "workflow", "outputs", "branding", "legal", "fabrication", "notes"):
            self.assertIn(f'info_nav_{section}', source)
            self.assertIn(f'info_section_{section}', source)
        self.assertNotIn("TabbedContent", source[source.find("class ProjectInfoScreen"):source.find("class ReviewArtifactsScreen")])
        self.assertNotIn("grid-columns", source[source.find("#project_info_dialog"):source.find("#change_message")])


    def test_project_info_modal_mounts_core_fields_at_small_size(self) -> None:
        if not tui.textual_available():
            self.skipTest("Textual is not installed")

        import asyncio

        async def check() -> None:
            app = tui._build_textual_app()()
            async with app.run_test(size=(82, 26)) as pilot:
                await pilot.pause(0.2)
                app.action_project_info()
                await pilot.pause(0.5)
                for widget_id in (
                    "project_name",
                    "project_pcba_name",
                    "project_document_revision",
                    "document_revision_rows",
                    "variant_dev",
                    "outputs_combined_review_pdf",
                    "template_sheet_image",
                    "legal_profile",
                    "manufacturing_rohs_pb_free",
                    "manufacturing_fabrication_notes",
                ):
                    app.screen.query_one(f"#{widget_id}")

        asyncio.run(check())

    def test_project_info_section_rail_switches_visible_pane(self) -> None:
        if not tui.textual_available():
            self.skipTest("Textual is not installed")

        import asyncio

        async def check() -> None:
            app = tui._build_textual_app()()
            async with app.run_test(size=(100, 32)) as pilot:
                await pilot.pause(0.2)
                app.action_project_info()
                await pilot.pause(0.5)
                app.screen.query_one("#info_section_project")
                app.screen.query_one("#info_section_drawing")
                self.assertTrue(app.screen.query_one("#info_section_project").display)
                self.assertFalse(app.screen.query_one("#info_section_drawing").display)

                app.screen._show_info_section("drawing")
                await pilot.pause(0.1)
                self.assertFalse(app.screen.query_one("#info_section_project").display)
                self.assertTrue(app.screen.query_one("#info_section_drawing").display)
                self.assertIn("info-nav-active", app.screen.query_one("#info_nav_drawing").classes)

        asyncio.run(check())

    def test_dashboard_state_collects(self) -> None:
        state = tui.collect_dashboard_state()

        self.assertTrue(state.status.project_id)
        self.assertIn("->", state.preview_summary)
        self.assertIsInstance(state.changed_files, tuple)

    def test_notification_severity(self) -> None:
        self.assertEqual(
            "warning",
            tui._notification_severity((ValidationIssue("warning", "Careful"),)),
        )
        self.assertEqual(
            "error",
            tui._notification_severity((ValidationIssue("error", "Broken"),)),
        )

    def test_issue_summary(self) -> None:
        self.assertEqual("validation ok", tui._issue_summary(()))
        self.assertIn(
            "warning",
            tui._issue_summary((ValidationIssue("warning", "Careful"),)),
        )

    def test_timeline_contains_release_steps(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_timeline(tui._workflow_steps(state)).plain

        self.assertIn("Edit", text)
        self.assertIn("Record", text)
        self.assertIn("Preview", text)
        self.assertIn("Accept", text)
        self.assertEqual(tui._workflow_steps(state), state.workflow.steps)

    def test_inspector_shows_next_action(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_inspector(state).plain

        self.assertTrue(text.strip())
        self.assertIn("EVIDENCE", text)
        self.assertIn("RELEASE", text)
        self.assertIn("Reason:", text)
        self.assertIn("Stage:", text)
        self.assertNotIn("Generate Preview", text)

    def test_inspector_prompts_fetch_when_preview_ready(self) -> None:
        config = load_config()
        status = ProjectStatus(
            project_id=config.project_id,
            project_name=config.project_name,
            branch=config.dev_branch,
            dirty_count=0,
            ahead=0,
            behind=0,
            latest_tag="v0.1.0",
            unreleased_changes=True,
            variant=config.default_variant,
        )
        preview_run = PreviewRun(
            database_id="42",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview_state = evaluate_preview_state((preview_run,), "same", "CHECKED")
        workflow = build_workflow_state(config, status, (), "ready for dry-run", preview_state)
        state = tui.DashboardState(
            status=status,
            issues=(),
            preview_summary="preview summary",
            promote_summary="promote summary",
            ci_release_summary="release summary",
            release_summary="ready for dry-run",
            changed_files=(),
            workflow=workflow,
            accepted_summary="Accepted main evidence not checked.",
        )
        text = tui._format_inspector(state, "CI not polled").plain

        self.assertIn("Next: Fetch", text)
        self.assertIn("download preview to unlock Accept.", text)

    def test_tiny_inspector_stays_brief(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_inspector(state, brief=True).plain

        self.assertIn("NOW", text)
        self.assertIn("EVIDENCE", text)
        self.assertIn("RELEASE", text)
        self.assertNotIn("LOCKED", text)
        self.assertNotIn("Review:", text)
        self.assertNotIn("Reason:", text)

    def test_inspector_evidence_uses_separate_lines(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_inspector(
            state,
            "Artifact: boardwright-preview-CHECKED\nState: ready\nRun: 42\nReviewed: yes",
        ).plain

        self.assertIn("EVIDENCE", text)
        self.assertIn("Preview:", text)
        self.assertIn("\nAccept:", text)
        self.assertIn("\nRelease:", text)

    def test_footer_hint_is_contextual_and_short(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_footer_hint(state).plain

        self.assertIn("Next:", text)
        self.assertIn("v details", text)
        self.assertIn("F1 help", text)
        self.assertIn("g preview", text)
        self.assertIn("n sheet", text)
        self.assertNotIn("Commit + Push", text)

    def test_shortcut_help_mentions_validation(self) -> None:
        text = tui._format_shortcut_help().plain

        self.assertIn("Main screen", text)
        self.assertIn("v details", text)
        self.assertIn("Cues", text)
        self.assertIn("g preview", text)
        self.assertIn("n new sheet", text)
        self.assertIn("o folder", text)
        self.assertIn("O README", text)
        self.assertNotIn("Open Preview", text)

    def test_ci_status_shortens(self) -> None:
        self.assertEqual("CI not polled", tui._ci_status_short("CI not polled"))
        self.assertLessEqual(len(tui._ci_status_short("x" * 80)), 36)
        self.assertEqual(
            "preview CHECKED running",
            tui._ci_status_short("RUNNING | boardwright-preview-CHECKED"),
        )
        self.assertEqual(
            "preview CHECKED ready",
            tui._ci_status_short(
                "Artifact: boardwright-preview-CHECKED\nState: ready\nRun: 42\nReviewed: yes"
            ),
        )
        self.assertEqual(
            "preview CHECKED review needed",
            tui._ci_status_short(
                "Artifact: boardwright-preview-CHECKED\nState: ready\nRun: 42\nReviewed: no"
            ),
        )
        self.assertEqual("preview PRELIMINARY dispatching", tui._ci_status_short("Preview PRELIMINARY dispatching..."))

    def test_top_status_is_rich_text(self) -> None:
        state = tui.collect_dashboard_state()

        self.assertTrue(tui._format_top_status(state.status, state.issues, "CI not polled").plain)

    def test_tiny_top_status_is_shorter(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_top_status(state.status, state.issues, "CI not polled", brief=True).plain

        self.assertIn(state.status.project_id, text)
        self.assertIn("dev", text)
        self.assertIn("validation", text)
        self.assertNotIn("branch", text)
        self.assertNotIn("remote", text)

    def test_tiny_project_summary_is_shorter(self) -> None:
        state = tui.collect_dashboard_state()
        text = tui._format_project_summary(state.status, brief=True)

        self.assertIn("PCBA:", text)
        self.assertIn("Dev default:", text)
        self.assertIn("Git:", text)
        self.assertNotIn("Preview default:", text)
        self.assertNotIn("Remote:", text)

    def test_changed_files_are_badged_by_git_status(self) -> None:
        text = tui._format_changed_files((" M src/boardwright/tui.py", "?? tests/new_file.txt")).plain

        self.assertIn("Legend:", text)
        self.assertIn("[MOD]", text)
        self.assertIn("[NEW]", text)
        self.assertIn("src/boardwright/tui.py", text)
        self.assertIn("tests/new_file.txt", text)

    def test_validation_summary_is_compact(self) -> None:
        issues = tuple(
            ValidationIssue("warning", f"Warn {index}") for index in range(6)
        ) + (ValidationIssue("error", "Broken"),)

        text = tui._format_issues(issues).plain

        self.assertIn("Validation: 1 error(s), 6 warning(s)", text)
        self.assertIn("Press `v` for details", text)
        self.assertLessEqual(text.count("\n"), 5)

    def test_tiny_validation_summary_limits_noise(self) -> None:
        issues = tuple(
            ValidationIssue("warning", f"Warn {index}") for index in range(5)
        ) + (ValidationIssue("error", "Broken"),)

        text = tui._format_issues(issues, brief=True).plain

        self.assertIn("Validation: 1 error(s), 5 warning(s)", text)
        self.assertLessEqual(text.count("\n"), 4)

    def test_tiny_changed_files_summary_limits_noise(self) -> None:
        changed = tuple(f" M file_{index}.txt" for index in range(9))

        text = tui._format_changed_files(changed, brief=True).plain

        self.assertIn("[MOD] file_0.txt", text)
        self.assertIn("[MOD] file_5.txt", text)
        self.assertIn("...and 3 more file(s)", text)

    def test_validation_details_are_narrative(self) -> None:
        issues = (
            ValidationIssue("error", "Broken"),
            ValidationIssue("warning", "Careful"),
        )

        text = tui._format_validation_details(issues).plain

        self.assertIn("1 error(s), 1 warning(s)", text)
        self.assertIn("Errors", text)
        self.assertIn("Warnings", text)
        self.assertIn("boardwright doctor", text)

    def test_screen_subtitle_is_short_brand_tagline(self) -> None:
        app = tui._build_textual_app()()

        self.assertEqual("Design. Ship.", app.SUB_TITLE)

    def test_happy_path_status_strip_and_inspector(self) -> None:
        config = load_config()
        status = ProjectStatus(
            project_id="TEST",
            project_name="Test Board",
            branch="dev",
            dirty_count=0,
            ahead=0,
            behind=0,
            latest_tag="v0.1.0",
            unreleased_changes=False,
            variant="CHECKED",
        )
        preview_run = PreviewRun(
            database_id="42",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview_state = evaluate_preview_state((preview_run,), "same", "CHECKED")
        preview_state = type(preview_state)(**{**preview_state.__dict__, "reviewed": True})
        accepted_run = AcceptedRun(
            database_id="77",
            status="completed",
            conclusion="success",
            branch="main",
            head_sha="same",
            created_at="2026-05-23T00:00:00Z",
            title="accepted",
        )
        accepted_state = evaluate_accepted_state((accepted_run,), "same", config.main_workflow)
        workflow = build_workflow_state(
            config,
            status,
            (),
            "ready for dry-run",
            preview_state,
            accepted_state,
        )
        dashboard = tui.DashboardState(
            status=status,
            issues=(),
            preview_summary="preview summary",
            promote_summary="promote summary",
            ci_release_summary="release summary",
            release_summary="ready for dry-run",
            changed_files=(),
            workflow=workflow,
            accepted_summary=format_accepted_state(accepted_state),
        )

        top_status = tui._format_top_status(dashboard.status, dashboard.issues, "CI not polled").plain
        inspector = tui._format_inspector(
            dashboard,
            "CI: Preview: CHECKED ready | Accept: ready | Release: prepare running",
        ).plain

        self.assertIn("validation ok", top_status)
        self.assertIn("Release", inspector)
        self.assertIn("Release inputs look good.", inspector)
        self.assertIn("Ready for dry run.", inspector)
        self.assertIn("Stage: release_ready", inspector)

    def test_embed_template_sheet_image_updates_all_templates(self) -> None:
        config = type(
            "Config",
            (),
            {
                "root": Path.cwd(),
                "template_sheet_image": "assets/logos/logo-block-black.png",
            },
        )()

        with patch.object(tui, "embed_logo_in_worksheets", return_value=()) as embed:
            tui._embed_template_sheet_image(config)

        self.assertTrue(embed.called)
        self.assertGreater(len(embed.call_args.args[0]), 1)

    def test_ci_status_style_prioritizes_active_work(self) -> None:
        self.assertEqual(
            f"bold {tui.STATUS_LOADING}",
            tui._ci_status_style("Preview:CHECKED ready | Accept:ready | Release:prepare running"),
        )
        self.assertEqual(f"bold {tui.STATUS_SUCCESS}", tui._ci_status_style("Preview:CHECKED ready | Accept:ready"))
        self.assertEqual(f"bold {tui.STATUS_ERROR}", tui._ci_status_style("Preview:CHECKED ready | Accept:failed"))

    def test_review_artifact_summary_contains_evidence(self) -> None:
        run = PreviewRun(
            database_id="42",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="abcdef",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview_state = evaluate_preview_state((run,), "abcdef", "CHECKED")

        text = tui._format_review_artifacts(preview_state, "Boardwright Dev Preview: completed/success")

        self.assertIn("READY | boardwright-preview-CHECKED", text)
        self.assertIn("Recent CI", text)
        self.assertIn("Run 42", text)

    def test_polled_ci_status_summarizes_preview_accepted_and_release(self) -> None:
        run = PreviewRun(
            database_id="42",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="abcdef",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview_state = evaluate_preview_state((run,), "abcdef", "CHECKED")
        accepted_state = AcceptedMainState(
            state="missing",
            workflow="main-outputs.yaml",
            expected_sha="abcdef",
            message="No accepted outputs.",
        )

        text = tui._format_polled_ci_status(
            preview_state,
            accepted_state,
            release_status="Release: prepare in_progress run 77 Prepare 0.1.3",
        )

        self.assertIn("CI: Preview: CHECKED review | Accept: missing | Release: prepare running", text)
        self.assertIn("Artifact: boardwright-preview-CHECKED", text)
        self.assertIn("Main:", text)
        self.assertIn("No accepted outputs.", text)
        self.assertIn("Release: prepare in_progress run 77", text)

    def test_inspector_splits_ci_evidence_by_workflow(self) -> None:
        state = tui.collect_dashboard_state()
        ci_status = (
            "CI: Preview: CHECKED ready | Accept: ready | Release: prepare running\n\n"
            "Preview:\nArtifact: boardwright-preview-CHECKED\n"
            "Main:\nState: ready\n"
            "Release: prepare in_progress run 77 Prepare 0.1.3"
        )

        text = tui._format_inspector(state, ci_status).plain

        self.assertIn("Preview: CHECKED ready", text)
        self.assertIn("Accept: ready", text)
        self.assertIn("Release: prepare running", text)
        self.assertNotIn("Preview: CHECKED ready | Accept: ready", text)

    def test_release_ci_status_from_recent_runs(self) -> None:
        runs = (
            WorkflowRunStatus(
                workflow="Boardwright Prepare Release Tag",
                status="in_progress",
                conclusion="",
                branch="main",
                title="Prepare 0.1.3 (CHECKED, release)",
                database_id="77",
            ),
            WorkflowRunStatus(
                workflow="Boardwright Publish Release",
                status="completed",
                conclusion="success",
                branch="0.1.2",
                title="Publish 0.1.2 release package",
                database_id="72",
            ),
        )

        text = tui._release_ci_status_from_runs(runs)

        self.assertIn("Release: prepare in_progress run 77", text)
        self.assertIn("publish success run 72", text)

    def test_review_artifact_summary_shows_selected_variant_artifact(self) -> None:
        run = PreviewRun(
            database_id="42",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="abcdef",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview_state = evaluate_preview_state((run,), "abcdef", "PRELIMINARY")

        text = tui._format_review_artifacts(preview_state, "Boardwright Dev Preview: completed/success")

        self.assertIn("READY | boardwright-preview-PRELIMINARY", text)

    def test_review_artifact_blocks_are_hierarchical(self) -> None:
        run = PreviewRun(
            database_id="42",
            status="completed",
            conclusion="success",
            branch="dev",
            head_sha="abcdef",
            created_at="2026-05-23T00:00:00Z",
            title="preview",
        )
        preview_state = evaluate_preview_state((run,), "abcdef", "CHECKED")

        status, message, run_summary = tui._review_artifact_blocks(preview_state)

        self.assertIn("READY | boardwright-preview-CHECKED", status)
        self.assertIn("fresh", message)
        self.assertIn("Run 42", run_summary)

    def test_download_progress_text_mentions_variant(self) -> None:
        text = tui._download_progress_text("PRELIMINARY")

        self.assertIn("boardwright-preview-PRELIMINARY", text)
        self.assertIn("[###.......]", text)

    def test_open_path_uses_system_opener(self) -> None:
        path = Path("tests")
        with patch.object(tui.os, "startfile", create=True) as startfile:
            message = tui._open_path(path)

        startfile.assert_called_once()
        self.assertIn("Opened", message)
        self.assertIn("tests", message)

    def test_release_checklist_blocks_unready_accepted_outputs(self) -> None:
        accepted_state = AcceptedMainState(
            state="stale",
            workflow="main-outputs.yaml",
            expected_sha="abcdef",
            message="Accepted outputs are stale.",
        )

        checklist = tui.build_release_checklist(
            load_config(),
            "0.1.2",
            "RELEASED",
            "release",
            "B",
            "Release connector update",
            accepted_state,
        )

        text = tui._format_release_checklist(checklist)
        self.assertFalse(checklist.can_dispatch)
        self.assertIn("[ ] Main", text)
        self.assertIn("Blockers:", text)
        self.assertIn("Resolve blockers first.", text)

    def test_release_checklist_reports_invalid_release_inputs(self) -> None:
        accepted_state = AcceptedMainState(
            state="ready",
            workflow="main-outputs.yaml",
            expected_sha="abcdef",
            message="Accepted main outputs are fresh.",
        )

        checklist = tui.build_release_checklist(
            load_config(),
            "v0.1.2",
            "RELEASED",
            "release",
            "B",
            "Release connector update",
            accepted_state,
        )

        text = tui._format_release_checklist(checklist)
        self.assertFalse(checklist.can_dispatch)
        self.assertIn("Release version must use semantic form", text)
        self.assertIn("[ ] Inputs", text)
        self.assertIn("Drawing rev B", text)


if __name__ == "__main__":
    unittest.main()
