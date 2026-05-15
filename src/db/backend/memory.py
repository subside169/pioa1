from .errors import DuplicateIDError, InvalidYearError, RecordNotFoundError

type BookRecord = tuple[int, str, str, int, str]


class BookTable:
    def __init__(self) -> None:
        self._books: list[BookRecord] = []

    def create_record(
        self,
        book_id: int,
        title: str,
        author: str,
        year: int,
        genre: str,
    ) -> BookRecord:
        """Создаёт новую запись книги. Возвращает созданную запись."""
        if year < 0:
            raise InvalidYearError("Год не может быть отрицательным.")

        if any(record[0] == book_id for record in self._books):
            raise DuplicateIDError(f"Книга с id={book_id} уже существует.")

        new_record: BookRecord = (
            book_id,
            title.strip(),
            author.strip(),
            year,
            genre.strip(),
        )
        self._books.append(new_record)
        return new_record

    def select_record(
        self,
        book_id: int | None = None,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        genre: str | None = None,
    ) -> list[BookRecord]:
        """Возвращает список записей, удовлетворяющих фильтрам."""
        if (
            book_id is None
            and title is None
            and author is None
            and year is None
            and genre is None
        ):
            return self._books.copy()

        result: list[BookRecord] = []
        for record in self._books:
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
        self,
        book_id: int,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        genre: str | None = None,
    ) -> BookRecord:
        """Обновляет запись по id. Возвращает обновлённую запись."""
        for i, record in enumerate(self._books):
            if record[0] == book_id:
                new_record: BookRecord = (
                    book_id,
                    title.strip() if title is not None else record[1],
                    author.strip() if author is not None else record[2],
                    year if year is not None else record[3],
                    genre.strip() if genre is not None else record[4],
                )
                if new_record[3] < 0:
                    raise InvalidYearError("Год не может быть отрицательным.")
                self._books[i] = new_record
                return new_record
        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")

    def delete_record(self, book_id: int) -> None:
        """Удаляет запись по id."""
        for i, record in enumerate(self._books):
            if record[0] == book_id:
                del self._books[i]
                return
        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")
