"""Theme definitions and manager for Word Search Book Maker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

import customtkinter as ctk


class ThemeColors(TypedDict):
    """Color scheme for a theme."""
    fg_color: str
    bg_color: str
    button_fg_color: str
    button_hover_color: str
    entry_fg_color: str
    entry_border_color: str
    text_color: str
    scrollbar_button_color: str
    scrollbar_button_hover_color: str
    progress_bar_color: str


THEMES: dict[str, ThemeColors] = {
    "light": {
        "fg_color": "#f0f0f0",
        "bg_color": "#ffffff",
        "button_fg_color": "#1a6dff",
        "button_hover_color": "#1555cc",
        "entry_fg_color": "#ffffff",
        "entry_border_color": "#a0a0a0",
        "text_color": "#000000",
        "scrollbar_button_color": "#c0c0c0",
        "scrollbar_button_hover_color": "#a0a0a0",
        "progress_bar_color": "#1a6dff",
    },
    "dark": {
        "fg_color": "#2b2b2b",
        "bg_color": "#1a1a1a",
        "button_fg_color": "#3d8bff",
        "button_hover_color": "#2d6fd9",
        "entry_fg_color": "#3a3a3a",
        "entry_border_color": "#555555",
        "text_color": "#ffffff",
        "scrollbar_button_color": "#404040",
        "scrollbar_button_hover_color": "#505050",
        "progress_bar_color": "#3d8bff",
    },
    "soft": {
        "fg_color": "#f5f5f0",
        "bg_color": "#fafaf8",
        "button_fg_color": "#7cb342",
        "button_hover_color": "#689f38",
        "entry_fg_color": "#ffffff",
        "entry_border_color": "#c0c0b0",
        "text_color": "#333333",
        "scrollbar_button_color": "#e0e0d8",
        "scrollbar_button_hover_color": "#d0d0c8",
        "progress_bar_color": "#7cb342",
    },
    "high_contrast": {
        "fg_color": "#000000",
        "bg_color": "#ffffff",
        "button_fg_color": "#000000",
        "button_hover_color": "#333333",
        "entry_fg_color": "#ffffff",
        "entry_border_color": "#000000",
        "text_color": "#000000",
        "scrollbar_button_color": "#000000",
        "scrollbar_button_hover_color": "#333333",
        "progress_bar_color": "#000000",
    },
}

_current_theme: str = "light"


def set_theme(theme_name: str) -> None:
    """Set the current theme."""
    global _current_theme
    if theme_name not in THEMES:
        theme_name = "light"  # Fallback
    _current_theme = theme_name


def get_theme() -> str:
    """Get the current theme name."""
    return _current_theme


def get_theme_colors(theme_name: str | None = None) -> ThemeColors:
    """Get the color scheme for a theme."""
    name = theme_name or _current_theme
    return THEMES.get(name, THEMES["light"])


def apply_theme(theme_name: str, root: ctk.CTk) -> None:
    """Apply a theme to the application root."""
    set_theme(theme_name)
    colors = get_theme_colors(theme_name)
    
    # CustomTkinter doesn't support full custom color schemes directly,
    # so we set appearance mode and use the closest built-in theme
    if theme_name == "dark":
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
    elif theme_name == "high_contrast":
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    else:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    
    # Note: CustomTkinter has limited theme customization capabilities.
    # For full custom theming, we would need to manually set colors on each widget.
    # This is a simplified approach that uses the built-in theme system.


class ThemeManager:
    """Manages theme settings and application."""
    
    def __init__(self, theme: str = "light") -> None:
        self.set_theme(theme)
    
    def set_theme(self, theme: str) -> None:
        """Set the theme."""
        set_theme(theme)
    
    def get_theme(self) -> str:
        """Get the current theme."""
        return get_theme()
    
    def get_colors(self) -> ThemeColors:
        """Get the current theme colors."""
        return get_theme_colors()
    
    def apply_to_app(self, root: ctk.CTk) -> None:
        """Apply the current theme to the application."""
        apply_theme(self.get_theme(), root)
