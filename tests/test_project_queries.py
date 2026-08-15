import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, call, patch

from postgrest.types import CountMethod, ReturnMethod

from folio_app.services.auth import AuthResult
from folio_app.services.project_mutations import delete_project, update_project
from folio_app.services.project_queries import _filter_public_projects, list_public_projects
from folio_app.services.project_types import ProjectServiceError


class ProjectMutationTests(unittest.TestCase):
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, "ok"))
    @patch("folio_app.services.project_mutations.get_supabase_client")
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

    @patch("folio_app.services.project_mutations.try_delete_project_thumbnail_file")
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, "ok"))
    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_update_deletes_stored_thumbnail_when_switching_to_auto_cover(
        self,
        get_client,
        _auth,
        delete_thumbnail,
    ) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=None, count=1)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = update_project("project-id", "author-id", {"thumbnail_mode": "auto_cover", "thumbnail_url": ""})

        self.assertTrue(result.ok)
        delete_thumbnail.assert_called_once_with("project-id")

    @patch("folio_app.services.project_mutations.maybe_capture_project_thumbnail")
    @patch("folio_app.services.project_mutations.try_delete_project_thumbnail_file")
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, "ok"))
    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_update_deletes_existing_capture_before_recapturing_thumbnail(
        self,
        get_client,
        _auth,
        delete_thumbnail,
        capture_thumbnail,
    ) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=None, count=1)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client
        calls = MagicMock()
        calls.attach_mock(delete_thumbnail, "delete_thumbnail")
        calls.attach_mock(capture_thumbnail, "capture_thumbnail")

        result = update_project(
            "project-id",
            "author-id",
            {
                "thumbnail_mode": "capture",
                "thumbnail_url": "",
                "power_bi_url": "https://example.com/embed",
                "delete_thumbnail": True,
            },
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            calls.mock_calls[:2],
            [
                call.delete_thumbnail("project-id"),
                call.capture_thumbnail("project-id", ANY, progress_callback=None),
            ],
        )

    @patch("folio_app.services.project_mutations.try_delete_project_thumbnail_file")
    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, "ok"))
    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_partial_update_without_thumbnail_mode_does_not_delete_thumbnail(
        self,
        get_client,
        _auth,
        delete_thumbnail,
    ) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=None, count=1)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = update_project("project-id", "author-id", {"is_public": False})

        self.assertTrue(result.ok)
        delete_thumbnail.assert_not_called()

    @patch("folio_app.services.auth.ensure_authenticated_session", return_value=AuthResult(True, "ok"))
    @patch("folio_app.services.project_mutations.get_supabase_client")
    def test_delete_project_soft_deletes_instead_of_physical_delete(self, get_client, _auth) -> None:
        builder = MagicMock()
        builder.update.return_value = builder
        builder.eq.return_value = builder
        builder.execute.return_value = SimpleNamespace(data=None, count=1)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = delete_project("project-id", "author-id")

        self.assertTrue(result.ok)
        builder.update.assert_called_once()
        update_payload = builder.update.call_args.args[0]
        self.assertEqual(update_payload["status"], "deleted")
        self.assertFalse(update_payload["is_public"])
        self.assertIn("deleted_at", update_payload)


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

    def test_public_filter_only_keeps_published_projects(self) -> None:
        projects = [
            {"id": "published", "title": "A", "status": "published"},
            {"id": "legacy", "title": "B"},
            {"id": "processing", "title": "C", "status": "processing"},
            {"id": "failed", "title": "D", "status": "failed"},
            {"id": "deleted", "title": "E", "status": "deleted"},
        ]

        result = _filter_public_projects(projects)

        self.assertEqual([project["id"] for project in result], ["published", "legacy"])

    def test_does_not_mutate_cached_source_rows(self) -> None:
        result = _filter_public_projects(self.projects)
        result[0]["title"] = "변경"
        self.assertEqual(self.projects[0]["title"], "프로젝트 0")

    def test_searches_by_author_name_and_organization(self) -> None:
        projects = [
            {"id": "author-match", "title": "A", "author": {"name": "홍길동", "organization": "스노우볼"}},
            {"id": "org-match", "title": "B", "author": {"name": "김철수", "organization": "폴리오랩"}},
            {"id": "no-match", "title": "C", "author": {"name": "이영희", "organization": "다른회사"}},
        ]
        self.assertEqual(
            [p["id"] for p in _filter_public_projects(projects, search="홍길동")],
            ["author-match"],
        )
        self.assertEqual(
            [p["id"] for p in _filter_public_projects(projects, search="폴리오랩")],
            ["org-match"],
        )

    def test_searches_by_created_at(self) -> None:
        projects = [
            {"id": "on-date", "title": "A", "created_at": "2026-06-23T01:30:22+00:00"},
            {"id": "other-date", "title": "B", "created_at": "2026-07-07T01:30:22+00:00"},
        ]
        self.assertEqual(
            [p["id"] for p in _filter_public_projects(projects, search="2026-06-23")],
            ["on-date"],
        )

    def test_search_does_not_require_author_key(self) -> None:
        projects = [{"id": "no-author", "title": "제목만 있음"}]
        self.assertEqual(
            [p["id"] for p in _filter_public_projects(projects, search="제목만")],
            ["no-author"],
        )


class ProjectReadFailureTests(unittest.TestCase):
    @patch("folio_app.services.project_queries._fetch_public_projects")
    def test_configuration_failure_is_not_reported_as_empty_data(self, fetch_projects) -> None:
        fetch_projects.side_effect = ProjectServiceError("Supabase 연결 설정을 확인하세요.")

        with self.assertRaisesRegex(ProjectServiceError, "Supabase 연결 설정"):
            list_public_projects()

    @patch("folio_app.services.project_queries._attach_related_data")
    @patch("folio_app.services.project_queries._fetch_public_projects", return_value=[{"id": "1"}])
    def test_related_data_failure_becomes_safe_service_error(self, _fetch_projects, attach_data) -> None:
        attach_data.side_effect = RuntimeError("provider details")

        with self.assertRaisesRegex(ProjectServiceError, "공개 프로젝트를 불러오지 못했습니다"):
            list_public_projects()


if __name__ == "__main__":
    unittest.main()
