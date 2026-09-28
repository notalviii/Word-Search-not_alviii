"""Locale manager for handling language switching and translations."""

from __future__ import annotations

from typing import Callable

from .translations import SUPPORTED_LANGUAGES, TRANSLATIONS, Translations


_current_language: str = "en"


def set_language(language: str) -> None:
    """Set the current language for the application."""
    global _current_language
    if language not in SUPPORTED_LANGUAGES:
        language = "en"  # Fallback to English
    _current_language = language


def get_language() -> str:
    """Get the current language."""
    return _current_language


def get_translations() -> Translations:
    """Get the translation dictionary for the current language."""
    return TRANSLATIONS.get(_current_language, TRANSLATIONS["en"])


def get_translator(category: str) -> Callable[[str], str]:
    """Get a translation function for a specific category (ui or pdf)."""
    
    def translate(key: str, **kwargs: object) -> str:
        """Translate a key using the current language and format with kwargs."""
        translations = get_translations()
        try:
            category_dict = translations[category]  # type: ignore[index]
            text = category_dict[key]  # type: ignore[index]
        except (KeyError, TypeError):
            # Fallback to English if key not found
            try:
                category_dict = TRANSLATIONS["en"][category]  # type: ignore[index]
                text = category_dict[key]  # type: ignore[index]
            except (KeyError, TypeError):
                return key  # Ultimate fallback: return the key itself
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text
    
    return translate


class LocaleManager:
    """Manages locale settings and provides translation access."""
    
    def __init__(self, language: str = "en") -> None:
        self.set_language(language)
    
    def set_language(self, language: str) -> None:
        """Set the language."""
        set_language(language)
    
    def get_language(self) -> str:
        """Get the current language."""
        return get_language()
    
    def ui(self, key: str, **kwargs: object) -> str:
        """Get a UI translation."""
        return get_translator("ui")(key, **kwargs)
    
    def pdf(self, key: str, **kwargs: object) -> str:
        """Get a PDF translation."""
        return get_translator("pdf")(key, **kwargs)
