"""Generador por búsqueda con retroceso para sopas de letras."""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Callable

from app.models import Coordinate, GenerationResult, GridConfig, Puzzle, ValidationError, WordPlacement


FILLER_ALPHABET = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZÁÉÍÓÚÜ"
CancelCheck = Callable[[], bool] | None


def _candidate_placements(word: str, config: GridConfig, rng: random.Random) -> list[tuple[int, int, int, int]]:
    candidates: list[tuple[int, int, int, int]] = []
    for row_step, column_step in config.direction_steps():
        for row in range(config.rows):
            for column in range(config.columns):
                end_row = row + (len(word) - 1) * row_step
                end_column = column + (len(word) - 1) * column_step
                if 0 <= end_row < config.rows and 0 <= end_column < config.columns:
                    candidates.append((row, column, row_step, column_step))
    rng.shuffle(candidates)
    return candidates


def _can_place(
    grid: list[list[str | None]], word: str, row: int, column: int,
    row_step: int, column_step: int, allow_intersections: bool,
) -> tuple[bool, int, int]:
    """Check if a word can be placed and return (valid, crossings, adjacency_score)."""
    crossings = 0
    adjacency_score = 0  # Lower is better (less crowded)
    rows = len(grid)
    columns = len(grid[0]) if grid else 0
    
    for index, letter in enumerate(word):
        current_row = row + index * row_step
        current_col = column + index * column_step
        current = grid[current_row][current_col]
        
        if current is not None:
            if current != letter:
                return False, 0, 0
            if not allow_intersections:
                return False, 0, 0
            crossings += 1
        else:
            # Check adjacency to existing letters (8-neighbor check)
            # This helps avoid placing words too close to each other
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = current_row + dr, current_col + dc
                    if 0 <= nr < rows and 0 <= nc < columns:
                        if grid[nr][nc] is not None:
                            adjacency_score += 1
    
    return True, crossings, adjacency_score


def _write_word(
    grid: list[list[str | None]], word: str, row: int, column: int, row_step: int, column_step: int,
) -> list[tuple[int, int, str | None]]:
    previous: list[tuple[int, int, str | None]] = []
    for index, letter in enumerate(word):
        target_row, target_column = row + index * row_step, column + index * column_step
        previous.append((target_row, target_column, grid[target_row][target_column]))
        grid[target_row][target_column] = letter
    return previous


def _undo(grid: list[list[str | None]], previous: list[tuple[int, int, str | None]]) -> None:
    for row, column, old_value in previous:
        grid[row][column] = old_value


def generate_puzzle(puzzle: Puzzle, config: GridConfig, cancelled: CancelCheck = None) -> GenerationResult:
    """Genera una cuadrícula completa o devuelve un error sin estado parcial.

    Se ordenan internamente las palabras largas primero para reducir la búsqueda,
    pero los placements finales vuelven al orden del CSV.
    """
    config_errors: list[ValidationError] = []
    if config.rows < 2 or config.columns < 2:
        config_errors.append(ValidationError("La cuadrícula debe tener al menos 2 filas y 2 columnas.", puzzle_number=puzzle.number))
    directions = config.direction_steps()
    if not directions:
        config_errors.append(ValidationError("Debe activar al menos una dirección de colocación.", puzzle_number=puzzle.number))
    for word in puzzle.words:
        if len(word.text) > max(config.rows, config.columns):
            config_errors.append(ValidationError("La palabra es más larga que cualquier dimensión de la cuadrícula.", puzzle_number=puzzle.number, word=word.text))
    if config_errors:
        return GenerationResult(None, config_errors)

    rng = random.Random(config.seed if config.seed is not None else random.SystemRandom().randrange(2**63))
    candidates = {word.text: _candidate_placements(word.text, config, rng) for word in puzzle.words}
    for word in puzzle.words:
        if not candidates[word.text]:
            return GenerationResult(None, [ValidationError("No hay posiciones posibles para la palabra con las direcciones configuradas.", puzzle_number=puzzle.number, word=word.text)])

    # Para empatar se conserva el orden de origen; al tener duplicados prohibidos
    # el texto sirve como identificador estable.
    ordered_words = sorted(puzzle.words, key=lambda word: (-len(word.text), puzzle.words.index(word)))
    grid: list[list[str | None]] = [[None for _ in range(config.columns)] for _ in range(config.rows)]
    chosen: dict[str, WordPlacement] = {}
    nodes = 0
    cancelled_error = ValidationError("La generación fue cancelada.", puzzle_number=puzzle.number)

    def place(index: int) -> bool:
        nonlocal nodes
        if cancelled and cancelled():
            raise InterruptedError
        if index == len(ordered_words):
            return True
        word = ordered_words[index]
        ranked: list[tuple[int, int, tuple[int, int, int, int]]] = []
        for candidate in candidates[word.text]:
            row, column, row_step, column_step = candidate
            valid, crossings, adjacency = _can_place(grid, word.text, row, column, row_step, column_step, config.allow_intersections)
            if valid:
                # Prioritize placements with fewer adjacent cells (better spacing)
                # while still preferring some crossings for density
                ranked.append((adjacency, crossings, candidate))
        # Sort based on prefer_spacing setting
        if config.prefer_spacing:
            # Prioritize spacing first, then crossings
            ranked.sort(key=lambda item: (item[0], -item[1]))
        else:
            # Prioritize crossings first (original behavior), then spacing
            ranked.sort(key=lambda item: (-item[1], item[0]))
        for _, _, (row, column, row_step, column_step) in ranked:
            nodes += 1
            if nodes > max(config.max_attempts, 1) * 1_000:
                return False
            previous = _write_word(grid, word.text, row, column, row_step, column_step)
            chosen[word.text] = WordPlacement(
                word=word,
                start=Coordinate(row, column),
                end=Coordinate(row + (len(word.text) - 1) * row_step, column + (len(word.text) - 1) * column_step),
                row_step=row_step,
                column_step=column_step,
            )
            if place(index + 1):
                return True
            chosen.pop(word.text, None)
            _undo(grid, previous)
        return False

    try:
        solved = place(0)
    except InterruptedError:
        return GenerationResult(None, [cancelled_error], attempts=nodes)
    if not solved:
        return GenerationResult(None, [ValidationError("No se pudo colocar todas las palabras con esta cuadrícula y opciones. Aumente el tamaño o permita más direcciones/cruces.", puzzle_number=puzzle.number)], attempts=nodes)

    completed_grid = [[cell if cell is not None else rng.choice(FILLER_ALPHABET) for cell in row] for row in grid]
    generated = replace(puzzle, grid=completed_grid, placements=[chosen[word.text] for word in puzzle.words])
    errors = validate_generated_puzzle(generated)
    return GenerationResult(generated if not errors else None, errors, attempts=nodes)


def validate_generated_puzzle(puzzle: Puzzle) -> list[ValidationError]:
    """Comprueba que placements, cuadrícula y letras sean exactamente coherentes."""
    errors: list[ValidationError] = []
    if puzzle.grid is None:
        return [ValidationError("La sopa no tiene cuadrícula generada.", puzzle_number=puzzle.number)]
    if len(puzzle.placements) != len(puzzle.words):
        errors.append(ValidationError("Faltan coordenadas de palabras.", puzzle_number=puzzle.number))
    placement_words = {placement.word.text for placement in puzzle.placements}
    for word in puzzle.words:
        if word.text not in placement_words:
            errors.append(ValidationError("La palabra no tiene coordenadas.", puzzle_number=puzzle.number, word=word.text))
    row_count = len(puzzle.grid)
    column_count = len(puzzle.grid[0]) if puzzle.grid else 0
    for placement in puzzle.placements:
        rendered: list[str] = []
        for coordinate in placement.coordinates:
            if not (0 <= coordinate.row < row_count and 0 <= coordinate.column < column_count):
                errors.append(ValidationError("Las coordenadas salen de la cuadrícula.", puzzle_number=puzzle.number, word=placement.word.text))
                break
            rendered.append(puzzle.grid[coordinate.row][coordinate.column])
        else:
            if "".join(rendered) != placement.word.text:
                errors.append(ValidationError("Las coordenadas no corresponden a la palabra.", puzzle_number=puzzle.number, word=placement.word.text))
    return errors
