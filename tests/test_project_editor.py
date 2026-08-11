import unittest
from unittest.mock import MagicMock, patch

from folio_app.config import Settings
from folio_app.components.project_editor import _create_and_publish_powerbi_project
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
    )


class _UploadedFile:
    name = "report.pbix"

    def getbuffer(self) -> memoryview:
        return memoryview(b"pbix")


class ProjectEditorPowerBITests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
