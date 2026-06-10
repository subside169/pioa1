import json
from pathlib import Path
from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError, StorageSaveError
from .table import Table


class FileDatabase(Database):
    """База данных, хранящая таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        path = self._get_table_path(table_name)
        if not path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidStorageDataError("Файл таблицы содержит некорректный JSON.") from e
        return self._deserialize(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        path = self._get_table_path(table_name)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(self._serialize(table), f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            raise StorageSaveError(f"Не удалось сохранить таблицу '{table_name}': {e}") from e

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": table.records.copy(),
            "indexed_columns": list(table._indexes.keys())
        }

    def _deserialize(self, data: dict) -> Table:
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError("Файл таблицы имеет некорректную структуру.")
        columns = tuple(data["columns"])
        indexed = data.get("indexed_columns", [])
        return Table(columns, data.get("records", []), indexed_columns=indexed)
