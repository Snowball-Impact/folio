import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import UUID

from folio_app.app import (
    _can_render_public_home_shell,
    _can_skip_cookie_manager_for_public_home,
    _ensure_visitor_id,
    _needs_visitor_id,
)
from folio_app.pages.project_detail import _record_project_view
from folio_app.services.project_mutations import increment_view_count
from folio_app.services.project_types import ViewCountResult


class CookieStub(dict):
    def __init__(self, **values) -> None:
        super().__init__(**values)
        self.save_count = 0

    def save(self) -> None:
        self.save_count += 1


class VisitorIdentityTests(unittest.TestCase):
    @patch("folio_app.app.st.session_state", new_callable=dict)
    def test_existing_valid_visitor_id_is_reused(self, session_state) -> None:
        visitor_id = "12345678-1234-5678-1234-567812345678"
        cookies = CookieStub(visitor_id=visitor_id)

        result = _ensure_visitor_id(cookies)

        self.assertEqual(result, visitor_id)
        self.assertEqual(session_state["folio_visitor_id"], visitor_id)
        self.assertEqual(cookies.save_count, 0)

    @patch("folio_app.app.st.session_state", new_callable=dict)
    def test_invalid_visitor_id_is_replaced_and_saved(self, session_state) -> None:
        cookies = CookieStub(visitor_id="broken")

        result = _ensure_visitor_id(cookies)

        self.assertEqual(str(UUID(result)), result)
        self.assertEqual(cookies["visitor_id"], result)
        self.assertEqual(session_state["folio_visitor_id"], result)
        self.assertEqual(cookies.save_count, 1)

    @patch("folio_app.app.st.query_params", {})
    def test_plain_home_does_not_need_visitor_id(self) -> None:
        self.assertFalse(_needs_visitor_id())

    @patch("folio_app.app.st.query_params", {"page": "Home", "project_id": "project-id"})
    def test_project_detail_needs_visitor_id(self) -> None:
        self.assertTrue(_needs_visitor_id())

    @patch("folio_app.app.st.query_params", {})
    def test_public_home_shell_can_render_before_cookies_are_ready(self) -> None:
        self.assertTrue(_can_render_public_home_shell())

    @patch("folio_app.app.st.query_params", {"page": "Home", "project_id": "project-id"})
    def test_detail_does_not_render_public_loading_shell(self) -> None:
        self.assertFalse(_can_render_public_home_shell())

    @patch("folio_app.app.get_current_user", return_value=None)
    @patch("folio_app.app.st.session_state", new_callable=dict)
    @patch("folio_app.app.st.query_params", {})
    def test_plain_logged_out_home_can_skip_cookie_manager(self, _session_state, _current_user) -> None:
        self.assertTrue(_can_skip_cookie_manager_for_public_home())

    @patch("folio_app.app.get_current_user", return_value=None)
    @patch("folio_app.app.st.session_state", new_callable=dict)
    @patch("folio_app.app.st.query_params", {"page": "Home", "project_id": "project-id"})
    def test_project_detail_cannot_skip_cookie_manager(self, _session_state, _current_user) -> None:
        self.assertFalse(_can_skip_cookie_manager_for_public_home())

    @patch("folio_app.app.get_current_user", return_value={"id": "user-id"})
    @patch("folio_app.app.st.session_state", new_callable=dict)
    @patch("folio_app.app.st.query_params", {})
    def test_logged_in_session_cannot_skip_cookie_manager(self, _session_state, _current_user) -> None:
        self.assertFalse(_can_skip_cookie_manager_for_public_home())

    @patch("folio_app.app.get_current_user", return_value=None)
    @patch("folio_app.app.st.session_state", new_callable=lambda: {"folio_clear_browser_auth": True})
    @patch("folio_app.app.st.query_params", {})
    def test_pending_auth_clear_cannot_skip_cookie_manager(self, _session_state, _current_user) -> None:
        self.assertFalse(_can_skip_cookie_manager_for_public_home())


class ViewCountServiceTests(unittest.TestCase):
    @patch("folio_app.services.project_mutations._fetch_public_projects.clear")
    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_counted_view_passes_anonymous_id_and_clears_cache(self, get_client, clear_cache) -> None:
        rpc = MagicMock()
        rpc.execute.return_value = SimpleNamespace(data=True)
        client = MagicMock()
        client.rpc.return_value = rpc
        get_client.return_value = client

        result = increment_view_count("project-id", "12345678-1234-5678-1234-567812345678")

        self.assertEqual(result, ViewCountResult(ok=True, counted=True))
        client.rpc.assert_called_once_with(
            "increment_project_view_count",
            {
                "project_id_input": "project-id",
                "anonymous_viewer_id_input": "12345678-1234-5678-1234-567812345678",
            },
        )
        clear_cache.assert_called_once()

    @patch("folio_app.services.project_mutations._fetch_public_projects.clear")
    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_duplicate_or_owner_view_is_successful_without_cache_clear(self, get_client, clear_cache) -> None:
        rpc = MagicMock()
        rpc.execute.return_value = SimpleNamespace(data=False)
        client = MagicMock()
        client.rpc.return_value = rpc
        get_client.return_value = client

        result = increment_view_count("project-id", "12345678-1234-5678-1234-567812345678")

        self.assertEqual(result, ViewCountResult(ok=True, counted=False))
        clear_cache.assert_not_called()

    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_rpc_failure_is_reported_separately(self, get_client) -> None:
        client = MagicMock()
        client.rpc.side_effect = RuntimeError("provider details")
        get_client.return_value = client

        result = increment_view_count("project-id", "12345678-1234-5678-1234-567812345678")

        self.assertEqual(result, ViewCountResult(ok=False, counted=False))


class DetailViewRetryTests(unittest.TestCase):
    @patch("folio_app.pages.project_detail.increment_view_count", return_value=ViewCountResult(False, False))
    @patch(
        "folio_app.pages.project_detail.st.session_state",
        new_callable=lambda: {"folio_visitor_id": "12345678-1234-5678-1234-567812345678"},
    )
    def test_rpc_failure_does_not_suppress_retry(self, session_state, increment) -> None:
        _record_project_view("project-id")

        self.assertNotIn("viewed_project-id", session_state)
        increment.assert_called_once()

    @patch("folio_app.pages.project_detail.increment_view_count", return_value=ViewCountResult(True, False))
    @patch(
        "folio_app.pages.project_detail.st.session_state",
        new_callable=lambda: {"folio_visitor_id": "12345678-1234-5678-1234-567812345678"},
    )
    def test_valid_non_counted_result_suppresses_same_session_retry(self, session_state, increment) -> None:
        _record_project_view("project-id")
        _record_project_view("project-id")

        self.assertTrue(session_state["viewed_project-id"])
        increment.assert_called_once()


class ViewCountSchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = (Path(__file__).parents[1] / "supabase" / "schema.sql").read_text(encoding="utf-8")

    def test_daily_deduplication_and_owner_exclusion_are_declared(self) -> None:
        self.assertIn("primary key (project_id, viewer_hash, viewed_on)", self.schema)
        self.assertIn("auth.uid() = project_author_id", self.schema)
        self.assertIn("timezone('Asia/Seoul', now())", self.schema)
        self.assertIn("on conflict do nothing", self.schema)

    def test_view_records_are_not_directly_available_to_clients(self) -> None:
        self.assertIn("revoke all on table public.project_views from anon, authenticated", self.schema)
        self.assertIn("grant execute on function public.increment_project_view_count", self.schema)

    def test_schema_does_not_reset_existing_view_counts(self) -> None:
        normalized = " ".join(self.schema.lower().split())
        self.assertNotIn("set view_count = 0", normalized)


if __name__ == "__main__":
    unittest.main()
