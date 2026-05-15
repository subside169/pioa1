from typing import Any
from .errors import MissingColumnError, UnknownColumnError, RecordNotFoundError


class Table:
    """Таблица с фиксированным набором колонок и операциями CRUD."""

    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []
        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        """Добавляет запись, проверяя соответствие схеме."""
        self._validate_record(record)
        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        """Возвращает записи, удовлетворяющие всем фильтрам."""
        unknown = [key for key in filters if key not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Поле '{unknown[0]}' не определено в структуре таблицы.")

        if not filters:
            return [r.copy() for r in self.records]

        result = []
        for record in self.records:
            if all(record.get(k) == v for k, v in filters.items()):
                result.append(record.copy())
        return result

    def update_record(self, record_id: int, **updates: Any) -> dict[str, Any]:
        """Обновляет запись с заданным id (предполагаем, что первая колонка — идентификатор)."""
        id_column = self.columns[0]  # book_id
        for i, record in enumerate(self.records):
            if record.get(id_column) == record_id:
                updated = record.copy()
                for key, value in updates.items():
                    if key not in self.columns:
                        raise UnknownColumnError(f"Поле '{key}' не определено в структуре таблицы.")
                    if key == id_column and value != record_id:
                        raise ValueError("Нельзя изменять идентификатор записи.")
                    updated[key] = value
                self.records[i] = updated
                return updated.copy()
        raise RecordNotFoundError(f"Запись с {id_column}={record_id} не найдена.")

    def delete_record(self, record_id: int) -> None:
        """Удаляет запись по идентификатору."""
        id_column = self.columns[0]
        for i, record in enumerate(self.records):
            if record.get(id_column) == record_id:
                del self.records[i]
                return
        raise RecordNotFoundError(f"Запись с {id_column}={record_id} не найдена.")

    def _validate_record(self, record: dict[str, Any]) -> None:
        """Проверяет, что запись содержит все колонки и не содержит лишних."""
        missing = [col for col in self.columns if col not in record]
        if missing:
            raise MissingColumnError(f"Отсутствует поле '{missing[0]}' в записи.")
        extra = [col for col in record if col not in self.columns]
        if extra:
            raise UnknownColumnError(f"Поле '{extra[0]}' не определено в структуре таблицы.")
