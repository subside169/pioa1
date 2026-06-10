import csv
import json
from pathlib import Path
from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError, StorageSaveError
from .table import Table


class CsvDatabase(Database):
    """База данных, хранящая таблицы в CSV-файлах + метаданные в JSON."""

    def __init__(self, directory: str = "data",
                 int_columns: list[str] | None = None,
                 indexed_columns: list[str] | None = None) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.int_columns = int_columns or []
        self.indexed_columns = indexed_columns or []

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        csv_path = self._get_table_path(table_name)
        if not csv_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")

        meta = self._load_meta(table_name)

        try:
            with csv_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise InvalidStorageDataError("CSV-файл не содержит заголовков столбцов.")
                columns = tuple(reader.fieldnames)
                records = []
                for row in reader:
                    record = {}
                    for key, value in row.items():
                        if key in meta.get("int_columns", []):
                            try:
                                record[key] = int(value)
                            except ValueError:
                                record[key] = value
                        else:
                            record[key] = value
                    records.append(record)
        except (csv.Error, IOError) as e:
            raise InvalidStorageDataError("Ошибка чтения CSV-файла.") from e

        return Table(columns, records, indexed_columns=meta.get("indexed_columns", []))

    def _save_table(self, table_name: str, table: Table) -> None:
        csv_path = self._get_table_path(table_name)
        try:
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=table.columns)
                writer.writeheader()
                writer.writerows(table.records)
            self._save_meta(table_name, table)
        except (OSError, IOError) as e:
            raise StorageSaveError(f"Не удалось сохранить таблицу '{table_name}': {e}") from e

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"

    def _get_meta_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.meta.json"

    def _save_meta(self, table_name: str, table: Table) -> None:
        meta = {
            "int_columns": self.int_columns,
            "indexed_columns": list(table._indexes.keys())
        }
        meta_path = self._get_meta_path(table_name)
        try:
            with meta_path.open("w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except (OSError, IOError) as e:
            raise StorageSaveError(f"Не удалось сохранить метаданные таблицы '{table_name}': {e}") from e

    def _load_meta(self, table_name: str) -> dict:
        meta_path = self._get_meta_path(table_name)
        if meta_path.exists():
            with meta_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "int_columns": self.int_columns,
            "indexed_columns": self.indexed_columns
        }
