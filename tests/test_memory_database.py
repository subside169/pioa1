import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableAlreadyExistsError, TableNotFoundError, MissingColumnError, RecordNotFoundError
from src.db.backend.errors import UnknownColumnError, DuplicateIDError

class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
        self.columns = ("book_id", "title", "author", "year", "genre")

    def test_create_table(self):
        self.db.create_table("books", self.columns)
        self.assertTrue(self.db._table_exists("books"))

    def test_create_duplicate_table(self):
        self.db.create_table("books", self.columns)
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("books", self.columns)

    def test_insert_and_select(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "Война и мир", "author": "Толстой", "year": 1869, "genre": "роман"})
        records = self.db.select_records("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Война и мир")

    def test_select_with_filters(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "X"})
        self.db.insert_record("books", {"book_id": 2, "title": "A", "author": "C", "year": 2001, "genre": "Y"})
        res = self.db.select_records("books", title="A")
        self.assertEqual(len(res), 2)
        res = self.db.select_records("books", year=2000)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["author"], "B")

    def test_insert_missing_column(self):
        self.db.create_table("books", self.columns)
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("books", {"book_id": 1, "title": "A"})  # нет author, year, genre

    def test_insert_unknown_column(self):
        self.db.create_table("books", self.columns)
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "X", "extra": 123})

    def test_update_record(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "Старое", "author": "Автор", "year": 2000, "genre": "жанр"})
        updated = self.db.update_record("books", 1, title="Новое", year=2021)
        self.assertEqual(updated["title"], "Новое")
        self.assertEqual(updated["year"], 2021)
        records = self.db.select_records("books", book_id=1)
        self.assertEqual(records[0]["title"], "Новое")

    def test_update_nonexistent_record(self):
        self.db.create_table("books", self.columns)
        with self.assertRaises(RecordNotFoundError):
            self.db.update_record("books", 999, title="Нет")

    def test_delete_record(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        self.db.delete_record("books", 1)
        self.assertEqual(len(self.db.select_records("books")), 0)

    def test_delete_nonexistent_record(self):
        self.db.create_table("books", self.columns)
        with self.assertRaises(RecordNotFoundError):
            self.db.delete_record("books", 999)

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("books")

    def test_insert_duplicate_id(self):
        self.db.create_table("books", self.columns)
        self.db.insert_record("books", {"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        with self.assertRaises(DuplicateIDError):
            self.db.insert_record("books", {"book_id": 1, "title": "D", "author": "E", "year": 2020, "genre": "F"})
