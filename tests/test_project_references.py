import unittest

from unittest.mock import patch

from folio_app.pages.home import _filter_projects_by_platforms, _platform_filter_options, _popular_tags_from_projects
from folio_app.pages.reference import (
    _next_visible_count,
    _reference_back_params,
    _reference_card_query_params,
    _reference_card_slot_html,
    _selected_platform_key,
    _selected_sort_key,
    _sort_label_for_query,
    _sort_item_html,
)
from folio_app.services.project_references import (
    DEFAULT_REFERENCE_PLATFORM_KEY,
    VISIBLE_REFERENCE_PLATFORMS,
    non_reference_projects,
    reference_platform_for_project,
    reference_projects_for_platform,
)


class ProjectReferenceTests(unittest.TestCase):
    def test_detects_platform_from_tags(self) -> None:
        self.assertEqual(reference_platform_for_project({"tags": ["Tableau"]}), "tableau")
        self.assertEqual(reference_platform_for_project({"tags": ["PowerBI"]}), "powerbi")
        self.assertEqual(reference_platform_for_project({"tags": ["Looker Studio"]}), "datastudio")
        self.assertEqual(reference_platform_for_project({"tags": ["Streamlit"]}), "streamlit")

    def test_detects_platform_from_urls(self) -> None:
        self.assertEqual(
            reference_platform_for_project({"power_bi_url": "https://datastudio.google.com/embed/reporting/abc"}),
            "datastudio",
        )
        self.assertEqual(
            reference_platform_for_project({"report_url": "https://demo-example.streamlit.app"}),
            "streamlit",
        )

    def test_splits_reference_and_non_reference_projects(self) -> None:
        projects = [
            {"id": "tableau", "tags": ["Tableau"]},
            {"id": "ordinary", "tags": ["고객 분석"]},
            {"id": "streamlit", "report_url": "https://demo.streamlit.app"},
        ]

        self.assertEqual([project["id"] for project in non_reference_projects(projects)], ["ordinary"])
        self.assertEqual(
            [project["id"] for project in reference_projects_for_platform(projects, "streamlit")],
            ["streamlit"],
        )

    def test_launch_mode_exposes_only_powerbi_reference_platform(self) -> None:
        self.assertEqual(DEFAULT_REFERENCE_PLATFORM_KEY, "powerbi")
        self.assertEqual([platform.key for platform in VISIBLE_REFERENCE_PLATFORMS], ["powerbi"])

    def test_home_content_type_filter_is_hidden_to_powerbi_only(self) -> None:
        self.assertEqual(_platform_filter_options(), [("powerbi", "Power BI")])

    @patch("folio_app.pages.reference.st.query_params", {"platform": "tableau"})
    def test_hidden_reference_platform_url_falls_back_to_powerbi(self) -> None:
        self.assertEqual(_selected_platform_key(), "powerbi")

    @patch("folio_app.pages.reference.st.query_params", {"sort": "likes"})
    def test_reference_sort_query_uses_home_gallery_sort_labels(self) -> None:
        self.assertEqual(_selected_sort_key(), "likes")
        self.assertEqual(_sort_label_for_query("latest"), "최신순")
        self.assertEqual(_sort_label_for_query("likes"), "좋아요순")
        self.assertEqual(_sort_label_for_query("views"), "조회수순")

    @patch("folio_app.pages.reference.st.query_params", {"sort": "unknown"})
    def test_unknown_reference_sort_falls_back_to_latest(self) -> None:
        self.assertEqual(_selected_sort_key(), "latest")

    @patch("folio_app.pages.reference.st.query_params", {"visible": "24"})
    def test_reference_card_query_params_preserve_sort_and_visible_count(self) -> None:
        self.assertEqual(
            _reference_card_query_params("powerbi", "views"),
            {"platform": "powerbi", "sort": "views", "visible": "24"},
        )

    def test_reference_back_params_preserve_non_default_sort(self) -> None:
        self.assertEqual(_reference_back_params("powerbi", "latest"), {"platform": "powerbi"})
        self.assertEqual(
            _reference_back_params("powerbi", "likes"),
            {"platform": "powerbi", "sort": "likes"},
        )

    def test_reference_sort_item_is_client_side_button(self) -> None:
        rendered = _sort_item_html("likes", "views", "조회수")
        self.assertIn('type="button"', rendered)
        self.assertIn('data-folio-reference-sort="views"', rendered)
        self.assertNotIn("<a ", rendered)

    @patch("folio_app.pages.reference.st.query_params", {})
    def test_reference_card_slot_exposes_client_sort_values(self) -> None:
        rendered = _reference_card_slot_html(
            {
                "id": "project-1",
                "title": "Power BI Sample",
                "created_at": "2026-08-23T10:00:00",
                "like_count": 7,
                "view_count": 42,
            },
            "powerbi",
            "latest",
            1,
            2,
        )
        self.assertIn("is-hidden", rendered)
        self.assertIn('data-created-at="2026-08-23T10:00:00"', rendered)
        self.assertIn('data-like-count="7"', rendered)
        self.assertIn('data-view-count="42"', rendered)

    def test_home_platform_filter_supports_all_other_and_reference_platform(self) -> None:
        projects = [
            {"id": "tableau", "tags": ["Tableau"]},
            {"id": "ordinary", "tags": ["고객 분석"]},
            {"id": "datastudio", "power_bi_url": "https://datastudio.google.com/embed/reporting/abc"},
        ]

        self.assertEqual(
            [project["id"] for project in _filter_projects_by_platforms(projects, {"all"})],
            ["tableau", "ordinary", "datastudio"],
        )
        self.assertEqual(
            [project["id"] for project in _filter_projects_by_platforms(projects, {"other"})],
            ["ordinary"],
        )
        self.assertEqual(
            [project["id"] for project in _filter_projects_by_platforms(projects, {"datastudio"})],
            ["datastudio"],
        )

    def test_popular_tags_exclude_reference_and_platform_menu_tags(self) -> None:
        projects = [
            {"id": "tableau", "tags": ["Tableau", "Reference", "인구 통계"]},
            {"id": "powerbi", "tags": ["Power BI", "reference", "매출 분석"]},
            {"id": "looker", "tags": ["Looker Studio", "레퍼런스", "인구 통계"]},
            {"id": "ordinary", "tags": ["기타", "Other", "참고", "고객 분석"]},
        ]

        self.assertEqual(
            _popular_tags_from_projects(projects),
            ["인구 통계", "매출 분석", "고객 분석"],
        )

    def test_reference_load_more_count_is_capped_by_total(self) -> None:
        self.assertEqual(_next_visible_count(12, 80), 24)
        self.assertEqual(_next_visible_count(72, 80), 80)


if __name__ == "__main__":
    unittest.main()
