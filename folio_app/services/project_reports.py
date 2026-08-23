from __future__ import annotations

import logging
from typing import Final

from folio_app.services.project_types import ProjectReportResult
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)

REPORT_REASON_EMBED_BROKEN: Final = "embed_broken"
REPORT_REASON_WRONG_CONTENT: Final = "wrong_content"
REPORT_REASON_INAPPROPRIATE: Final = "inappropriate"
REPORT_REASON_OTHER: Final = "other"

REPORT_REASON_LABELS: Final = {
    REPORT_REASON_EMBED_BROKEN: "대시보드/임베딩이 열리지 않음",
    REPORT_REASON_WRONG_CONTENT: "제목이나 설명이 실제 내용과 다름",
    REPORT_REASON_INAPPROPRIATE: "부적절한 콘텐츠",
    REPORT_REASON_OTHER: "기타",
}

REPORT_DETAIL_MAX_CHARS: Final = 500


def submit_project_report(
    project_id: str,
    reporter_id: str,
    reason: str,
    details: str = "",
) -> ProjectReportResult:
    from folio_app.services.auth import ensure_authenticated_session

    auth_result = ensure_authenticated_session()
    if not auth_result.ok:
        return ProjectReportResult(False, auth_result.message)

    client = get_supabase_client()
    if client is None:
        return ProjectReportResult(False, "Supabase 환경 변수가 설정되지 않았습니다.")

    normalized_reason = reason if reason in REPORT_REASON_LABELS else REPORT_REASON_OTHER
    normalized_details = " ".join(str(details or "").split())[:REPORT_DETAIL_MAX_CHARS] or None
    payload = {
        "project_id": project_id,
        "reporter_id": reporter_id,
        "reason": normalized_reason,
        "details": normalized_details,
    }

    try:
        response = client.table("content_reports").insert(payload).execute()
    except Exception as exc:
        if _is_missing_project_reports_schema(exc):
            logger.exception("Project report failed because schema is missing")
            return ProjectReportResult(False, "신고 기능을 사용하려면 Supabase content_reports 스키마를 먼저 적용해야 합니다.")
        logger.exception("Failed to submit project report")
        return ProjectReportResult(False, "신고를 접수하지 못했습니다. 잠시 후 다시 시도하세요.")

    report_id = None
    if response.data:
        report_id = response.data[0].get("id")
    return ProjectReportResult(True, "신고가 접수되었습니다. 확인 후 필요한 조치를 진행하겠습니다.", report_id)


def _is_missing_project_reports_schema(exc: Exception) -> bool:
    message = str(exc).lower()
    return "content_reports" in message and (
        "relation" in message
        or "schema cache" in message
        or "does not exist" in message
    )
