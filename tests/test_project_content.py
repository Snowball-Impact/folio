import unittest

from folio_app.services.project_content import sanitize_project_html


class SanitizeProjectHTMLTests(unittest.TestCase):
    def test_keeps_editor_markup(self) -> None:
        source = '<h2>문제 정의</h2><p><strong>핵심</strong><br>내용</p>'
        self.assertEqual(sanitize_project_html(source), source)

    def test_removes_executable_markup_and_attributes(self) -> None:
        source = '<p onclick="alert(1)">안전<script>alert(1)</script></p>'
        self.assertEqual(sanitize_project_html(source), "<p>안전</p>")

    def test_allows_only_http_links(self) -> None:
        source = '<a href="javascript:alert(1)">위험</a><a href="https://example.com">안전</a>'
        expected = (
            '<a>위험</a>'
            '<a href="https://example.com" target="_blank" rel="noopener noreferrer">안전</a>'
        )
        self.assertEqual(sanitize_project_html(source), expected)


if __name__ == "__main__":
    unittest.main()
