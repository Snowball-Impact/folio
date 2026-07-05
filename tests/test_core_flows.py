import unittest
from unittest.mock import patch

from folio_app.components.project_form import parse_project_body
from folio_app.navigation import navigate
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
