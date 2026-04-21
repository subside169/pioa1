import unittest

from src.db.backend.memory import BookTable
from src.db.backend.errors import (
    DuplicateIDError,
    InvalidYearError,
    RecordNotFoundError,
)


class TestBookTable(unittest.TestCase):

    def setUp(self):
        self.table = BookTable()

        # тестовые данные
        self.books = [
            (1, "1984", "Orwell", 1949, "Dystopia"),
            (2, "Dune", "Herbert", 1965, "Sci-Fi"),
            (3, "It", "King", 1986, "Horror"),
            (4, "Foundation", "Asimov", 1951, "Sci-Fi"),
        ]

        for book in self.books:
            self.table.create_record(*book)

    # ---------- CREATE ----------

    def test_create_record(self):
        book = (10, "Test", "Author", 2000, "Test")
        result = self.table.create_record(*book)
        self.assertEqual(result, book)

    def test_create_record_negative_year(self):
        with self.assertRaises(InvalidYearError):
            self.table.create_record(100, "Bad", "Author", -1, "Test")

    def test_create_record_duplicate_id(self):
        with self.assertRaises(DuplicateIDError):
            self.table.create_record(1, "Duplicate", "Author", 2000, "Test")

    # ---------- SELECT ----------

    def test_select_all(self):
        result = self.table.select_record()
        self.assertEqual(result, self.books)

    def test_select_by_id(self):
        result = self.table.select_record(book_id=1)
        self.assertEqual(result, [self.books[0]])

    def test_select_by_author(self):
        result = self.table.select_record(author="King")
        self.assertEqual(result, [self.books[2]])

    def test_select_by_genre(self):
        result = self.table.select_record(genre="Sci-Fi")
        self.assertEqual(result, [self.books[1], self.books[3]])

    def test_select_no_results(self):
        result = self.table.select_record(author="Unknown")
        self.assertEqual(result, [])

    def test_select_record_skips_non_matching_records(self):
        result = self.table.select_record(title="Dune")
        self.assertEqual(result, [(2, "Dune", "Herbert", 1965, "Sci-Fi")])


    # ---------- UPDATE ----------

    def test_update_record(self):
        updated = self.table.update_record(1, title="Animal Farm")
        self.assertEqual(updated[1], "Animal Farm")

    def test_update_multiple_fields(self):
        updated = self.table.update_record(2, title="Dune Messiah", year=1969)
        self.assertEqual(updated[1], "Dune Messiah")
        self.assertEqual(updated[3], 1969)

    def test_update_invalid_year(self):
        with self.assertRaises(InvalidYearError):
            self.table.update_record(1, year=-100)

    def test_update_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record(999, title="Ghost")

    # ---------- DELETE ----------

    def test_delete_record(self):
        self.table.delete_record(1)
        result = self.table.select_record(book_id=1)
        self.assertEqual(result, [])

    def test_delete_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record(999)



