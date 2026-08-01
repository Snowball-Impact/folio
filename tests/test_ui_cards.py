import unittest

from folio_app.components.ui import _cover_variant, render_project_card_html


class AutomaticProjectCoverTests(unittest.TestCase):
    def test_same_project_always_uses_same_cover_variant(self) -> None:
        project = {"id": "project-123", "title": "분석 프로젝트"}
        self.assertEqual(_cover_variant(project), _cover_variant(dict(project)))

    def test_card_contains_four_tags_and_more_count_tooltip(self) -> None:
        project = {
            "id": "project-123",
            "title": "고객 <이탈> 분석",
            "tags": ["Python", "고객&분석", "세 번째", "네 번째", "다섯 번째"],
            "one_liner": "프로젝트 설명",
        }

        rendered = render_project_card_html(project)

        self.assertIn("고객 &lt;이탈&gt; 분석", rendered)
        self.assertIn("#Python", rendered)
        self.assertIn("#고객&amp;분석", rendered)
        self.assertIn("#세 번째", rendered)
        self.assertIn("#네 번째", rendered)
        self.assertIn("+1", rendered)
        self.assertIn('title="Python, 고객&amp;분석, 세 번째, 네 번째, 다섯 번째"', rendered)
        self.assertNotIn("#다섯 번째", rendered)
        self.assertEqual(rendered.count("고객 &lt;이탈&gt; 분석"), 1)
        self.assertIn('aria-label="조회수 0"', rendered)
        self.assertIn('aria-label="좋아요 0"', rendered)
        self.assertNotIn("조회 0 · 좋아요 0", rendered)

    def test_card_keeps_summary_and_empty_tag_zones_separate(self) -> None:
        project = {
            "id": "project-no-tags",
            "title": "태그 없는 프로젝트",
            "one_liner": "요약만 있는 프로젝트",
            "tags": [],
        }

        rendered = render_project_card_html(project)

        self.assertIn("folio-home-card-summary-zone", rendered)
        self.assertIn("folio-home-card-tags-zone", rendered)
        self.assertIn("요약만 있는 프로젝트", rendered)
        self.assertNotIn("folio-home-card-tags\"><span", rendered)

    def test_author_organization_is_shown_when_present(self) -> None:
        project = {
            "id": "project-456",
            "title": "제목",
            "author": {"name": "홍길동", "organization": "스노우볼"},
        }

        rendered = render_project_card_html(project)

        self.assertIn("홍길동 · 스노우볼", rendered)

    def test_author_line_falls_back_to_name_only_without_organization(self) -> None:
        project = {
            "id": "project-789",
            "title": "제목",
            "author": {"name": "홍길동"},
        }

        rendered = render_project_card_html(project)

        self.assertIn(">홍길동<", rendered)
        self.assertNotIn(" · ", rendered)

    def test_card_includes_hover_preview_when_preview_url_is_present(self) -> None:
        project = {
            "id": "project-preview",
            "title": "미리보기 프로젝트",
        }

        rendered = render_project_card_html(project, preview_url="https://example.com/report")

        self.assertIn("folio-home-card-has-preview", rendered)
        self.assertIn("folio-home-card-preview", rendered)
        self.assertIn('data-folio-preview-src="https://example.com/report"', rendered)

    def test_card_omits_hover_preview_without_preview_url(self) -> None:
        project = {
            "id": "project-no-preview",
            "title": "미리보기 없는 프로젝트",
        }

        rendered = render_project_card_html(project)

        self.assertNotIn("folio-home-card-has-preview", rendered)
        self.assertNotIn("folio-home-card-preview", rendered)


if __name__ == "__main__":
    unittest.main()
