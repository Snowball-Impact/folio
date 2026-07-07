import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from folio_app.app import _restore_auth_from_cookies
from folio_app.services.auth import AuthResult, resend_signup_confirmation, sign_up
from folio_app.services.profiles import ensure_profile, get_onboarding_status
from folio_app.services.supabase_client import clear_supabase_client, get_supabase_client


class CookieStub(dict):
    def save(self) -> None:
        self.saved = True


class AuthRestoreUXTests(unittest.TestCase):
    @patch("folio_app.app.restore_session", return_value=AuthResult(False, "로그인 복원 실패"))
    @patch("folio_app.app.get_current_user", return_value=None)
    @patch("folio_app.app.st")
    def test_public_home_silently_clears_expired_cookies(self, streamlit, _current_user, _restore) -> None:
        streamlit.session_state = {}
        streamlit.query_params = {"page": "Home"}
        cookies = CookieStub(access_token="expired", refresh_token="expired")

        _restore_auth_from_cookies(cookies)

        self.assertNotIn("access_token", cookies)
        self.assertNotIn("refresh_token", cookies)
        streamlit.warning.assert_not_called()
        streamlit.rerun.assert_not_called()

    @patch("folio_app.app.restore_session", return_value=AuthResult(False, "로그인 복원 실패"))
    @patch("folio_app.app.get_current_user", return_value=None)
    @patch("folio_app.app.st")
    def test_protected_page_redirects_to_login_after_restore_failure(self, streamlit, _current_user, _restore) -> None:
        streamlit.session_state = {}
        streamlit.query_params = {"page": "My Portfolio"}
        cookies = CookieStub(access_token="expired", refresh_token="expired")

        _restore_auth_from_cookies(cookies)

        self.assertEqual(streamlit.query_params, {"page": "Login"})
        self.assertEqual(streamlit.session_state["login_notice"], "로그인 복원 실패")
        streamlit.rerun.assert_called_once()


class SignupStabilityTests(unittest.TestCase):
    @patch("folio_app.services.auth.get_settings")
    @patch("folio_app.services.auth.profile_exists_for_email", return_value=True)
    @patch("folio_app.services.auth.get_supabase_client")
    def test_existing_profile_email_does_not_call_auth_signup(self, get_client, _profile_exists, get_settings) -> None:
        get_settings.return_value = SimpleNamespace(login_redirect_url="http://localhost:8501")
        client = MagicMock()
        get_client.return_value = client

        result = sign_up("user@example.com", "password123", "사용자", "개인")

        self.assertFalse(result.ok)
        self.assertIn("이미 가입된 이메일", result.message)
        client.auth.sign_up.assert_not_called()

    @patch("folio_app.services.auth.get_settings")
    @patch("folio_app.services.auth.profile_exists_for_email", return_value=False)
    @patch("folio_app.services.auth.get_supabase_client")
    def test_signup_without_session_uses_request_processed_copy(self, get_client, _profile_exists, get_settings) -> None:
        get_settings.return_value = SimpleNamespace(login_redirect_url="http://localhost:8501")
        client = MagicMock()
        client.auth.sign_up.return_value = SimpleNamespace(user=SimpleNamespace(id="user-id"), session=None)
        get_client.return_value = client

        result = sign_up("user@example.com", "password123", "사용자", "개인")

        self.assertTrue(result.ok)
        self.assertIn("회원가입 요청을 처리했습니다", result.message)

    @patch("folio_app.services.auth.get_settings")
    @patch("folio_app.services.auth.profile_exists_for_email", return_value=False)
    @patch("folio_app.services.auth.get_supabase_client")
    def test_signup_obfuscated_existing_auth_user_is_rejected(self, get_client, _profile_exists, get_settings) -> None:
        get_settings.return_value = SimpleNamespace(login_redirect_url="http://localhost:8501")
        client = MagicMock()
        client.auth.sign_up.return_value = SimpleNamespace(
            user=SimpleNamespace(id="existing-user-id", identities=[]),
            session=None,
        )
        get_client.return_value = client

        result = sign_up("user@example.com", "password123", "사용자", "개인")

        self.assertFalse(result.ok)
        self.assertIn("이미 가입된 이메일", result.message)

    @patch("folio_app.services.auth.get_settings")
    @patch("folio_app.services.auth.get_supabase_client")
    def test_resend_confirmation_uses_request_processed_copy(self, get_client, get_settings) -> None:
        get_settings.return_value = SimpleNamespace(login_redirect_url="http://localhost:8501")
        client = MagicMock()
        get_client.return_value = client

        result = resend_signup_confirmation("user@example.com")

        self.assertTrue(result.ok)
        self.assertIn("재발송 요청을 처리했습니다", result.message)


class SupabaseClientIsolationTests(unittest.TestCase):
    @patch("folio_app.services.supabase_client.st.session_state", new_callable=dict)
    @patch("folio_app.services.supabase_client.create_client")
    @patch("folio_app.services.supabase_client.get_settings")
    def test_client_is_reused_only_inside_current_session(self, get_settings, create_client, session_state) -> None:
        get_settings.return_value = SimpleNamespace(
            is_supabase_configured=True,
            supabase_url="https://example.supabase.co",
            supabase_key="anon-key",
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
