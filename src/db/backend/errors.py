class BookTableError(Exception):
    """Базовый класс для ошибок таблицы книг."""
    pass

class InvalidYearError(BookTableError):
    """Некорректный год издания."""
    pass

class DuplicateIDError(BookTableError):
    """Книга с таким ID уже существует."""
    pass

class RecordNotFoundError(BookTableError):
    """Запись не найдена."""
    pass
