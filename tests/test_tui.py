import unittest
from unittest.mock import Mock, patch
from io import StringIO
from src.db.tui import BookTUI


class TestBookTUI(unittest.TestCase):
    def setUp(self):
        self.tui = BookTUI()

    def _mock_input(self, responses):
        return Mock(side_effect=responses)

    def _get_output(self, func, input_func, *args, **kwargs):
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            func(input_func=input_func, *args, **kwargs)
            return fake_out.getvalue()

    # --- _print_menu ---
    def test_menu_display(self):
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui._print_menu()
        self.assertIn("=== База книг ===", fake_out.getvalue())

    # --- _read_int ---
    def test_read_int_valid(self):
        mock = self._mock_input(["42"])
        with patch("sys.stdout", new_callable=StringIO):
            result = self.tui._read_int("id: ", input_func=mock)
        self.assertEqual(result, 42)

    def test_read_int_invalid_then_valid(self):
        mock = self._mock_input(["abc", "10"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            result = self.tui._read_int("id: ", input_func=mock)
        self.assertIn("Ошибка: введите целое число.", fake_out.getvalue())
        self.assertEqual(result, 10)

    # --- _read_optional_int ---
    def test_read_optional_int_empty(self):
        mock = self._mock_input([""])
        with patch("sys.stdout", new_callable=StringIO):
            result = self.tui._read_optional_int("year: ", input_func=mock)
        self.assertIsNone(result)

    def test_read_optional_int_invalid_then_valid(self):
        mock = self._mock_input(["xyz", "2021"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            result = self.tui._read_optional_int("year: ", input_func=mock)
        self.assertIn("Ошибка: введите целое число или оставьте поле пустым.", fake_out.getvalue())
        self.assertEqual(result, 2021)

    # --- _add_book ---
    def test_add_book(self):
        inputs = self._mock_input(["1", "Война и мир", "Толстой", "1869", "роман"])
        out = self._get_output(self.tui._add_book, inputs)
        self.assertIn("Запись добавлена: (1, 'Война и мир', 'Толстой', 1869, 'роман')", out)

    def test_add_duplicate_id(self):
        self.tui.table.create_record(1, "Book1", "Author1", 2000, "genre")
        inputs = self._mock_input(["1", "Book2", "Author2", "2001", "genre"])
        out = self._get_output(self.tui._add_book, inputs)
        self.assertIn("Книга с id=1 уже существует.", out)

    # --- _show_all_books ---
    def test_show_all_books_empty(self):
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui._show_all_books()
        self.assertIn("Записи не найдены.", fake_out.getvalue())

    def test_show_all_after_add(self):
        self.tui.table.create_record(1, "Title", "Author", 2020, "genre")
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui._show_all_books()
        self.assertIn("(1, 'Title', 'Author', 2020, 'genre')", fake_out.getvalue())

    # --- _find_books_by_filter (ранее не покрыт) ---
    def test_find_books_empty(self):
        inputs = self._mock_input(["", "", "", "", ""])
        out = self._get_output(self.tui._find_books_by_filter, inputs)
        self.assertIn("Записи не найдены.", out)

    def test_find_books_by_id(self):
        self.tui.table.create_record(1, "A", "B", 2000, "C")
        inputs = self._mock_input(["1", "", "", "", ""])
        out = self._get_output(self.tui._find_books_by_filter, inputs)
        self.assertIn("(1, 'A', 'B', 2000, 'C')", out)

    def test_find_books_by_genre(self):
        self.tui.table.create_record(1, "A", "B", 2000, "роман")
        self.tui.table.create_record(2, "D", "E", 2001, "повесть")
        inputs = self._mock_input(["", "", "", "", "роман"])
        out = self._get_output(self.tui._find_books_by_filter, inputs)
        self.assertIn("(1, 'A', 'B', 2000, 'роман')", out)
        self.assertNotIn("повесть", out)

    # --- _update_book ---
    def test_update_book(self):
        self.tui.table.create_record(1, "Old", "Author", 2000, "genre")
        inputs = self._mock_input(["1", "New", "", "2021", ""])
        out = self._get_output(self.tui._update_book, inputs)
        self.assertIn("Запись обновлена: (1, 'New', 'Author', 2021, 'genre')", out)

    def test_update_nonexistent(self):
        inputs = self._mock_input(["999", "", "", "", ""])
        out = self._get_output(self.tui._update_book, inputs)
        self.assertIn("Запись с id=999 не найдена.", out)

    # --- _delete_book ---
    def test_delete_book(self):
        self.tui.table.create_record(1, "Book", "Author", 2000, "genre")
        inputs = self._mock_input(["1"])
        out = self._get_output(self.tui._delete_book, inputs)
        self.assertIn("Запись удалена.", out)
        self.assertEqual(len(self.tui.table.select_record()), 0)

    def test_delete_nonexistent(self):
        inputs = self._mock_input(["999"])
        out = self._get_output(self.tui._delete_book, inputs)
        self.assertIn("Запись с id=999 не найдена.", out)

    # --- run (покрываем все варианты меню) ---
    def test_run_add_and_exit(self):
        inputs = self._mock_input(["1", "1", "Title", "Author", "2020", "genre", "0"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui.run(input_func=inputs)
        out = fake_out.getvalue()
        self.assertIn("Запись добавлена", out)
        self.assertIn("Выход из программы.", out)

    def test_run_show_all(self):
        self.tui.table.create_record(1, "X", "Y", 2022, "Z")
        inputs = self._mock_input(["2", "0"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui.run(input_func=inputs)
        self.assertIn("(1, 'X', 'Y', 2022, 'Z')", fake_out.getvalue())

    def test_run_find_books(self):
        self.tui.table.create_record(1, "A", "B", 2000, "C")
        inputs = self._mock_input(["3", "1", "", "", "", "", "0"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui.run(input_func=inputs)
        self.assertIn("(1, 'A', 'B', 2000, 'C')", fake_out.getvalue())

    def test_run_update(self):
        self.tui.table.create_record(1, "Old", "Author", 2000, "genre")
        inputs = self._mock_input(["4", "1", "New", "", "", "", "0"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui.run(input_func=inputs)
        self.assertIn("Запись обновлена: (1, 'New', 'Author', 2000, 'genre')", fake_out.getvalue())

    def test_run_delete(self):
        self.tui.table.create_record(1, "Book", "Author", 2000, "genre")
        inputs = self._mock_input(["5", "1", "0"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui.run(input_func=inputs)
        self.assertIn("Запись удалена.", fake_out.getvalue())

    def test_run_invalid_choice(self):
        inputs = self._mock_input(["abc", "0"])
        with patch("sys.stdout", new_callable=StringIO) as fake_out:
            self.tui.run(input_func=inputs)
        self.assertIn("Неизвестная команда.", fake_out.getvalue())
