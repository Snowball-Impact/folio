import unittest
from unittest.mock import patch

from folio_app.pages.protected import _editing_project_id_from_query, render_my_page


class ProtectedMyPageTests(unittest.TestCase):
    @patch("folio_app.pages.protected.st.query_params", {"edit_project_id": "project-1"})
    def test_editing_project_id_comes_from_query(self) -> None:
        self.assertEqual(_editing_project_id_from_query(), "project-1")

    @patch("folio_app.pages.protected.render_edit_project_form")
    @patch("folio_app.pages.protected.annotate_unread_comment_status")
    @patch("folio_app.pages.protected.list_projects_by_author")
    @patch("folio_app.pages.protected.get_current_user")
    @patch("folio_app.pages.protected.st.session_state", {})
    @patch("folio_app.pages.protected.st.query_params", {"page": "My Page", "edit_project_id": "project-1"})
    def test_my_page_refresh_with_edit_query_renders_edit_form(
        self,
        get_current_user,
        list_projects_by_author,
        _annotate_unread,
        render_edit_project_form,
    ) -> None:
        user = {"id": "user-1"}
        project = {"id": "project-1", "title": "Project"}
        get_current_user.return_value = user
        list_projects_by_author.return_value = [project]

        render_my_page()

        render_edit_project_form.assert_called_once_with("user-1", project)


if __name__ == "__main__":
    unittest.main()
