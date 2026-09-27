from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.csv.parser import import_csv, normalize_word


class CsvParserTests(unittest.TestCase):
    def _csv(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", delete=False, newline="")
        handle.write(text)
        handle.close()
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return Path(handle.name)

    def test_normalization_keeps_spanish_characters(self) -> None:
        self.assertEqual(normalize_word(" perro "), "PERRO")
        self.assertEqual(normalize_word("árbol"), "ÁRBOL")
        self.assertEqual(normalize_word("niño"), "NIÑO")
        self.assertEqual(normalize_word("pingüino"), "PINGÜINO")

    def test_each_line_becomes_one_puzzle_with_variable_word_count(self) -> None:
        result = import_csv(self._csv(" perro ,gAtO, árbol\nNIÑO,ÑANDÚ\n"))
        self.assertTrue(result.success, [error.display() for error in result.errors])
        assert result.book is not None
        self.assertEqual(len(result.book.puzzles), 2)
        self.assertEqual([word.text for word in result.book.puzzles[0].words], ["PERRO", "GATO", "ÁRBOL"])
        self.assertEqual([word.text for word in result.book.puzzles[1].words], ["NIÑO", "ÑANDÚ"])

    def test_empty_field_duplicate_and_empty_line_are_blocking(self) -> None:
        result = import_csv(self._csv("PERRO,,GATO\nLEÓN,LEÓN\n\n"))
        self.assertFalse(result.success)
        messages = "\n".join(error.display() for error in result.errors)
        self.assertIn("palabra vacía", messages)
        self.assertIn("duplicada", messages)
        self.assertIn("línea está vacía", messages)

    def test_empty_file_is_explicitly_rejected(self) -> None:
        result = import_csv(self._csv("  \n"))
        self.assertFalse(result.success)
        self.assertIn("vacío", result.errors[0].message)
