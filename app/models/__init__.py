"""Modelos de dominio independientes de la interfaz."""

from .domain import (
    AppConfig,
    Coordinate,
    ExportConfig,
    GenerationResult,
    GridConfig,
    LayoutConfig,
    MarginConfig,
    PageConfig,
    PAGE_PRESETS,
    Puzzle,
    PuzzleBook,
    ValidationError,
    Word,
    WordPlacement,
    word_list_rows,
)

__all__ = [
    "AppConfig", "Coordinate", "ExportConfig", "GenerationResult", "GridConfig", "PAGE_PRESETS",
    "LayoutConfig", "MarginConfig", "PageConfig", "Puzzle", "PuzzleBook",
    "ValidationError", "Word", "WordPlacement",
    "word_list_rows",
]
