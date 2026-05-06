# Структура записи:
# (id, title, author, year, genre)
type BookRecord = tuple[int, str, str, int, str]

Book: list[BookRecord] = []
def create_record(
    book_id: int,
    title: str,
    author: str,
    year: int,
    genre: str,
) -> BookRecord:
    """
    Создаёт новую запись книги.
    """

    # Проверка года
    if year < 0:
        raise ValueError("Год не может быть отрицательным.")

    # Проверка уникальности id
    if any(record[0] == book_id for record in Book):
        raise ValueError(f"Книга с id={book_id} уже существует.")

    new_record: BookRecord = (
        book_id,
        title.strip(),
        author.strip(),
        year,
        genre.strip(),
    )

    Book.append(new_record)
    return new_record

def select_record(
    book_id: int | None = None,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    genre: str | None = None,
) -> list[BookRecord]:

    if (
        book_id is None
        and title is None
        and author is None
        and year is None
        and genre is None
    ):
        return Book.copy()

    result: list[BookRecord] = []

    for record in Book:

        if book_id is not None and record[0] != book_id:
            continue

        if title is not None and record[1] != title:
            continue

        if author is not None and record[2] != author:
            continue

        if year is not None and record[3] != year:
            continue

        if genre is not None and record[4] != genre:
            continue

        result.append(record)

    return result

def update_record(
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    genre: str | None = None,
) -> BookRecord:
    """
    Обновляет запись по id.
    """

    for i, record in enumerate(Book):
        if record[0] == book_id:

            new_record: BookRecord = (
                book_id,
                title.strip() if title is not None else record[1],
                author.strip() if author is not None else record[2],
                year if year is not None else record[3],
                genre.strip() if genre is not None else record[4],
            )

            if new_record[3] < 0:
                raise ValueError("Год не может быть отрицательным.")

            Book[i] = new_record
            return new_record

    raise ValueError(f"Запись с id={book_id} не найдена.")

def delete_record(book_id: int) -> None:
    """
    Удаляет запись по id.
    """

    for i, record in enumerate(Book):
        if record[0] == book_id:
            del Book[i]
            return

    raise ValueError(f"Запись с id={book_id} не найдена.")
