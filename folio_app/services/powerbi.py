"""Power BI REST API integration for PBIX publishing and embed metadata."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Any, Callable
from urllib.parse import quote

import requests

from folio_app.config import Settings, get_settings
from folio_app.services.project_normalizers import EMBED_STATUS_SUPPORTED, PROJECT_STATUS_FAILED, PROJECT_STATUS_PUBLISHED
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
IMPORT_SUCCEEDED_STATES = {"succeeded", "completed"}
IMPORT_FAILED_STATES = {"failed"}
PowerBIProgressCallback = Callable[[int, str], None]


class PowerBIServiceError(RuntimeError):
    """A Power BI operation failed in a way the UI can safely report."""


@dataclass(frozen=True)
class PowerBIImportResult:
    ok: bool
    message: str
    project_id: str
    import_id: str | None = None
    import_status: str | None = None
    report_id: str | None = None
    dataset_id: str | None = None
    embed_url: str | None = None


@dataclass(frozen=True)
class PowerBIEmbedConfig:
    report_id: str
    dataset_id: str
    embed_url: str
    embed_token: str
    token_expiration: str | None = None


def publish_pbix_for_project(
    project_id: str,
    pbix_bytes: bytes,
    original_filename: str,
    *,
    settings: Settings | None = None,
    session: requests.Session | None = None,
    progress_callback: PowerBIProgressCallback | None = None,
) -> PowerBIImportResult:
    settings = settings or get_settings()
    if not settings.is_powerbi_configured:
        return PowerBIImportResult(False, "Power BI 게시 환경 변수가 설정되지 않았습니다.", project_id)

    try:
        _validate_pbix_upload(pbix_bytes, original_filename, settings.pbix_max_upload_mb)
    except PowerBIServiceError as exc:
        return PowerBIImportResult(False, str(exc), project_id)

    try:
        access_token = fetch_powerbi_access_token(settings, session=session)
        import_payload = post_pbix_import(
            settings,
            access_token,
            pbix_bytes,
            _dataset_display_name(project_id, original_filename),
            session=session,
        )
        import_id = import_payload.get("id")
        if not import_id:
            raise PowerBIServiceError("Power BI Import 응답을 확인할 수 없습니다.")

        import_state = poll_import_completion(
            settings,
            access_token,
            import_id,
            session=session,
            progress_callback=progress_callback,
        )
        import_status = str(import_state.get("importState") or import_state.get("state") or "").lower()
        if import_status not in IMPORT_SUCCEEDED_STATES:
            if import_status in IMPORT_FAILED_STATES:
                _mark_project_powerbi_failed(project_id, import_id, import_status, "Power BI Import가 실패했습니다.")
                message = "Power BI 게시에 실패했습니다. PBIX 파일과 Workspace 권한을 확인하세요."
            else:
                _mark_project_powerbi_processing(
                    project_id,
                    import_id,
                    import_status,
                    "Power BI Import가 아직 완료되지 않았습니다.",
                    settings=settings,
                )
                message = "Power BI 게시가 아직 완료되지 않았습니다. 잠시 후 다시 확인하세요."
            return PowerBIImportResult(
                False,
                message,
                project_id,
                import_id=import_id,
                import_status=import_status,
            )

        report = _first_report_from_import(import_state)
        report_id = report.get("id")
        if not report_id:
            raise PowerBIServiceError("Power BI Report ID를 확인할 수 없습니다.")

        report_metadata = get_report_metadata(settings, access_token, report_id, session=session)
        upsert_powerbi_report(
            project_id,
            {
                "workspace_id": settings.powerbi_workspace_id,
                "report_id": report_id,
                "dataset_id": report_metadata.get("datasetId") or report.get("datasetId"),
                "embed_url": report_metadata.get("embedUrl") or report.get("embedUrl"),
                "web_url": report_metadata.get("webUrl") or report.get("webUrl"),
                "import_id": import_id,
                "import_status": import_status,
                "error_code": None,
                "error_message": None,
            },
        )
        _mark_project_powerbi_published(project_id, report_metadata.get("embedUrl") or report.get("embedUrl"))
        return PowerBIImportResult(
            True,
            "Power BI 보고서가 게시되었습니다.",
            project_id,
            import_id=import_id,
            import_status=import_status,
            report_id=report_id,
            dataset_id=report_metadata.get("datasetId") or report.get("datasetId"),
            embed_url=report_metadata.get("embedUrl") or report.get("embedUrl"),
        )
    except PowerBIServiceError as exc:
        logger.warning("Power BI publish failed: %s", exc)
        _mark_project_powerbi_failed(project_id, None, "failed", str(exc))
        return PowerBIImportResult(False, str(exc), project_id, import_status="failed")
    except Exception as exc:
        logger.exception("Power BI publish failed unexpectedly")
        _mark_project_powerbi_failed(project_id, None, "failed", str(exc))
        return PowerBIImportResult(False, "Power BI 게시에 실패했습니다. 잠시 후 다시 시도하세요.", project_id, import_status="failed")


def fetch_powerbi_access_token(settings: Settings, *, session: requests.Session | None = None) -> str:
    http = session or requests.Session()
    response = http.post(
        f"https://login.microsoftonline.com/{settings.powerbi_tenant_id}/oauth2/v2.0/token",
        data={
            "client_id": settings.powerbi_client_id,
            "client_secret": settings.powerbi_client_secret,
            "grant_type": "client_credentials",
            "scope": POWERBI_SCOPE,
        },
        timeout=20,
    )
    payload = _json_response(response, "Power BI 인증에 실패했습니다.")
    token = payload.get("access_token")
    if not token:
        raise PowerBIServiceError("Power BI 인증 토큰을 확인할 수 없습니다.")
    return str(token)


def post_pbix_import(
    settings: Settings,
    access_token: str,
    pbix_bytes: bytes,
    dataset_display_name: str,
    *,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    http = session or requests.Session()
    response = http.post(
        _powerbi_url(settings, f"groups/{settings.powerbi_workspace_id}/imports"),
        headers=_auth_headers(access_token),
        params={
            "datasetDisplayName": dataset_display_name,
            "nameConflict": "Abort",
        },
        files={"file": (dataset_display_name, pbix_bytes, "application/octet-stream")},
        timeout=60,
    )
    return _json_response(response, "Power BI PBIX 업로드에 실패했습니다.")


def poll_import_completion(
    settings: Settings,
    access_token: str,
    import_id: str,
    *,
    session: requests.Session | None = None,
    progress_callback: PowerBIProgressCallback | None = None,
) -> dict[str, Any]:
    poll_seconds = max(settings.powerbi_import_poll_seconds, 1)
    deadline = time.monotonic() + poll_seconds
    latest_payload: dict[str, Any] = {}
    elapsed_seconds = 0
    while time.monotonic() <= deadline:
        latest_payload = get_import(settings, access_token, import_id, session=session)
        import_status = str(latest_payload.get("importState") or latest_payload.get("state") or "").lower()
        if import_status in IMPORT_SUCCEEDED_STATES | IMPORT_FAILED_STATES:
            return latest_payload
        remaining_seconds = max(poll_seconds - elapsed_seconds, 0)
        _notify_powerbi_progress(
            progress_callback,
            36 + int((elapsed_seconds / poll_seconds) * 8),
            f"Power BI 게시 및 배포를 기다리는 중입니다. {remaining_seconds}/{poll_seconds}초",
        )
        time.sleep(1)
        elapsed_seconds += 1
    return latest_payload


def _notify_powerbi_progress(progress_callback: PowerBIProgressCallback | None, value: int, text: str) -> None:
    if progress_callback is not None:
        progress_callback(value, text)


def get_import(
    settings: Settings,
    access_token: str,
    import_id: str,
    *,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    http = session or requests.Session()
    response = http.get(
        _powerbi_url(settings, f"groups/{settings.powerbi_workspace_id}/imports/{quote(import_id)}"),
        headers=_auth_headers(access_token),
        timeout=20,
    )
    return _json_response(response, "Power BI Import 상태 확인에 실패했습니다.")


def get_report_metadata(
    settings: Settings,
    access_token: str,
    report_id: str,
    *,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    http = session or requests.Session()
    response = http.get(
        _powerbi_url(settings, f"groups/{settings.powerbi_workspace_id}/reports/{quote(report_id)}"),
        headers=_auth_headers(access_token),
        timeout=20,
    )
    return _json_response(response, "Power BI Report 메타데이터 조회에 실패했습니다.")


def generate_embed_token(
    report_id: str,
    dataset_id: str,
    *,
    settings: Settings | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    settings = settings or get_settings()
    if not settings.is_powerbi_configured:
        raise PowerBIServiceError("Power BI 게시 환경 변수가 설정되지 않았습니다.")
    access_token = fetch_powerbi_access_token(settings, session=session)
    http = session or requests.Session()
    response = http.post(
        _powerbi_url(settings, "GenerateToken"),
        headers={**_auth_headers(access_token), "Content-Type": "application/json"},
        json={
            "datasets": [{"id": dataset_id}],
            "reports": [{"id": report_id}],
        },
        timeout=20,
    )
    return _json_response(response, "Power BI Embed Token 발급에 실패했습니다.")


def get_powerbi_embed_config(project_id: str) -> PowerBIEmbedConfig | None:
    report = get_powerbi_report_for_project(project_id)
    if not report:
        return None
    report_id = report.get("report_id")
    dataset_id = report.get("dataset_id")
    embed_url = report.get("embed_url")
    if not report_id or not dataset_id or not embed_url:
        return None
    token_payload = generate_embed_token(str(report_id), str(dataset_id))
    embed_token = token_payload.get("token")
    if not embed_token:
        raise PowerBIServiceError("Power BI Embed Token 응답을 확인할 수 없습니다.")
    return PowerBIEmbedConfig(
        report_id=str(report_id),
        dataset_id=str(dataset_id),
        embed_url=str(embed_url),
        embed_token=str(embed_token),
        token_expiration=token_payload.get("expiration"),
    )


def get_powerbi_report_for_project(project_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        raise PowerBIServiceError("Supabase 환경 변수가 설정되지 않았습니다.")
    response = (
        client.table("powerbi_reports")
        .select("*")
        .eq("project_id", project_id)
        .maybe_single()
        .execute()
    )
    return response.data or None


def delete_powerbi_report_for_project(project_id: str) -> None:
    client = get_supabase_client()
    if client is None:
        raise PowerBIServiceError("Supabase 환경 변수가 설정되지 않았습니다.")
    client.table("powerbi_reports").delete().eq("project_id", project_id).execute()
    client.table("projects").update(
        {
            "power_bi_url": None,
            "embed_status": "external_only",
            "status": PROJECT_STATUS_PUBLISHED,
        }
    ).eq("id", project_id).execute()


def upsert_powerbi_report(project_id: str, metadata: dict[str, Any]) -> None:
    client = get_supabase_client()
    if client is None:
        raise PowerBIServiceError("Supabase 환경 변수가 설정되지 않았습니다.")

    payload = {"project_id": project_id, **metadata}
    client.table("powerbi_reports").upsert(payload, on_conflict="project_id").execute()


def _mark_project_powerbi_published(project_id: str, embed_url: str | None) -> None:
    client = get_supabase_client()
    if client is None:
        raise PowerBIServiceError("Supabase 환경 변수가 설정되지 않았습니다.")
    payload = {
        "project_type": "powerbi",
        "status": PROJECT_STATUS_PUBLISHED,
        "embed_status": EMBED_STATUS_SUPPORTED if embed_url else "external_only",
        "power_bi_url": embed_url,
    }
    client.table("projects").update(payload).eq("id", project_id).execute()


def _mark_project_powerbi_processing(
    project_id: str,
    import_id: str,
    import_status: str,
    message: str,
    *,
    settings: Settings,
) -> None:
    client = get_supabase_client()
    if client is None:
        return
    client.table("projects").update(
        {
            "project_type": "powerbi",
            "status": "processing",
            "embed_status": "external_only",
        }
    ).eq("id", project_id).execute()
    client.table("powerbi_reports").upsert(
        {
            "project_id": project_id,
            "workspace_id": settings.powerbi_workspace_id,
            "import_id": import_id,
            "import_status": import_status,
            "error_message": message[:1000],
        },
        on_conflict="project_id",
    ).execute()


def _mark_project_powerbi_failed(project_id: str, import_id: str | None, import_status: str, message: str) -> None:
    client = get_supabase_client()
    if client is None:
        return
    client.table("projects").update(
        {
            "project_type": "powerbi",
            "status": PROJECT_STATUS_FAILED,
            "embed_status": "failed",
        }
    ).eq("id", project_id).execute()
    if import_id:
        client.table("powerbi_reports").upsert(
            {
                "project_id": project_id,
                "workspace_id": get_settings().powerbi_workspace_id,
                "import_id": import_id,
                "import_status": import_status,
                "error_message": message[:1000],
            },
            on_conflict="project_id",
        ).execute()


def _validate_pbix_upload(pbix_bytes: bytes, original_filename: str, max_upload_mb: int) -> None:
    if not original_filename.lower().endswith(".pbix"):
        raise PowerBIServiceError("PBIX 파일만 업로드할 수 있습니다.")
    if not pbix_bytes:
        raise PowerBIServiceError("PBIX 파일이 비어 있습니다.")
    if len(pbix_bytes) > max_upload_mb * 1024 * 1024:
        raise PowerBIServiceError(f"PBIX 파일은 최대 {max_upload_mb}MB까지 업로드할 수 있습니다.")


def _dataset_display_name(project_id: str, original_filename: str) -> str:
    safe_name = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in original_filename)
    return f"{project_id}_{int(time.time())}_{safe_name}"[:120]


def _first_report_from_import(import_payload: dict[str, Any]) -> dict[str, Any]:
    reports = import_payload.get("reports") or []
    if not reports:
        datasets = import_payload.get("datasets") or []
        if datasets and datasets[0].get("id"):
            raise PowerBIServiceError("Power BI Import는 완료됐지만 Report를 찾지 못했습니다.")
        raise PowerBIServiceError("Power BI Import 결과를 확인할 수 없습니다.")
    return reports[0]


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _powerbi_url(settings: Settings, path: str) -> str:
    return f"{settings.powerbi_api_base_url.rstrip('/')}/{path.lstrip('/')}"


def _json_response(response: requests.Response, safe_error_message: str) -> dict[str, Any]:
    if response.status_code >= 400:
        logger.warning("Power BI API returned %s: %s", response.status_code, response.text[:500])
        raise PowerBIServiceError(safe_error_message)
    try:
        payload = response.json()
    except ValueError as exc:
        raise PowerBIServiceError(safe_error_message) from exc
    if not isinstance(payload, dict):
        raise PowerBIServiceError(safe_error_message)
    return payload
