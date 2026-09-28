"""Translation dictionaries for English and Spanish.

All user-facing text should be translated here. The same translations
are used for both the UI and PDF generation to avoid duplication.
"""

from __future__ import annotations

from typing import TypedDict


class UITranslations(TypedDict):
    # Main window
    app_title: str
    configuration: str
    preview: str
    ready: str
    preparing_generation: str
    cancelling: str
    operation_cancelled: str
    operation_failed: str
    
    # CSV section
    csv_file: str
    load_csv: str
    csv_not_loaded: str
    csv_loaded: str
    csv_ready: str
    csv_line_1: str
    csv_line_2: str
    csv_line_3: str
    csv_line_4: str
    
    # Page section
    page_and_margins: str
    preset: str
    width: str
    height: str
    unit: str
    margin_top: str
    margin_bottom: str
    margin_left: str
    margin_right: str
    
    # Puzzle section
    puzzle: str
    rows: str
    columns: str
    allow_reversed: str
    allow_diagonals: str
    allow_intersections: str
    
    # Layout section
    words_and_layout: str
    title: str
    subtitle: str
    grid_position: str
    position_x: str
    position_y: str
    font: str
    title_size: str
    subtitle_size: str
    grid_font_size: str
    words_font_size: str
    cell_size: str
    line_width: str
    word_columns: str
    order: str
    word_list: str
    auto_fit: str
    
    # Export section
    solutions_and_export: str
    include_solutions: str
    style: str
    export_order: str
    selected_puzzles: str
    output_pdf: str
    folder: str
    open_folder: str
    
    # Config section
    config_json: str
    save: str
    load: str
    reset: str
    
    # Preview controls
    previous: str
    next: str
    view_solution: str
    preview_button: str
    generate_pdf: str
    cancel: str
    no_pages: str
    solution: str
    puzzle: str
    
    # Dialogs
    select_csv: str
    invalid_csv: str
    save_config: str
    load_config: str
    reset_config: str
    save_pdf: str
    config_invalid: str
    config_saved: str
    config_loaded: str
    defaults_restored: str
    missing_csv: str
    cannot_open_folder: str
    pdf_generated: str
    generation_error: str
    
    # Progress messages
    generating_puzzle: str
    puzzle_generated: str
    rendering_puzzle: str
    rendering_solutions: str
    page_prepared: str
    
    # New features
    language: str
    theme: str
    regenerate_puzzle: str
    regenerating_puzzle: str
    puzzle_regenerated: str
    other_unchanged: str


class PDFTranslations(TypedDict):
    # PDF labels
    word_search: str
    solution: str
    puzzle_number: str
    solution_prefix: str
    words: str
    
    # Error messages
    no_space_vertical: str
    no_space_horizontal: str
    no_space_solution: str
    no_space_grid: str


class Translations(TypedDict):
    ui: UITranslations
    pdf: PDFTranslations


TRANSLATIONS: dict[str, Translations] = {
    "en": {
        "ui": {
            "app_title": "Word Search Book Maker",
            "configuration": "CONFIGURATION",
            "preview": "PREVIEW",
            "ready": "Ready.",
            "preparing_generation": "Preparing generation…",
            "cancelling": "Cancelling safely…",
            "operation_cancelled": "Operation cancelled; no incomplete PDF was created.",
            "operation_failed": "The operation could not be completed.",
            "csv_file": "1. CSV File",
            "load_csv": "LOAD CSV",
            "csv_not_loaded": "No CSV loaded yet.",
            "csv_loaded": "CSV loaded successfully\nPuzzles: {puzzles}\nTotal words: {total}\nWords per puzzle: {range}",
            "csv_ready": "CSV ready to generate.",
            "csv_line_1": "Puzzles:",
            "csv_line_2": "Total words:",
            "csv_line_3": "Words per puzzle:",
            "csv_line_4": "No CSV loaded.",
            "page_and_margins": "2. Page and margins",
            "preset": "Preset",
            "width": "Width",
            "height": "Height",
            "unit": "Unit",
            "margin_top": "Top margin",
            "margin_bottom": "Bottom margin",
            "margin_left": "Left margin",
            "margin_right": "Right margin",
            "puzzle": "3. Puzzle",
            "rows": "Rows",
            "columns": "Columns",
            "allow_reversed": "Allow reversed words",
            "allow_diagonals": "Allow diagonals",
            "allow_intersections": "Allow intersections",
            "words_and_layout": "4. Words and layout",
            "title": "Title",
            "subtitle": "Subtitle",
            "grid_position": "Grid position",
            "position_x": "Position X (%)",
            "position_y": "Position Y (%)",
            "font": "Font",
            "title_size": "Title size",
            "subtitle_size": "Subtitle size",
            "grid_font_size": "Grid letter size",
            "words_font_size": "Words letter size",
            "cell_size": "Cell (pt)",
            "line_width": "Line width",
            "word_columns": "Word columns",
            "order": "Order",
            "word_list": "List",
            "auto_fit": "Auto fit",
            "solutions_and_export": "5. Solutions and export",
            "include_solutions": "Include solutions",
            "style": "Style",
            "export_order": "Order",
            "selected_puzzles": "Puzzles (all/1-3)",
            "output_pdf": "PDF file",
            "folder": "Folder",
            "open_folder": "OPEN FOLDER",
            "config_json": "6. Configuration JSON",
            "save": "Save",
            "load": "Load",
            "reset": "Reset",
            "previous": "← Previous",
            "next": "Next →",
            "view_solution": "View solution",
            "preview_button": "PREVIEW",
            "generate_pdf": "GENERATE PDF",
            "cancel": "Cancel",
            "no_pages": "No pages",
            "solution": "Solution",
            "puzzle": "Puzzle",
            "select_csv": "Select CSV",
            "invalid_csv": "Invalid CSV",
            "save_config": "Save configuration",
            "load_config": "Load configuration",
            "reset_config": "Reset configuration",
            "save_pdf": "Save PDF book",
            "config_invalid": "Invalid configuration",
            "config_saved": "Configuration saved: {name}",
            "config_loaded": "Configuration loaded: {name}",
            "defaults_restored": "Default values restored.",
            "missing_csv": "Missing CSV",
            "cannot_open_folder": "Could not open folder",
            "pdf_generated": "PDF generated",
            "generation_error": "Generation error",
            "generating_puzzle": "Generating puzzle {current} of {total}",
            "puzzle_generated": "Puzzle {number} generated",
            "rendering_puzzle": "Rendering puzzle {number}",
            "rendering_solutions": "Rendering solutions {numbers}",
            "page_prepared": "Page {current} of {total} prepared",
            "language": "Language",
            "theme": "Theme",
            "regenerate_puzzle": "REGENERATE PUZZLE",
            "regenerating_puzzle": "Regenerating puzzle {number}…",
            "puzzle_regenerated": "Puzzle {number} regenerated. Other puzzles unchanged.",
            "other_unchanged": "Other puzzles remain unchanged.",
        },
        "pdf": {
            "word_search": "Word Search",
            "solution": "Solution",
            "puzzle_number": "Puzzle {number}",
            "solution_prefix": "Solution — ",
            "words": "Words",
            "no_space_vertical": "Not enough vertical space for the grid and word list.",
            "no_space_horizontal": "Not enough horizontal space for the grid.",
            "no_space_solution": "Not enough space for four solutions on the page.",
            "no_space_grid": "Not enough space for the grid; reduce content or margins.",
            "no_margin_space": "Margins leave no usable space on the page.",
        },
    },
    "es": {
        "ui": {
            "app_title": "Word Search Book Maker",
            "configuration": "CONFIGURACIÓN",
            "preview": "PREVISUALIZACIÓN",
            "ready": "Listo.",
            "preparing_generation": "Preparando generación…",
            "cancelling": "Cancelando de forma segura…",
            "operation_cancelled": "Operación cancelada; no se creó un PDF incompleto.",
            "operation_failed": "La operación no pudo completarse.",
            "csv_file": "1. Archivo CSV",
            "load_csv": "CARGAR CSV",
            "csv_not_loaded": "Aún no se ha cargado ningún CSV.",
            "csv_loaded": "CSV cargado correctamente\nSopas: {puzzles}\nPalabras totales: {total}\nPalabras por sopa: {range}",
            "csv_ready": "CSV listo para generar.",
            "csv_line_1": "Sopas:",
            "csv_line_2": "Palabras totales:",
            "csv_line_3": "Palabras por sopa:",
            "csv_line_4": "No se ha cargado ningún CSV.",
            "page_and_margins": "2. Página y márgenes",
            "preset": "Preset",
            "width": "Ancho",
            "height": "Alto",
            "unit": "Unidad",
            "margin_top": "Margen superior",
            "margin_bottom": "Margen inferior",
            "margin_left": "Margen izquierdo",
            "margin_right": "Margen derecho",
            "puzzle": "3. Sopa",
            "rows": "Filas",
            "columns": "Columnas",
            "allow_reversed": "Permitir palabras invertidas",
            "allow_diagonals": "Permitir diagonales",
            "allow_intersections": "Permitir cruces",
            "words_and_layout": "4. Palabras y diseño",
            "title": "Título",
            "subtitle": "Subtítulo",
            "grid_position": "Posición sopa",
            "position_x": "Posición X (%)",
            "position_y": "Posición Y (%)",
            "font": "Fuente",
            "title_size": "Tamaño título",
            "subtitle_size": "Tamaño subtítulo",
            "grid_font_size": "Letra cuadrícula",
            "words_font_size": "Letra palabras",
            "cell_size": "Casilla (pt)",
            "line_width": "Grosor línea",
            "word_columns": "Columnas palabras",
            "order": "Orden",
            "word_list": "Lista",
            "auto_fit": "Ajustar automáticamente",
            "solutions_and_export": "5. Soluciones y exportación",
            "include_solutions": "Incluir soluciones",
            "style": "Estilo",
            "export_order": "Orden",
            "selected_puzzles": "Sopas (todas/1-3)",
            "output_pdf": "Archivo PDF",
            "folder": "Carpeta",
            "open_folder": "ABRIR CARPETA",
            "config_json": "6. Configuración JSON",
            "save": "Guardar",
            "load": "Cargar",
            "reset": "Restablecer",
            "previous": "← Anterior",
            "next": "Siguiente →",
            "view_solution": "Ver solución",
            "preview_button": "PREVISUALIZAR",
            "generate_pdf": "GENERAR PDF",
            "cancel": "Cancelar",
            "no_pages": "Sin páginas",
            "solution": "Solución",
            "puzzle": "Sopa",
            "select_csv": "Seleccionar CSV",
            "invalid_csv": "CSV inválido",
            "save_config": "Guardar configuración",
            "load_config": "Cargar configuración",
            "reset_config": "Restablecer configuración",
            "save_pdf": "Guardar libro PDF",
            "config_invalid": "Configuración inválida",
            "config_saved": "Configuración guardada: {name}",
            "config_loaded": "Configuración cargada: {name}",
            "defaults_restored": "Valores predeterminados restaurados.",
            "missing_csv": "Falta el CSV",
            "cannot_open_folder": "No se pudo abrir la carpeta",
            "pdf_generated": "PDF generado",
            "generation_error": "Error de generación",
            "generating_puzzle": "Generando sopa {current} de {total}",
            "puzzle_generated": "Sopa {number} generada",
            "rendering_puzzle": "Renderizando sopa {number}",
            "rendering_solutions": "Renderizando soluciones {numbers}",
            "page_prepared": "Página {current} de {total} preparada",
            "language": "Idioma",
            "theme": "Tema",
            "regenerate_puzzle": "REGENERAR SOPA",
            "regenerating_puzzle": "Regenerando sopa {number}…",
            "puzzle_regenerated": "Sopa {number} regenerada. Otras sopas sin cambios.",
            "other_unchanged": "Otras sopas permanecen sin cambios.",
        },
        "pdf": {
            "word_search": "Sopa de letras",
            "solution": "Solución",
            "puzzle_number": "Sopa {number}",
            "solution_prefix": "Solución — ",
            "words": "Palabras",
            "no_space_vertical": "No hay espacio vertical suficiente para la cuadrícula y la lista de palabras.",
            "no_space_horizontal": "No hay espacio horizontal suficiente para la cuadrícula.",
            "no_space_solution": "No hay espacio suficiente para cuatro soluciones en la página.",
            "no_space_grid": "No hay espacio suficiente para la cuadrícula; reduzca el contenido o los márgenes.",
            "no_margin_space": "Los márgenes no dejan espacio útil en la página.",
        },
    },
}

SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())
