import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.services.profiles import ensure_profile, get_onboarding_status
from folio_app.services.supabase_client import clear_supabase_client, get_supabase_client


class SupabaseClientIsolationTests(unittest.TestCase):
    @patch("folio_app.services.supabase_client.st.session_state", new_callable=dict)
    @patch("folio_app.services.supabase_client.create_client")
    @patch("folio_app.services.supabase_client.get_settings")
    def test_client_is_reused_only_inside_current_session(self, get_settings, create_client, session_state) -> None:
        get_settings.return_value = SimpleNamespace(
            is_supabase_configured=True,
            supabase_url="https://example.supabase.co",
            supabase_anon_key="anon-key",
        )
        create_client.return_value = object()

        first = get_supabase_client()
        second = get_supabase_client()
        self.assertIs(first, second)
        create_client.assert_called_once()

        clear_supabase_client()
        get_supabase_client()
        self.assertEqual(create_client.call_count, 2)


class OnboardingStabilityTests(unittest.TestCase):
    @patch("folio_app.services.profiles.get_profile", side_effect=RuntimeError("network"))
    def test_status_failure_does_not_mark_onboarding_complete(self, _get_profile) -> None:
        status = get_onboarding_status("user-id")
        self.assertTrue(status.required)
        self.assertFalse(status.is_complete)
        self.assertIsNotNone(status.error_message)


class ProfileRepairTests(unittest.TestCase):
    @patch("folio_app.services.profiles.get_supabase_client")
    def test_existing_profile_is_not_overwritten(self, get_client) -> None:
        existing_profile = {
            "id": "user-id",
            "email": "user@example.com",
            "name": "사용자가 수정한 이름",
            "organization": "수정한 소속",
        }
        builder = MagicMock()
        builder.select.return_value = builder
        builder.eq.return_value = builder
        builder.limit.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=[existing_profile])
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = ensure_profile("user-id", "user@example.com", "가입 당시 이름", "예전 소속")

        self.assertEqual(result, existing_profile)
        builder.insert.assert_not_called()


if __name__ == "__main__":
    unittest.main()
