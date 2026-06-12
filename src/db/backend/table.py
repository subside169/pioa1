from typing import Any
from .errors import MissingColumnError, UnknownColumnError, RecordNotFoundError, DuplicateIDError


class Table:
    """Таблица с фиксированным набором колонок и поддержкой индексов."""

    def __init__(
        self,
        columns: tuple[str, ...],
        records: list[dict[str, Any]] | None = None,
        indexed_columns: list[str] | None = None
    ) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []
        # Индексы: {column_name: {value: [indices_in_self.records, ...]}}
        self._indexes: dict[str, dict[Any, list[int]]] = {}
        if indexed_columns:
            for col in indexed_columns:
                if col not in columns:
                    raise UnknownColumnError(f"Поле '{col}' не определено в структуре таблицы.")
                self._indexes[col] = {}
        if records:
            for record in records:
                self.insert_record(record)

    @property
    def indexed_columns(self) -> list[str]:
        """Список колонок, по которым построены индексы."""
        return list(self._indexes.keys())

    # --------------------------------------------------------------
    # Внутренние методы работы с индексами
    # --------------------------------------------------------------
    def _add_to_indexes(self, record_index: int, record: dict[str, Any]) -> None:
        for col, index in self._indexes.items():
            value = record[col]
            index.setdefault(value, []).append(record_index)

    def _remove_from_indexes(self, record_index: int, record: dict[str, Any]) -> None:
        for col, index in self._indexes.items():
            value = record[col]
            if value in index:
                try:
                    index[value].remove(record_index)
                except ValueError:
                    pass

    def _update_indexes(self, old_index: int, old_record: dict[str, Any], new_record: dict[str, Any]) -> None:
        self._remove_from_indexes(old_index, old_record)
        self._add_to_indexes(old_index, new_record)

    def _rebuild_indexes(self) -> None:
        """Полная перестройка индексов (после удаления записи)."""
        for col in self._indexes:
            self._indexes[col].clear()
        for i, record in enumerate(self.records):
            self._add_to_indexes(i, record)

    # --------------------------------------------------------------
    # Основные CRUD-методы
    # --------------------------------------------------------------
    def insert_record(self, record: dict[str, Any]) -> None:
        self._validate_record(record)
        id_column = self.columns[0]
        record_id = record[id_column]
        # Проверка уникальности идентификатора
        if any(rec[id_column] == record_id for rec in self.records):
            raise DuplicateIDError(f"Запись с {id_column}={record_id} уже существует.")
        self.records.append(record.copy())
        self._add_to_indexes(len(self.records) - 1, record)

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        unknown = [key for key in filters if key not in self.columns]
        if unknown:
            raise UnknownColumnError(f"Поле '{unknown[0]}' не определено в структуре таблицы.")
        if not filters:
            return [r.copy() for r in self.records]

        # Пытаемся использовать индекс для одного из фильтров
        candidate_indices = None
        for col in filters:
            if col in self._indexes:
                value = filters[col]
                idx = self._indexes[col].get(value)
                if idx is not None:
                    candidate_indices = idx
                    break

        if candidate_indices is not None:
            result = []
            for i in candidate_indices:
                record = self.records[i]
                if all(record.get(k) == v for k, v in filters.items()):
                    result.append(record.copy())
            return result
        else:
            result = []
            for record in self.records:
                if all(record.get(k) == v for k, v in filters.items()):
                    result.append(record.copy())
            return result

    def update_record(self, record_id: int, **updates: Any) -> dict[str, Any]:
        id_column = self.columns[0]
        for i, record in enumerate(self.records):
            if record.get(id_column) == record_id:
                updated = record.copy()
                for key, value in updates.items():
                    if key not in self.columns:
                        raise UnknownColumnError(f"Поле '{key}' не определено в структуре таблицы.")
                    if key == id_column and value != record_id:
                        raise ValueError("Нельзя изменять идентификатор записи.")
                    updated[key] = value
                self._update_indexes(i, record, updated)
                self.records[i] = updated
                return updated.copy()
        raise RecordNotFoundError(f"Запись с {id_column}={record_id} не найдена.")

    def delete_record(self, record_id: int) -> None:
        id_column = self.columns[0]
        for i, record in enumerate(self.records):
            if record.get(id_column) == record_id:
                self._remove_from_indexes(i, record)
                del self.records[i]
                self._rebuild_indexes()
                return
        raise RecordNotFoundError(f"Запись с {id_column}={record_id} не найдена.")

    def _validate_record(self, record: dict[str, Any]) -> None:
        missing = [col for col in self.columns if col not in record]
        if missing:
            raise MissingColumnError(f"Отсутствует поле '{missing[0]}' в записи.")
        extra = [col for col in record if col not in self.columns]
        if extra:
            raise UnknownColumnError(f"Поле '{extra[0]}' не определено в структуре таблицы.")
