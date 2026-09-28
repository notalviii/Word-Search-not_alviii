"""Modelos de datos para la aplicación.

No contienen referencias a CustomTkinter, Pillow ni ReportLab, de modo que el
motor de generación se puede probar y reutilizar de forma aislada.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import ceil
from typing import Any


MM_TO_POINTS = 72.0 / 25.4
INCH_TO_POINTS = 72.0
PAGE_PRESETS: dict[str, tuple[float, float, str]] = {
    "A4": (210.0, 297.0, "mm"),
    "Letter": (8.5, 11.0, "in"),
    "6 × 9 in": (6.0, 9.0, "in"),
    "8.5 × 11 in": (8.5, 11.0, "in"),
    "Personalizado": (210.0, 297.0, "mm"),
}


@dataclass(frozen=True, slots=True)
class ValidationError:
    message: str
    line: int | None = None
    puzzle_number: int | None = None
    word: str | None = None
    field: str | None = None
    blocking: bool = True

    def display(self) -> str:
        location: list[str] = []
        if self.line is not None:
            location.append(f"línea {self.line}")
        if self.puzzle_number is not None:
            location.append(f"sopa {self.puzzle_number}")
        if self.word:
            location.append(f"palabra «{self.word}»")
        return f"{' · '.join(location)}: {self.message}" if location else self.message


@dataclass(frozen=True, slots=True)
class Word:
    text: str
    source_line: int | None = None
    source_column: int | None = None


@dataclass(frozen=True, slots=True)
class Coordinate:
    """Coordenada de cuadrícula indexada desde cero: fila, columna."""

    row: int
    column: int


@dataclass(frozen=True, slots=True)
class WordPlacement:
    word: Word
    start: Coordinate
    end: Coordinate
    row_step: int
    column_step: int

    @property
    def coordinates(self) -> tuple[Coordinate, ...]:
        return tuple(
            Coordinate(self.start.row + i * self.row_step, self.start.column + i * self.column_step)
            for i in range(len(self.word.text))
        )


@dataclass(slots=True)
class Puzzle:
    number: int
    words: list[Word]
    grid: list[list[str]] | None = None
    placements: list[WordPlacement] = field(default_factory=list)
    source_line: int | None = None

    @property
    def is_generated(self) -> bool:
        return self.grid is not None and len(self.placements) == len(self.words)


@dataclass(slots=True)
class PuzzleBook:
    puzzles: list[Puzzle]
    source_path: str | None = None

    @property
    def word_count(self) -> int:
        return sum(len(puzzle.words) for puzzle in self.puzzles)

    @property
    def word_count_range(self) -> tuple[int, int]:
        counts = [len(puzzle.words) for puzzle in self.puzzles]
        return (min(counts), max(counts)) if counts else (0, 0)


@dataclass(slots=True)
class MarginConfig:
    top: float = 15.0
    bottom: float = 15.0
    left: float = 15.0
    right: float = 15.0

    def as_points(self, unit: str) -> tuple[float, float, float, float]:
        factor = MM_TO_POINTS if unit == "mm" else INCH_TO_POINTS
        return tuple(value * factor for value in (self.top, self.bottom, self.left, self.right))


@dataclass(slots=True)
class PageConfig:
    width: float = 210.0
    height: float = 297.0
    unit: str = "mm"
    preset: str = "A4"
    margins: MarginConfig = field(default_factory=MarginConfig)

    def size_points(self) -> tuple[float, float]:
        factor = MM_TO_POINTS if self.unit == "mm" else INCH_TO_POINTS
        return self.width * factor, self.height * factor

    def apply_preset(self, preset: str) -> None:
        width, height, unit = PAGE_PRESETS[preset]
        self.width, self.height, self.unit, self.preset = width, height, unit, preset


@dataclass(slots=True)
class GridConfig:
    rows: int = 15
    columns: int = 15
    # Direcciones en forma (delta_fila, delta_columna). Las ocho se pueden activar
    # de forma independiente desde la interfaz.
    directions: dict[str, bool] = field(default_factory=lambda: {
        "derecha": True, "izquierda": False, "abajo": True, "arriba": False,
        "diagonal_descendente": True, "diagonal_ascendente": True,
        "diagonal_descendente_inversa": False, "diagonal_ascendente_inversa": False,
    })
    allow_reversed: bool = False
    allow_diagonals: bool = True
    allow_intersections: bool = True
    max_attempts: int = 120
    seed: int | None = None
    prefer_spacing: bool = True  # If True, prefer less crowded placements

    def direction_steps(self) -> list[tuple[int, int]]:
        candidates = {
            "derecha": (0, 1), "izquierda": (0, -1), "abajo": (1, 0), "arriba": (-1, 0),
            "diagonal_descendente": (1, 1), "diagonal_ascendente": (1, -1),
            "diagonal_descendente_inversa": (-1, 1), "diagonal_ascendente_inversa": (-1, -1),
        }
        enabled = [candidates[name] for name, active in self.directions.items() if active]
        if not self.allow_diagonals:
            enabled = [step for step in enabled if 0 in step]
        if self.allow_reversed:
            enabled.extend([(-row, -column) for row, column in enabled])
        # La deduplicación preserva el orden y evita explorar dos veces una dirección.
        return list(dict.fromkeys(enabled))


@dataclass(slots=True)
class LayoutConfig:
    title: str = "Sopa de letras"
    subtitle: str = "Encuentra todas las palabras"
    show_puzzle_number: bool = True
    grid_position: str = "centro"
    # Porcentajes dentro del rectángulo disponible; se usan con posición personalizada.
    custom_grid_x_percent: float = 50.0
    custom_grid_y_percent: float = 50.0
    words_position: str = "abajo"
    font_name: str = "Arial"
    title_size: float = 18.0
    subtitle_size: float = 10.0
    grid_font_size: float = 11.0
    words_font_size: float = 9.0
    word_columns: int = 3
    word_order: str = "original"  # original | alfabetico
    cell_size: float = 18.0
    line_width: float = 0.6
    spacing: float = 8.0
    auto_fit: bool = True


@dataclass(slots=True)
class ExportConfig:
    include_solutions: bool = True
    order_mode: str = "consecutivo"  # consecutivo | soluciones_al_final
    solution_style: str = "círculo"  # círculo | línea | resaltado
    output_path: str = "output/libro_sopas.pdf"
    selected_puzzles: str = "todas"  # todas | rango CSV (p. ej. 1-3,7)


@dataclass(slots=True)
class AppConfig:
    page: PageConfig = field(default_factory=PageConfig)
    grid: GridConfig = field(default_factory=GridConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    language: str = "en"  # en | es
    theme: str = "light"  # light | dark | soft | high_contrast

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AppConfig":
        page_raw = raw.get("page", {})
        margin_raw = page_raw.get("margins", {})
        page = PageConfig(
            width=float(page_raw.get("width", 210.0)), height=float(page_raw.get("height", 297.0)),
            unit=page_raw.get("unit", "mm"), preset=page_raw.get("preset", "Personalizado"),
            margins=MarginConfig(**{key: float(margin_raw.get(key, 15.0)) for key in ("top", "bottom", "left", "right")}),
        )
        grid_raw = raw.get("grid", {})
        default_directions = GridConfig().directions
        directions = default_directions | dict(grid_raw.get("directions", {}))
        grid = GridConfig(
            rows=int(grid_raw.get("rows", 15)), columns=int(grid_raw.get("columns", 15)), directions=directions,
            allow_reversed=bool(grid_raw.get("allow_reversed", False)),
            allow_diagonals=bool(grid_raw.get("allow_diagonals", True)),
            allow_intersections=bool(grid_raw.get("allow_intersections", True)),
            max_attempts=int(grid_raw.get("max_attempts", 120)), seed=grid_raw.get("seed"),
            prefer_spacing=bool(grid_raw.get("prefer_spacing", True)),
        )
        layout_raw = raw.get("layout", {})
        layout_defaults = asdict(LayoutConfig())
        layout = LayoutConfig(**(layout_defaults | layout_raw))
        export_raw = raw.get("export", {})
        export_defaults = asdict(ExportConfig())
        export = ExportConfig(**(export_defaults | export_raw))
        language = raw.get("language", "en")
        theme = raw.get("theme", "light")
        return cls(page=page, grid=grid, layout=layout, export=export, language=language, theme=theme)

    def selected_numbers(self, available: list[int]) -> list[int]:
        """Interpreta «todas» o una selección segura como 1-3,7,9-10."""
        expression = self.export.selected_puzzles.strip().lower()
        if not expression or expression == "todas":
            return available
        requested: set[int] = set()
        for token in expression.split(","):
            token = token.strip()
            if "-" in token:
                start_text, end_text = token.split("-", 1)
                start, end = int(start_text.strip()), int(end_text.strip())
                if start > end:
                    raise ValueError("El inicio de un rango no puede superar el final.")
                requested.update(range(start, end + 1))
            else:
                requested.add(int(token))
        missing = sorted(requested.difference(available))
        if missing:
            raise ValueError(f"Las sopas no existen: {', '.join(map(str, missing))}.")
        return [number for number in available if number in requested]


@dataclass(slots=True)
class GenerationResult:
    puzzle: Puzzle | None
    errors: list[ValidationError] = field(default_factory=list)
    attempts: int = 0

    @property
    def success(self) -> bool:
        return self.puzzle is not None and not self.errors and self.puzzle.is_generated


def word_list_rows(word_count: int, columns: int) -> int:
    return ceil(word_count / max(columns, 1))
