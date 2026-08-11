import unittest
from unittest.mock import patch

from folio_app.components.project_form import (
    _normalize_tag_preview,
    _raw_tag_count,
    project_type_for_platform,
    build_project_payload,
    hero_preview_project,
    tags_with_platform,
    validate_project_form,
)
from folio_app.services.project_normalizers import clean_project_payload
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
            "thumbnail_mode": "auto_cover",
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
            "thumbnail_mode": "auto_cover",
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
            "thumbnail_mode": "auto_cover",
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
                "thumbnail_mode": "auto_cover",
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

    def test_project_type_follows_selected_platform(self) -> None:
        self.assertEqual(project_type_for_platform("powerbi"), "powerbi")
        self.assertEqual(project_type_for_platform("tableau"), "tableau")
        self.assertEqual(project_type_for_platform("datastudio"), "looker")
        self.assertEqual(project_type_for_platform("streamlit"), "streamlit")
        self.assertEqual(project_type_for_platform("other"), "other")

    def test_hero_preview_project_uses_widget_state_when_available(self) -> None:
        form_data = {
            "title": "초기 제목",
            "one_liner": "초기 소개",
            "tags": "초기",
            "platform": "other",
            "thumbnail_mode": "auto_cover",
            "thumbnail_url": "",
        }
        with patch(
            "folio_app.components.project_form.st.session_state",
            {
                "submit_title": "입력 제목",
                "submit_one_liner": "입력 소개",
                "submit_tags": "매출",
                "submit_platform": "powerbi",
            },
        ):
            preview = hero_preview_project(form_data, "submit")

        self.assertEqual(preview["title"], "입력 제목")
        self.assertEqual(preview["one_liner"], "입력 소개")
        self.assertEqual(preview["tags"], ["Power BI", "매출"])

    def test_manual_thumbnail_requires_valid_url(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "thumbnail_mode": "manual_url",
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIn("썸네일 URL", url_error or "")

    def test_capture_thumbnail_requires_capture_source(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "thumbnail_mode": "capture",
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIn("자동 캡처", url_error or "")

    def test_capture_thumbnail_allows_pbix_upload_as_future_source(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "thumbnail_mode": "capture",
            "pbix_file": type("Uploaded", (), {"name": "report.pbix", "size": 10})(),
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIsNone(url_error)

    def test_auto_cover_clears_thumbnail_url_in_clean_payload(self) -> None:
        payload = clean_project_payload(
            {
                "thumbnail_mode": "auto_cover",
                "thumbnail_url": "https://example.com/thumb.png",
            }
        )

        self.assertEqual(payload["thumbnail_mode"], "auto_cover")
        self.assertIsNone(payload["thumbnail_url"])

    def test_clean_payload_normalizes_project_status_foundation_fields(self) -> None:
        payload = clean_project_payload(
            {
                "project_type": "powerbi",
                "status": "processing",
                "embed_status": "supported",
            }
        )

        self.assertEqual(payload["project_type"], "powerbi")
        self.assertEqual(payload["status"], "processing")
        self.assertEqual(payload["embed_status"], "supported")

    def test_pbix_upload_rejects_non_pbix_file(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "thumbnail_mode": "auto_cover",
            "pbix_file": type("Uploaded", (), {"name": "report.txt", "size": 10})(),
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIn("PBIX 파일만", url_error or "")


if __name__ == "__main__":
    unittest.main()
