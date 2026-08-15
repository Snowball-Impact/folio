import unittest
from unittest.mock import MagicMock, patch

from folio_app.config import Settings
from folio_app.components.project_editor import (
    _create_and_publish_powerbi_project,
    _publish_replacement_pbix,
    _wait_for_powerbi_report_ready,
    render_edit_project_form,
)
from folio_app.services.powerbi import PowerBIImportResult
from folio_app.services.project_thumbnails import ThumbnailCaptureResult
from folio_app.services.project_types import ProjectResult


def _powerbi_settings() -> Settings:
    return Settings(
        supabase_url="https://example.supabase.co",
        supabase_key="publishable",
        app_url="http://localhost:8501",
        cookie_password="password",
        ga_measurement_id="",
        powerbi_tenant_id="tenant-id",
        powerbi_client_id="client-id",
        powerbi_client_secret="client-secret",
        powerbi_workspace_id="workspace-id",
        powerbi_capture_ready_wait_seconds=0,
    )


class _UploadedFile:
    name = "report.pbix"

    def getbuffer(self) -> memoryview:
        return memoryview(b"pbix")


def _valid_edit_form_data() -> dict:
    return {
        "title": "Edited Project",
        "one_liner": "",
        "tags": "",
        "platform": "other",
        "project_body": "## 문제 정의\n내용",
        "power_bi_url": "",
        "report_url": "",
        "github_url": "",
        "thumbnail_url": "",
        "thumbnail_mode": "auto_cover",
        "thumbnail_file": None,
        "delete_thumbnail": False,
        "pbix_file": None,
        "delete_pbix": False,
        "is_public": True,
    }


class ProjectEditorFlowTests(unittest.TestCase):
    @patch("folio_app.components.project_editor.navigate")
    @patch("folio_app.components.project_editor.clear_project_draft")
    @patch("folio_app.components.project_editor.update_project", return_value=ProjectResult(True, "프로젝트가 수정되었습니다.", "project-1"))
    @patch("folio_app.components.project_editor.save_project_draft")
    @patch("folio_app.components.project_editor.load_project_draft", return_value=_valid_edit_form_data())
    @patch("folio_app.components.project_editor.apply_pending_draft_clear")
    @patch("folio_app.components.project_editor.get_powerbi_report_for_project", return_value=None)
    @patch("folio_app.components.project_editor.render_project_form", return_value=(_valid_edit_form_data(), True, False))
    @patch("folio_app.components.project_editor.render_hero")
    @patch("folio_app.components.project_editor.st.session_state", {})
    def test_edit_success_navigates_to_home_project_detail(
        self,
        _render_hero,
        _render_form,
        _powerbi_report,
        _apply_draft_clear,
        _load_draft,
        _save_draft,
        _update_project,
        _clear_draft,
        navigate,
    ) -> None:
        render_edit_project_form("author-id", {"id": "project-1", "title": "Project"})

        navigate.assert_called_once_with("Home", project_id="project-1")

    @patch("folio_app.components.project_editor.navigate")
    @patch("folio_app.components.project_editor.clear_project_draft")
    @patch("folio_app.components.project_editor._publish_replacement_pbix")
    @patch("folio_app.components.project_editor.update_project", return_value=ProjectResult(True, "프로젝트가 수정되었습니다.", "project-1"))
    @patch("folio_app.components.project_editor.save_project_draft")
    @patch("folio_app.components.project_editor.load_project_draft", return_value=_valid_edit_form_data())
    @patch("folio_app.components.project_editor.apply_pending_draft_clear")
    @patch("folio_app.components.project_editor.get_powerbi_report_for_project", return_value=None)
    @patch("folio_app.components.project_editor.render_project_form")
    @patch("folio_app.components.project_editor.render_hero")
    @patch("folio_app.components.project_editor.st.session_state", {})
    def test_edit_with_pbix_skips_pre_publish_thumbnail_capture(
        self,
        _render_hero,
        render_form,
        _powerbi_report,
        _apply_draft_clear,
        _load_draft,
        _save_draft,
        update_project,
        publish_replacement,
        _clear_draft,
        _navigate,
    ) -> None:
        form_data = _valid_edit_form_data()
        form_data["platform"] = "powerbi"
        form_data["thumbnail_mode"] = "capture"
        form_data["pbix_file"] = _UploadedFile()
        render_form.return_value = (form_data, True, False)
        publish_replacement.return_value = PowerBIImportResult(True, "published", "project-1")

        render_edit_project_form("author-id", {"id": "project-1", "title": "Project"})

        payload = update_project.call_args.args[2]
        self.assertTrue(payload["skip_thumbnail_capture"])
        publish_replacement.assert_called_once_with("project-1", form_data["pbix_file"], payload)


class ProjectEditorPowerBITests(unittest.TestCase):
    @patch("folio_app.components.project_editor.time.sleep")
    def test_powerbi_capture_wait_reports_progress_each_second(self, sleep) -> None:
        events = []

        _wait_for_powerbi_report_ready(3, lambda value, text: events.append((value, text)))

        self.assertEqual(sleep.call_count, 3)
        self.assertEqual(events[0], (41, "Power BI 보고서 렌더링 준비를 기다리는 중입니다. 3/3초"))
        self.assertEqual(events[-1], (44, "Power BI 보고서 렌더링 준비를 기다리는 중입니다. 1/3초"))

    @patch("folio_app.components.project_editor.st.progress")
    @patch("folio_app.components.project_editor.capture_project_thumbnail_from_html")
    @patch("folio_app.components.project_editor.publish_pbix_for_project")
    @patch("folio_app.components.project_editor.create_project")
    @patch("folio_app.components.project_editor.get_settings", return_value=_powerbi_settings())
    def test_create_and_publish_sets_processing_before_pbix_import(
        self,
        _settings,
        create_project,
        publish_pbix,
        capture_thumbnail,
        progress,
    ) -> None:
        progress.return_value = MagicMock()
        create_project.return_value = ProjectResult(True, "created", "project-id")
        publish_pbix.return_value = PowerBIImportResult(True, "published", "project-id")
        capture_thumbnail.return_value = ThumbnailCaptureResult(True, skipped=True)

        result = _create_and_publish_powerbi_project("user-id", {"title": "Project"}, _UploadedFile())

        self.assertTrue(result.ok)
        create_payload = create_project.call_args.args[1]
        self.assertEqual(create_payload["project_type"], "powerbi")
        self.assertEqual(create_payload["status"], "processing")
        self.assertEqual(create_payload["embed_status"], "external_only")
        publish_pbix.assert_called_once()
        capture_thumbnail.assert_not_called()

    @patch("folio_app.components.project_editor.clear_project_caches")
    @patch("folio_app.components.project_editor.st.progress")
    @patch("folio_app.components.project_editor.capture_project_thumbnail_from_html")
    @patch("folio_app.components.project_editor.generate_embed_token")
    @patch("folio_app.components.project_editor.publish_pbix_for_project")
    @patch("folio_app.components.project_editor.create_project")
    @patch("folio_app.components.project_editor.get_settings", return_value=_powerbi_settings())
    def test_create_and_publish_captures_thumbnail_after_pbix_publish(
        self,
        _settings,
        create_project,
        publish_pbix,
        generate_token,
        capture_thumbnail,
        progress,
        clear_caches,
    ) -> None:
        progress.return_value = MagicMock()
        create_project.return_value = ProjectResult(True, "created", "project-id")
        publish_pbix.return_value = PowerBIImportResult(
            True,
            "published",
            "project-id",
            report_id="report-id",
            dataset_id="dataset-id",
            embed_url="https://app.powerbi.com/reportEmbed?reportId=report-id",
        )
        generate_token.return_value = {"token": "embed-token"}
        capture_thumbnail.return_value = ThumbnailCaptureResult(True, url="https://cdn.example.com/thumb.jpg")

        result = _create_and_publish_powerbi_project(
            "user-id",
            {"title": "Project", "thumbnail_mode": "capture"},
            _UploadedFile(),
        )

        self.assertTrue(result.ok)
        create_payload = create_project.call_args.args[1]
        self.assertTrue(create_payload["skip_thumbnail_capture"])
        self.assertIn("썸네일 캡처도 완료", result.message)
        generate_token.assert_called_once_with("report-id", "dataset-id")
        self.assertEqual(capture_thumbnail.call_args.args[0], "project-id")
        self.assertIn("embed-token", capture_thumbnail.call_args.args[1])
        self.assertIn("https://app.powerbi.com/reportEmbed?reportId=report-id", capture_thumbnail.call_args.args[1])
        clear_caches.assert_called_once()

    @patch("folio_app.components.project_editor.st.error")
    @patch("folio_app.components.project_editor.get_settings")
    def test_create_and_publish_stops_when_powerbi_settings_are_missing(self, get_settings, error) -> None:
        get_settings.return_value = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable",
            app_url="http://localhost:8501",
            cookie_password="password",
            ga_measurement_id="",
        )

        result = _create_and_publish_powerbi_project("user-id", {"title": "Project"}, _UploadedFile())

        self.assertIsNone(result)
        error.assert_called_once()

    @patch("folio_app.components.project_editor.clear_project_caches")
    @patch("folio_app.components.project_editor.st.progress")
    @patch("folio_app.components.project_editor.capture_project_thumbnail_from_html")
    @patch("folio_app.components.project_editor.generate_embed_token")
    @patch("folio_app.components.project_editor.publish_pbix_for_project")
    @patch("folio_app.components.project_editor.get_settings", return_value=_powerbi_settings())
    def test_publish_replacement_captures_thumbnail_after_pbix_publish(
        self,
        _settings,
        publish_pbix,
        generate_token,
        capture_thumbnail,
        progress,
        _clear_caches,
    ) -> None:
        progress.return_value = MagicMock()
        publish_pbix.return_value = PowerBIImportResult(
            True,
            "published",
            "project-id",
            report_id="new-report-id",
            dataset_id="new-dataset-id",
            embed_url="https://app.powerbi.com/reportEmbed?reportId=new-report-id",
        )
        generate_token.return_value = {"token": "new-embed-token"}
        capture_thumbnail.return_value = ThumbnailCaptureResult(True, url="https://cdn.example.com/new-thumb.jpg")

        result = _publish_replacement_pbix(
            "project-id",
            _UploadedFile(),
            {"thumbnail_mode": "capture", "skip_thumbnail_capture": True},
        )

        self.assertTrue(result.ok)
        self.assertIn("썸네일 캡처도 완료", result.message)
        publish_pbix.assert_called_once()
        generate_token.assert_called_once_with("new-report-id", "new-dataset-id")
        self.assertIn("new-embed-token", capture_thumbnail.call_args.args[1])
        self.assertIn("new-report-id", capture_thumbnail.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
