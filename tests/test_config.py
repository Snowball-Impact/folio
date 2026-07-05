import os
import unittest
from unittest.mock import patch

from folio_app.config import _read_first_setting, _read_setting


class SettingsLoadingTests(unittest.TestCase):
    def test_environment_value_has_priority(self) -> None:
        with patch.dict(os.environ, {"FOLIO_TEST_SETTING": " from-env "}):
            with patch("folio_app.config.st.secrets", {"FOLIO_TEST_SETTING": "from-secrets"}):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING"), "from-env")

    def test_streamlit_secret_is_used_when_environment_is_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("folio_app.config.st.secrets", {"FOLIO_TEST_SETTING": " from-secrets "}):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING"), "from-secrets")

    def test_default_is_used_without_local_secrets_file(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("folio_app.config.st.secrets.get", side_effect=FileNotFoundError):
                self.assertEqual(_read_setting("FOLIO_TEST_SETTING", "fallback"), "fallback")

    def test_publishable_key_can_fall_back_to_legacy_anon_key(self) -> None:
        with patch.dict(os.environ, {"SUPABASE_ANON_KEY": "legacy-key"}, clear=True):
            with patch("folio_app.config.st.secrets", {}):
                self.assertEqual(
                    _read_first_setting("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"),
                    "legacy-key",
                )
