import unittest

from folio_app.components.project_form import (
    _normalize_tag_preview,
    _raw_tag_count,
    validate_project_form,
)


class ProjectFormTests(unittest.TestCase):
    def test_tag_preview_deduplicates_and_limits_to_ten(self) -> None:
        value = "#python, python, sql, powerbi, 통계, 시각화, 공공데이터, ai, pandas, numpy, 취업, 추가"
        self.assertEqual(len(_normalize_tag_preview(value)), 10)
        self.assertEqual(_raw_tag_count(value), 11)

    def test_validation_reports_invalid_optional_url(self) -> None:
        form_data = {
            "title": "프로젝트",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "javascript:alert(1)",
            "github_url": "",
            "thumbnail_url": "",
        }
        _, missing, url_error = validate_project_form(form_data)
        self.assertEqual(missing, [])
        self.assertIn("보고서 URL", url_error or "")


if __name__ == "__main__":
    unittest.main()
