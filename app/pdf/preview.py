"""Previsualización Pillow que utiliza las mismas geometrías de layout."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from app.models import AppConfig, Puzzle
from .fonts import resolve_preview_font_path
from .layout import PageLayout, calculate_layout


def _font(size: int, bold: bool = False, font_name: str = "Arial") -> ImageFont.ImageFont:
    size = max(1, int(size))
    path = resolve_preview_font_path(font_name)
    candidates: list[str] = []
    if path:
        candidates.append(path)
    candidates.extend(["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"])
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _point(value: float, scale: float) -> int:
    return round(value * scale)


def render_preview(puzzle: Puzzle, config: AppConfig, solution: bool = False, max_width: int = 900) -> Image.Image:
    """Rasteriza una página para el widget, sin alterar modelos ni posiciones."""
    page = calculate_layout(puzzle, config)
    scale = min(max_width / page.page_width, 1.8)
    image = Image.new("RGB", (_point(page.page_width, scale), _point(page.page_height, scale)), "white")
    draw = ImageDraw.Draw(image, "RGBA")
    # Convierte origen PDF (abajo) a origen Pillow (arriba).
    def xy(x: float, y: float) -> tuple[int, int]:
        return _point(x, scale), _point(page.page_height - y, scale)

    font_name = config.layout.font_name
    title_font = _font(max(8, _point(config.layout.title_size, scale)), True, font_name)
    text_font = _font(max(7, _point(config.layout.subtitle_size, scale)), False, font_name)
    grid_font_size = max(6, _point(min(config.layout.grid_font_size, page.cell_size * 0.62), scale))
    grid_font = _font(grid_font_size, True, font_name)
    words_font = _font(max(6, _point(config.layout.words_font_size, scale)), False, font_name)
    center_x = page.content.x + page.content.width / 2
    if config.layout.title:
        draw.text(xy(center_x, page.title_y), config.layout.title, fill="black", font=title_font, anchor="ms")
    if config.layout.subtitle and page.subtitle_y is not None:
        draw.text(xy(center_x, page.subtitle_y), config.layout.subtitle, fill="black", font=text_font, anchor="ms")
    if page.number_y is not None:
        number = f"{'Solución — ' if solution else ''}Sopa {puzzle.number}"
        draw.text(xy(center_x, page.number_y), number, fill="black", font=text_font, anchor="ms")
    # Grid lines and letters.
    for row in range(config.grid.rows + 1):
        y = page.grid.y + row * page.cell_size
        draw.line([xy(page.grid.x, y), xy(page.grid.x + page.grid.width, y)], fill="black", width=max(1, _point(config.layout.line_width, scale)))
    for col in range(config.grid.columns + 1):
        x = page.grid.x + col * page.cell_size
        draw.line([xy(x, page.grid.y), xy(x, page.grid.y + page.grid.height)], fill="black", width=max(1, _point(config.layout.line_width, scale)))
    assert puzzle.grid is not None
    for row in range(config.grid.rows):
        for col in range(config.grid.columns):
            x = page.grid.x + (col + .5) * page.cell_size
            y = page.grid.y + (config.grid.rows - row - .5) * page.cell_size
            draw.text(xy(x, y), puzzle.grid[row][col], fill="black", font=grid_font, anchor="mm")
    if solution:
        for placement in puzzle.placements:
            points = [xy(page.grid.x + (coord.column + .5) * page.cell_size, page.grid.y + (config.grid.rows - coord.row - .5) * page.cell_size) for coord in placement.coordinates]
            if config.export.solution_style == "resaltado":
                draw.line(points, fill=(255, 207, 0, 125), width=max(3, _point(page.cell_size * .68, scale)))
            elif config.export.solution_style == "línea":
                draw.line([points[0], points[-1]], fill="#d22c2c", width=max(2, _point(page.cell_size * .11, scale)))
            else:
                radius = _point(page.cell_size * .41, scale)
                for x, y in points:
                    draw.ellipse([x - radius, y - radius, x + radius, y + radius], outline="#d22c2c", width=max(1, _point(page.cell_size * .08, scale)))
    _draw_preview_words(draw, xy, puzzle, page, config, words_font, scale)
    return image


def _draw_preview_words(
    draw: ImageDraw.ImageDraw,
    xy,
    puzzle: Puzzle,
    page: PageLayout,
    config: AppConfig,
    words_font: ImageFont.ImageFont,
    scale: float,
) -> None:
    words = [word.text for word in puzzle.words]
    if config.layout.word_order == "alfabetico":
        words.sort()
    column_width = page.words.width / max(page.words_columns, 1)
    line_height = config.layout.words_font_size * 1.35
    available = max(column_width - 4.0, 8.0)
    font_name = config.layout.font_name
    for index, word in enumerate(words):
        column, row = index // page.words_rows, index % page.words_rows
        center_x = page.words.x + column * column_width + column_width / 2
        y = page.words.top - (row + 1) * line_height
        font = words_font
        size_pt = float(config.layout.words_font_size)
        box = draw.textbbox((0, 0), word, font=font)
        width = (box[2] - box[0]) / scale if scale else (box[2] - box[0])
        while size_pt > 4.0 and width > available:
            size_pt -= 0.4
            font = _font(max(6, _point(size_pt, scale)), False, font_name)
            box = draw.textbbox((0, 0), word, font=font)
            width = (box[2] - box[0]) / scale if scale else (box[2] - box[0])
        draw.text(xy(center_x, y), word, fill="black", font=font, anchor="ms")
