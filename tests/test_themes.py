from __future__ import annotations

import unittest

from app.themes import THEMES, ThemeManager, get_theme, set_theme
from app.models import AppConfig


class ThemeTests(unittest.TestCase):
    def test_available_themes(self) -> None:
        self.assertIn("light", THEMES)
        self.assertIn("dark", THEMES)
        self.assertIn("soft", THEMES)
        self.assertIn("high_contrast", THEMES)
    
    def test_theme_switching(self) -> None:
        set_theme("dark")
        self.assertEqual(get_theme(), "dark")
        set_theme("light")
        self.assertEqual(get_theme(), "light")
    
    def test_invalid_theme_fallback(self) -> None:
        set_theme("invalid")
        self.assertEqual(get_theme(), "light")  # Fallback to light
    
    def test_theme_manager(self) -> None:
        manager = ThemeManager("dark")
        self.assertEqual(manager.get_theme(), "dark")
        manager.set_theme("soft")
        self.assertEqual(manager.get_theme(), "soft")
    
    def test_theme_colors_structure(self) -> None:
        for theme_name, colors in THEMES.items():
            self.assertIn("fg_color", colors)
            self.assertIn("bg_color", colors)
            self.assertIn("button_fg_color", colors)
            self.assertIn("button_hover_color", colors)
            self.assertIn("text_color", colors)
    
    def test_config_theme_persistence(self) -> None:
        config = AppConfig()
        self.assertEqual(config.theme, "light")  # Default
        
        config.theme = "dark"
        self.assertEqual(config.theme, "dark")
        
        config_dict = config.to_dict()
        self.assertEqual(config_dict["theme"], "dark")
        
        loaded = AppConfig.from_dict(config_dict)
        self.assertEqual(loaded.theme, "dark")
    
    def test_get_theme_colors(self) -> None:
        from app.themes import get_theme_colors
        colors = get_theme_colors("dark")
        self.assertEqual(colors["fg_color"], THEMES["dark"]["fg_color"])
        
        # Test with current theme
        set_theme("soft")
        colors = get_theme_colors(None)
        self.assertEqual(colors["fg_color"], THEMES["soft"]["fg_color"])


if __name__ == "__main__":
    unittest.main()
