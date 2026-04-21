import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.db.__main__ import main
from src.db.tui import BookTUI, run


class TestBookTUI(unittest.TestCase):
    def setUp(self) -> None:
        self.ui = BookTUI()
        self.ui._table.create_record(1, "1984", "Orwell", 1949, "Dystopia")
        self.ui._table.create_record(2, "Dune", "Herbert", 1965, "Sci-Fi")

    def test_read_int_retries_on_invalid_input(self):
        with patch("builtins.input", side_effect=["abc", "7"]):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                value = self.ui._read_int("id: ")

        self.assertEqual(value, 7)
        self.assertIn("Ошибка: введите целое число.", buffer.getvalue())

    def test_read_optional_int_retries_and_returns_none(self):
        with patch("builtins.input", side_effect=["abc", ""]):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                value = self.ui._read_optional_int("year: ")

        self.assertIsNone(value)
        self.assertIn(
            "Ошибка: введите целое число или оставьте поле пустым.",
            buffer.getvalue(),
        )

    def test_add_book_success(self):
        ui = BookTUI()

        with patch(
            "builtins.input",
            side_effect=["10", "Test Title", "Test Author", "2000", "Drama"],
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                ui._add_book()

        output = buffer.getvalue()
        self.assertIn("Запись добавлена:", output)
        self.assertEqual(
            ui._table.select_record(book_id=10),
            [(10, "Test Title", "Test Author", 2000, "Drama")],
        )

    def test_add_book_duplicate_error(self):
        with patch(
            "builtins.input",
            side_effect=["1", "New Title", "New Author", "2001", "Drama"],
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui._add_book()

        output = buffer.getvalue()
        self.assertIn("Ошибка:", output)
        self.assertIn("уже существует", output)

    def test_show_all_books(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.ui._show_all_books()

        output = buffer.getvalue()
        self.assertIn("Список записей", output)
        self.assertIn("1984", output)
        self.assertIn("Dune", output)

    def test_find_books_by_filter(self):
        with patch(
            "builtins.input",
            side_effect=["", "", "Herbert", "", ""],
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui._find_books_by_filter()

        output = buffer.getvalue()
        self.assertIn("Dune", output)
        self.assertNotIn("1984", output)

    def test_update_book_success(self):
        with patch(
            "builtins.input",
            side_effect=["1", "Animal Farm", "", "", ""],
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui._update_book()

        output = buffer.getvalue()
        self.assertIn("Запись обновлена:", output)

        result = self.ui._table.select_record(book_id=1)
        self.assertEqual(result[0][1], "Animal Farm")

    def test_update_book_not_found(self):
        with patch(
            "builtins.input",
            side_effect=["999", "New Title", "", "", ""],
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui._update_book()

        output = buffer.getvalue()
        self.assertIn("Ошибка:", output)
        self.assertIn("не найдена", output)

    def test_delete_book_success(self):
        with patch("builtins.input", side_effect=["2"]):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui._delete_book()

        output = buffer.getvalue()
        self.assertIn("Запись удалена.", output)
        self.assertEqual(self.ui._table.select_record(book_id=2), [])

    def test_delete_book_not_found(self):
        with patch("builtins.input", side_effect=["999"]):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui._delete_book()

        output = buffer.getvalue()
        self.assertIn("Ошибка:", output)
        self.assertIn("не найдена", output)

    def test_run_handles_unknown_command(self):
        with patch("builtins.input", side_effect=["9", "0"]):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.ui.run()

        output = buffer.getvalue()
        self.assertIn("Неизвестная команда. Повторите ввод.", output)
        self.assertIn("Выход из программы.", output)

    def test_module_run_function(self):
        with patch("builtins.input", side_effect=["0"]):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                run()

        output = buffer.getvalue()
        self.assertIn("=== База книг ===", output)
        self.assertIn("Выход из программы.", output)

    def test_main_calls_run(self):
        with patch("src.db.__main__.run") as mocked_run:
            main()
            mocked_run.assert_called_once()