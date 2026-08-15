import os
import unittest
from unittest.mock import MagicMock, patch

from folio_app.config import (
    Settings,
    _read_bool_setting,
    _read_first_setting,
    _read_int_setting,
    _read_secret_section,
    _read_setting,
    get_settings,
)


class SettingsLoadingTests(unittest.TestCase):
    def test_environment_value_has_priority(self) -> None:
        with patch.dict(os.environ, {"FOLIO_TEST_SETTING": " from-env "}):
            with patch("folio_app.config.st.secrets", {"FOLIO_TEST_SETTING": "from-secrets"}):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING"), "from-env")

    def test_streamlit_secret_is_used_when_environment_is_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("folio_app.config.st.secrets", {"FOLIO_TEST_SETTING": " from-secrets "}):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING"), "from-secrets")

    def test_empty_environment_value_does_not_hide_streamlit_secret(self) -> None:
        with patch.dict(os.environ, {"FOLIO_TEST_SETTING": "  "}, clear=True):
            with patch("folio_app.config.st.secrets", {"FOLIO_TEST_SETTING": "from-secrets"}):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING"), "from-secrets")

    def test_default_is_used_without_local_secrets_file(self) -> None:
        missing_secrets = MagicMock()
        missing_secrets.get.side_effect = FileNotFoundError
        with patch.dict(os.environ, {}, clear=True):
            with patch("folio_app.config.st.secrets", missing_secrets):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING", "fallback"), "fallback")

    def test_publishable_key_can_fall_back_to_legacy_anon_key(self) -> None:
        with patch.dict(os.environ, {"SUPABASE_ANON_KEY": "legacy-key"}, clear=True):
            with patch("folio_app.config.st.secrets", {}):
                self.assertEqual(
                    _read_first_setting("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"),
                    "legacy-key",
                )

    def test_section_style_streamlit_secrets_are_supported(self) -> None:
        with patch(
            "folio_app.config.st.secrets",
            {"supabase": {"url": "https://example.supabase.co", "key": "section-key"}},
        ):
            self.assertEqual(_read_secret_section("supabase", "SUPABASE_URL", "url"), "https://example.supabase.co")
            self.assertEqual(_read_secret_section("supabase", "SUPABASE_KEY", "key"), "section-key")

    def test_missing_settings_names_do_not_include_secret_values(self) -> None:
        settings = Settings(
            supabase_url="",
            supabase_key="",
            app_url="http://localhost:8501",
            cookie_password="password",
            ga_measurement_id="",
        )
        self.assertEqual(
            settings.missing_supabase_settings,
            ("SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY"),
        )

    def test_password_reset_redirect_uses_reset_query(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="http://localhost:8501",
            cookie_password="password",
            ga_measurement_id="",
        )
        self.assertEqual(settings.login_redirect_url, "http://localhost:8501/?page=Login&verified=1")
        self.assertEqual(settings.password_reset_redirect_url, "http://localhost:8501/?page=Login&reset=1")

    def test_redirect_url_preserves_existing_query(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="https://example.com/app?source=email",
            cookie_password="password",
            ga_measurement_id="",
        )
        self.assertEqual(
            settings.password_reset_redirect_url,
            "https://example.com/app?source=email&page=Login&reset=1",
        )

    def test_email_notification_settings_are_optional(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="http://localhost:8501",
            cookie_password="password",
            ga_measurement_id="",
        )

        self.assertFalse(settings.is_email_notifications_configured)

    def test_email_notification_settings_require_smtp_and_service_role(self) -> None:
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_key="publishable-key",
            app_url="http://localhost:8501",
            cookie_password="password",
            ga_measurement_id="",
            supabase_service_role_key="service-role",
            smtp_host="smtp.example.com",
            smtp_from_email="noreply@example.com",
        )

        self.assertTrue(settings.is_email_notifications_configured)

    def test_int_and_bool_settings_parse_environment_values(self) -> None:
        with patch.dict(os.environ, {"SMTP_PORT": "2525", "SMTP_USE_TLS": "false"}, clear=True):
            with patch("folio_app.config.st.secrets", {}):
                self.assertEqual(_read_int_setting("SMTP_PORT", 587), 2525)
                self.assertFalse(_read_bool_setting("SMTP_USE_TLS", True))

    def test_thumbnail_capture_browser_path_is_loaded_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {"CHROME_BINARY_PATH": "/usr/bin/chromium"},
            clear=True,
        ):
            with patch("folio_app.config.st.secrets", {}):
                settings = get_settings()

        self.assertEqual(settings.chrome_binary_path, "/usr/bin/chromium")

    def test_powerbi_settings_are_loaded_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {
                "POWERBI_TENANT_ID": "tenant-id",
                "POWERBI_CLIENT_ID": "client-id",
                "POWERBI_CLIENT_SECRET": "client-secret",
                "POWERBI_WORKSPACE_ID": "workspace-id",
                "PBIX_MAX_UPLOAD_MB": "7",
                "POWERBI_IMPORT_POLL_SECONDS": "100",
                "POWERBI_CAPTURE_READY_WAIT_SECONDS": "25",
            },
            clear=True,
        ):
            with patch("folio_app.config.st.secrets", {}):
                settings = get_settings()

        self.assertTrue(settings.is_powerbi_configured)
        self.assertEqual(settings.powerbi_tenant_id, "tenant-id")
        self.assertEqual(settings.powerbi_client_id, "client-id")
        self.assertEqual(settings.powerbi_client_secret, "client-secret")
        self.assertEqual(settings.powerbi_workspace_id, "workspace-id")
        self.assertEqual(settings.pbix_max_upload_mb, 7)
        self.assertEqual(settings.powerbi_import_poll_seconds, 100)
        self.assertEqual(settings.powerbi_capture_ready_wait_seconds, 25)
