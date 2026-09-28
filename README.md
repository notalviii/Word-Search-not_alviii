# Word Search Book Maker v2.0.0

A Windows desktop application that converts a UTF-8 CSV file into a word search puzzle book and its solutions in PDF format. The application maintains the grid, words and coordinates as domain data; the solution is drawn over **the same grid**, never over a regenerated puzzle.

## Version 2.0.0 New Features

### Multi-language Support
- **Application Interface**: The UI now supports English and Spanish
- **PDF Generation**: The selected language determines the language of all generated PDF interface text (titles, labels, headings)
- **Language Selection**: Choose your preferred language from the settings panel
- **Persistence**: Your language choice is saved in the configuration file
- **Extensible**: The architecture allows for easy addition of new languages in the future

Note: User-provided puzzle words are never translated automatically. CSV words remain exactly as supplied, apart from existing normalisation rules.

### Custom Visual Themes
- **Light/Clean**: A clean, modern light theme
- **Dark/Modern**: A sleek dark theme for reduced eye strain
- **Soft/Minimal**: A gentle, minimal colour scheme
- **High Contrast**: High contrast theme for accessibility
- **Theme Selection**: Choose your preferred theme from the settings panel
- **Persistence**: Your theme choice is saved in the configuration file

### Individual Puzzle Regeneration
- **Regenerate Single Puzzle**: Regenerate only the currently selected puzzle without regenerating the entire project
- **Preserves Other Puzzles**: Other puzzles remain completely unchanged
- **Valid Regeneration**: The regenerated puzzle receives new valid grid and coordinate data
- **Exact Solution**: The solution corresponds exactly to the new grid
- **CSV Unchanged**: The source CSV file is not modified
- **Stable Numbering**: Puzzle numbering and ordering remain stable
- **Preview**: The regenerated puzzle can be previewed before export

### Improved Word Spacing
- **Better Spacing Algorithm**: Modified puzzle generation to prefer placements with better word separation
- **Less Crowding**: Words are slightly more separated from each other where possible
- **Respects Constraints**: The improvement respects existing grid size and direction settings
- **Graceful Fallback**: If preferred spacing cannot be achieved, the system falls back to existing placement behaviour
- **Configurable**: The "Prefer spacing" option in the puzzle settings allows you to enable or disable this feature

### Enhanced Windows Executable
- **Improved Packaging**: Updated PyInstaller configuration for better resource inclusion
- **Complete Dependencies**: All required dependencies are included in the executable
- **Translation Files**: Translation files are bundled with the executable
- **Theme Resources**: Theme resources are included in the package
- **No Console**: The executable launches without a console window
- **Standalone**: No Python installation required on the target computer

## Requirements and Installation

- Windows and Python 3.12 or later
- Updated `pip`

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

If PowerShell does not allow activating the environment, you can run `.\.venv\Scripts\python.exe main.py` directly.

## Usage

1. Click **LOAD CSV** and select a UTF-8 file
2. Configure page, margins, grid, directions and layout
3. Click **PREVIEW**. Generation occurs outside the window thread
4. Navigate between puzzles, enable *View solution* and use `+`/`−` to zoom in or out
5. Choose the output path and click **GENERATE PDF**. You can cancel without preserving an incomplete PDF

The panel allows you to select `all` puzzles, specific numbers (`1,4,8`) or ranges (`1-5,9`). It also allows two orders: consecutive puzzle/solution or all puzzles followed by all solutions.

**New in v2.0.0**:
- Use the **Language** dropdown in the settings to switch between English and Spanish
- Use the **Theme** dropdown in the settings to switch between visual themes
- Use the **REGENERATE PUZZLE** button to regenerate only the currently selected puzzle
- Enable **Prefer spacing** in the puzzle settings to improve word separation

## CSV Format

No header. Each line is a puzzle and each comma-separated field is a word. Lines may have different numbers of words.

```csv
perro,gato,tigre,león,oso
caballo,VACA,cerdo,oveja,gallina
árbol,niño,pingüino,ÑANDÚ,camión
```

The application removes external spaces and converts internally to uppercase: ` árbol ` becomes `ÁRBOL`. It preserves accents, `Ñ` and `Ü`. Before generation, it blocks empty files, empty lines, empty fields (including trailing commas), duplicates within the same puzzle, non-UTF-8 encoding and words incompatible with the grid.

A file ready for testing is available at [examples/palabras.csv](examples/palabras.csv) and a configuration at [examples/configuracion_animales.json](examples/configuracion_animales.json).

## Configuration and PDF

- Page sizes A4, Letter, 6 × 9 in, 8.5 × 11 in and custom are independent of rows and columns
- The four margins are edited separately in the active page unit (`mm` or `in`)
- Activate directions individually; diagonals, reversed words and intersections are independent options
- *Auto fit* calculates the largest cell that fits together with titles and word list. If it does not fit, the application reports the error before export
- Save/load configuration in JSON from the interface. The CSV is not altered when loading a JSON

The PDF is created with ReportLab and uses lines, text and vector marks. Solutions use circles, lines or highlights over the coordinates preserved by the generator.

**New in v2.0.0**:
- Configuration files now include `language` and `theme` settings
- Old configuration files without these fields will load with sensible defaults (English, Light theme)
- The `prefer_spacing` grid option controls word spacing behaviour

## Testing

```powershell
python -m unittest discover -s tests -v
```

The suite covers Spanish normalisation, variable/erroneous CSV, generation, direction constraints, coordinates, configurations, layout, valid PDF, language switching, theme loading, individual puzzle regeneration, word spacing behaviour and backwards compatibility. For manual performance tests, use CSV with 10, 50, 100, 500 and 1,000 lines; progress indicates current puzzle/page and the Cancel button leaves the final destination intact.

**New in v2.0.0**:
- Tests for UI language switching
- Tests for PDF language switching
- Tests for Spanish and English PDF output
- Tests for translation fallback behaviour
- Tests for theme loading and saving
- Tests for individual puzzle regeneration
- Tests for ensuring other puzzles remain unchanged during regeneration
- Tests for ensuring regenerated coordinates match the regenerated grid
- Tests for ensuring the CSV remains unchanged during regeneration
- Tests for word-spacing behaviour
- Tests for backwards compatibility with old configuration files

## Windows Executable

After installing dependencies, run:

```powershell
.\build_windows.bat
```

The executable will appear in `dist\WordSearchBookMaker.exe`. The manual equivalent is:

```powershell
pyinstaller --noconfirm --clean WordSearchBookMaker.spec
```

**Updated in v2.0.0**:
- Uses a spec file for better control over packaging
- Includes translation files and theme resources
- Includes all required runtime assets
- No Python installation required on target computer
- Launches without console window

## Troubleshooting

- **`python` opens Microsoft Store or does not exist**: Install Python 3.12+ from python.org and check `py -3.12 --version`
- **CSV not loaded**: Save it as UTF-8 and check for trailing commas, duplicates and blank lines
- **Cannot place a puzzle**: Increase rows/columns, allow intersections or activate more directions
- **Layout does not fit**: Reduce margins, title/list or enable auto fit
- **Window does not open**: Confirm the virtual environment is active and that `customtkinter` was installed from `requirements.txt`
- **Language not changing**: Ensure the language is saved in the configuration file
- **Theme not applying**: Some themes may have limited effect due to CustomTkinter's constraints

## Configuration Options (v2.0.0)

### New Settings
- `language`: Application and PDF language (`en` or `es`, default: `en`)
- `theme`: Visual theme (`light`, `dark`, `soft`, or `high_contrast`, default: `light`)
- `grid.prefer_spacing`: Whether to prefer less crowded word placements (default: `true`)

### Backwards Compatibility
- Old configuration files without the new settings will load with defaults
- All existing settings are preserved
- No existing functionality is removed

## Language Support

The application currently supports:
- **English (en)**: Full UI and PDF support
- **Spanish (es)**: Full UI and PDF support

Additional languages can be added by extending the translation dictionaries in `app/i18n/translations.py`.

## Theme Options

The application includes four built-in themes:
- **Light**: Clean, modern light theme (default)
- **Dark**: Sleek dark theme for reduced eye strain
- **Soft**: Gentle, minimal colour scheme
- **High Contrast**: High contrast theme for accessibility

## Architecture Notes

- The core rule remains: A solution must always be generated from the exact grid and coordinates of its corresponding puzzle
- The application is stable, maintainable and suitable for distribution as a Windows executable
- The localisation system is shared between UI and PDF generation to avoid duplication
- The theme system uses CustomTkinter's built-in theming with some custom extensions
- Individual puzzle regeneration preserves all other puzzles and their grids
