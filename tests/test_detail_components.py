import unittest

from folio_app.components.dashboard import embedded_dashboard_html
from folio_app.components.project_detail_content import (
    project_report_html,
    project_report_sections,
    project_visual_context,
)
from folio_app.components.share import project_action_group_html, project_share_button_html
from folio_app.pages.project_detail import _detail_hero_card_html


class DashboardComponentTests(unittest.TestCase):
    def test_dashboard_embed_escapes_url(self) -> None:
        rendered = embedded_dashboard_html('https://example.com/report?title="x"&q=<tag>')

        self.assertIn("Embedded dashboard", rendered)
        self.assertIn("https://example.com/report?title=&quot;x&quot;&amp;q=&lt;tag&gt;", rendered)
        self.assertNotIn('src="https://example.com/report?title="x"&q=<tag>"', rendered)


class ShareComponentTests(unittest.TestCase):
    def test_share_button_contains_canonical_tracking_params(self) -> None:
        rendered = project_share_button_html("project-123")

        self.assertIn('searchParams.set("page", "Home")', rendered)
        self.assertIn('searchParams.set("project_id", projectId)', rendered)
        self.assertIn('searchParams.set("utm_source", "folio")', rendered)
        self.assertIn('searchParams.set("utm_medium", "share")', rendered)
        self.assertIn('searchParams.set("utm_campaign", "project_share")', rendered)
        self.assertIn('"project-123"', rendered)
        self.assertIn("navigator.clipboard.writeText", rendered)

    def test_action_group_keeps_status_chips_with_share_button(self) -> None:
        rendered = project_action_group_html("project-123", view_count=102, is_public=True, comment_count=7)

        self.assertIn("folio-detail-action-group", rendered)
        self.assertIn('aria-label="조회수 102"', rendered)
        self.assertIn('aria-label="댓글 7"', rendered)
        self.assertIn(">공개</span>", rendered)
        self.assertIn("folio-detail-share-button", rendered)
        self.assertIn("data-folio-share-button", rendered)


class DetailHelperTests(unittest.TestCase):
    def test_detail_hero_uses_static_home_card_markup(self) -> None:
        rendered = _detail_hero_card_html(
            {
                "id": "project-detail-card",
                "title": "상세 히어로 카드",
                "one_liner": "홈 갤러리와 같은 카드",
                "tags": ["PowerBI", "Reference"],
            }
        )

        self.assertIn("folio-home-card", rendered)
        self.assertIn("상세 히어로 카드", rendered)
        self.assertIn("홈 갤러리와 같은 카드", rendered)
        self.assertIn("#PowerBI", rendered)
        self.assertNotIn("folio-home-card-preview", rendered)

    def test_visual_context_detects_any_resource(self) -> None:
        context = project_visual_context(
            {
                "power_bi_url": "",
                "report_url": "https://example.com/report",
                "github_url": "",
            }
        )

        self.assertIsNone(context["power_bi_url"])
        self.assertTrue(context["has_report"])
        self.assertFalse(context["has_github"])
        self.assertTrue(context["has_visual_panel"])

    def test_report_sections_omit_empty_values(self) -> None:
        sections = project_report_sections(
            {
                "problem": "<p>문제</p>",
                "dataset": "",
                "process": None,
                "insights": "<p>인사이트</p>",
            }
        )

        self.assertEqual(sections, ["<p>문제</p>", "<p>인사이트</p>"])

    def test_report_html_sanitizes_script_content(self) -> None:
        rendered = project_report_html(["<p>안전한 내용</p><script>alert(1)</script>"])

        self.assertIn("프로젝트 리포트", rendered)
        self.assertIn("안전한 내용", rendered)
        self.assertNotIn("<script>", rendered)


if __name__ == "__main__":
    unittest.main()
