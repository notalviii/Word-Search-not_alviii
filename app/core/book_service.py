"""Servicio de alto nivel para generar libros sin depender de la interfaz."""

from __future__ import annotations

from dataclasses import replace
from typing import Callable

from app.models import GridConfig, Puzzle, PuzzleBook, ValidationError
from .generator import generate_puzzle


ProgressCallback = Callable[[int, int, str], None]
CancelCheck = Callable[[], bool]


class BookGenerationCancelled(Exception):
    """Señal explícita de cancelación, nunca produce un libro parcial válido."""


class BookGenerationService:
    def generate(
        self,
        book: PuzzleBook,
        grid_config: GridConfig,
        selected_numbers: list[int] | None = None,
        progress: ProgressCallback | None = None,
        cancelled: CancelCheck | None = None,
    ) -> PuzzleBook:
        selected = set(selected_numbers or [puzzle.number for puzzle in book.puzzles])
        originals = [puzzle for puzzle in book.puzzles if puzzle.number in selected]
        generated: list[Puzzle] = []
        for index, puzzle in enumerate(originals, start=1):
            if cancelled and cancelled():
                raise BookGenerationCancelled()
            if progress:
                progress(index - 1, len(originals), f"Generando sopa {puzzle.number} de {len(originals)}")
            result = generate_puzzle(puzzle, grid_config, cancelled)
            if result.errors:
                if cancelled and cancelled():
                    raise BookGenerationCancelled()
                joined = "\n".join(error.display() for error in result.errors)
                raise ValueError(joined)
            generated.append(result.puzzle)  # success guarantees this is Puzzle
            if progress:
                progress(index, len(originals), f"Sopa {puzzle.number} generada")
        return PuzzleBook(puzzles=generated, source_path=book.source_path)
