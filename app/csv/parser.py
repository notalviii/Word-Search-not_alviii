"""Lectura estricta de CSV, normalización Unicode y trazabilidad de errores."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from app.models import Puzzle, PuzzleBook, ValidationError, Word


@dataclass(slots=True)
class CsvImportResult:
    book: PuzzleBook | None
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.book is not None and not self.errors


def normalize_word(value: str) -> str:
    """Conserva acentos, Ñ y Ü: strip + upper no elimina información Unicode."""
    return value.strip().upper()


def _read_rows(path: Path) -> tuple[list[tuple[int, list[str]]], list[ValidationError]]:
    """Lee el CSV con pandas y conserva el número físico de cada línea.

    El módulo csv se usa para identificar los campos de cada registro; pandas se
    emplea como lectura/validación adicional y devuelve errores de formato más
    útiles para CSV de ancho irregular.
    """
    errors: list[ValidationError] = []
    raw_text: str | None = None
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            raw_text = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            return [], [ValidationError(f"No se pudo leer el archivo: {exc}")]
    if raw_text is None:
        return [], [ValidationError("El archivo no está codificado en UTF-8 o UTF-8 con BOM.")]
    if not raw_text.strip():
        return [], [ValidationError("El archivo CSV está vacío.")]

    try:
        parsed = list(csv.reader(io.StringIO(raw_text, newline=""), strict=True))
    except csv.Error as exc:
        return [], [ValidationError(f"Formato CSV incorrecto: {exc}")]
    try:
        # pandas valida/normaliza la tabla en memoria sin imponer un mismo número
        # de columnas: el formato admite deliberadamente distintas cantidades de
        # palabras en cada sopa.
        pd.DataFrame(parsed, dtype="string")
    except (TypeError, ValueError) as exc:
        return [], [ValidationError(f"Formato CSV incorrecto: {exc}")]
    return list(enumerate(parsed, start=1)), errors


def import_csv(path: str | Path) -> CsvImportResult:
    source = Path(path)
    if not source.exists() or not source.is_file():
        return CsvImportResult(None, [ValidationError("El archivo seleccionado no existe.")])

    rows, errors = _read_rows(source)
    if errors:
        return CsvImportResult(None, errors)

    puzzles: list[Puzzle] = []
    for line_number, fields in rows:
        # Una línea en blanco llega como [] con csv.reader.
        if not fields or (len(fields) == 1 and not fields[0].strip()):
            errors.append(ValidationError("La línea está vacía.", line=line_number))
            continue
        words: list[Word] = []
        seen: set[str] = set()
        for column, raw_word in enumerate(fields, start=1):
            normalized = normalize_word(raw_word)
            if not normalized:
                errors.append(ValidationError("Hay una palabra vacía o una coma adicional.", line=line_number, field=f"columna {column}"))
                continue
            if normalized in seen:
                errors.append(ValidationError("La palabra está duplicada dentro de la sopa.", line=line_number, word=normalized))
                continue
            seen.add(normalized)
            words.append(Word(normalized, source_line=line_number, source_column=column))
        if words:
            puzzles.append(Puzzle(number=len(puzzles) + 1, words=words, source_line=line_number))

    if not puzzles and not errors:
        errors.append(ValidationError("El CSV no contiene líneas válidas."))
    if errors:
        return CsvImportResult(None, errors)
    return CsvImportResult(PuzzleBook(puzzles=puzzles, source_path=str(source)))
