from .backend.memory import MemoryDatabase
from .backend.file import FileDatabase
from .backend.csv_file import CsvDatabase
from .backend.database import Database
from .backend.errors import DatabaseError


class BookTUI:
    TABLE_NAME = "books"
    COLUMNS = ("book_id", "title", "author", "year", "genre")

    def __init__(self) -> None:
        self.db: Database = self._choose_database()
        self._ensure_table()

    def _choose_database(self) -> Database:
        print("Выберите тип базы данных:")
        print("1. In-memory")
        print("2. Файловая (JSON)")
        print("3. Файловая (CSV)")
        choice = input("Ваш выбор: ").strip()
        if choice == "2":
            return FileDatabase()
        elif choice == "3":
            return CsvDatabase(int_columns=["book_id", "year"])
        else:
            return MemoryDatabase()

    def _ensure_table(self) -> None:
        try:
            self.db.create_table(self.TABLE_NAME, self.COLUMNS, indexed_columns=["book_id", "year"])
            print(f"Таблица '{self.TABLE_NAME}' создана.")
        except DatabaseError as e:
            # Если таблица уже существует – просто используем существующую
            print(f"Таблица '{self.TABLE_NAME}' уже существует. Используем существующую.")

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
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте пустым.")

    def _add_book(self, input_func=input) -> None:
        print("\nДобавление записи")
        book_id = self._read_int("book_id: ", input_func)
        title = input_func("title: ").strip()
        author = input_func("author: ").strip()
        year = self._read_int("year: ", input_func)
        genre = input_func("genre: ").strip()
        record = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "year": year,
            "genre": genre
        }
        try:
            self.db.insert_record(self.TABLE_NAME, record)
            print(f"Запись добавлена: {record}")
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _show_all_books(self) -> None:
        print("\nСписок записей")
        records = self.db.select_records(self.TABLE_NAME)
        if not records:
            print("Записи не найдены.")
        else:
            for r in records:
                print(r)

    def _find_books_by_filter(self, input_func=input) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")
        book_id = self._read_optional_int("book_id: ", input_func)
        title = input_func("title: ").strip() or None
        author = input_func("author: ").strip() or None
        year = self._read_optional_int("year: ", input_func)
        genre = input_func("genre: ").strip() or None
        filters = {}
        if book_id is not None:
            filters["book_id"] = book_id
        if title:
            filters["title"] = title
        if author:
            filters["author"] = author
        if year is not None:
            filters["year"] = year
        if genre:
            filters["genre"] = genre
        try:
            records = self.db.select_records(self.TABLE_NAME, **filters)
            if not records:
                print("Записи не найдены.")
            else:
                for r in records:
                    print(r)
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _update_book(self, input_func=input) -> None:
        print("\nОбновление записи (Enter = оставить без изменений)")
        book_id = self._read_int("book_id: ", input_func)
        title = input_func("title: ").strip() or None
        author = input_func("author: ").strip() or None
        year = self._read_optional_int("year: ", input_func)
        genre = input_func("genre: ").strip() or None
        updates = {}
        if title is not None:
            updates["title"] = title
        if author is not None:
            updates["author"] = author
        if year is not None:
            updates["year"] = year
        if genre is not None:
            updates["genre"] = genre
        try:
            updated = self.db.update_record(self.TABLE_NAME, book_id, **updates)
            print(f"Запись обновлена: {updated}")
        except DatabaseError as e:
            print(f"Ошибка: {e}")

    def _delete_book(self, input_func=input) -> None:
        print("\nУдаление записи")
        book_id = self._read_int("book_id: ", input_func)
        try:
            self.db.delete_record(self.TABLE_NAME, book_id)
            print("Запись удалена.")
        except DatabaseError as e:
            print(f"Ошибка: {e}")

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
