import unittest
from src.db.backend.table import Table
from src.db.backend.errors import (
    UnknownColumnError,
    DuplicateIDError,
    InvalidValueTypeError,
    ImmutableFieldError,
)


class TestTableIndexes(unittest.TestCase):
    def setUp(self):
        self.columns = ("book_id", "title", "author", "year", "genre")

    # --- Старые тесты ---
    def test_index_creation(self):
        table = Table(self.columns, indexed_columns=["author", "year"])
        self.assertIn("author", table._indexes)
        self.assertIn("year", table._indexes)
        with self.assertRaises(UnknownColumnError):
            Table(self.columns, indexed_columns=["nonexistent"])

    def test_insert_and_select_with_index(self):
        table = Table(self.columns, indexed_columns=["author"])
        rec1 = {"book_id": 1, "title": "A", "author": "Пушкин", "year": 1830, "genre": "поэзия"}
        rec2 = {"book_id": 2, "title": "B", "author": "Толстой", "year": 1869, "genre": "роман"}
        table.insert_record(rec1)
        table.insert_record(rec2)
        res = table.select_records(author="Пушкин")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["title"], "A")
        res = table.select_records(year=1869)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["author"], "Толстой")

    def test_index_updated_after_update(self):
        table = Table(self.columns, indexed_columns=["author"])
        table.insert_record({"book_id": 1, "title": "X", "author": "Пушкин", "year": 1830, "genre": "поэзия"})
        table.update_record(1, author="Лермонтов")
        self.assertEqual(len(table.select_records(author="Пушкин")), 0)
        self.assertEqual(len(table.select_records(author="Лермонтов")), 1)

    def test_index_after_delete(self):
        table = Table(self.columns, indexed_columns=["genre"])
        table.insert_record({"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "фантастика"})
        table.insert_record({"book_id": 2, "title": "C", "author": "D", "year": 2005, "genre": "фантастика"})
        table.delete_record(1)
        res = table.select_records(genre="фантастика")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["book_id"], 2)

    def test_index_with_multiple_filters(self):
        table = Table(self.columns, indexed_columns=["author", "year"])
        table.insert_record({"book_id": 1, "title": "A", "author": "Пушкин", "year": 1830, "genre": "поэзия"})
        table.insert_record({"book_id": 2, "title": "B", "author": "Пушкин", "year": 1833, "genre": "роман"})
        res = table.select_records(author="Пушкин", year=1833)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["title"], "B")

    def test_insert_duplicate_id_raises_error(self):
        table = Table(self.columns, indexed_columns=["book_id"])
        table.insert_record({"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        with self.assertRaises(DuplicateIDError):
            table.insert_record({"book_id": 1, "title": "D", "author": "E", "year": 2020, "genre": "F"})

    # --- Новые тесты ---
    def test_insert_invalid_type_raises_error(self):
        # Создаём таблицу со схемой типов
        table = Table(
            self.columns,
            column_types={"book_id": int, "year": int, "title": str, "author": str, "genre": str}
        )
        with self.assertRaises(InvalidValueTypeError):
            table.insert_record({"book_id": "abc", "title": "A", "author": "B", "year": 2000, "genre": "C"})

    def test_update_changes_id_raises_immutable_field_error(self):
        table = Table(
            self.columns,
            column_types={"book_id": int, "year": int, "title": str, "author": str, "genre": str}
        )
        table.insert_record({"book_id": 1, "title": "A", "author": "B", "year": 2000, "genre": "C"})
        with self.assertRaises(ImmutableFieldError):
            table.update_record(1, book_id=2)
