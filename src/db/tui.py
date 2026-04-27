from .backend.memory import create_record, select_record, update_record, delete_record


def _print_menu() -> None:
    print("\n=== База книг ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить запись")
    print("5. Удалить запись")
    print("0. Выход")


def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _add_book() -> None:
    print("\nДобавление записи")

    book_id = _read_int("id: ")
    title = input("title: ").strip()
    author = input("author: ").strip()
    year = _read_int("year: ")
    genre = input("genre: ").strip()

    try:
        record = create_record(book_id, title, author, year, genre)
        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    if not records:
        print("Записи не найдены.")
        return

    for record in records:
        print(record)


def _show_all_books() -> None:
    print("\nСписок записей")
    _print_records(select_record())


def _find_books_by_filter() -> None:
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    book_id = _read_optional_int("id: ")
    title = input("title: ").strip() or None
    author = input("author: ").strip() or None
    year = _read_optional_int("year: ")
    genre = input("genre: ").strip() or None

    records = select_record(
        book_id=book_id,
        title=title,
        author=author,
        year=year,
        genre=genre,
    )

    _print_records(records)


def run() -> None:
    while True:
        _print_menu()
        action = input("Выберите действие: ").strip()

        if action == "1":
            _add_book()

        elif action == "2":
            _show_all_books()

        elif action == "3":
            _find_books_by_filter()

        elif action == "4":
            _update_book()

        elif action == "5":
            _delete_book()

        elif action == "0":
            print("Выход из программы.")
            break

        else:
            print("Неизвестная команда. Повторите ввод.")

def _update_book() -> None:
    print("\nОбновление записи (Enter = оставить без изменений)")

    book_id = _read_int("id: ")

    title = input("title: ").strip() or None
    author = input("author: ").strip() or None

    year_input = input("year: ").strip()
    year = int(year_input) if year_input else None

    genre = input("genre: ").strip() or None

    try:
        record = update_record(book_id, title, author, year, genre)
        print(f"Запись обновлена: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")

def _delete_book() -> None:
    print("\nУдаление записи")

    book_id = _read_int("id: ")

    try:
        delete_record(book_id)
        print("Запись удалена.")

    except ValueError as exc:
        print(f"Ошибка: {exc}")