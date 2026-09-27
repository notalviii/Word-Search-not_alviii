from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.core.generator import generate_puzzle
from app.models import AppConfig, GridConfig, Puzzle, PuzzleBook, Word
from app.pdf import PdfBookRenderer, calculate_layout
from app.pdf.fonts import resolve_pdf_font
from app.pdf.layout import SOLUTIONS_PER_PAGE, compact_layout_config, page_content_rect, solution_cell_rects
from app.utils import load_config, save_config


class ConfigLayoutPdfTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AppConfig()
        self.config.grid = GridConfig(rows=12, columns=12, seed=42, max_attempts=200)
        result = generate_puzzle(Puzzle(1, [Word("PERRO"), Word("GATO"), Word("ÁRBOL"), Word("NIÑO")]), self.config.grid)
        self.assertTrue(result.success, result.errors)
        assert result.puzzle is not None
        self.book = PuzzleBook([result.puzzle])

    def test_layout_stays_inside_page_content(self) -> None:
        page = calculate_layout(self.book.puzzles[0], self.config)
        self.assertGreater(page.cell_size, 3)
        self.assertGreaterEqual(page.grid.x, page.content.x - 0.01)
        self.assertGreaterEqual(page.grid.y, page.content.y - 0.01)
        self.assertLessEqual(page.grid.x + page.grid.width, page.content.x + page.content.width + 0.01)
        self.assertLessEqual(page.grid.y + page.grid.height, page.content.y + page.content.height + 0.01)

    def test_grid_alignment_options_remain_inside_available_page_area(self) -> None:
        for position in ("centro", "arriba", "abajo", "izquierda", "derecha", "personalizado"):
            self.config.layout.grid_position = position
            self.config.layout.custom_grid_x_percent = 23.0
            self.config.layout.custom_grid_y_percent = 77.0
            page = calculate_layout(self.book.puzzles[0], self.config)
            self.assertGreaterEqual(page.grid.x, page.content.x - 0.01)
            self.assertGreaterEqual(page.grid.y, page.content.y - 0.01)
            self.assertLessEqual(page.grid.x + page.grid.width, page.content.x + page.content.width + 0.01)
            self.assertLessEqual(page.grid.y + page.grid.height, page.content.y + page.content.height + 0.01)

    def test_config_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            self.config.export.selected_puzzles = "1-3,7"
            save_config(self.config, path)
            loaded = load_config(path)
        self.assertEqual(loaded.grid.rows, 12)
        self.assertEqual(loaded.export.selected_puzzles, "1-3,7")
        self.assertEqual(loaded.page.margins.left, 15.0)

    def test_pdf_contains_expected_pages_and_never_uses_regenerated_solution(self) -> None:
        self.config.export.include_solutions = True
        self.config.export.order_mode = "consecutivo"
        renderer = PdfBookRenderer()
        sequence = renderer.page_sequence(self.book, self.config)
        self.assertEqual(
            [(tuple(puzzle.number for puzzle in puzzles), solution) for puzzles, solution in sequence],
            [((1,), False), ((1,), True)],
        )
        self.assertIs(sequence[0][0][0].grid, sequence[1][0][0].grid)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "book.pdf"
            renderer.export(self.book, self.config, output)
            raw = output.read_bytes()
        self.assertTrue(raw.startswith(b"%PDF"))
        self.assertGreater(len(raw), 500)

    def _book_with(self, count: int) -> PuzzleBook:
        puzzles: list[Puzzle] = []
        for number in range(1, count + 1):
            result = generate_puzzle(
                Puzzle(number, [Word("PERRO"), Word("GATO"), Word("SOL"), Word("LUNA")]),
                GridConfig(rows=12, columns=12, seed=40 + number, max_attempts=200),
            )
            self.assertTrue(result.success, result.errors)
            assert result.puzzle is not None
            puzzles.append(result.puzzle)
        return PuzzleBook(puzzles)

    def test_solutions_are_grouped_four_per_page_without_blank_pages(self) -> None:
        renderer = PdfBookRenderer()
        self.config.export.include_solutions = True
        self.config.export.order_mode = "soluciones_al_final"
        for total, expected_solution_pages, last_count in ((1, 1, 1), (2, 1, 2), (3, 1, 3), (4, 1, 4), (5, 2, 1), (8, 2, 4)):
            book = self._book_with(total)
            sequence = renderer.page_sequence(book, self.config)
            puzzle_pages = [item for item in sequence if not item[1]]
            solution_pages = [item for item in sequence if item[1]]
            self.assertEqual(len(puzzle_pages), total)
            self.assertEqual(len(solution_pages), expected_solution_pages)
            self.assertTrue(all(1 <= len(puzzles) <= SOLUTIONS_PER_PAGE for puzzles, _ in solution_pages))
            self.assertEqual(len(solution_pages[-1][0]), last_count)
            self.assertEqual(sum(len(puzzles) for puzzles, _ in solution_pages), total)
            with tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / f"book_{total}.pdf"
                renderer.export(book, self.config, output)
                self.assertTrue(output.read_bytes().startswith(b"%PDF"))

    def test_solution_quadrants_stay_inside_margins(self) -> None:
        content = page_content_rect(self.config)
        cells = solution_cell_rects(self.config, occupied=4)
        self.assertEqual(len(cells), 4)
        for cell in cells:
            self.assertGreaterEqual(cell.x, content.x - 0.01)
            self.assertGreaterEqual(cell.y, content.y - 0.01)
            self.assertLessEqual(cell.x + cell.width, content.x + content.width + 0.01)
            self.assertLessEqual(cell.y + cell.height, content.y + content.height + 0.01)
        compact_config = compact_layout_config(self.config, cells[0])
        compact = calculate_layout(self.book.puzzles[0], compact_config, bounds=cells[0])
        self.assertGreaterEqual(compact.grid.x, cells[0].x - 0.01)
        self.assertLessEqual(compact.grid.x + compact.grid.width, cells[0].x + cells[0].width + 0.01)

    def test_selected_font_is_registered_for_pdf_export(self) -> None:
        self.config.layout.font_name = "Courier New"
        resolved = resolve_pdf_font(self.config.layout.font_name)
        renderer = PdfBookRenderer()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "font.pdf"
            renderer.export(self.book, self.config, output)
            raw = output.read_bytes()
        self.assertTrue(resolved.encode("latin-1", "ignore") in raw or b"Courier" in raw)
        self.assertIn(self.config.layout.font_name, ("Courier New", "Courier"))

