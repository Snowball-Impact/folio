from dataclasses import replace
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.config import Settings
from folio_app.services.powerbi import (
    PowerBIServiceError,
    delete_powerbi_report_for_project,
    fetch_powerbi_access_token,
    generate_embed_token,
    get_powerbi_embed_config,
    post_pbix_import,
    poll_import_completion,
    publish_pbix_for_project,
)


def _settings() -> Settings:
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
        pbix_max_upload_mb=10,
        powerbi_import_poll_seconds=1,
    )


class _Response:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload


class PowerBIAuthTests(unittest.TestCase):
    def test_fetch_access_token_uses_client_credentials(self) -> None:
        session = MagicMock()
        session.post.return_value = _Response({"access_token": "token"})

        token = fetch_powerbi_access_token(_settings(), session=session)

        self.assertEqual(token, "token")
        session.post.assert_called_once()
        url = session.post.call_args.args[0]
        data = session.post.call_args.kwargs["data"]
        self.assertIn("/tenant-id/oauth2/v2.0/token", url)
        self.assertEqual(data["client_id"], "client-id")
        self.assertEqual(data["client_secret"], "client-secret")
        self.assertEqual(data["grant_type"], "client_credentials")

    def test_fetch_access_token_raises_safe_error_without_token(self) -> None:
        session = MagicMock()
        session.post.return_value = _Response({})

        with self.assertRaisesRegex(PowerBIServiceError, "인증 토큰"):
            fetch_powerbi_access_token(_settings(), session=session)


class PowerBIImportTests(unittest.TestCase):
    def test_post_pbix_import_sends_multipart_to_workspace(self) -> None:
        session = MagicMock()
        session.post.return_value = _Response({"id": "import-id"})

        result = post_pbix_import(_settings(), "token", b"pbix", "project_report.pbix", session=session)

        self.assertEqual(result["id"], "import-id")
        session.post.assert_called_once()
        url = session.post.call_args.args[0]
        kwargs = session.post.call_args.kwargs
        self.assertTrue(url.endswith("/groups/workspace-id/imports"))
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token")
        self.assertEqual(kwargs["params"]["datasetDisplayName"], "project_report.pbix")
        self.assertIn("file", kwargs["files"])

    @patch("folio_app.services.powerbi.time.sleep")
    @patch("folio_app.services.powerbi.get_import")
    def test_poll_import_completion_reports_remaining_wait_time(self, get_import, sleep) -> None:
        get_import.side_effect = [
            {"importState": "Publishing"},
            {"importState": "Publishing"},
            {"importState": "Succeeded"},
        ]
        events = []
        settings = replace(_settings(), powerbi_import_poll_seconds=3)

        result = poll_import_completion(
            settings,
            "token",
            "import-id",
            progress_callback=lambda value, text: events.append((value, text)),
        )

        self.assertEqual(result["importState"], "Succeeded")
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(events[0], (36, "Power BI 게시 및 배포를 기다리는 중입니다. 3/3초"))
        self.assertEqual(events[-1], (38, "Power BI 게시 및 배포를 기다리는 중입니다. 2/3초"))

    @patch("folio_app.services.powerbi.get_supabase_client")
    @patch("folio_app.services.powerbi.get_report_metadata")
    @patch("folio_app.services.powerbi.poll_import_completion")
    @patch("folio_app.services.powerbi.post_pbix_import")
    @patch("folio_app.services.powerbi.fetch_powerbi_access_token")
    def test_publish_pbix_upserts_report_and_marks_project_published(
        self,
        fetch_token,
        post_import,
        poll_import,
        get_report,
        get_client,
    ) -> None:
        fetch_token.return_value = "token"
        post_import.return_value = {"id": "import-id"}
        poll_import.return_value = {
            "importState": "Succeeded",
            "reports": [{"id": "report-id", "datasetId": "dataset-id"}],
        }
        get_report.return_value = {
            "id": "report-id",
            "datasetId": "dataset-id",
            "embedUrl": "https://app.powerbi.com/reportEmbed",
            "webUrl": "https://app.powerbi.com/report",
        }
        table_builders = {}

        def table(name):
            builder = table_builders.setdefault(name, MagicMock())
            builder.upsert.return_value = builder
            builder.update.return_value = builder
            builder.eq.return_value = builder
            builder.execute.return_value = SimpleNamespace(data=[{}])
            return builder

        client = MagicMock()
        client.table.side_effect = table
        get_client.return_value = client

        progress_callback = MagicMock()
        result = publish_pbix_for_project(
            "project-id",
            b"pbix",
            "report.pbix",
            settings=_settings(),
            progress_callback=progress_callback,
        )

        self.assertTrue(result.ok)
        self.assertIs(poll_import.call_args.kwargs["progress_callback"], progress_callback)
        self.assertEqual(result.report_id, "report-id")
        powerbi_payload = table_builders["powerbi_reports"].upsert.call_args.args[0]
        self.assertEqual(powerbi_payload["project_id"], "project-id")
        self.assertEqual(powerbi_payload["workspace_id"], "workspace-id")
        self.assertEqual(powerbi_payload["report_id"], "report-id")
        project_payload = table_builders["projects"].update.call_args.args[0]
        self.assertEqual(project_payload["status"], "published")
        self.assertEqual(project_payload["project_type"], "powerbi")

    @patch("folio_app.services.powerbi.get_supabase_client")
    @patch("folio_app.services.powerbi.poll_import_completion")
    @patch("folio_app.services.powerbi.post_pbix_import")
    @patch("folio_app.services.powerbi.fetch_powerbi_access_token")
    def test_publish_pbix_keeps_processing_when_import_is_still_publishing(
        self,
        fetch_token,
        post_import,
        poll_import,
        get_client,
    ) -> None:
        fetch_token.return_value = "token"
        post_import.return_value = {"id": "import-id"}
        poll_import.return_value = {"importState": "Publishing"}
        table_builders = {}

        def table(name):
            builder = table_builders.setdefault(name, MagicMock())
            builder.upsert.return_value = builder
            builder.update.return_value = builder
            builder.eq.return_value = builder
            builder.execute.return_value = SimpleNamespace(data=[{}])
            return builder

        client = MagicMock()
        client.table.side_effect = table
        get_client.return_value = client

        result = publish_pbix_for_project("project-id", b"pbix", "report.pbix", settings=_settings())

        self.assertFalse(result.ok)
        self.assertEqual(result.import_status, "publishing")
        project_payload = table_builders["projects"].update.call_args.args[0]
        self.assertEqual(project_payload["status"], "processing")
        report_payload = table_builders["powerbi_reports"].upsert.call_args.args[0]
        self.assertEqual(report_payload["import_status"], "publishing")

    def test_publish_pbix_rejects_non_pbix_file(self) -> None:
        result = publish_pbix_for_project("project-id", b"content", "report.txt", settings=_settings())

        self.assertFalse(result.ok)
        self.assertIn("PBIX", result.message)

    @patch("folio_app.services.powerbi.get_supabase_client")
    def test_delete_powerbi_report_removes_metadata_and_clears_project_embed(self, get_client) -> None:
        table_builders = {}

        def table(name):
            builder = table_builders.setdefault(name, MagicMock())
            builder.delete.return_value = builder
            builder.update.return_value = builder
            builder.eq.return_value = builder
            builder.execute.return_value = SimpleNamespace(data=[{}])
            return builder

        client = MagicMock()
        client.table.side_effect = table
        get_client.return_value = client

        delete_powerbi_report_for_project("project-id")

        table_builders["powerbi_reports"].delete.assert_called_once()
        table_builders["powerbi_reports"].eq.assert_called_with("project_id", "project-id")
        project_payload = table_builders["projects"].update.call_args.args[0]
        self.assertIsNone(project_payload["power_bi_url"])
        self.assertEqual(project_payload["embed_status"], "external_only")


class PowerBIEmbedTokenTests(unittest.TestCase):
    @patch("folio_app.services.powerbi.fetch_powerbi_access_token", return_value="token")
    def test_generate_embed_token_posts_report_and_dataset(self, _fetch_token) -> None:
        session = MagicMock()
        session.post.return_value = _Response({"token": "embed-token"})

        result = generate_embed_token("report-id", "dataset-id", settings=_settings(), session=session)

        self.assertEqual(result["token"], "embed-token")
        url = session.post.call_args.args[0]
        kwargs = session.post.call_args.kwargs
        self.assertTrue(url.endswith("/GenerateToken"))
        self.assertEqual(kwargs["json"]["reports"], [{"id": "report-id"}])
        self.assertEqual(kwargs["json"]["datasets"], [{"id": "dataset-id"}])

    @patch("folio_app.services.powerbi.generate_embed_token", return_value={"token": "embed-token", "expiration": "2026-08-11T00:00:00Z"})
    @patch("folio_app.services.powerbi.get_supabase_client")
    def test_get_embed_config_reads_metadata_and_generates_runtime_token(self, get_client, _generate_token) -> None:
        builder = MagicMock()
        builder.select.return_value = builder
        builder.eq.return_value = builder
        builder.maybe_single.return_value = builder
        builder.execute.return_value = SimpleNamespace(
            data={
                "report_id": "report-id",
                "dataset_id": "dataset-id",
                "embed_url": "https://app.powerbi.com/reportEmbed",
            }
        )
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        config = get_powerbi_embed_config("project-id")

        self.assertEqual(config.report_id, "report-id")
        self.assertEqual(config.dataset_id, "dataset-id")
        self.assertEqual(config.embed_token, "embed-token")
        client.table.assert_called_once_with("powerbi_reports")


if __name__ == "__main__":
    unittest.main()
