import unittest

from folio_app.services.project_drafts import (
    apply_pending_draft_clear,
    clear_project_draft,
    draft_state_key,
    load_project_draft,
    save_project_draft,
)


class ProjectDraftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state: dict = {}
        self.defaults = {
            "title": "원본 제목",
            "project_body": "원본 본문",
            "is_public": True,
            "thumbnail_url": "https://example.com/original.png",
        }

    def test_missing_draft_returns_independent_defaults(self) -> None:
        restored = load_project_draft(self.state, "user-1", "submit", self.defaults)
        restored["title"] = "변경"

        self.assertEqual(self.defaults["title"], "원본 제목")

    def test_saved_values_override_defaults_and_preserve_false(self) -> None:
        save_project_draft(
            self.state,
            "user-1",
            "submit",
            {"title": "작성 중", "project_body": "초안", "is_public": False},
        )

        restored = load_project_draft(self.state, "user-1", "submit", self.defaults)

        self.assertEqual(restored["title"], "작성 중")
        self.assertEqual(restored["project_body"], "초안")
        self.assertIs(restored["is_public"], False)
        self.assertEqual(restored["thumbnail_url"], self.defaults["thumbnail_url"])

    def test_unknown_form_fields_are_not_saved(self) -> None:
        save_project_draft(self.state, "user-1", "submit", {"title": "초안", "secret": "ignore"})

        self.assertNotIn("secret", self.state[draft_state_key("user-1", "submit")])

    def test_users_and_edit_projects_are_isolated(self) -> None:
        save_project_draft(self.state, "user-1", "edit:project-1", {"title": "프로젝트 1"})
        save_project_draft(self.state, "user-1", "edit:project-2", {"title": "프로젝트 2"})
        save_project_draft(self.state, "user-2", "edit:project-1", {"title": "다른 사용자"})

        self.assertEqual(
            load_project_draft(self.state, "user-1", "edit:project-1", self.defaults)["title"],
            "프로젝트 1",
        )
        self.assertEqual(
            load_project_draft(self.state, "user-1", "edit:project-2", self.defaults)["title"],
            "프로젝트 2",
        )
        self.assertEqual(
            load_project_draft(self.state, "user-2", "edit:project-1", self.defaults)["title"],
            "다른 사용자",
        )

    def test_clear_is_applied_before_next_render(self) -> None:
        self.state.update(
            {
                draft_state_key("user-1", "submit"): {"title": "초안"},
                "submit_title": "위젯 제목",
                "submit_body": "위젯 본문",
                "unrelated": "keep",
            }
        )

        clear_project_draft(self.state, "user-1", "submit", "submit")

        self.assertNotIn(draft_state_key("user-1", "submit"), self.state)
        self.assertIn("submit_title", self.state)
        self.assertTrue(apply_pending_draft_clear(self.state, "user-1", "submit"))
        self.assertNotIn("submit_title", self.state)
        self.assertNotIn("submit_body", self.state)
        self.assertEqual(self.state["unrelated"], "keep")

    def test_no_pending_clear_is_a_noop(self) -> None:
        self.assertFalse(apply_pending_draft_clear(self.state, "user-1", "submit"))


if __name__ == "__main__":
    unittest.main()
