import unittest
import tempfile
from src.db.backend.csv_file import CsvDatabase
from src.db.backend.errors import TableNotFoundError

class TestCsvDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = CsvDatabase(self.temp_dir.name)
        self.columns = ("book_id", "title", "author", "year", "genre")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persistence(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        second_db = CsvDatabase(self.temp_dir.name)
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
