from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.models import AppConfig
from app.utils import load_config, save_config


class BackwardsCompatibilityTests(unittest.TestCase):
    def test_old_config_without_language_theme_loads(self) -> None:
        """Test that old config files without language/theme fields load with defaults."""
        old_config_dict = {
            "page": {
                "width": 210.0,
                "height": 297.0,
                "unit": "mm",
                "preset": "A4",
                "margins": {"top": 15.0, "bottom": 15.0, "left": 15.0, "right": 15.0}
            },
            "grid": {
                "rows": 15,
                "columns": 15,
                "directions": {
                    "derecha": True,
                    "izquierda": False,
                    "abajo": True,
                    "arriba": False,
                    "diagonal_descendente": True,
                    "diagonal_ascendente": True,
                    "diagonal_descendente_inversa": False,
                    "diagonal_ascendente_inversa": False
                },
                "allow_reversed": False,
                "allow_diagonals": True,
                "allow_intersections": True,
                "max_attempts": 120
            },
            "layout": {
                "title": "Sopa de letras",
                "subtitle": "Encuentra todas las palabras",
                "show_puzzle_number": True,
                "grid_position": "centro",
                "custom_grid_x_percent": 50.0,
                "custom_grid_y_percent": 50.0,
                "words_position": "abajo",
                "font_name": "Arial",
                "title_size": 18.0,
                "subtitle_size": 10.0,
                "grid_font_size": 11.0,
                "words_font_size": 9.0,
                "word_columns": 3,
                "word_order": "original",
                "cell_size": 18.0,
                "line_width": 0.6,
                "spacing": 8.0,
                "auto_fit": True
            },
            "export": {
                "include_solutions": True,
                "order_mode": "consecutivo",
                "solution_style": "círculo",
                "output_path": "output/libro_sopas.pdf",
                "selected_puzzles": "todas"
            }
        }
        
        config = AppConfig.from_dict(old_config_dict)
        
        # Check that new fields have defaults
        self.assertEqual(config.language, "en")
        self.assertEqual(config.theme, "light")
        
        # Check that old fields are preserved
        self.assertEqual(config.page.width, 210.0)
        self.assertEqual(config.grid.rows, 15)
        self.assertEqual(config.layout.title, "Sopa de letras")
    
    def test_config_round_trip_preserves_all_fields(self) -> None:
        """Test that saving and loading preserves all fields including new ones."""
        config = AppConfig()
        config.language = "es"
        config.theme = "dark"
        config.grid.prefer_spacing = False
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            save_config(config, path)
            loaded = load_config(path)
        
        self.assertEqual(loaded.language, "es")
        self.assertEqual(loaded.theme, "dark")
        self.assertEqual(loaded.grid.prefer_spacing, False)
    
    def test_config_with_new_fields_only(self) -> None:
        """Test that a config with only new fields uses defaults for old fields."""
        new_config_dict = {
            "language": "es",
            "theme": "dark"
        }
        
        config = AppConfig.from_dict(new_config_dict)
        
        self.assertEqual(config.language, "es")
        self.assertEqual(config.theme, "dark")
        
        # Old fields should have defaults
        self.assertEqual(config.page.width, 210.0)
        self.assertEqual(config.grid.rows, 15)
        self.assertEqual(config.layout.title, "Sopa de letras")
    
    def test_partial_config_merges_with_defaults(self) -> None:
        """Test that partial config merges with defaults correctly."""
        partial_config = {
            "page": {"width": 200.0},
            "language": "es"
        }
        
        config = AppConfig.from_dict(partial_config)
        
        self.assertEqual(config.page.width, 200.0)
        self.assertEqual(config.page.height, 297.0)  # Default
        self.assertEqual(config.language, "es")
        self.assertEqual(config.theme, "light")  # Default


if __name__ == "__main__":
    unittest.main()
