import unittest

from folio_app.pages.home import _filter_projects_by_platforms, _popular_tags_from_projects
from folio_app.pages.reference import _next_visible_count
from folio_app.services.project_references import (
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
