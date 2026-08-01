import unittest
from unittest.mock import patch

from folio_app.components.layout import _header_nav_items
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
from folio_app.pages.project_detail import _share_button_html, _track_share_open
from folio_app.services.projects import normalize_optional_url, normalize_power_bi_embed_url


class NavigationTests(unittest.TestCase):
    def test_header_nav_items_for_logged_out_users(self) -> None:
        self.assertEqual(
            _header_nav_items(False),
            [("Home", "홈 갤러리"), ("Login", "로그인")],
        )

    def test_header_nav_items_for_logged_in_users(self) -> None:
        self.assertEqual(
            _header_nav_items(True),
            [
                ("Home", "홈 갤러리"),
                ("Submit", "프로젝트 등록"),
                ("My Page", "마이 페이지"),
                ("__logout__", "로그아웃"),
            ],
        )

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


class ProjectShareLinkTests(unittest.TestCase):
    def test_share_button_copies_canonical_project_detail_url(self) -> None:
        markup = _share_button_html("project-123")

        self.assertIn('searchParams.set("page", "Home")', markup)
        self.assertIn('searchParams.set("project_id", projectId)', markup)
        self.assertIn('searchParams.set("utm_source", "folio")', markup)
        self.assertIn('searchParams.set("utm_medium", "share")', markup)
        self.assertIn('searchParams.set("utm_campaign", "project_share")', markup)
        self.assertIn('"project-123"', markup)
        self.assertIn("navigator.clipboard.writeText", markup)

    @patch("folio_app.pages.project_detail.track_event")
    @patch("folio_app.pages.project_detail.st.session_state", new_callable=dict)
    @patch(
        "folio_app.pages.project_detail.st.query_params",
        {"utm_medium": "share", "utm_campaign": "project_share"},
    )
    def test_share_open_event_is_tracked_once_per_session(self, session_state, track_event_mock) -> None:
        _track_share_open("project-123")
        _track_share_open("project-123")

        track_event_mock.assert_called_once_with(
            "project_share_open",
            {"item_id": "project-123", "source": "copied_link"},
        )
        self.assertTrue(session_state["tracked_share_open_project-123"])

    @patch("folio_app.pages.project_detail.track_event")
    @patch("folio_app.pages.project_detail.st.session_state", new_callable=dict)
    @patch("folio_app.pages.project_detail.st.query_params", {"utm_medium": "organic"})
    def test_share_open_event_requires_share_utm(self, _session_state, track_event_mock) -> None:
        _track_share_open("project-123")

        track_event_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
