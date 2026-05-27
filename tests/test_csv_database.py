import unittest
import tempfile
from pathlib import Path
from src.db.backend.csv_file import CsvDatabase
from src.db.backend.errors import TableNotFoundError, InvalidStorageDataError

class TestCsvDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # Передаём список числовых колонок
        self.db = CsvDatabase(self.temp_dir.name, int_columns=["book_id", "year"])
        self.columns = ("book_id", "title", "author", "year", "genre")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persistence(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        second_db = CsvDatabase(self.temp_dir.name, int_columns=["book_id", "year"])
        records = second_db.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "A")
        # Проверяем, что year загрузился как число
        self.assertEqual(records[0]["year"], 2000)

    def test_select_filters(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "X", "author": "Y", "year": 2020, "genre": "Z"})
        self.db.insert_record("books", {"book_id": 2, "title": "X", "author": "Z", "year": 2021, "genre": "Z"})
        res = self.db.select_records("books", title="X")
        self.assertEqual(len(res), 2)
        res = self.db.select_records("books", year=2021)
        self.assertEqual(len(res), 1)

    def test_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("books")

    def test_string_field_with_digits(self):
        """Проверка, что название книги, состоящее из цифр, не становится числом."""
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949, "genre": "dystopia"})
        records = self.db.select_records("books")
        self.assertEqual(records[0]["title"], "1984")   # осталось строкой
        self.assertEqual(records[0]["year"], 1949)       # число
