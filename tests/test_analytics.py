import unittest
from unittest.mock import patch

from folio_app.components.analytics import render_google_analytics, track_event, track_page_view


class GoogleAnalyticsTests(unittest.TestCase):
    @patch("folio_app.components.analytics.components.html")
    def test_does_nothing_without_a_measurement_id(self, html) -> None:
        render_google_analytics("")

        html.assert_not_called()

    @patch("folio_app.components.analytics.components.html")
    def test_embeds_the_measurement_id_when_configured(self, html) -> None:
        render_google_analytics("G-3VB889G8VK")

        html.assert_called_once()
        rendered_script = html.call_args[0][0]
        self.assertIn("G-3VB889G8VK", rendered_script)
        self.assertIn("window.parent.document", rendered_script)


class TrackEventTests(unittest.TestCase):
    @patch("folio_app.components.analytics.components.html")
    def test_guards_against_a_missing_gtag_before_calling_it(self, html) -> None:
        track_event("like", {"item_id": "project-123"})

        rendered_script = html.call_args[0][0]
        self.assertIn("typeof window.parent.gtag !== 'function'", rendered_script)
        self.assertIn('"like"', rendered_script)
        self.assertIn("project-123", rendered_script)

    @patch("folio_app.components.analytics.components.html")
    def test_page_view_includes_title_and_path(self, html) -> None:
        track_page_view("Home", "/?page=Home")

        rendered_script = html.call_args[0][0]
        self.assertIn('"page_view"', rendered_script)
        self.assertIn("Home", rendered_script)
        self.assertIn("/?page=Home", rendered_script)

    @patch("folio_app.components.analytics.components.html")
    def test_korean_params_are_not_escaped_to_ascii(self, html) -> None:
        track_event("search", {"search_term": "고객 이탈"})

        rendered_script = html.call_args[0][0]
        self.assertIn("고객 이탈", rendered_script)


if __name__ == "__main__":
    unittest.main()
