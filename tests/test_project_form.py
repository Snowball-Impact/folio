import unittest
from types import SimpleNamespace
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
    def test_tag_preview_deduplicates_and_limits_to_five(self) -> None:
        value = "#python, python, sql, powerbi, 통계, 시각화, 공공데이터, ai, pandas, numpy, 취업, 추가"
        self.assertEqual(len(_normalize_tag_preview(value)), 5)
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

    def test_tags_with_platform_limits_saved_tags_to_five(self) -> None:
        self.assertEqual(
            tags_with_platform("a, b, c, d, e, f", "powerbi"),
            ["Power BI", "a", "b", "c", "d"],
        )

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

    def test_hero_preview_project_uses_uploaded_thumbnail_file(self) -> None:
        form_data = {
            "title": "초기 제목",
            "one_liner": "초기 소개",
            "tags": "",
            "platform": "other",
            "thumbnail_mode": "auto_cover",
            "thumbnail_url": "",
        }
        uploaded_file = SimpleNamespace(
            type="image/png",
            getbuffer=lambda: memoryview(b"image"),
        )
        with patch(
            "folio_app.components.project_form.st.session_state",
            {
                "submit_thumbnail_mode": "upload",
                "submit_thumbnail_file": uploaded_file,
            },
        ):
            preview = hero_preview_project(form_data, "submit")

        self.assertEqual(preview["thumbnail_url"], "data:image/png;base64,aW1hZ2U=")

    def test_hero_preview_project_uses_existing_capture_thumbnail(self) -> None:
        form_data = {
            "title": "초기 제목",
            "one_liner": "초기 소개",
            "tags": "",
            "platform": "other",
            "thumbnail_mode": "capture",
            "thumbnail_url": "https://cdn.example.com/capture.jpg",
        }
        with patch("folio_app.components.project_form.st.session_state", {"edit_project_thumbnail_mode": "capture"}):
            preview = hero_preview_project(form_data, "edit_project")

        self.assertEqual(preview["thumbnail_url"], "https://cdn.example.com/capture.jpg")

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

    def test_upload_thumbnail_requires_file_without_existing_url(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "thumbnail_mode": "upload",
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIn("이미지 업로드 썸네일", url_error or "")

    def test_upload_thumbnail_allows_existing_url_without_new_file(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "https://cdn.example.com/thumb.jpg",
            "thumbnail_mode": "upload",
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIsNone(url_error)

    def test_delete_thumbnail_switches_payload_to_auto_cover(self) -> None:
        payload = build_project_payload(
            {
                "title": "프로젝트",
                "one_liner": "",
                "power_bi_url": "",
                "report_url": "",
                "github_url": "",
                "thumbnail_url": "https://cdn.example.com/thumb.jpg",
                "thumbnail_mode": "upload",
                "delete_thumbnail": True,
                "tags": "",
                "is_public": True,
            },
            {
                "problem": "문제",
                "dataset": "",
                "process": "",
                "insights": "",
            },
        )

        self.assertEqual(payload["thumbnail_mode"], "auto_cover")
        self.assertEqual(payload["thumbnail_url"], "")

    def test_delete_thumbnail_with_new_file_keeps_upload_mode(self) -> None:
        payload = build_project_payload(
            {
                "title": "프로젝트",
                "one_liner": "",
                "power_bi_url": "",
                "report_url": "",
                "github_url": "",
                "thumbnail_url": "https://cdn.example.com/thumb.jpg",
                "thumbnail_mode": "upload",
                "thumbnail_file": object(),
                "delete_thumbnail": True,
                "tags": "",
                "is_public": True,
            },
            {
                "problem": "문제",
                "dataset": "데이터",
                "process": "과정",
                "insights": "인사이트",
            },
        )

        self.assertEqual(payload["thumbnail_mode"], "upload")
        self.assertEqual(payload["thumbnail_url"], "")

    def test_delete_capture_thumbnail_keeps_capture_mode_for_recapture(self) -> None:
        payload = build_project_payload(
            {
                "title": "프로젝트",
                "one_liner": "",
                "power_bi_url": "https://example.com/embed",
                "report_url": "",
                "github_url": "",
                "thumbnail_url": "https://cdn.example.com/old-capture.jpg",
                "thumbnail_mode": "capture",
                "delete_thumbnail": True,
                "tags": "",
                "is_public": True,
            },
            {
                "problem": "문제",
                "dataset": "",
                "process": "",
                "insights": "",
            },
        )

        self.assertEqual(payload["thumbnail_mode"], "capture")
        self.assertEqual(payload["thumbnail_url"], "")
        self.assertTrue(payload["delete_thumbnail"])

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

    def test_pbix_delete_with_new_file_is_allowed_for_replacement(self) -> None:
        form_data = {
            "title": "프로젝트",
            "one_liner": "",
            "project_body": "## 문제 정의\n내용",
            "power_bi_url": "",
            "report_url": "",
            "github_url": "",
            "thumbnail_url": "",
            "thumbnail_mode": "auto_cover",
            "delete_pbix": True,
            "pbix_file": type("Uploaded", (), {"name": "report.pbix", "size": 10})(),
        }

        _, missing, url_error = validate_project_form(form_data)

        self.assertEqual(missing, [])
        self.assertIsNone(url_error)


if __name__ == "__main__":
    unittest.main()
