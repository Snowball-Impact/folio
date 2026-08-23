import unittest
from unittest.mock import MagicMock, patch

from folio_app.services.project_reports import REPORT_REASON_OTHER, submit_project_report
from folio_app.services.auth_types import AuthResult


class ProjectReportServiceTests(unittest.TestCase):
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, ""))
    @patch("folio_app.services.project_reports.get_supabase_client")
    def test_submit_project_report_inserts_normalized_payload(self, get_client, _ensure_auth) -> None:
        client = MagicMock()
        table = client.table.return_value
        table.insert.return_value.execute.return_value.data = [{"id": "report-1"}]
        get_client.return_value = client

        result = submit_project_report("project-1", "user-1", "embed_broken", "  iframe   is blank  ")

        self.assertTrue(result.ok)
        self.assertEqual(result.report_id, "report-1")
        client.table.assert_called_once_with("content_reports")
        table.insert.assert_called_once_with(
            {
                "project_id": "project-1",
                "reporter_id": "user-1",
                "reason": "embed_broken",
                "details": "iframe is blank",
            }
        )

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, ""))
    @patch("folio_app.services.project_reports.get_supabase_client")
    def test_submit_project_report_falls_back_to_other_reason(self, get_client, _ensure_auth) -> None:
        client = MagicMock()
        table = client.table.return_value
        table.insert.return_value.execute.return_value.data = [{"id": "report-1"}]
        get_client.return_value = client

        submit_project_report("project-1", "user-1", "unexpected", "")

        payload = table.insert.call_args.args[0]
        self.assertEqual(payload["reason"], REPORT_REASON_OTHER)
        self.assertIsNone(payload["details"])

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, ""))
    @patch("folio_app.services.project_reports.get_supabase_client")
    def test_submit_project_report_reports_missing_schema(self, get_client, _ensure_auth) -> None:
        client = MagicMock()
        client.table.return_value.insert.return_value.execute.side_effect = RuntimeError(
            'relation "public.content_reports" does not exist'
        )
        get_client.return_value = client

        result = submit_project_report("project-1", "user-1", "embed_broken")

        self.assertFalse(result.ok)
        self.assertIn("content_reports 스키마", result.message)

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(False, "다시 로그인하세요."))
    def test_submit_project_report_requires_authenticated_session(self, _ensure_auth) -> None:
        result = submit_project_report("project-1", "user-1", "embed_broken")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "다시 로그인하세요.")


if __name__ == "__main__":
    unittest.main()
