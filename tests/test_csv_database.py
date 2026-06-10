import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.db.backend.csv_file import CsvDatabase
from src.db.backend.errors import TableNotFoundError, InvalidStorageDataError, StorageSaveError


class TestCsvDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = CsvDatabase(self.temp_dir.name, int_columns=["book_id", "year"], indexed_columns=["book_id", "year"])
        self.columns = ("book_id", "title", "author", "year", "genre")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persistence(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        second_db = CsvDatabase(self.temp_dir.name, int_columns=["book_id", "year"], indexed_columns=["book_id", "year"])
        records = second_db.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "A")
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
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "1984", "author": "Orwell", "year": 1949, "genre": "dystopia"})
        records = self.db.select_records("books")
        self.assertEqual(records[0]["title"], "1984")
        self.assertEqual(records[0]["year"], 1949)

    def test_corrupted_csv(self):
        csv_path = Path(self.temp_dir.name) / "books.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("")
        with self.assertRaises(InvalidStorageDataError):
            self.db._load_table("books")

    def test_save_error_raises_storage_save_error(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        with patch("csv.DictWriter.writerows", side_effect=OSError("No space left on device")):
            with self.assertRaises(StorageSaveError):
                self.db._save_table("books", self.db._load_table("books"))
