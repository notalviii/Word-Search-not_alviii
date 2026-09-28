"""Renderizador vectorial ReportLab de libros de sopas y soluciones."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from app.models import AppConfig, Puzzle, PuzzleBook, WordPlacement
from app.i18n import LocaleManager
from .fonts import resolve_pdf_font
from .layout import (
    PageLayout,
    Rect,
    SOLUTIONS_PER_PAGE,
    calculate_layout,
    compact_layout_config,
    solution_cell_rects,
)


ProgressCallback = Callable[[int, int, str], None]
CancelCheck = Callable[[], bool]
PageSpec = tuple[list[Puzzle], bool]


def _chunks(items: list[Puzzle], size: int) -> list[list[Puzzle]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


class PdfBookRenderer:
    def __init__(self) -> None:
        self.locale = LocaleManager()
    
    def set_language(self, language: str) -> None:
        """Set the language for PDF generation."""
        self.locale.set_language(language)
    
    def page_sequence(self, book: PuzzleBook, config: AppConfig) -> list[PageSpec]:
        puzzles = book.puzzles
        puzzle_pages: list[PageSpec] = [([puzzle], False) for puzzle in puzzles]
        if not config.export.include_solutions:
            return puzzle_pages
        solution_pages: list[PageSpec] = [(group, True) for group in _chunks(puzzles, SOLUTIONS_PER_PAGE)]
        if config.export.order_mode == "consecutivo":
            pages: list[PageSpec] = []
            for group in _chunks(puzzles, SOLUTIONS_PER_PAGE):
                pages.extend(([puzzle], False) for puzzle in group)
                pages.append((group, True))
            return pages
        return puzzle_pages + solution_pages

    def validate_layouts(self, book: PuzzleBook, config: AppConfig) -> None:
        for puzzle in book.puzzles:
            calculate_layout(puzzle, config)
        if config.export.include_solutions and book.puzzles:
            cell = solution_cell_rects(config, occupied=1)[0]
            inset = Rect(cell.x + 6, cell.y + 6, max(cell.width - 12, 4), max(cell.height - 12, 4))
            compact = compact_layout_config(config, inset)
            calculate_layout(book.puzzles[0], compact, bounds=inset)

    def export(
        self,
        book: PuzzleBook,
        config: AppConfig,
        path: str | Path | None = None,
        progress: ProgressCallback | None = None,
        cancelled: CancelCheck | None = None,
    ) -> Path:
        self.set_language(config.language)
        output = Path(path or config.export.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        self.validate_layouts(book, config)
        sequence = self.page_sequence(book, config)
        temporary = output.with_suffix(output.suffix + ".incompleto")
        if temporary.exists():
            temporary.unlink()
        canvas = Canvas(str(temporary), pagesize=config.page.size_points(), pageCompression=1)
        canvas.setTitle(config.layout.title or self.locale.pdf("word_search"))
        try:
            for index, (puzzles, solution) in enumerate(sequence, start=1):
                if cancelled and cancelled():
                    raise InterruptedError
                if progress:
                    if solution:
                        numbers = ", ".join(str(puzzle.number) for puzzle in puzzles)
                        label = f"Renderizando soluciones {numbers}"
                    else:
                        label = f"Renderizando sopa {puzzles[0].number}"
                    progress(index - 1, len(sequence), label)
                if solution:
                    self.draw_solution_page(canvas, puzzles, config)
                else:
                    self.draw_page(canvas, puzzles[0], config, False)
                canvas.showPage()
                if progress:
                    progress(index, len(sequence), f"Página {index} de {len(sequence)} preparada")
            canvas.save()
            if cancelled and cancelled():
                raise InterruptedError
            if output.exists():
                output.unlink()
            temporary.replace(output)
            return output
        except Exception:
            # ReportLab debe cerrar el stream antes de retirar el temporal.
            try:
                canvas.save()
            except Exception:
                pass
            if temporary.exists():
                temporary.unlink()
            raise

    def draw_solution_page(self, canvas: Canvas, puzzles: list[Puzzle], config: AppConfig) -> None:
        cells = solution_cell_rects(config, occupied=len(puzzles))
        canvas.setStrokeColor(colors.HexColor("#B8B8B8"))
        canvas.setLineWidth(0.7)
        for puzzle, cell in zip(puzzles, cells):
            canvas.rect(cell.x, cell.y, cell.width, cell.height, stroke=1, fill=0)
            inset = Rect(cell.x + 6, cell.y + 6, max(cell.width - 12, 4), max(cell.height - 12, 4))
            self.draw_page(canvas, puzzle, config, True, bounds=inset)

    def draw_page(
        self,
        canvas: Canvas,
        puzzle: Puzzle,
        config: AppConfig,
        solution: bool = False,
        bounds: Rect | None = None,
    ) -> PageLayout:
        working = compact_layout_config(config, bounds) if bounds is not None else config
        page = calculate_layout(puzzle, working, bounds=bounds)
        layout = working.layout
        font = resolve_pdf_font(layout.font_name)
        center_x = page.content.x + page.content.width / 2
        canvas.setFillColor(colors.black)
        if layout.title:
            canvas.setFont(font, layout.title_size)
            canvas.drawCentredString(center_x, page.title_y, layout.title)
        if layout.subtitle and page.subtitle_y is not None:
            canvas.setFont(font, layout.subtitle_size)
            canvas.drawCentredString(center_x, page.subtitle_y, layout.subtitle)
        if page.number_y is not None:
            if solution:
                text = self.locale.pdf("solution_prefix", number=puzzle.number)
            else:
                text = self.locale.pdf("puzzle_number", number=puzzle.number)
            canvas.setFont(font, layout.subtitle_size)
            canvas.drawCentredString(center_x, page.number_y, text)
        self._draw_grid(canvas, puzzle, page, working, font)
        if solution:
            self._draw_solution_marks(canvas, puzzle.placements, page, working)
        self._draw_word_list(canvas, puzzle, page, working, font)
        return page

    def _draw_grid(self, canvas: Canvas, puzzle: Puzzle, page: PageLayout, config: AppConfig, font: str) -> None:
        assert puzzle.grid is not None
        rows, columns = config.grid.rows, config.grid.columns
        canvas.setStrokeColor(colors.black)
        canvas.setFillColor(colors.black)
        canvas.setLineWidth(config.layout.line_width)
        for row in range(rows + 1):
            y = page.grid.y + row * page.cell_size
            canvas.line(page.grid.x, y, page.grid.x + page.grid.width, y)
        for column in range(columns + 1):
            x = page.grid.x + column * page.cell_size
            canvas.line(x, page.grid.y, x, page.grid.y + page.grid.height)
        font_size = min(config.layout.grid_font_size, page.cell_size * 0.62)
        canvas.setFont(font, max(font_size, 4.0))
        for row in range(rows):
            for column in range(columns):
                x = page.grid.x + (column + 0.5) * page.cell_size
                # La fila cero del dominio aparece visualmente arriba.
                y = page.grid.y + (rows - row - 0.5) * page.cell_size - font_size * 0.34
                canvas.drawCentredString(x, y, puzzle.grid[row][column])

    def _grid_point(self, row: int, column: int, page: PageLayout, rows: int) -> tuple[float, float]:
        return (
            page.grid.x + (column + 0.5) * page.cell_size,
            page.grid.y + (rows - row - 0.5) * page.cell_size,
        )

    def _draw_solution_marks(self, canvas: Canvas, placements: Iterable[WordPlacement], page: PageLayout, config: AppConfig) -> None:
        rows = config.grid.rows
        style = config.export.solution_style
        for placement in placements:
            start_x, start_y = self._grid_point(placement.start.row, placement.start.column, page, rows)
            end_x, end_y = self._grid_point(placement.end.row, placement.end.column, page, rows)
            if style == "resaltado":
                canvas.saveState()
                canvas.setStrokeColor(colors.Color(1, 0.82, 0.05, alpha=0.55))
                canvas.setLineWidth(page.cell_size * 0.72)
                canvas.line(start_x, start_y, end_x, end_y)
                canvas.restoreState()
            elif style == "línea":
                canvas.saveState()
                canvas.setStrokeColor(colors.HexColor("#D22C2C"))
                canvas.setLineWidth(max(1.4, page.cell_size * 0.11))
                canvas.line(start_x, start_y, end_x, end_y)
                canvas.restoreState()
            else:  # círculo
                canvas.saveState()
                canvas.setStrokeColor(colors.HexColor("#D22C2C"))
                canvas.setLineWidth(max(1.0, page.cell_size * 0.08))
                for coordinate in placement.coordinates:
                    x, y = self._grid_point(coordinate.row, coordinate.column, page, rows)
                    canvas.circle(x, y, page.cell_size * 0.41, stroke=1, fill=0)
                canvas.restoreState()

    def _draw_word_list(self, canvas: Canvas, puzzle: Puzzle, page: PageLayout, config: AppConfig, font: str) -> None:
        words = [word.text for word in puzzle.words]
        if config.layout.word_order == "alfabetico":
            words.sort()
        columns = page.words_columns
        rows = page.words_rows
        if not words or rows <= 0:
            return
        column_width = page.words.width / max(columns, 1)
        line_height = config.layout.words_font_size * 1.35
        available = max(column_width - 4.0, 8.0)
        canvas.setFillColor(colors.black)
        # Se rellena por columnas: cada palabra queda centrada en su columna.
        for index, word in enumerate(words):
            column = index // rows
            row = index % rows
            center_x = page.words.x + column * column_width + column_width / 2
            y = page.words.top - (row + 1) * line_height
            size = float(config.layout.words_font_size)
            while size > 4.0 and stringWidth(word, font, size) > available:
                size -= 0.4
            canvas.setFont(font, size)
            canvas.drawCentredString(center_x, y, word)
