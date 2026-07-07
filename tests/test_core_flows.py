import unittest
from unittest.mock import patch

from folio_app.components.project_form import parse_project_body
from folio_app.navigation import navigate
from folio_app.pages.auth import (
    SignupEmailCheckError,
    _email_already_registered,
    _is_existing_account_message,
    _should_show_resend_confirmation,
    _should_show_signup_login_link,
    _signup_missing_required_fields,
)
from folio_app.services.projects import normalize_optional_url, normalize_power_bi_embed_url


class NavigationTests(unittest.TestCase):
    @patch("folio_app.navigation.st.rerun", side_effect=RuntimeError("rerun"))
    @patch("folio_app.navigation.st.query_params", new_callable=dict)
    def test_navigation_replaces_query_and_omits_empty_values(self, query_params, _rerun) -> None:
        query_params["old"] = "value"
        with self.assertRaisesRegex(RuntimeError, "rerun"):
            navigate("Home", project_id="project-1", tag=None, q="")
        self.assertEqual(query_params, {"page": "Home", "project_id": "project-1"})

    @patch("folio_app.navigation.st.rerun", side_effect=RuntimeError("rerun"))
    @patch("folio_app.navigation.st.query_params", new_callable=dict)
    def test_unknown_page_falls_back_to_home(self, query_params, _rerun) -> None:
        with self.assertRaisesRegex(RuntimeError, "rerun"):
            navigate("Unknown")
        self.assertEqual(query_params, {"page": "Home"})


class SignupValidationTests(unittest.TestCase):
    def test_organization_is_required_for_signup(self) -> None:
        self.assertEqual(
            _signup_missing_required_fields(
                email="user@example.com",
                password="password123",
                password_confirm="password123",
                name="사용자",
                organization="",
            ),
            ["소속"],
        )

    def test_signup_required_fields_pass_when_all_values_are_present(self) -> None:
        self.assertEqual(
            _signup_missing_required_fields(
                email="user@example.com",
                password="password123",
                password_confirm="password123",
                name="사용자",
                organization="개인",
            ),
            [],
        )

    @patch("folio_app.pages.auth._cached_profile_exists_for_email", side_effect=RuntimeError("network"))
    def test_email_registration_check_failure_blocks_signup(self, _profile_exists) -> None:
        with self.assertRaisesRegex(SignupEmailCheckError, "가입 여부"):
            _email_already_registered("user@example.com")

    def test_resend_confirmation_is_hidden_until_needed(self) -> None:
        with patch("folio_app.pages.auth.st.session_state", {}):
            self.assertFalse(_should_show_resend_confirmation(email_registered=False))

    def test_resend_confirmation_is_visible_after_signup_success_or_existing_email(self) -> None:
        with patch("folio_app.pages.auth.st.session_state", {"signup_confirmation_email": "user@example.com"}):
            self.assertTrue(_should_show_resend_confirmation(email_registered=False))
        with patch("folio_app.pages.auth.st.session_state", {}):
            self.assertTrue(_should_show_resend_confirmation(email_registered=True))

    def test_signup_login_link_is_visible_only_for_existing_account_context(self) -> None:
        with patch("folio_app.pages.auth.st.session_state", {}):
            self.assertFalse(_should_show_signup_login_link(email_registered=False, email="user@example.com"))
            self.assertTrue(_should_show_signup_login_link(email_registered=True, email="user@example.com"))

        with patch("folio_app.pages.auth.st.session_state", {"signup_existing_email": "user@example.com"}):
            self.assertTrue(_should_show_signup_login_link(email_registered=False, email="user@example.com"))
            self.assertFalse(_should_show_signup_login_link(email_registered=False, email="other@example.com"))

    def test_existing_account_message_is_detected_for_signup_cta(self) -> None:
        self.assertTrue(_is_existing_account_message("이미 가입된 이메일입니다. Login 메뉴에서 로그인하세요."))
        self.assertFalse(_is_existing_account_message("회원가입 요청을 처리했습니다. 메일함을 확인하세요."))


class ProjectBodyParsingTests(unittest.TestCase):
    def test_html_headings_with_editor_attributes_are_split(self) -> None:
        body = (
            '<h2 class="ql-align-center">문제 정의</h2><p>문제</p>'
            '<h2 data-section="dataset">사용 데이터</h2><p>데이터</p>'
            '<h2>핵심 인사이트</h2><p>인사이트</p>'
        )
        sections = parse_project_body(body)
        self.assertEqual(sections["problem"], "<p>문제</p>")
        self.assertEqual(sections["dataset"], "<p>데이터</p>")
        self.assertEqual(sections["insights"], "<p>인사이트</p>")

    def test_unstructured_html_falls_back_to_problem(self) -> None:
        sections = parse_project_body("<p>자유 형식 본문</p>")
        self.assertEqual(sections["problem"], "<p>자유 형식 본문</p>")


class URLNormalizationTests(unittest.TestCase):
    def test_power_bi_iframe_extracts_https_source(self) -> None:
        iframe = '<iframe title="report" src="https://app.powerbi.com/view?r=test"></iframe>'
        self.assertEqual(
            normalize_power_bi_embed_url(iframe),
            "https://app.powerbi.com/view?r=test",
        )

    def test_non_http_url_is_rejected(self) -> None:
        self.assertIsNone(normalize_optional_url("javascript:alert(1)"))


if __name__ == "__main__":
    unittest.main()
