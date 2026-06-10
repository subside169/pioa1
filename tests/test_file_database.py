import unittest
import tempfile
from unittest.mock import patch
from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, StorageSaveError


class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = FileDatabase(self.temp_dir.name)
        self.columns = ("book_id", "title", "author", "year", "genre")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persistence(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        second_db = FileDatabase(self.temp_dir.name)
        records = second_db.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "A")

    def test_select_filters(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "X", "author": "Y", "year": 2020, "genre": "Z"})
        self.db.insert_record("books", {"book_id": 2, "title": "X", "author": "Z", "year": 2021, "genre": "Z"})
        res = self.db.select_records("books", genre="Z")
        self.assertEqual(len(res), 2)
        res = self.db.select_records("books", year=2020)
        self.assertEqual(len(res), 1)

    def test_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("books")

    def test_save_error_raises_storage_save_error(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        with patch("json.dump", side_effect=OSError("Disk full")):
            with self.assertRaises(StorageSaveError):
                self.db._save_table("books", self.db._load_table("books"))
