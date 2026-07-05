import unittest

from folio_app.services.projects import _filter_public_projects


class FilterPublicProjectsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.projects = [
            {
                "id": str(index),
                "title": f"프로젝트 {index}",
                "insights": "고객 이탈 분석" if index == 299 else "매출 분석",
                "tags": ["python", "고객"] if index == 299 else ["powerbi"],
            }
            for index in range(300)
        ]

    def test_searches_beyond_previous_250_item_limit(self) -> None:
        result = _filter_public_projects(self.projects, search="이탈")
        self.assertEqual([project["id"] for project in result], ["299"])

    def test_filters_by_exact_tag(self) -> None:
        result = _filter_public_projects(self.projects, tag="고객")
        self.assertEqual([project["id"] for project in result], ["299"])

    def test_does_not_mutate_cached_source_rows(self) -> None:
        result = _filter_public_projects(self.projects)
        result[0]["title"] = "변경"
        self.assertEqual(self.projects[0]["title"], "프로젝트 0")


if __name__ == "__main__":
    unittest.main()
