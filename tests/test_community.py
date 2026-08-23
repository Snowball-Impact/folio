import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.services.community import create_community_post, list_community_posts, update_community_post
from folio_app.services.comments import create_community_comment, list_community_comments


class CommunityServiceTests(unittest.TestCase):
    @patch("folio_app.services.community.is_admin_user", return_value=False)
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.community.get_supabase_client")
    def test_create_community_post_rejects_notice_for_regular_user(self, get_client, _ensure_auth, _is_admin) -> None:
        result = create_community_post("user-1", "notice", "공지", "내용")

        self.assertFalse(result.ok)
        self.assertEqual(result.message, "선택할 수 없는 카테고리입니다.")
        get_client.assert_not_called()

    @patch("folio_app.services.community.is_admin_user", return_value=False)
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.community.get_supabase_client")
    def test_create_community_post_inserts_regular_category(self, get_client, _ensure_auth, _is_admin) -> None:
        builder = MagicMock()
        builder.insert.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "post-1"}])
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = create_community_post("user-1", "question", "  질문입니다  ", " 내용 ")

        self.assertTrue(result.ok)
        self.assertEqual(result.post_id, "post-1")
        builder.insert.assert_called_once_with(
            {
                "user_id": "user-1",
                "category": "question",
                "title": "질문입니다",
                "content": "내용",
                "is_pinned": False,
            }
        )

    @patch("folio_app.services.community.is_admin_user", return_value=False)
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.community.get_supabase_client")
    def test_update_community_post_preserves_author(self, get_client, _ensure_auth, _is_admin) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "post-1"}])
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = update_community_post("post-1", "user-1", "question", "질문", "내용")

        self.assertTrue(result.ok)
        update_payload = builder.update.call_args.args[0]
        self.assertNotIn("user_id", update_payload)
        builder.eq.assert_any_call("id", "post-1")
        builder.eq.assert_any_call("user_id", "user-1")

    @patch("folio_app.services.community._attach_post_related_data", side_effect=lambda rows: rows)
    @patch("folio_app.services.community.get_supabase_client")
    def test_list_community_posts_filters_category_and_orders_pinned_first(self, get_client, _attach) -> None:
        builder = MagicMock()
        builder.select.return_value = builder
        builder.is_.return_value = builder
        builder.eq.return_value = builder
        builder.order.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[{"id": "post-1"}])
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = list_community_posts("question")

        self.assertEqual(result, [{"id": "post-1"}])
        builder.eq.assert_any_call("is_hidden", False)
        builder.eq.assert_any_call("category", "question")
        self.assertEqual(builder.order.call_args_list[0].args, ("is_pinned",))
        self.assertEqual(builder.order.call_args_list[0].kwargs, {"desc": True})
        self.assertEqual(builder.order.call_args_list[1].args, ("created_at",))
        self.assertEqual(builder.order.call_args_list[1].kwargs, {"desc": True})


class CommunityCommentTests(unittest.TestCase):
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=SimpleNamespace(ok=True))
    @patch("folio_app.services.comment_mutations.get_supabase_client")
    @patch("folio_app.services.comment_queries.get_supabase_client")
    def test_create_community_comment_inserts_community_target(self, query_get_client, mutation_get_client, _ensure_auth) -> None:
        insert_builder = MagicMock()
        insert_builder.insert.return_value = insert_builder
        insert_builder.select.return_value = insert_builder
        insert_builder.execute.return_value = SimpleNamespace(data=[{"id": "comment-1", "body": "안녕"}])
        profile_builder = MagicMock()
        profile_builder.select.return_value = profile_builder
        profile_builder.in_.return_value = profile_builder
        profile_builder.execute.return_value = SimpleNamespace(data=[])

        mutation_client = MagicMock()
        mutation_client.table.return_value = insert_builder
        mutation_get_client.return_value = mutation_client
        query_client = MagicMock()
        query_client.table.return_value = profile_builder
        query_get_client.return_value = query_client

        result = create_community_comment("post-1", "user-1", " 안녕 ")

        self.assertTrue(result.ok)
        insert_builder.insert.assert_called_once_with(
            {
                "community_post_id": "post-1",
                "author_id": "user-1",
                "body": "안녕",
                "parent_id": None,
                "depth": 0,
            }
        )

    @patch("folio_app.services.comment_queries.get_supabase_client")
    def test_list_community_comments_filters_by_post(self, get_client) -> None:
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

        result = list_community_comments("post-1")

        self.assertEqual(result[0]["id"], "comment-1")
        builder.eq.assert_called_once_with("community_post_id", "post-1")


class CommunitySchemaContractTests(unittest.TestCase):
    def test_schema_declares_community_posts_and_comment_extension(self) -> None:
        schema_sql = Path("supabase/schema.sql").read_text(encoding="utf-8")

        self.assertIn("create table if not exists public.community_posts", schema_sql)
        self.assertIn("create table if not exists public.community_post_views", schema_sql)
        self.assertIn("community_post_id uuid references public.community_posts", schema_sql)
        self.assertIn("comments_single_target_check", schema_sql)
        self.assertIn("create policy \"Visible community posts are readable\"", schema_sql)
        self.assertIn("create policy \"Users can create own community posts\"", schema_sql)
        self.assertIn("category <> 'notice'", schema_sql)
        self.assertIn("create or replace function public.increment_community_post_view_count", schema_sql)
        self.assertIn("community_posts.id = comments.community_post_id", schema_sql)


if __name__ == "__main__":
    unittest.main()
