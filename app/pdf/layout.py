"""Cálculo de layout independiente del medio de salida.

Las unidades aquí son puntos PDF y se comparten por el renderizador vectorial y
por la previsualización rasterizada.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from app.models import AppConfig, Puzzle, word_list_rows
from app.i18n import LocaleManager


SOLUTION_COLUMNS = 2
SOLUTION_ROWS = 2
SOLUTIONS_PER_PAGE = SOLUTION_COLUMNS * SOLUTION_ROWS
SOLUTION_GUTTER = 10.0

# Global locale manager for PDF layout
_locale = LocaleManager()


def set_pdf_language(language: str) -> None:
    """Set the language for PDF layout error messages."""
    _locale.set_language(language)


@dataclass(frozen=True, slots=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def top(self) -> float:
        return self.y + self.height


@dataclass(frozen=True, slots=True)
class PageLayout:
    page_width: float
    page_height: float
    content: Rect
    grid: Rect
    cell_size: float
    title_y: float
    subtitle_y: float | None
    number_y: float | None
    words: Rect
    words_columns: int
    words_rows: int


def page_content_rect(config: AppConfig) -> Rect:
    page_width, page_height = config.page.size_points()
    top, bottom, left, right = config.page.margins.as_points(config.page.unit)
    content = Rect(left, bottom, page_width - left - right, page_height - top - bottom)
    if content.width <= 0 or content.height <= 0:
        raise ValueError(_locale.pdf("no_margin_space"))
    return content


def solution_cell_rects(config: AppConfig, occupied: int = SOLUTIONS_PER_PAGE) -> list[Rect]:
    """Rectángulos 2×2 (origen PDF abajo-izquierda) para hasta cuatro soluciones."""
    content = page_content_rect(config)
    gutter = SOLUTION_GUTTER
    cell_width = (content.width - gutter) / SOLUTION_COLUMNS
    cell_height = (content.height - gutter) / SOLUTION_ROWS
    if cell_width <= 8 or cell_height <= 8:
        raise ValueError(_locale.pdf("no_space_solution"))
    cells: list[Rect] = []
    count = max(0, min(int(occupied), SOLUTIONS_PER_PAGE))
    for index in range(count):
        column = index % SOLUTION_COLUMNS
        row_from_top = index // SOLUTION_COLUMNS
        x = content.x + column * (cell_width + gutter)
        y = content.top - (row_from_top + 1) * cell_height - row_from_top * gutter
        cells.append(Rect(x, y, cell_width, cell_height))
    return cells


def _validate_fits(content: Rect, grid_width: float, grid_height: float, words_height: float, header_height: float, spacing: float) -> None:
    required_height = header_height + grid_height + words_height + (2 * spacing if words_height else spacing)
    if required_height > content.height + 0.001:
        raise ValueError(_locale.pdf("no_space_vertical"))
    if grid_width > content.width + 0.001:
        raise ValueError(_locale.pdf("no_space_horizontal"))


def compact_layout_config(config: AppConfig, bounds: Rect) -> AppConfig:
    """Reduce tipografía y huecos lo justo para que cada solución llene su cuadrante."""
    full_content = page_content_rect(config)
    scale = min(bounds.width / max(full_content.width, 1.0), bounds.height / max(full_content.height, 1.0))
    font_scale = max(0.66, min(1.0, scale * 1.25))
    layout = replace(
        config.layout,
        title_size=max(8.0, config.layout.title_size * font_scale),
        subtitle_size=max(6.5, config.layout.subtitle_size * font_scale),
        grid_font_size=max(5.5, config.layout.grid_font_size * font_scale),
        words_font_size=max(6.0, config.layout.words_font_size * font_scale),
        spacing=max(3.0, config.layout.spacing * font_scale),
        auto_fit=True,
    )
    return replace(config, layout=layout)


def calculate_layout(puzzle: Puzzle, config: AppConfig, bounds: Rect | None = None) -> PageLayout:
    """Calcula una página (o un recuadro) sin solapamientos para abajo, arriba, izquierda o derecha."""
    set_pdf_language(config.language)
    if puzzle.grid is None:
        raise ValueError("No es posible crear un layout para una sopa sin generar.")
    page_width, page_height = config.page.size_points()
    content = bounds if bounds is not None else page_content_rect(config)
    if content.width <= 0 or content.height <= 0:
        raise ValueError("Los márgenes no dejan espacio útil en la página.")

    layout = config.layout
    rows, columns = config.grid.rows, config.grid.columns
    words = list(puzzle.words)
    word_rows = word_list_rows(len(words), layout.word_columns)
    line_height = layout.words_font_size * 1.35
    words_height = word_rows * line_height + 3
    words_width = content.width
    spacing = max(layout.spacing, 2.0)
    title_height = layout.title_size * 1.35 if layout.title else 0
    subtitle_height = layout.subtitle_size * 1.35 if layout.subtitle else 0
    number_height = layout.subtitle_size * 1.2 if layout.show_puzzle_number else 0
    header_height = title_height + subtitle_height + number_height
    if header_height:
        header_height += spacing

    position = layout.words_position.lower()
    grid_position = layout.grid_position.lower()

    def align(minimum: float, maximum: float, axis: str) -> float:
        """Alinea el origen de la cuadrícula dentro de un intervalo válido."""
        if maximum < minimum - 0.001:
            raise ValueError("No hay espacio suficiente para colocar la cuadrícula sin solapamientos.")
        if grid_position in {"izquierda", "abajo"}:
            return minimum
        if grid_position in {"derecha", "arriba"}:
            return maximum
        if grid_position == "personalizado":
            percentage = layout.custom_grid_x_percent if axis == "x" else layout.custom_grid_y_percent
            return minimum + (maximum - minimum) * (percentage / 100.0)
        return minimum + (maximum - minimum) / 2

    side_words = position in {"izquierda", "derecha"}
    if side_words:
        # La columna de palabras ocupa al menos una tercera parte, pero se adapta
        # a los textos sin rebasar el contenido.
        longest = max((len(word.text) for word in words), default=1)
        words_width = min(content.width * 0.42, max(content.width * 0.25, longest * layout.words_font_size * 0.72 + 14))
        available_width = content.width - words_width - spacing
        available_height = content.height - header_height
        maximum_cell = min(available_width / columns, available_height / rows)
        cell_size = maximum_cell if layout.auto_fit else layout.cell_size
        grid_width, grid_height = cell_size * columns, cell_size * rows
        if cell_size <= 3 or grid_width > available_width + 0.001 or grid_height > available_height + 0.001:
            raise ValueError("No hay espacio suficiente para la cuadrícula lateral con esta configuración.")
        if position == "izquierda":
            words_rect = Rect(content.x, content.y, words_width, available_height)
            available_x = content.x + words_width + spacing
        else:
            available_x = content.x
            words_rect = Rect(content.x + content.width - words_width, content.y, words_width, available_height)
        # Si no se ajusta automáticamente puede quedar espacio para alinear la
        # sopa dentro de la zona que no ocupa la lista.
        grid_x = align(available_x, available_x + available_width - grid_width, "x")
        grid_y = align(content.y, content.y + available_height - grid_height, "y")
    else:
        available_height = content.height - header_height - words_height - 2 * spacing
        maximum_cell = min(content.width / columns, available_height / rows)
        cell_size = maximum_cell if layout.auto_fit else layout.cell_size
        grid_width, grid_height = cell_size * columns, cell_size * rows
        if cell_size <= 3:
            raise ValueError("No hay espacio suficiente para la cuadrícula; reduzca el contenido o los márgenes.")
        _validate_fits(content, grid_width, grid_height, words_height, header_height, spacing)
        if position == "arriba":
            words_rect = Rect(content.x, content.top - header_height - words_height, words_width, words_height)
            grid_min_y = content.y
            grid_max_y = words_rect.y - spacing - grid_height
        else:  # abajo y cualquier valor no lateral
            words_rect = Rect(content.x, content.y, words_width, words_height)
            grid_min_y = words_rect.top + spacing
            grid_max_y = content.top - header_height - grid_height
        grid_x = align(content.x, content.x + content.width - grid_width, "x")
        grid_y = align(grid_min_y, grid_max_y, "y")

    header_top = content.top
    title_y = header_top - layout.title_size if layout.title else header_top
    subtitle_y = title_y - title_height - 1 if layout.subtitle else None
    number_y = (subtitle_y - subtitle_height - 1 if subtitle_y is not None else title_y - number_height - 1) if layout.show_puzzle_number else None
    return PageLayout(
        page_width=page_width, page_height=page_height, content=content,
        grid=Rect(grid_x, grid_y, grid_width, grid_height), cell_size=cell_size,
        title_y=title_y, subtitle_y=subtitle_y, number_y=number_y,
        words=words_rect, words_columns=layout.word_columns, words_rows=word_rows,
    )
