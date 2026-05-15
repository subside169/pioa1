import unittest
from unittest.mock import Mock, patch
from io import StringIO
from src.db.tui import BookTUI


class TestBookTUI(unittest.TestCase):
    def _create_tui_with_memory(self):
        """Создаёт TUI с выбором in-memory БД (первый ввод '1' при создании)."""
        with patch('builtins.input', side_effect=['1']):
            tui = BookTUI()
        return tui

    def _run_with_input_func(self, tui, actions: list[str]) -> str:
        """Запускает run, передавая mock-функцию ввода, и возвращает вывод."""
        mock_input = Mock(side_effect=actions)
        with patch('sys.stdout', new_callable=StringIO) as fake_out:
            tui.run(input_func=mock_input)
        return fake_out.getvalue()

    # ----------------------------------------------------------------
    # Тесты
    # ----------------------------------------------------------------
    def test_initial_menu_and_exit(self):
        tui = self._create_tui_with_memory()
        output = self._run_with_input_func(tui, ['0'])
        self.assertIn('=== База книг ===', output)
        self.assertIn('Выход из программы.', output)

    def test_add_book(self):
        tui = self._create_tui_with_memory()
        output = self._run_with_input_func(tui, [
            '1', '1', 'Война и мир', 'Толстой', '1869', 'роман', '0'
        ])
        self.assertIn('Запись добавлена', output)

    def test_show_all_books(self):
        tui = self._create_tui_with_memory()
        tui.db.insert_record('books', {'book_id': 1, 'title': 'Test', 'author': 'A', 'year': 2000, 'genre': 'G'})
        output = self._run_with_input_func(tui, ['2', '0'])
        self.assertIn('Test', output)

    def test_find_books_by_filter(self):
        tui = self._create_tui_with_memory()
        tui.db.insert_record('books', {'book_id': 1, 'title': 'A', 'author': 'B', 'year': 2000, 'genre': 'C'})
        # Фильтр по book_id=1, остальное пусто
        output = self._run_with_input_func(tui, ['3', '1', '', '', '', '', '0'])
        self.assertIn("'book_id': 1", output)

    def test_update_book(self):
        tui = self._create_tui_with_memory()
        tui.db.insert_record('books', {'book_id': 1, 'title': 'Old', 'author': 'A', 'year': 2000, 'genre': 'G'})
        output = self._run_with_input_func(tui, ['4', '1', 'New', '', '2021', '', '0'])
        self.assertIn('Запись обновлена', output)
        self.assertIn('New', output)

    def test_delete_book(self):
        tui = self._create_tui_with_memory()
        tui.db.insert_record('books', {'book_id': 1, 'title': 'Del', 'author': 'A', 'year': 2000, 'genre': 'G'})
        output = self._run_with_input_func(tui, ['5', '1', '2', '0'])  # 2 - просмотр после удаления
        self.assertIn('Запись удалена.', output)
        self.assertIn('Записи не найдены.', output)  # после удаления

    def test_invalid_menu_choice(self):
        tui = self._create_tui_with_memory()
        output = self._run_with_input_func(tui, ['abc', '0'])
        self.assertIn('Неизвестная команда.', output)


if __name__ == '__main__':
    unittest.main()
