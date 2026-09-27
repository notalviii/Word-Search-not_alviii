from __future__ import annotations

import unittest

from app.core.generator import generate_puzzle, validate_generated_puzzle
from app.models import GridConfig, Puzzle, Word


class PuzzleGeneratorTests(unittest.TestCase):
    def _puzzle(self) -> Puzzle:
        return Puzzle(1, [Word("PERRO"), Word("GATO"), Word("ÁRBOL"), Word("NIÑO"), Word("PINGÜINO")])

    def test_generates_every_word_and_coordinates_match_grid(self) -> None:
        config = GridConfig(rows=12, columns=12, seed=11, max_attempts=200)
        result = generate_puzzle(self._puzzle(), config)
        self.assertTrue(result.success, [error.display() for error in result.errors])
        assert result.puzzle is not None
        self.assertEqual(len(result.puzzle.placements), 5)
        self.assertEqual(validate_generated_puzzle(result.puzzle), [])
        for placement in result.puzzle.placements:
            found = "".join(result.puzzle.grid[point.row][point.column] for point in placement.coordinates)  # type: ignore[index]
            self.assertEqual(found, placement.word.text)

    def test_deactivated_directions_are_not_used(self) -> None:
        config = GridConfig(
            rows=10, columns=10, seed=4, max_attempts=200,
            directions={"derecha": True, "izquierda": False, "abajo": False, "arriba": False,
                        "diagonal_descendente": False, "diagonal_ascendente": False,
                        "diagonal_descendente_inversa": False, "diagonal_ascendente_inversa": False},
        )
        result = generate_puzzle(Puzzle(1, [Word("PERRO"), Word("GATO")]), config)
        self.assertTrue(result.success, result.errors)
        assert result.puzzle is not None
        self.assertTrue(all(placement.row_step == 0 and placement.column_step == 1 for placement in result.puzzle.placements))

    def test_word_too_long_is_rejected_before_generation(self) -> None:
        result = generate_puzzle(Puzzle(1, [Word("EXCESIVAMENTE")]), GridConfig(rows=5, columns=5, seed=1))
        self.assertFalse(result.success)
        self.assertIn("más larga", result.errors[0].message)

    def test_disallowing_intersections_preserves_integrity(self) -> None:
        result = generate_puzzle(self._puzzle(), GridConfig(rows=15, columns=15, seed=7, allow_intersections=False, max_attempts=250))
        self.assertTrue(result.success, [error.display() for error in result.errors])
