from .backend.memory import BookTable
from .backend.errors import (
    InvalidYearError,
    DuplicateIDError,
    RecordNotFoundError,
)


class BookTUI:
    def __init__(self, book_table: BookTable | None = None):
        self.table = book_table or BookTable()

    def _print_menu(self) -> None:
        print("\n=== База книг ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("0. Выход")

    def _read_int(self, prompt: str, input_func=input) -> int:
        while True:
            raw = input_func(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str, input_func=input) -> int | None:
        while True:
            raw = input_func(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _add_book(self, input_func=input) -> None:
        print("\nДобавление записи")
        book_id = self._read_int("id: ", input_func)
        title = input_func("title: ").strip()
        author = input_func("author: ").strip()
        year = self._read_int("year: ", input_func)
        genre = input_func("genre: ").strip()
        try:
            record = self.table.create_record(book_id, title, author, year, genre)
            print(f"Запись добавлена: {record}")
        except (InvalidYearError, DuplicateIDError) as exc:
            print(f"Ошибка: {exc}")

    def _print_records(self, records: list) -> None:
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(record)

    def _show_all_books(self) -> None:
        print("\nСписок записей")
        self._print_records(self.table.select_record())

    def _find_books_by_filter(self, input_func=input) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")
        book_id = self._read_optional_int("id: ", input_func)
        title = input_func("title: ").strip() or None
        author = input_func("author: ").strip() or None
        year = self._read_optional_int("year: ", input_func)
        genre = input_func("genre: ").strip() or None
        records = self.table.select_record(
            book_id=book_id, title=title, author=author, year=year, genre=genre
        )
        self._print_records(records)

    def _update_book(self, input_func=input) -> None:
        print("\nОбновление записи (Enter = оставить без изменений)")
        book_id = self._read_int("id: ", input_func)
        title = input_func("title: ").strip() or None
        author = input_func("author: ").strip() or None
        year = self._read_optional_int("year: ", input_func)
        genre = input_func("genre: ").strip() or None
        try:
            record = self.table.update_record(book_id, title, author, year, genre)
            print(f"Запись обновлена: {record}")
        except (RecordNotFoundError, InvalidYearError) as exc:
            print(f"Ошибка: {exc}")

    def _delete_book(self, input_func=input) -> None:
        print("\nУдаление записи")
        book_id = self._read_int("id: ", input_func)
        try:
            self.table.delete_record(book_id)
            print("Запись удалена.")
        except RecordNotFoundError as exc:
            print(f"Ошибка: {exc}")

    def run(self, input_func=input) -> None:
        while True:
            self._print_menu()
            action = input_func("Выберите действие: ").strip()
            if action == "1":
                self._add_book(input_func)
            elif action == "2":
                self._show_all_books()
            elif action == "3":
                self._find_books_by_filter(input_func)
            elif action == "4":
                self._update_book(input_func)
            elif action == "5":
                self._delete_book(input_func)
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")
