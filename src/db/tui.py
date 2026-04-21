from .backend.errors import BookTableError
from .backend.memory import BookTable


class BookTUI:
    def __init__(self) -> None:
        self._table = BookTable()

    def _print_menu(self) -> None:
        print("\n=== База книг ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()

            if raw == "":
                return None

            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _add_book(self) -> None:
        print("\nДобавление записи")

        book_id = self._read_int("id: ")
        title = input("title: ").strip()
        author = input("author: ").strip()
        year = self._read_int("year: ")
        genre = input("genre: ").strip()

        try:
            record = self._table.create_record(book_id, title, author, year, genre)
            print(f"Запись добавлена: {record}")
        except BookTableError as exc:
            print(f"Ошибка: {exc}")

    def _print_records(self, records: list[tuple[int, str, str, int, str]]) -> None:
        if not records:
            print("Записи не найдены.")
            return

        for record in records:
            print(record)

    def _show_all_books(self) -> None:
        print("\nСписок записей")
        self._print_records(self._table.select_record())

    def _find_books_by_filter(self) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")

        book_id = self._read_optional_int("id: ")
        title = input("title: ").strip() or None
        author = input("author: ").strip() or None
        year = self._read_optional_int("year: ")
        genre = input("genre: ").strip() or None

        records = self._table.select_record(
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            genre=genre,
        )

        self._print_records(records)

    def _update_book(self) -> None:
        print("\nОбновление записи (Enter = оставить без изменений)")

        book_id = self._read_int("id: ")
        title = input("title: ").strip() or None
        author = input("author: ").strip() or None
        year = self._read_optional_int("year: ")
        genre = input("genre: ").strip() or None

        try:
            record = self._table.update_record(book_id, title, author, year, genre)
            print(f"Запись обновлена: {record}")
        except BookTableError as exc:
            print(f"Ошибка: {exc}")

    def _delete_book(self) -> None:
        print("\nУдаление записи")

        book_id = self._read_int("id: ")

        try:
            self._table.delete_record(book_id)
            print("Запись удалена.")
        except BookTableError as exc:
            print(f"Ошибка: {exc}")

    def run(self) -> None:
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self._add_book()
            elif action == "2":
                self._show_all_books()
            elif action == "3":
                self._find_books_by_filter()
            elif action == "4":
                self._update_book()
            elif action == "5":
                self._delete_book()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")


def run() -> None:
    BookTUI().run()
#проверка