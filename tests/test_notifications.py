import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.services.notifications import (
    count_unread_notifications,
    create_project_comment_notification,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    mark_project_comment_notifications_read,
)


class NotificationServiceTests(unittest.TestCase):
    @patch("folio_app.services.notifications._send_project_comment_email")
    @patch("folio_app.services.notifications.get_supabase_client")
    @patch("folio_app.services.notifications.get_supabase_service_role_client")
    def test_create_project_comment_notification_inserts_for_project_author(
        self,
        get_service_client,
        get_client,
        send_email,
    ) -> None:
        project_builder = MagicMock()
        project_builder.select.return_value = project_builder
        project_builder.eq.return_value = project_builder
        project_builder.limit.return_value = project_builder
        project_builder.execute.return_value = SimpleNamespace(
            data=[{"id": "project-1", "title": "분석 프로젝트", "author_id": "author-1"}]
        )
        notification_builder = MagicMock()
        notification_builder.insert.return_value = notification_builder
        notification_builder.execute.return_value = SimpleNamespace(data=[{"id": "notice-1"}])

        client = MagicMock()
        client.table.side_effect = [project_builder, notification_builder]
        get_service_client.return_value = client
        get_client.return_value = None

        result = create_project_comment_notification(
            "project-1",
            {"id": "comment-1", "body": "좋아요"},
            "commenter-1",
        )

        self.assertTrue(result.ok)
        send_email.assert_called_once()
        notification_builder.insert.assert_called_once_with(
            {
                "user_id": "author-1",
                "actor_id": "commenter-1",
                "project_id": "project-1",
                "comment_id": "comment-1",
                "type": "project_comment",
                "title": "분석 프로젝트에 새 댓글이 남겨졌습니다.",
                "body": "좋아요",
            }
        )

    @patch("folio_app.services.notifications.get_supabase_client")
    @patch("folio_app.services.notifications.get_supabase_service_role_client")
    def test_create_project_comment_notification_skips_self_comment(self, get_service_client, get_client) -> None:
        project_builder = MagicMock()
        project_builder.select.return_value = project_builder
        project_builder.eq.return_value = project_builder
        project_builder.limit.return_value = project_builder
        project_builder.execute.return_value = SimpleNamespace(
            data=[{"id": "project-1", "title": "분석 프로젝트", "author_id": "author-1"}]
        )

        client = MagicMock()
        client.table.return_value = project_builder
        get_service_client.return_value = client
        get_client.return_value = None

        result = create_project_comment_notification(
            "project-1",
            {"id": "comment-1", "body": "내 댓글"},
            "author-1",
        )

        self.assertTrue(result.ok)
        project_builder.insert.assert_not_called()

    @patch("folio_app.services.notifications._send_project_comment_email")
    @patch("folio_app.services.notifications.get_supabase_client")
    @patch("folio_app.services.notifications.get_supabase_service_role_client")
    def test_create_project_comment_notification_falls_back_to_user_client(
        self,
        get_service_client,
        get_client,
        send_email,
    ) -> None:
        project_builder = MagicMock()
        project_builder.select.return_value = project_builder
        project_builder.eq.return_value = project_builder
        project_builder.limit.return_value = project_builder
        project_builder.execute.return_value = SimpleNamespace(
            data=[{"id": "project-1", "title": "분석 프로젝트", "author_id": "author-1"}]
        )
        notification_builder = MagicMock()
        notification_builder.insert.return_value = notification_builder
        notification_builder.execute.return_value = SimpleNamespace(data=[{"id": "notice-1"}])

        client = MagicMock()
        client.table.side_effect = [project_builder, notification_builder]
        get_service_client.return_value = None
        get_client.return_value = client

        result = create_project_comment_notification(
            "project-1",
            {"id": "comment-1", "body": "좋아요"},
            "commenter-1",
        )

        self.assertTrue(result.ok)
        send_email.assert_called_once()

    @patch("folio_app.services.notifications._send_project_comment_email")
    @patch("folio_app.services.notifications.get_supabase_client")
    @patch("folio_app.services.notifications.get_supabase_service_role_client")
    def test_create_project_comment_notification_treats_duplicate_as_success(
        self,
        get_service_client,
        get_client,
        send_email,
    ) -> None:
        project_builder = MagicMock()
        project_builder.select.return_value = project_builder
        project_builder.eq.return_value = project_builder
        project_builder.limit.return_value = project_builder
        project_builder.execute.return_value = SimpleNamespace(
            data=[{"id": "project-1", "title": "분석 프로젝트", "author_id": "author-1"}]
        )
        notification_builder = MagicMock()
        notification_builder.insert.return_value = notification_builder
        notification_builder.execute.side_effect = RuntimeError("duplicate key value violates unique constraint 23505")

        client = MagicMock()
        client.table.side_effect = [project_builder, notification_builder]
        get_service_client.return_value = client
        get_client.return_value = None

        result = create_project_comment_notification(
            "project-1",
            {"id": "comment-1", "body": "좋아요"},
            "commenter-1",
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.message, "이미 생성된 알림입니다.")
        send_email.assert_not_called()

    @patch("folio_app.services.notifications.get_supabase_client")
    def test_list_notifications_orders_recent_first(self, get_client) -> None:
        builder = MagicMock()
        builder.select.return_value = builder
        builder.eq.return_value = builder
        builder.order.return_value = builder
        builder.limit.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "notice-1"}])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = list_notifications("user-1")

        self.assertEqual(result, [{"id": "notice-1"}])
        builder.order.assert_called_once_with("created_at", desc=True)
        builder.limit.assert_called_once_with(20)

    @patch("folio_app.services.notifications.get_supabase_client")
    def test_count_unread_notifications_counts_rows(self, get_client) -> None:
        from folio_app.services.notifications import clear_notification_caches

        clear_notification_caches()
        builder = MagicMock()
        builder.select.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "notice-1"}, {"id": "notice-2"}])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        self.assertEqual(count_unread_notifications("user-1"), 2)

    @patch("folio_app.services.notifications.get_supabase_client")
    def test_mark_notification_read_updates_own_row(self, get_client) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "notice-1"}])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        self.assertTrue(mark_notification_read("notice-1", "user-1"))
        self.assertEqual(builder.eq.call_args_list[0].args, ("id", "notice-1"))
        self.assertEqual(builder.eq.call_args_list[1].args, ("user_id", "user-1"))

    @patch("folio_app.services.notifications.get_supabase_client")
    def test_mark_all_notifications_read_updates_unread_rows(self, get_client) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        self.assertTrue(mark_all_notifications_read("user-1"))
        self.assertEqual(builder.eq.call_args_list[0].args, ("user_id", "user-1"))
        self.assertEqual(builder.eq.call_args_list[1].args, ("is_read", False))

    @patch("folio_app.services.notifications.get_supabase_client")
    def test_mark_project_comment_notifications_read_scopes_to_project_comment(self, get_client) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        self.assertTrue(mark_project_comment_notifications_read("project-1", "user-1"))
        self.assertEqual(builder.eq.call_args_list[0].args, ("user_id", "user-1"))
        self.assertEqual(builder.eq.call_args_list[1].args, ("project_id", "project-1"))
        self.assertEqual(builder.eq.call_args_list[2].args, ("type", "project_comment"))
        self.assertEqual(builder.eq.call_args_list[3].args, ("is_read", False))


class NotificationSchemaContractTests(unittest.TestCase):
    def test_schema_declares_notification_table_and_policies(self) -> None:
        schema_sql = Path("supabase/schema.sql").read_text(encoding="utf-8")

        self.assertIn("create table if not exists public.notifications", schema_sql)
        self.assertIn("grant select, insert, update on public.notifications to authenticated", schema_sql)
        self.assertIn("create policy \"Users can read own notifications\"", schema_sql)
        self.assertIn("create policy \"Users can update own notifications\"", schema_sql)
        self.assertIn("create policy \"Comment authors can create project comment notifications\"", schema_sql)
        self.assertIn("create unique index if not exists notifications_project_comment_unique_idx", schema_sql)
        self.assertIn("comments.author_id = auth.uid()", schema_sql)


if __name__ == "__main__":
    unittest.main()
