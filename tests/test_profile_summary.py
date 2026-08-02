import unittest

from folio_app.components.profile_summary import profile_overview_html


class ProfileSummaryTests(unittest.TestCase):
    def test_profile_overview_escapes_user_content(self) -> None:
        rendered = profile_overview_html(
            {"email": "user@example.com"},
            {
                "name": "홍<script>",
                "email": "profile@example.com",
                "organization": "A&B",
                "bio": "<b>소개</b>",
            },
            [{"is_public": True, "like_count": 3}, {"is_public": False, "like_count": 2}],
            {"project_count": 2, "view_count": 1200},
        )

        self.assertIn("홍&lt;script&gt;", rendered)
        self.assertIn("A&amp;B", rendered)
        self.assertIn("&lt;b&gt;소개&lt;/b&gt;", rendered)
        self.assertIn("1,200", rendered)
        self.assertIn(">5</strong>", rendered)


if __name__ == "__main__":
    unittest.main()
