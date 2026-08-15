from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import logging
from pathlib import Path
import shutil
import time
from typing import Any, Callable
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlsplit, urlunsplit

from folio_app.config import get_settings
from folio_app.services.project_normalizers import (
    THUMBNAIL_MODE_CAPTURE,
    normalize_optional_url,
    normalize_power_bi_embed_url,
)
from folio_app.services.supabase_client import get_supabase_client, get_supabase_service_role_client


logger = logging.getLogger(__name__)
ThumbnailProgressCallback = Callable[[int, str], None]

THUMBNAIL_WIDTH = 960
THUMBNAIL_HEIGHT = 540
THUMBNAIL_CAPTURE_TIMEOUT_SECONDS = 18
THUMBNAIL_CAPTURE_SETTLE_SECONDS = 10
THUMBNAIL_UPLOAD_MAX_BYTES = 5 * 1024 * 1024
THUMBNAIL_UPLOAD_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
CHROME_BINARY_COMMANDS = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")
CHROME_BINARY_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
)


@dataclass(frozen=True)
class ThumbnailCaptureResult:
    ok: bool
    skipped: bool = False
    url: str | None = None


def maybe_capture_project_thumbnail(
    project_id: str,
    payload: dict,
    progress_callback: ThumbnailProgressCallback | None = None,
) -> ThumbnailCaptureResult:
    if payload.get("thumbnail_mode") != THUMBNAIL_MODE_CAPTURE:
        return ThumbnailCaptureResult(ok=True, skipped=True)

    source_url = thumbnail_capture_source_url(payload)
    if source_url is None:
        return ThumbnailCaptureResult(ok=False)

    try:
        _notify(progress_callback, 45, "캡처할 화면을 여는 중입니다.")
        image_bytes = capture_thumbnail_bytes(source_url, progress_callback=progress_callback)
        _notify(progress_callback, 82, "썸네일 이미지를 업로드하는 중입니다.")
        public_url = upload_project_thumbnail(project_id, image_bytes)
        _notify(progress_callback, 92, "프로젝트에 썸네일을 연결하는 중입니다.")
        update_project_thumbnail_url(project_id, public_url)
        return ThumbnailCaptureResult(ok=True, url=public_url)
    except Exception:
        logger.exception("Failed to capture project thumbnail")
        return ThumbnailCaptureResult(ok=False)


def capture_project_thumbnail_from_html(
    project_id: str,
    document_html: str,
    progress_callback: ThumbnailProgressCallback | None = None,
) -> ThumbnailCaptureResult:
    try:
        _notify(progress_callback, 45, "캡처할 화면을 여는 중입니다.")
        image_bytes = capture_thumbnail_document_bytes(document_html, progress_callback=progress_callback)
        _notify(progress_callback, 82, "썸네일 이미지를 업로드하는 중입니다.")
        public_url = upload_project_thumbnail(project_id, image_bytes)
        _notify(progress_callback, 92, "프로젝트에 썸네일을 연결하는 중입니다.")
        update_project_thumbnail_url(project_id, public_url)
        return ThumbnailCaptureResult(ok=True, url=public_url)
    except Exception:
        logger.exception("Failed to capture project thumbnail from HTML")
        return ThumbnailCaptureResult(ok=False)


def upload_project_thumbnail_file(project_id: str, uploaded_file: Any) -> ThumbnailCaptureResult:
    try:
        image_bytes = prepare_uploaded_thumbnail_bytes(uploaded_file)
        public_url = upload_project_thumbnail(project_id, image_bytes)
        update_project_thumbnail_url(project_id, public_url)
        return ThumbnailCaptureResult(ok=True, url=public_url)
    except Exception:
        logger.exception("Failed to upload project thumbnail file")
        return ThumbnailCaptureResult(ok=False)


def prepare_uploaded_thumbnail_bytes(uploaded_file: Any) -> bytes:
    filename = str(getattr(uploaded_file, "name", "") or "")
    mime_type = str(getattr(uploaded_file, "type", "") or "")
    size = int(getattr(uploaded_file, "size", 0) or 0)
    if size > THUMBNAIL_UPLOAD_MAX_BYTES:
        raise ValueError("Thumbnail file is too large.")
    if mime_type and mime_type not in THUMBNAIL_UPLOAD_ALLOWED_TYPES:
        raise ValueError("Unsupported thumbnail file type.")

    raw_bytes = bytes(uploaded_file.getbuffer())
    if not raw_bytes:
        raise ValueError("Thumbnail file is empty.")
    if len(raw_bytes) > THUMBNAIL_UPLOAD_MAX_BYTES:
        raise ValueError("Thumbnail file is too large.")
    if filename and not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise ValueError("Unsupported thumbnail file extension.")

    from PIL import Image

    image = Image.open(BytesIO(raw_bytes))
    image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
    canvas = Image.new("RGB", (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), (245, 248, 252))
    if image.mode in {"RGBA", "LA"}:
        alpha = image.getchannel("A")
        rgb_image = image.convert("RGB")
        x = (THUMBNAIL_WIDTH - image.width) // 2
        y = (THUMBNAIL_HEIGHT - image.height) // 2
        canvas.paste(rgb_image, (x, y), alpha)
    else:
        rgb_image = image.convert("RGB")
        x = (THUMBNAIL_WIDTH - rgb_image.width) // 2
        y = (THUMBNAIL_HEIGHT - rgb_image.height) // 2
        canvas.paste(rgb_image, (x, y))

    output = BytesIO()
    canvas.save(output, format="JPEG", quality=86, optimize=True)
    return output.getvalue()


def thumbnail_capture_source_url(payload: dict) -> str | None:
    return normalize_power_bi_embed_url(payload.get("power_bi_url")) or normalize_optional_url(payload.get("report_url"))


def capture_thumbnail_bytes(url: str, progress_callback: ThumbnailProgressCallback | None = None) -> bytes:
    return _capture_thumbnail_target(_fullscreen_iframe_capture_url(url), progress_callback=progress_callback)


def capture_thumbnail_document_bytes(
    document_html: str,
    progress_callback: ThumbnailProgressCallback | None = None,
) -> bytes:
    return _capture_thumbnail_target(_document_capture_url(document_html), progress_callback=progress_callback)


def _capture_thumbnail_target(target_url: str, progress_callback: ThumbnailProgressCallback | None = None) -> bytes:
    try:
        from PIL import Image
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Thumbnail capture dependencies are not installed.") from exc

    settings = get_settings()
    with sync_playwright() as playwright:
        browser = _launch_playwright_browser(playwright, settings.chrome_binary_path)
        try:
            page = browser.new_page(
                viewport={"width": THUMBNAIL_WIDTH, "height": THUMBNAIL_HEIGHT},
                device_scale_factor=1,
            )
            page.set_default_timeout(THUMBNAIL_CAPTURE_TIMEOUT_SECONDS * 1000)
            page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=THUMBNAIL_CAPTURE_TIMEOUT_SECONDS * 1000,
            )
            try:
                page.wait_for_load_state("networkidle", timeout=7000)
            except PlaywrightTimeoutError:
                logger.info("Thumbnail capture continued before networkidle.")
            for second in range(THUMBNAIL_CAPTURE_SETTLE_SECONDS):
                progress = 50 + int(((second + 1) / THUMBNAIL_CAPTURE_SETTLE_SECONDS) * 24)
                _notify(
                    progress_callback,
                    progress,
                    f"화면을 불러오는 중입니다. {second + 1}/{THUMBNAIL_CAPTURE_SETTLE_SECONDS}초",
                )
                page.wait_for_timeout(1000)
            _notify(progress_callback, 78, "화면 이미지를 캡처하는 중입니다.")
            png_bytes = page.screenshot(type="png", full_page=False)
        finally:
            browser.close()

    image = Image.open(BytesIO(png_bytes)).convert("RGB")
    image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
    canvas = Image.new("RGB", (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), (245, 248, 252))
    x = (THUMBNAIL_WIDTH - image.width) // 2
    y = (THUMBNAIL_HEIGHT - image.height) // 2
    canvas.paste(image, (x, y))

    output = BytesIO()
    canvas.save(output, format="JPEG", quality=88, optimize=True)
    return output.getvalue()


def upload_project_thumbnail(project_id: str, image_bytes: bytes, client: Any | None = None) -> str:
    client = client or get_supabase_service_role_client() or get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase client is not configured.")

    settings = get_settings()
    bucket_name = settings.thumbnail_storage_bucket or "project-thumbnails"
    storage = client.storage
    _ensure_public_bucket(storage, bucket_name)

    path = _project_thumbnail_storage_path(project_id, int(time.time() * 1000))
    storage.from_(bucket_name).upload(
        path,
        image_bytes,
        {
            "content-type": "image/jpeg",
            "cache-control": "3600",
            "upsert": "true",
        },
    )
    return _cache_busted_url(storage.from_(bucket_name).get_public_url(path))


def delete_project_thumbnail_file(project_id: str, client: Any | None = None) -> bool:
    client = client or get_supabase_service_role_client() or get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase client is not configured.")

    settings = get_settings()
    bucket_name = settings.thumbnail_storage_bucket or "project-thumbnails"
    bucket = client.storage.from_(bucket_name)
    storage_dir = _project_thumbnail_storage_directory(project_id)
    paths = _list_project_thumbnail_paths(bucket, storage_dir) or [_project_thumbnail_storage_path(project_id)]
    bucket.remove(paths)
    return True


def try_delete_project_thumbnail_file(project_id: str) -> bool:
    try:
        return delete_project_thumbnail_file(project_id)
    except Exception:
        logger.exception("Failed to delete project thumbnail file")
        return False


def update_project_thumbnail_url(project_id: str, thumbnail_url: str) -> None:
    client = get_supabase_service_role_client() or get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase client is not configured.")
    client.table("projects").update({"thumbnail_url": thumbnail_url}).eq("id", project_id).execute()


def _resolve_chrome_binary(explicit_path: str = "") -> str | None:
    if explicit_path.strip():
        return explicit_path.strip()

    for command in CHROME_BINARY_COMMANDS:
        resolved = shutil.which(command)
        if resolved:
            return resolved

    for path in CHROME_BINARY_PATHS:
        if Path(path).exists():
            return path
    return None


def _launch_playwright_browser(playwright: Any, explicit_chrome_path: str = "") -> Any:
    launch_args = ["--disable-dev-shm-usage", "--no-sandbox"]
    managed_path = getattr(playwright.chromium, "executable_path", "")
    if managed_path and not Path(str(managed_path)).exists():
        return _launch_system_chromium(playwright, explicit_chrome_path, launch_args)
    try:
        return playwright.chromium.launch(headless=True, args=launch_args)
    except Exception as managed_exc:
        return _launch_system_chromium(playwright, explicit_chrome_path, launch_args, managed_exc=managed_exc)


def _launch_system_chromium(
    playwright: Any,
    explicit_chrome_path: str,
    launch_args: list[str],
    *,
    managed_exc: Exception | None = None,
) -> Any:
    chrome_binary = _resolve_chrome_binary(explicit_chrome_path)
    if not chrome_binary:
        if managed_exc is not None:
            raise managed_exc
        raise RuntimeError("Playwright Chromium is not installed and no system Chromium binary was found.")
    logger.info("Using system Chromium for Playwright thumbnail capture: %s.", chrome_binary)
    return playwright.chromium.launch(
        headless=True,
        executable_path=chrome_binary,
        args=launch_args,
    )


def _ensure_public_bucket(storage: object, bucket_name: str) -> None:
    try:
        storage.get_bucket(bucket_name)
    except Exception:
        storage.create_bucket(
            bucket_name,
            options={
                "public": True,
                "allowed_mime_types": ["image/jpeg"],
                "file_size_limit": "1048576",
            },
        )


def _project_thumbnail_storage_directory(project_id: str) -> str:
    return f"projects/{_safe_storage_name(project_id)}"


def _project_thumbnail_storage_path(project_id: str, version: int | None = None) -> str:
    filename = "thumbnail.jpg" if version is None else f"thumbnail-{version}.jpg"
    return f"{_project_thumbnail_storage_directory(project_id)}/{filename}"


def _list_project_thumbnail_paths(bucket: Any, storage_dir: str) -> list[str]:
    try:
        entries = bucket.list(storage_dir)
    except Exception:
        logger.exception("Failed to list project thumbnail files")
        return []
    paths = []
    for entry in entries or []:
        name = entry.get("name") if isinstance(entry, dict) else getattr(entry, "name", "")
        if str(name).startswith("thumbnail"):
            paths.append(f"{storage_dir}/{name}")
    return paths


def _cache_busted_url(url: str) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={int(time.time())}"


def _cache_busted_capture_source_url(url: str) -> str:
    parsed = urlsplit(url)
    query = parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("folio_capture_v", str(int(time.time() * 1000))))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def _safe_storage_name(value: str) -> str:
    parsed = urlparse(f"scheme://storage/{value}")
    return (parsed.path.strip("/") or "unknown").replace("\\", "_").replace("/", "_")


def _fullscreen_iframe_capture_url(url: str) -> str:
    escaped_url = _cache_busted_capture_source_url(url).replace('"', "%22")
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html, body {{
    background: #ffffff;
    height: 100%;
    margin: 0;
    overflow: hidden;
    width: 100%;
}}
iframe {{
    border: 0;
    height: 100vh;
    inset: 0;
    position: fixed;
    width: 100vw;
}}
</style>
</head>
<body>
<iframe src="{escaped_url}" allowfullscreen></iframe>
</body>
</html>"""
    return "data:text/html;charset=utf-8," + quote(html, safe="")


def _document_capture_url(document_html: str) -> str:
    return "data:text/html;charset=utf-8," + quote(document_html, safe="")


def _notify(progress_callback: ThumbnailProgressCallback | None, value: int, text: str) -> None:
    if progress_callback is not None:
        progress_callback(value, text)
