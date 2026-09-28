from __future__ import annotations

import unittest

from app.i18n import LocaleManager, SUPPORTED_LANGUAGES, set_language, get_language
from app.models import AppConfig


class I18nTests(unittest.TestCase):
    def test_supported_languages(self) -> None:
        self.assertIn("en", SUPPORTED_LANGUAGES)
        self.assertIn("es", SUPPORTED_LANGUAGES)
    
    def test_language_switching(self) -> None:
        set_language("en")
        self.assertEqual(get_language(), "en")
        set_language("es")
        self.assertEqual(get_language(), "es")
    
    def test_invalid_language_fallback(self) -> None:
        set_language("invalid")
        self.assertEqual(get_language(), "en")  # Fallback to English
    
    def test_locale_manager(self) -> None:
        manager = LocaleManager("es")
        self.assertEqual(manager.get_language(), "es")
        manager.set_language("en")
        self.assertEqual(manager.get_language(), "en")
    
    def test_ui_translations(self) -> None:
        manager = LocaleManager("en")
        result = manager.ui("app_title")
        # Check that we get a string back (the translation system is working)
        self.assertIsInstance(result, str)
        result = manager.ui("ready")
        self.assertIsInstance(result, str)
        
        manager.set_language("es")
        result = manager.ui("configuration")
        self.assertIsInstance(result, str)
        result = manager.ui("ready")
        self.assertIsInstance(result, str)
    
    def test_pdf_translations(self) -> None:
        manager = LocaleManager("en")
        result = manager.pdf("word_search")
        # Check that we get a string back
        self.assertIsInstance(result, str)
        result = manager.pdf("solution")
        self.assertIsInstance(result, str)
        
        manager.set_language("es")
        result = manager.pdf("word_search")
        self.assertIsInstance(result, str)
        result = manager.pdf("solution")
        self.assertIsInstance(result, str)
    
    def test_translation_with_formatting(self) -> None:
        manager = LocaleManager("en")
        # Test that the translation system can handle formatting parameters
        result = manager.ui("csv_loaded", puzzles=5, total=20, range="3-7")
        # Just check that it returns a string and doesn't crash
        self.assertIsInstance(result, str)
    
    def test_config_language_persistence(self) -> None:
        config = AppConfig()
        self.assertEqual(config.language, "en")  # Default
        
        config.language = "es"
        self.assertEqual(config.language, "es")
        
        config_dict = config.to_dict()
        self.assertEqual(config_dict["language"], "es")
        
        loaded = AppConfig.from_dict(config_dict)
        self.assertEqual(loaded.language, "es")
    
    def test_missing_translation_key_fallback(self) -> None:
        manager = LocaleManager("en")
        # A non-existent key should return the key itself
        result = manager.ui("nonexistent_key")
        self.assertEqual(result, "nonexistent_key")


if __name__ == "__main__":
    unittest.main()
