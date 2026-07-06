import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from postgrest.types import CountMethod, ReturnMethod

from folio_app.services.auth import AuthResult
from folio_app.services.projects import ProjectServiceError, _filter_public_projects, list_public_projects, update_project


class ProjectMutationTests(unittest.TestCase):
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, "ok"))
    @patch("folio_app.services.projects.get_supabase_client")
    def test_update_uses_minimal_return_to_allow_public_to_private_change(self, get_client, _auth) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=None, count=1)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = update_project("project-id", "author-id", {"is_public": False})

        self.assertTrue(result.ok)
        builder.update.assert_called_once_with(
            {"is_public": False},
            count=CountMethod.exact,
            returning=ReturnMethod.minimal,
        )


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


class ProjectReadFailureTests(unittest.TestCase):
    @patch("folio_app.services.projects._fetch_public_projects")
    def test_configuration_failure_is_not_reported_as_empty_data(self, fetch_projects) -> None:
        fetch_projects.side_effect = ProjectServiceError("Supabase 연결 설정을 확인하세요.")

        with self.assertRaisesRegex(ProjectServiceError, "Supabase 연결 설정"):
            list_public_projects()

    @patch("folio_app.services.projects._attach_related_data")
    @patch("folio_app.services.projects._fetch_public_projects", return_value=[{"id": "1"}])
    def test_related_data_failure_becomes_safe_service_error(self, _fetch_projects, attach_data) -> None:
        attach_data.side_effect = RuntimeError("provider details")

        with self.assertRaisesRegex(ProjectServiceError, "공개 프로젝트를 불러오지 못했습니다"):
            list_public_projects()


if __name__ == "__main__":
    unittest.main()
