import os
import unittest
from unittest.mock import MagicMock, patch

from folio_app.config import Settings, _read_first_setting, _read_secret_section, _read_setting


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
