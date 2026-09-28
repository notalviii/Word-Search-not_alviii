from __future__ import annotations

import unittest

from app.core.book_service import BookGenerationService
from app.core.generator import generate_puzzle, validate_generated_puzzle
from app.models import GridConfig, Puzzle, PuzzleBook, Word


class RegenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BookGenerationService()
        self.config = GridConfig(rows=12, columns=12, seed=42, max_attempts=200)
    
    def _create_test_book(self, puzzle_count: int = 3) -> PuzzleBook:
        puzzles: list[Puzzle] = []
        for i in range(puzzle_count):
            words = [Word(f"WORD{j}") for j in range(5)]
            result = generate_puzzle(Puzzle(i + 1, words), self.config)
            self.assertTrue(result.success, result.errors)
            assert result.puzzle is not None
            puzzles.append(result.puzzle)
        return PuzzleBook(puzzles)
    
    def test_regenerate_single_puzzle(self) -> None:
        book = self._create_test_book(3)
        original_grid = book.puzzles[1].grid
        original_placements = book.puzzles[1].placements
        
        # Regenerate puzzle 2
        new_book = self.service.regenerate_single_puzzle(book, 2, self.config)
        
        # Check that puzzle 2 changed
        self.assertIsNot(new_book.puzzles[1].grid, original_grid)
        self.assertIsNot(new_book.puzzles[1].placements, original_placements)
        
        # Check that other puzzles remain unchanged
        self.assertIs(new_book.puzzles[0].grid, book.puzzles[0].grid)
        self.assertIs(new_book.puzzles[2].grid, book.puzzles[2].grid)
    
    def test_regenerated_puzzle_is_valid(self) -> None:
        book = self._create_test_book(2)
        new_book = self.service.regenerate_single_puzzle(book, 1, self.config)
        
        # Validate the regenerated puzzle
        errors = validate_generated_puzzle(new_book.puzzles[0])
        self.assertEqual(errors, [])
    
    def test_regenerated_coordinates_match_grid(self) -> None:
        book = self._create_test_book(2)
        new_book = self.service.regenerate_single_puzzle(book, 1, self.config)
        
        puzzle = new_book.puzzles[0]
        for placement in puzzle.placements:
            rendered = "".join(
                puzzle.grid[coord.row][coord.column]  # type: ignore[index]
                for coord in placement.coordinates
            )
            self.assertEqual(rendered, placement.word.text)
    
    def test_regenerate_nonexistent_puzzle(self) -> None:
        book = self._create_test_book(2)
        with self.assertRaises(ValueError) as context:
            self.service.regenerate_single_puzzle(book, 99, self.config)
        self.assertIn("not found", str(context.exception))
    
    def test_regenerate_preserves_puzzle_numbers(self) -> None:
        book = self._create_test_book(3)
        new_book = self.service.regenerate_single_puzzle(book, 2, self.config)
        
        # Check that puzzle numbers are preserved
        self.assertEqual(new_book.puzzles[0].number, 1)
        self.assertEqual(new_book.puzzles[1].number, 2)
        self.assertEqual(new_book.puzzles[2].number, 3)
    
    def test_regenerate_preserves_source_path(self) -> None:
        book = self._create_test_book(2)
        book.source_path = "test.csv"
        new_book = self.service.regenerate_single_puzzle(book, 1, self.config)
        
        self.assertEqual(new_book.source_path, "test.csv")


if __name__ == "__main__":
    unittest.main()
