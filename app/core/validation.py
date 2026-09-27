"""Validación previa de configuración y exportación."""

from __future__ import annotations

from app.models import AppConfig, Puzzle, ValidationError
from app.pdf.fonts import FONT_OPTION_NAMES
from .generator import validate_generated_puzzle


def validate_app_config(config: AppConfig, puzzles: list[Puzzle] | None = None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    page = config.page
    if page.unit not in {"mm", "in"}:
        errors.append(ValidationError("La unidad de página debe ser mm o in.", field="unidad"))
    if page.width <= 0 or page.height <= 0:
        errors.append(ValidationError("El ancho y el alto de página deben ser positivos.", field="página"))
    if any(value < 0 for value in (page.margins.top, page.margins.bottom, page.margins.left, page.margins.right)):
        errors.append(ValidationError("Los márgenes no pueden ser negativos.", field="márgenes"))
    width_points, height_points = page.size_points()
    top, bottom, left, right = page.margins.as_points(page.unit)
    if left + right >= width_points or top + bottom >= height_points:
        errors.append(ValidationError("Los márgenes no dejan área útil en la página.", field="márgenes"))
    grid = config.grid
    if grid.rows < 2 or grid.columns < 2:
        errors.append(ValidationError("La cuadrícula debe tener, como mínimo, 2 × 2.", field="cuadrícula"))
    if not grid.direction_steps():
        errors.append(ValidationError("Active al menos una dirección.", field="direcciones"))
    if config.layout.word_columns < 1:
        errors.append(ValidationError("La lista de palabras necesita al menos una columna.", field="columnas de palabras"))
    if config.layout.grid_position not in {"centro", "arriba", "abajo", "izquierda", "derecha", "personalizado"}:
        errors.append(ValidationError("La posición de la sopa no es válida.", field="posición de sopa"))
    if not (0 <= config.layout.custom_grid_x_percent <= 100 and 0 <= config.layout.custom_grid_y_percent <= 100):
        errors.append(ValidationError("Las coordenadas personalizadas deben estar entre 0 y 100 %.", field="posición personalizada"))
    if config.layout.cell_size <= 0 or config.layout.grid_font_size <= 0:
        errors.append(ValidationError("Los tamaños de cuadrícula y fuente deben ser positivos.", field="diseño"))
    if config.layout.font_name not in FONT_OPTION_NAMES:
        errors.append(ValidationError("La fuente seleccionada no es válida.", field="fuente"))
    if config.export.solution_style not in {"círculo", "línea", "resaltado"}:
        errors.append(ValidationError("El estilo de solución no es válido.", field="soluciones"))
    if config.export.order_mode not in {"consecutivo", "soluciones_al_final"}:
        errors.append(ValidationError("El orden de exportación no es válido.", field="exportación"))
    for puzzle in puzzles or []:
        errors.extend(validate_generated_puzzle(puzzle))
    return errors
