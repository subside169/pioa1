class BookTableError(Exception):
    """
    Базовый класс для всех ошибок, связанных с таблицей книг.
    """
    pass


class InvalidYearError(BookTableError):
    """
    Ошибка: год книги некорректный (например, отрицательный).
    """
    pass


class DuplicateIDError(BookTableError):
    """
    Ошибка: запись с таким id уже существует.
    """
    pass


class RecordNotFoundError(BookTableError):
    """
    Ошибка: запись с указанным id не найдена.
    """
    pass