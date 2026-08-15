import unittest
from io import BytesIO
from unittest.mock import ANY, patch
from types import SimpleNamespace

from PIL import Image

from folio_app.services.project_thumbnails import (
    ThumbnailCaptureResult,
    _cache_busted_capture_source_url,
    _cache_busted_url,
    _fullscreen_iframe_capture_url,
    _launch_playwright_browser,
    _project_thumbnail_storage_path,
    _resolve_chrome_binary,
    delete_project_thumbnail_file,
    maybe_capture_project_thumbnail,
    prepare_uploaded_thumbnail_bytes,
    thumbnail_capture_source_url,
    try_delete_project_thumbnail_file,
)


class ProjectThumbnailTests(unittest.TestCase):
    def test_capture_source_prefers_embed_url(self) -> None:
        self.assertEqual(
            thumbnail_capture_source_url(
                {
                    "power_bi_url": '<iframe src="https://example.com/embed"></iframe>',
                    "report_url": "https://example.com/report",
                }
            ),
            "https://example.com/embed",
        )

    def test_capture_source_falls_back_to_report_url(self) -> None:
        self.assertEqual(
            thumbnail_capture_source_url({"power_bi_url": "", "report_url": "https://example.com/report"}),
            "https://example.com/report",
        )

    def test_fullscreen_iframe_capture_url_wraps_target(self) -> None:
        with patch("folio_app.services.project_thumbnails.time.time", return_value=12345.678):
            wrapped = _fullscreen_iframe_capture_url("https://example.com/embed?x=1&y=2")

        self.assertTrue(wrapped.startswith("data:text/html;charset=utf-8,"))
        self.assertIn("iframe", wrapped)
        self.assertIn("100vw", wrapped)
        self.assertIn("100vh", wrapped)
        self.assertIn("https%3A%2F%2Fexample.com%2Fembed%3Fx%3D1%26y%3D2%26folio_capture_v%3D12345678", wrapped)

    def test_chrome_binary_prefers_explicit_path(self) -> None:
        with patch("folio_app.services.project_thumbnails.shutil.which", return_value="/usr/bin/chromium"):
            self.assertEqual(_resolve_chrome_binary(" /custom/chrome "), "/custom/chrome")

    def test_chrome_binary_uses_path_lookup(self) -> None:
        with patch("folio_app.services.project_thumbnails.shutil.which", return_value="/usr/bin/chromium"):
            self.assertEqual(_resolve_chrome_binary(), "/usr/bin/chromium")

    @patch("folio_app.services.project_thumbnails.Path.exists", return_value=True)
    def test_playwright_launch_prefers_managed_chromium(self, _exists) -> None:
        chromium = SimpleNamespace(executable_path="/playwright/chromium", launch=lambda **kwargs: {"kwargs": kwargs})
        playwright = SimpleNamespace(chromium=chromium)

        browser = _launch_playwright_browser(playwright, "/usr/bin/chromium")

        self.assertNotIn("executable_path", browser["kwargs"])

    @patch("folio_app.services.project_thumbnails.Path.exists", return_value=False)
    def test_playwright_launch_falls_back_to_system_chromium_without_managed_launch(self, _exists) -> None:
        calls = []

        def launch(**kwargs):
            calls.append(kwargs)
            return {"kwargs": kwargs}

        playwright = SimpleNamespace(chromium=SimpleNamespace(executable_path="/missing/chromium", launch=launch))

        browser = _launch_playwright_browser(playwright, " /usr/bin/chromium ")

        self.assertEqual(len(calls), 1)
        self.assertEqual(browser["kwargs"]["executable_path"], "/usr/bin/chromium")

    def test_project_thumbnail_storage_path_is_deterministic(self) -> None:
        self.assertEqual(
            _project_thumbnail_storage_path("project/id"),
            "projects/project_id/thumbnail.jpg",
        )
        self.assertEqual(
            _project_thumbnail_storage_path("project/id", 12345),
            "projects/project_id/thumbnail-12345.jpg",
        )

    @patch("folio_app.services.project_thumbnails.time.time", return_value=12345)
    def test_cache_busted_url_adds_capture_version(self, _time) -> None:
        self.assertEqual(_cache_busted_url("https://cdn.example.com/thumb.jpg"), "https://cdn.example.com/thumb.jpg?v=12345")
        self.assertEqual(
            _cache_busted_url("https://cdn.example.com/thumb.jpg?token=abc"),
            "https://cdn.example.com/thumb.jpg?token=abc&v=12345",
        )

    @patch("folio_app.services.project_thumbnails.time.time", return_value=12345.678)
    def test_cache_busted_capture_source_url_preserves_existing_query(self, _time) -> None:
        self.assertEqual(
            _cache_busted_capture_source_url("https://example.com/embed?x=1#view"),
            "https://example.com/embed?x=1&folio_capture_v=12345678#view",
        )

    def test_non_capture_mode_is_skipped(self) -> None:
        result = maybe_capture_project_thumbnail("project-id", {"thumbnail_mode": "auto_cover"})

        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    def test_prepare_uploaded_thumbnail_converts_image_to_optimized_jpeg(self) -> None:
        source = BytesIO()
        Image.new("RGB", (1200, 800), (20, 80, 140)).save(source, format="PNG")
        uploaded_file = SimpleNamespace(
            name="thumb.png",
            type="image/png",
            size=len(source.getvalue()),
            getbuffer=lambda: source.getvalue(),
        )

        result = prepare_uploaded_thumbnail_bytes(uploaded_file)

        with Image.open(BytesIO(result)) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(image.size, (960, 540))

    @patch("folio_app.services.project_thumbnails.update_project_thumbnail_url")
    @patch("folio_app.services.project_thumbnails.upload_project_thumbnail", return_value="https://cdn.example.com/thumb.jpg")
    @patch("folio_app.services.project_thumbnails.capture_thumbnail_bytes", return_value=b"image")
    def test_capture_uploads_and_updates_project(self, capture_bytes, upload, update) -> None:
        progress_events = []
        result = maybe_capture_project_thumbnail(
            "project-id",
            {"thumbnail_mode": "capture", "power_bi_url": "https://example.com/embed"},
            progress_callback=lambda value, text: progress_events.append((value, text)),
        )

        self.assertEqual(result, ThumbnailCaptureResult(ok=True, url="https://cdn.example.com/thumb.jpg"))
        capture_bytes.assert_called_once_with(
            "https://example.com/embed",
            progress_callback=ANY,
        )
        upload.assert_called_once_with("project-id", b"image")
        update.assert_called_once_with("project-id", "https://cdn.example.com/thumb.jpg")
        self.assertIn((45, "캡처할 화면을 여는 중입니다."), progress_events)
        self.assertIn((82, "썸네일 이미지를 업로드하는 중입니다."), progress_events)

    @patch("folio_app.services.project_thumbnails.capture_thumbnail_bytes", side_effect=RuntimeError("browser"))
    def test_capture_failure_is_reported_without_raising(self, _capture_bytes) -> None:
        result = maybe_capture_project_thumbnail(
            "project-id",
            {"thumbnail_mode": "capture", "power_bi_url": "https://example.com/embed"},
        )

        self.assertFalse(result.ok)
        self.assertFalse(result.skipped)

    @patch("folio_app.services.project_thumbnails.get_settings")
    def test_delete_project_thumbnail_removes_all_thumbnail_files(self, get_settings) -> None:
        class StorageBucket:
            def __init__(self) -> None:
                self.removed = []

            def list(self, path):
                self.listed_path = path
                return [
                    {"name": "thumbnail-111.jpg"},
                    {"name": "thumbnail-222.jpg"},
                    {"name": "notes.txt"},
                ]

            def remove(self, paths):
                self.removed.extend(paths)

        class Storage:
            def __init__(self) -> None:
                self.bucket = StorageBucket()
                self.bucket_name = ""

            def from_(self, bucket_name):
                self.bucket_name = bucket_name
                return self.bucket

        class Client:
            def __init__(self) -> None:
                self.storage = Storage()

        client = Client()
        get_settings.return_value.thumbnail_storage_bucket = "project-thumbnails"

        self.assertTrue(delete_project_thumbnail_file("project-id", client=client))
        self.assertEqual(client.storage.bucket_name, "project-thumbnails")
        self.assertEqual(client.storage.bucket.listed_path, "projects/project-id")
        self.assertEqual(
            client.storage.bucket.removed,
            ["projects/project-id/thumbnail-111.jpg", "projects/project-id/thumbnail-222.jpg"],
        )

    @patch("folio_app.services.project_thumbnails.delete_project_thumbnail_file", side_effect=RuntimeError("storage"))
    def test_try_delete_project_thumbnail_file_reports_failure(self, _delete) -> None:
        self.assertFalse(try_delete_project_thumbnail_file("project-id"))


if __name__ == "__main__":
    unittest.main()
