"""Internationalisation (i18n) system for Word Search Book Maker."""

from __future__ import annotations

from .locale import LocaleManager, get_language, get_translator, set_language
from .translations import TRANSLATIONS, SUPPORTED_LANGUAGES

__all__ = ["LocaleManager", "get_language", "get_translator", "set_language", "TRANSLATIONS", "SUPPORTED_LANGUAGES"]
