import unittest

from folio_app.components.project_form import (
    _normalize_tag_preview,
    _raw_tag_count,
    build_project_payload,
    tags_with_platform,
    validate_project_form,
)
from folio_app.services.project_references import reference_platform_for_project


class ProjectFormTests(unittest.TestCase):
    def test_tag_preview_deduplicates_and_limits_to_ten(self) -> None:
        value = "#python, python, sql, powerbi, 통계, 시각화, 공공데이터, ai, pandas, numpy, 취업, 추가"
        self.assertEqual(len(_normalize_tag_preview(value)), 10)
        self.assertEqual(_raw_tag_count(value), 11)

    def test_validation_reports_invalid_optional_url(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "javascript:alert(1)",
            "github_url": "",
            "thumbnail_url": "",
        }
        _, missing, url_error = validate_project_form(form_data)
        self.assertEqual(missing, [])
        self.assertIn("보고서 URL", url_error or "")

    def test_validation_reports_text_that_exceeds_card_limits(self) -> None:
        form_data = {
            "title": "가" * 49,
            "one_liner": "나" * 57,
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIn("프로젝트명은 최대 48자", url_error or "")
        self.assertIn("프로젝트 한 줄 소개는 최대 56자", url_error or "")

    def test_build_payload_preserves_private_visibility(self) -> None:
        form_data = {
            "title": "비공개 프로젝트",
            "one_liner": "",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "tags": "python",
            "is_public": False,
        }
        parsed_body = {
            "problem": "문제",
            "dataset": "데이터",
            "process": "과정",
            "insights": "인사이트",
        }

        payload = build_project_payload(form_data, parsed_body)

        self.assertIs(payload["is_public"], False)

    def test_platform_selection_is_saved_as_reference_tag(self) -> None:
        self.assertEqual(
            tags_with_platform("매출 분석, PowerBI, 대시보드", "tableau"),
            ["Tableau", "매출 분석", "대시보드"],
        )

        payload = build_project_payload(
            {
                "title": "레퍼런스",
                "one_liner": "",
                "power_bi_url": "",
                "report_url": "",
                "github_url": "",
                "thumbnail_url": "",
                "tags": "고객 분석",
                "platform": "datastudio",
                "is_public": True,
            },
            {
                "problem": "문제",
                "dataset": "데이터",
                "process": "과정",
                "insights": "인사이트",
            },
        )

        self.assertEqual(payload["tags"], ["Data Studio", "고객 분석"])
        self.assertEqual(reference_platform_for_project(payload), "datastudio")


if __name__ == "__main__":
    unittest.main()
