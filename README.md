# Word Search Book Maker

Desktop application for Windows that converts a CSV file into a word search puzzle book and its solutions in PDF format. The application keeps the grid, words and coordinates as domain data; the solution is drawn on **the same grid**, never on a regenerated puzzle.

## Requirements and Installation

- Windows and Python 3.12 or later.
- Up-to-date `pip`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

If PowerShell does not allow the environment to be activated, you can run `.\.venv\Scripts\python.exe main.py` directly.

## Usage

1. Click **LOAD CSV** and select a UTF-8 file.
2. Configure the page, margins, grid, directions and layout.
3. Click **PREVIEW**. Generation takes place outside the window thread.
4. Navigate between the puzzles, enable *View solution*, and use `+`/`−` to zoom in or out.
5. Choose the output path and click **GENERATE PDF**. You can cancel without an incomplete PDF being kept.

The panel allows you to select `all` puzzles, specific numbers (`1,4,8`) or ranges (`1-5,9`). It also provides two ordering options: puzzle/solution consecutively, or all puzzles followed by all solutions.

## CSV Format

There is no header. Each line represents one puzzle, and each comma-separated field is a word. Lines can contain different numbers of words.

```csv
dog,cat,tiger,lion,bear
horse,COW,pig,sheep,hen
tree,child,penguin,EMU,lorry
```

The application removes leading and trailing spaces and converts text to uppercase internally: ` tree ` becomes `TREE`. Accented characters, `Ñ` and `Ü` are preserved. Before generation, empty files, empty lines, empty fields (including trailing commas), duplicates within the same puzzle, non-UTF-8 encoding and words that are incompatible with the grid are rejected.

A ready-to-use test file is available at [examples/palabras.csv](examples/palabras.csv), along with a configuration file at [examples/configuracion_animales.json](examples/configuracion_animales.json).

## Configuration and PDF

- A4, Letter, 6 × 9 in, 8.5 × 11 in and custom page sizes are independent of the number of rows and columns.
- All four margins can be edited separately using the active page unit (`mm` or `in`).
- Directions can be enabled individually; diagonals, reversed words and intersections are independent options.
- *Auto-fit* calculates the largest cell size that fits alongside the titles and word list. If it does not fit, the application reports the error before exporting.
- Save/load the configuration as JSON directly from the interface. Loading a JSON file does not modify the CSV.

The PDF is created using ReportLab and uses vector lines, text and markers. Solutions use circles, lines or highlights drawn over the coordinates retained by the generator.

## Testing

```powershell
python -m unittest discover -s tests -v
```

The test suite covers Spanish normalisation, variable/invalid CSV files, generation, direction restrictions, coordinates, configurations, layout and a valid PDF. For manual performance testing, use CSV files containing 10, 50, 100, 500 and 1,000 lines; the progress indicator shows the current puzzle/page, and the Cancel button leaves the final destination untouched.

## Windows Executable

After installing the dependencies, run:

```powershell
.\build_windows.bat
```

The executable will appear at `dist\WordSearchBookMaker.exe`. The equivalent manual command is:

```powershell
pyinstaller --noconfirm --clean --onefile --windowed --name WordSearchBookMaker main.py
```

## Troubleshooting

- **`python` opens the Microsoft Store or does not exist:** install Python 3.12+ from python.org and check `py -3.12 --version`.
- **CSV not loaded:** save it as UTF-8 and check for trailing commas, duplicates and blank lines.
- **A puzzle cannot be placed:** increase the number of rows/columns, allow intersections or enable more directions.
- **The layout does not fit:** reduce the margins, title/word list size, or enable auto-fit.
- **The window does not open:** make sure the virtual environment is active and that `customtkinter` was installed from `requirements.txt`.
