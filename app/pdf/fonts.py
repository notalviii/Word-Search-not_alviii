"""Resolución de fuentes para PDF y previsualización.

Usa las fuentes TrueType del sistema (Windows) cuando existen, de modo que
queden incrustadas en el PDF. Si un archivo no está disponible, se usa un
equivalente estándar de PDF (Helvetica, Times-Roman, Courier) que no requiere
redistribuir tipografías con restricciones de licencia.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Nombre interno (guardado en JSON) → etiqueta de interfaz.
FONT_CHOICES: tuple[tuple[str, str], ...] = (
    ("Arial", "Arial"),
    ("Times New Roman", "Times New Roman"),
    ("Courier New", "Courier New"),
    ("Georgia", "Georgia"),
    ("Verdana", "Verdana"),
    ("Helvetica", "Helvetica"),
)

FONT_OPTION_NAMES: tuple[str, ...] = tuple(name for name, _ in FONT_CHOICES)

_STANDARD_FALLBACK: dict[str, str] = {
    "Arial": "Helvetica",
    "Times New Roman": "Times-Roman",
    "Courier New": "Courier",
    "Georgia": "Times-Roman",
    "Verdana": "Helvetica",
    "Helvetica": "Helvetica",
}

_FILE_CANDIDATES: dict[str, tuple[str, ...]] = {
    "Arial": ("arial.ttf", "Arial.ttf", "arial.TTF"),
    "Times New Roman": ("times.ttf", "Times New Roman.ttf", "times.TTF"),
    "Courier New": ("cour.ttf", "cour.TTF", "Courier New.ttf"),
    "Georgia": ("georgia.ttf", "Georgia.ttf", "georgia.TTF"),
    "Verdana": ("verdana.ttf", "Verdana.ttf", "verdana.TTF"),
}

_registered: dict[str, str] = {}


def _font_search_dirs() -> list[Path]:
    directories: list[Path] = []
    windir = os.environ.get("WINDIR") or os.environ.get("SystemRoot")
    if windir:
        directories.append(Path(windir) / "Fonts")
    if sys.platform == "darwin":
        directories.extend([Path("/Library/Fonts"), Path("/System/Library/Fonts")])
    else:
        directories.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
            ]
        )
    return directories


def find_system_font_file(font_name: str) -> Path | None:
    names = _FILE_CANDIDATES.get(font_name, ())
    if not names:
        return None
    for directory in _font_search_dirs():
        if not directory.is_dir():
            continue
        for filename in names:
            candidate = directory / filename
            if candidate.is_file():
                return candidate
        try:
            by_lower = {item.name.lower(): item for item in directory.iterdir() if item.is_file()}
        except OSError:
            continue
        for filename in names:
            match = by_lower.get(filename.lower())
            if match is not None:
                return match
    return None


def resolve_pdf_font(font_name: str) -> str:
    """Devuelve el nombre de fuente registrado en ReportLab, incrustando TTF si es posible."""
    requested = font_name if font_name in FONT_OPTION_NAMES else "Helvetica"
    cached = _registered.get(requested)
    if cached:
        return cached
    path = find_system_font_file(requested)
    if path is not None:
        internal = f"KDP-{requested.replace(' ', '')}"
        if internal not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(internal, str(path)))
        _registered[requested] = internal
        return internal
    fallback = _STANDARD_FALLBACK.get(requested, "Helvetica")
    _registered[requested] = fallback
    return fallback


@lru_cache(maxsize=16)
def resolve_preview_font_path(font_name: str) -> str | None:
    path = find_system_font_file(font_name if font_name in FONT_OPTION_NAMES else "Arial")
    return str(path) if path is not None else None
