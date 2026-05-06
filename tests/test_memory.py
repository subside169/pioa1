import unittest
from src.db.backend.memory import BookTable
from src.db.backend.errors import (
    InvalidYearError,
    DuplicateIDError,
    RecordNotFoundError,
)


class TestBookTable(unittest.TestCase):
    def setUp(self):
        self.table = BookTable()
        self.assertIsInstance(self.table, BookTable)

    def test_create_record(self):
        test_data = (1, "Война и мир", "Лев Толстой", 1869, "роман")
        record = self.table.create_record(*test_data)
        self.assertEqual(record, test_data)

    def test_create_record_with_negative_year(self):
        with self.assertRaises(InvalidYearError) as context:
            self.table.create_record(1, "Книга", "Автор", -5, "жанр")
        self.assertEqual(str(context.exception), "Год не может быть отрицательным.")

    def test_create_record_duplicate_id(self):
        self.table.create_record(1, "Книга1", "Автор1", 2020, "жанр")
        with self.assertRaises(DuplicateIDError) as context:
            self.table.create_record(1, "Книга2", "Автор2", 2021, "жанр")
        self.assertEqual(str(context.exception), "Книга с id=1 уже существует.")

    def test_select_all(self):
        records = [
            (1, "А", "Б", 2000, "В"),
            (2, "Г", "Д", 2001, "Е"),
        ]
        for r in records:
            self.table.create_record(*r)
        self.assertEqual(self.table.select_record(), records)

    def test_select_with_filter(self):
        records = [
            (1, "А", "Б", 2000, "роман"),
            (2, "А", "Д", 2001, "повесть"),
            (3, "В", "Б", 2000, "роман"),
        ]
        for r in records:
            self.table.create_record(*r)

        result = self.table.select_record(genre="роман")
        self.assertEqual(result, [records[0], records[2]])

        result = self.table.select_record(author="Б", year=2000)
        self.assertEqual(result, [records[0], records[2]])

        result = self.table.select_record(book_id=2)
        self.assertEqual(result, [records[1]])

    def test_select_year_filter_skip(self):
        """Гарантирует покрытие continue при несовпадении года."""
        self.table.create_record(1, "A", "B", 2000, "X")
        self.table.create_record(2, "C", "D", 2001, "X")
        result = self.table.select_record(year=2000)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (1, "A", "B", 2000, "X"))

    def test_select_year_filter_no_match(self):
        self.table.create_record(1, "A", "B", 2000, "X")
        self.table.create_record(2, "C", "D", 2001, "X")
        result = self.table.select_record(year=9999)
        self.assertEqual(result, [])

    # Новые тесты для покрытия всех остальных continue
    def test_select_filter_no_match_by_id(self):
        self.table.create_record(1, "A", "B", 2000, "X")
        result = self.table.select_record(book_id=999)
        self.assertEqual(result, [])

    def test_select_filter_no_match_by_title(self):
        self.table.create_record(1, "A", "B", 2000, "X")
        result = self.table.select_record(title="Z")
        self.assertEqual(result, [])

    def test_select_filter_no_match_by_author(self):
        self.table.create_record(1, "A", "B", 2000, "X")
        result = self.table.select_record(author="Z")
        self.assertEqual(result, [])

    def test_select_filter_no_match_by_genre(self):
        self.table.create_record(1, "A", "B", 2000, "X")
        result = self.table.select_record(genre="Z")
        self.assertEqual(result, [])

    def test_update_record(self):
        self.table.create_record(1, "Старое название", "Автор", 2000, "жанр")
        updated = self.table.update_record(1, title="Новое название", year=2005)
        self.assertEqual(updated, (1, "Новое название", "Автор", 2005, "жанр"))
        self.assertEqual(self.table.select_record(book_id=1)[0], updated)

    def test_update_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError) as context:
            self.table.update_record(999, title="Неважно")
        self.assertEqual(str(context.exception), "Запись с id=999 не найдена.")

    def test_update_with_negative_year(self):
        self.table.create_record(1, "Книга", "Автор", 2000, "жанр")
        with self.assertRaises(InvalidYearError):
            self.table.update_record(1, year=-5)

    def test_delete_record(self):
        self.table.create_record(1, "Книга", "Автор", 2000, "жанр")
        self.table.delete_record(1)
        self.assertEqual(self.table.select_record(), [])

    def test_delete_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError) as context:
            self.table.delete_record(999)
        self.assertEqual(str(context.exception), "Запись с id=999 не найдена.")

