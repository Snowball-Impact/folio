import unittest
from unittest.mock import MagicMock, patch

from folio_app.services.auth import _friendly_auth_error
from folio_app.services.profiles import ProfileServiceError, get_profile
from folio_app.services.projects import (
    ProjectServiceError,
    _execute_public_read,
    _fetch_like_counts,
    _fetch_public_profiles,
    create_project,
    delete_project,
    set_project_liked,
)


PROVIDER_DETAIL = "provider-secret-detail"


class SafeMutationMessageTests(unittest.TestCase):
    @patch("folio_app.services.projects.get_supabase_client")
    def test_create_error_does_not_expose_provider_detail(self, get_client) -> None:
        builder = MagicMock()
        builder.insert.return_value = builder
        builder.execute.side_effect = RuntimeError(PROVIDER_DETAIL)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = create_project("author-id", {"title": "test"})

        self.assertFalse(result.ok)
        self.assertNotIn(PROVIDER_DETAIL, result.message)

    @patch("folio_app.services.projects.get_supabase_client")
    def test_delete_error_does_not_expose_provider_detail(self, get_client) -> None:
        builder = MagicMock()
        builder.delete.return_value = builder
        builder.eq.return_value = builder
        builder.execute.side_effect = RuntimeError(PROVIDER_DETAIL)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = delete_project("project-id", "author-id")

        self.assertFalse(result.ok)
        self.assertNotIn(PROVIDER_DETAIL, result.message)

    @patch("folio_app.services.projects.get_supabase_client")
    def test_like_error_does_not_expose_provider_detail(self, get_client) -> None:
        builder = MagicMock()
        builder.insert.return_value = builder
        builder.execute.side_effect = RuntimeError(PROVIDER_DETAIL)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        result = set_project_liked("project-id", "user-id", True)

        self.assertFalse(result.ok)
        self.assertNotIn(PROVIDER_DETAIL, result.message)

    def test_unknown_auth_error_does_not_expose_provider_detail(self) -> None:
        message = _friendly_auth_error("로그인", RuntimeError(PROVIDER_DETAIL))

        self.assertNotIn(PROVIDER_DETAIL, message)


class ReadFailureDistinctionTests(unittest.TestCase):
    def tearDown(self) -> None:
        _fetch_like_counts.clear()
        _fetch_public_profiles.clear()

    @patch("folio_app.services.profiles.get_supabase_client")
    def test_profile_provider_failure_is_not_reported_as_missing_profile(self, get_client) -> None:
        builder = MagicMock()
        builder.select.return_value = builder
        builder.eq.return_value = builder
        builder.maybe_single.return_value = builder
        builder.execute.side_effect = RuntimeError(PROVIDER_DETAIL)
        client = MagicMock()
        client.table.return_value = builder
        get_client.return_value = client

        with self.assertRaisesRegex(ProfileServiceError, "프로필 정보를 불러오지 못했습니다") as raised:
            get_profile("user-id")

        self.assertNotIn(PROVIDER_DETAIL, str(raised.exception))

    @patch("folio_app.services.projects._execute_public_read", return_value=None)
    @patch("folio_app.services.projects.get_supabase_client")
    def test_like_count_failure_is_not_reported_as_zero(self, get_client, _execute) -> None:
        get_client.return_value = MagicMock()

        with self.assertRaisesRegex(ProjectServiceError, "좋아요 통계를 불러오지 못했습니다"):
            _fetch_like_counts(("project-error-case",))

    @patch("folio_app.services.projects._execute_public_read", side_effect=[RuntimeError("view"), None])
    @patch("folio_app.services.projects.get_supabase_client")
    def test_author_failure_is_not_reported_as_empty_author(self, get_client, _execute) -> None:
        get_client.return_value = MagicMock()

        with self.assertRaisesRegex(ProjectServiceError, "작성자 정보를 불러오지 못했습니다"):
            _fetch_public_profiles(("author-error-case",))

    @patch("folio_app.services.projects.logger")
    @patch("folio_app.services.projects.recover_from_expired_jwt", return_value=True)
    def test_failed_retry_after_jwt_recovery_is_logged(self, _recover, logger) -> None:
        operation = MagicMock(side_effect=[RuntimeError("expired"), RuntimeError(PROVIDER_DETAIL)])

        result = _execute_public_read(operation)

        self.assertIsNone(result)
        self.assertEqual(operation.call_count, 2)
        logger.exception.assert_called_once_with("Public read failed after JWT recovery")


if __name__ == "__main__":
    unittest.main()
