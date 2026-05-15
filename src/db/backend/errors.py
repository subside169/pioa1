class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""

class TableAlreadyExistsError(DatabaseError):
    """Попытка создать уже существующую таблицу."""

class TableNotFoundError(DatabaseError):
    """Обращение к несуществующей таблице."""

class MissingColumnError(DatabaseError):
    """Отсутствует обязательное поле в записи."""

class UnknownColumnError(DatabaseError):
    """Поле не определено в схеме таблицы."""

class InvalidStorageDataError(DatabaseError):
    """Повреждённые данные в файле."""

# Дополнительные ошибки, специфичные для операций update/delete
class RecordNotFoundError(DatabaseError):
    """Запись не найдена (например, по id)."""
