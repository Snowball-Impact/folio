import unittest

from folio_app.components.ui import _cover_variant, render_project_card_html


class AutomaticProjectCoverTests(unittest.TestCase):
    def test_same_project_always_uses_same_cover_variant(self) -> None:
        project = {"id": "project-123", "title": "분석 프로젝트"}
        self.assertEqual(_cover_variant(project), _cover_variant(dict(project)))

    def test_cover_contains_escaped_title_and_two_tags(self) -> None:
        project = {
            "id": "project-123",
            "title": "고객 <이탈> 분석",
            "tags": ["Python", "고객&분석", "세 번째"],
            "one_liner": "프로젝트 설명",
        }

        rendered = render_project_card_html(project)

        self.assertIn("고객 &lt;이탈&gt; 분석", rendered)
        self.assertIn("#Python", rendered)
        self.assertIn("#고객&amp;분석", rendered)
        self.assertNotIn("세 번째", rendered)
        self.assertEqual(rendered.count("고객 &lt;이탈&gt; 분석"), 1)
        self.assertIn('aria-label="조회수 0"', rendered)
        self.assertIn('aria-label="좋아요 0"', rendered)
        self.assertNotIn("조회 0 · 좋아요 0", rendered)


if __name__ == "__main__":
    unittest.main()
