import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.services.comments import (
    annotate_unread_comment_status,
    build_comment_tree,
    clear_comment_caches,
    count_comments_by_project,
    create_comment,
    delete_comment,
    latest_comment_at_by_project,
    get_unread_comment_project_ids,
    list_project_comments,
    mark_project_comments_read,
)


class CommentTreeTests(unittest.TestCase):
    def test_build_comment_tree_groups_replies_under_parent(self) -> None:
        rows = [
            {
                "id": "root",
                "project_id": "project-1",
                "author_id": "user-1",
                "parent_id": None,
                "body": "첫 댓글",
                "depth": 0,
                "created_at": "2026-08-02T00:00:00+00:00",
                "author": {"name": "홍길동"},
            },
            {
                "id": "reply-1",
                "project_id": "project-1",
                "author_id": "user-2",
                "parent_id": "root",
                "body": "대댓글",
                "depth": 1,
                "created_at": "2026-08-02T00:01:00+00:00",
                "author": {"name": "김철수"},
            },
        ]

        tree = build_comment_tree(rows)

        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["id"], "root")
        self.assertEqual([child["id"] for child in tree[0]["children"]], ["reply-1"])


class CommentServiceTests(unittest.TestCase):
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.comments.get_supabase_client")
    def test_create_comment_inserts_payload(self, get_client, _ensure_auth) -> None:
        builder = MagicMock()
        builder.insert.return_value = builder
        builder.select.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "new-comment", "body": "안녕"}])
        profile_builder = MagicMock()
        profile_builder.select.return_value = profile_builder
        profile_builder.in_.return_value = profile_builder
        profile_builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.side_effect = [builder, profile_builder]
        get_client.return_value = client

        result = create_comment("project-1", "user-1", "안녕")

        self.assertTrue(result.ok)
        self.assertEqual(result.comment["id"], "new-comment")
        builder.insert.assert_called_once_with(
            {
                "project_id": "project-1",
                "author_id": "user-1",
                "body": "안녕",
                "parent_id": None,
                "depth": 0,
            }
        )

    @patch("folio_app.services.auth.ensure_authenticated_session")
    @patch("folio_app.services.comments.get_supabase_client")
    def test_create_comment_validates_body_before_auth(self, get_client, ensure_auth) -> None:
        result = create_comment("project-1", "user-1", "가" * 1001)

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "댓글은 1,000자 이내로 입력하세요.")
        ensure_auth.assert_not_called()
        get_client.assert_not_called()

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.comments.get_supabase_client")
    def test_create_reply_requires_top_level_parent_in_same_project(self, get_client, _ensure_auth) -> None:
        parent_builder = MagicMock()
        parent_builder.select.return_value = parent_builder
        parent_builder.eq.return_value = parent_builder
        parent_builder.limit.return_value = parent_builder
        parent_builder.execute.return_value = SimpleNamespace(
            data=[{"id": "parent-1", "project_id": "project-1", "parent_id": None, "depth": 0}]
        )
        insert_builder = MagicMock()
        insert_builder.insert.return_value = insert_builder
        insert_builder.select.return_value = insert_builder
        insert_builder.execute.return_value = SimpleNamespace(data=[{"id": "reply-1", "body": "답글"}])
        profile_builder = MagicMock()
        profile_builder.select.return_value = profile_builder
        profile_builder.in_.return_value = profile_builder
        profile_builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.side_effect = [parent_builder, insert_builder, profile_builder]
        get_client.return_value = client

        result = create_comment("project-1", "user-1", " 답글 ", parent_id="parent-1")

        self.assertTrue(result.ok)
        insert_builder.insert.assert_called_once_with(
            {
                "project_id": "project-1",
                "author_id": "user-1",
                "body": "답글",
                "parent_id": "parent-1",
                "depth": 1,
            }
        )

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.comments.get_supabase_client")
    def test_create_reply_rejects_nested_parent(self, get_client, _ensure_auth) -> None:
        parent_builder = MagicMock()
        parent_builder.select.return_value = parent_builder
        parent_builder.eq.return_value = parent_builder
        parent_builder.limit.return_value = parent_builder
        parent_builder.execute.return_value = SimpleNamespace(
            data=[{"id": "reply-1", "project_id": "project-1", "parent_id": "root", "depth": 1}]
        )

        client = MagicMock()
        client.table.return_value = parent_builder
        get_client.return_value = client

        result = create_comment("project-1", "user-1", "중첩 답글", parent_id="reply-1")

        self.assertFalse(result.ok)
        parent_builder.insert.assert_not_called()

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.comments.get_supabase_client")
    def test_delete_comment_requires_author_match(self, get_client, _ensure_auth) -> None:
        builder = MagicMock()
        builder.delete.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "comment-1"}])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = delete_comment("comment-1", "user-1")

        self.assertTrue(result.ok)
        self.assertEqual(result.comment_id, "comment-1")

    @patch("folio_app.services.comments.get_supabase_client")
    def test_list_project_comments_returns_rows(self, get_client) -> None:
        builder = MagicMock()
        builder.select.return_value = builder
        builder.eq.return_value = builder
        builder.order.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "comment-1", "body": "hello"}])
        profile_builder = MagicMock()
        profile_builder.select.return_value = profile_builder
        profile_builder.in_.return_value = profile_builder
        profile_builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.side_effect = [builder, profile_builder]
        get_client.return_value = client

        result = list_project_comments("project-1")

        self.assertEqual(result[0]["id"], "comment-1")

    @patch("folio_app.services.comments.get_supabase_client")
    def test_count_comments_by_project_counts_rows(self, get_client) -> None:
        clear_comment_caches()
        builder = MagicMock()
        builder.select.return_value = builder
        builder.in_.return_value = builder
        builder.execute.return_value = SimpleNamespace(
            data=[
                {"project_id": "project-1"},
                {"project_id": "project-1"},
                {"project_id": "project-2"},
            ]
        )

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = count_comments_by_project(["project-1", "project-2"])

        self.assertEqual(result, {"project-1": 2, "project-2": 1})

    @patch("folio_app.services.comments.get_supabase_client")
    def test_latest_comment_at_by_project_uses_latest_row(self, get_client) -> None:
        clear_comment_caches()
        builder = MagicMock()
        builder.select.return_value = builder
        builder.in_.return_value = builder
        builder.execute.return_value = SimpleNamespace(
            data=[
                {"project_id": "project-1", "created_at": "2026-08-02T08:00:00+00:00"},
                {"project_id": "project-1", "created_at": "2026-08-02T09:00:00+00:00"},
                {"project_id": "project-2", "created_at": "2026-08-02T07:00:00+00:00"},
            ]
        )

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = latest_comment_at_by_project(["project-1", "project-2"])

        self.assertEqual(result["project-1"], "2026-08-02T09:00:00+00:00")
        self.assertEqual(result["project-2"], "2026-08-02T07:00:00+00:00")

    @patch("folio_app.services.comments.get_supabase_client")
    def test_get_unread_comment_project_ids_ignores_own_comments_and_read_comments(self, get_client) -> None:
        comments_builder = MagicMock()
        comments_builder.select.return_value = comments_builder
        comments_builder.in_.return_value = comments_builder
        comments_builder.neq.return_value = comments_builder
        comments_builder.execute.return_value = SimpleNamespace(
            data=[
                {"project_id": "project-1", "author_id": "other", "created_at": "2026-08-02T09:00:00+00:00"},
                {"project_id": "project-2", "author_id": "other", "created_at": "2026-08-02T08:00:00+00:00"},
            ]
        )
        reads_builder = MagicMock()
        reads_builder.select.return_value = reads_builder
        reads_builder.eq.return_value = reads_builder
        reads_builder.in_.return_value = reads_builder
        reads_builder.execute.return_value = SimpleNamespace(
            data=[
                {"project_id": "project-1", "last_read_at": "2026-08-02T08:30:00+00:00"},
                {"project_id": "project-2", "last_read_at": "2026-08-02T08:30:00+00:00"},
            ]
        )

        client = MagicMock()
        client.table.side_effect = [comments_builder, reads_builder]
        get_client.return_value = client

        result = get_unread_comment_project_ids(
            [{"id": "project-1"}, {"id": "project-2"}],
            "author-1",
        )

        self.assertEqual(result, {"project-1"})
        comments_builder.neq.assert_called_once_with("author_id", "author-1")

    @patch("folio_app.services.comments.get_supabase_client")
    def test_annotate_unread_comment_status_sets_project_flag(self, get_client) -> None:
        comments_builder = MagicMock()
        comments_builder.select.return_value = comments_builder
        comments_builder.in_.return_value = comments_builder
        comments_builder.neq.return_value = comments_builder
        comments_builder.execute.return_value = SimpleNamespace(
            data=[{"project_id": "project-1", "author_id": "other", "created_at": "2026-08-02T09:00:00+00:00"}]
        )
        reads_builder = MagicMock()
        reads_builder.select.return_value = reads_builder
        reads_builder.eq.return_value = reads_builder
        reads_builder.in_.return_value = reads_builder
        reads_builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.side_effect = [comments_builder, reads_builder]
        get_client.return_value = client

        projects = [{"id": "project-1"}, {"id": "project-2"}]

        annotate_unread_comment_status(projects, "author-1")

        self.assertTrue(projects[0]["has_unread_comments"])
        self.assertFalse(projects[1]["has_unread_comments"])

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.comments.get_supabase_client")
    def test_mark_project_comments_read_upserts_timestamp(self, get_client, _ensure_auth) -> None:
        builder = MagicMock()
        builder.upsert.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[])

        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = mark_project_comments_read("project-1", "author-1")

        self.assertTrue(result)
        client.table.assert_called_once_with("project_comment_reads")
        upsert_payload = builder.upsert.call_args.args[0]
        self.assertEqual(upsert_payload["project_id"], "project-1")
        self.assertEqual(upsert_payload["user_id"], "author-1")
        self.assertIn("last_read_at", upsert_payload)
        self.assertEqual(builder.upsert.call_args.kwargs["on_conflict"], "project_id,user_id")


class CommentSchemaContractTests(unittest.TestCase):
    def test_schema_declares_comment_permissions_and_thread_validation(self) -> None:
        schema_sql = Path("supabase/schema.sql").read_text(encoding="utf-8")

        self.assertIn("create table if not exists public.comments", schema_sql)
        self.assertIn("create table if not exists public.project_comment_reads", schema_sql)
        self.assertIn("grant select on public.comments to anon", schema_sql)
        self.assertIn("grant select, insert, delete on public.comments to authenticated", schema_sql)
        self.assertIn("grant select, insert, update on public.project_comment_reads to authenticated", schema_sql)
        self.assertIn("create or replace function public.validate_comment_thread()", schema_sql)
        self.assertIn("create policy \"Visible project comments are readable\"", schema_sql)
        self.assertIn("create policy \"Project authors can read own comment read state\"", schema_sql)
        self.assertIn("projects.is_public = true or auth.uid() = projects.author_id", schema_sql)
        self.assertIn("with check (\n    auth.uid() = author_id", schema_sql)
        self.assertIn("using (auth.uid() = author_id)", schema_sql)


if __name__ == "__main__":
    unittest.main()
