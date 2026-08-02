import unittest
from email.message import EmailMessage
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.config import Settings
from folio_app.services.email_notifications import (
    _build_comment_email_message,
    _project_url,
    send_project_comment_email,
)


class EmailNotificationTests(unittest.TestCase):
    def test_send_project_comment_email_skips_when_unconfigured(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="http://localhost:8501",
            cookie_password="password",
            ga_measurement_id="",
        )

        with patch("folio_app.services.email_notifications.get_settings", return_value=settings):
            result = send_project_comment_email(
                {"id": "project-1", "title": "분석 프로젝트"},
                "author-1",
                {"id": "comment-1", "body": "좋아요"},
                "commenter-1",
            )

        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    @patch("folio_app.services.email_notifications._send_email")
    @patch("folio_app.services.email_notifications.create_client")
    def test_send_project_comment_email_loads_profiles_and_sends(self, create_client, send_email) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="https://folio.example",
            cookie_password="password",
            ga_measurement_id="",
            supabase_service_role_key="service-role",
            smtp_host="smtp.example.com",
            smtp_from_email="noreply@example.com",
        )
        recipient_builder = _profile_builder({"id": "author-1", "email": "author@example.com", "name": "작성자"})
        actor_builder = _profile_builder({"id": "commenter-1", "email": "commenter@example.com", "name": "댓글러"})
        client = MagicMock()
        client.table.side_effect = [recipient_builder, actor_builder]
        create_client.return_value = client

        with patch("folio_app.services.email_notifications.get_settings", return_value=settings):
            result = send_project_comment_email(
                {"id": "project-1", "title": "분석 프로젝트"},
                "author-1",
                {"id": "comment-1", "body": "좋아요"},
                "commenter-1",
            )

        self.assertTrue(result.ok)
        self.assertEqual(create_client.call_count, 2)
        sent_message = send_email.call_args.args[1]
        self.assertIsInstance(sent_message, EmailMessage)
        self.assertEqual(sent_message["To"], "author@example.com")
        self.assertIn("[FOLIO] 분석 프로젝트", sent_message["Subject"])

    def test_build_comment_email_message_contains_project_link(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="https://folio.example",
            cookie_password="password",
            ga_measurement_id="",
            smtp_from_email="noreply@example.com",
        )

        message = _build_comment_email_message(
            settings,
            "author@example.com",
            "새 댓글",
            {"id": "project-1", "title": "분석 프로젝트"},
            {"body": "좋아요"},
            "댓글러",
        )

        text_body = message.get_body(preferencelist=("plain",)).get_content()
        self.assertIn("https://folio.example?page=Home&project_id=project-1", text_body)

    def test_project_url_preserves_existing_query(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="https://folio.example/app?source=email",
            cookie_password="password",
            ga_measurement_id="",
        )

        self.assertEqual(
            _project_url(settings, "project-1"),
            "https://folio.example/app?source=email&page=Home&project_id=project-1",
        )


def _profile_builder(profile: dict) -> MagicMock:
    builder = MagicMock()
    builder.select.return_value = builder
    builder.eq.return_value = builder
    builder.limit.return_value = builder
    builder.execute.return_value = SimpleNamespace(data=[profile])
    return builder


if __name__ == "__main__":
    unittest.main()
