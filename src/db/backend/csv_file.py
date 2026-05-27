import csv
from pathlib import Path
from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class CsvDatabase(Database):
    """База данных, хранящая таблицы в CSV-файлах."""

    def __init__(self, directory: str = "data", int_columns: list[str] | None = None) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.int_columns = int_columns or []   # список колонок, которые нужно хранить как целые числа

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        path = self._get_table_path(table_name)
        if not path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        try:
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise InvalidStorageDataError("CSV-файл не содержит заголовков столбцов.")
                columns = tuple(reader.fieldnames)
                records = []
                for row in reader:
                    record = {}
                    for key, value in row.items():
                        if key in self.int_columns:
                            try:
                                record[key] = int(value)
                            except ValueError:
                                record[key] = value  # оставляем строку, если не число
                        else:
                            record[key] = value
                    records.append(record)
        except (csv.Error, IOError) as e:
            raise InvalidStorageDataError("Ошибка чтения CSV-файла.") from e
        return Table(columns, records)

    def _save_table(self, table_name: str, table: Table) -> None:
        path = self._get_table_path(table_name)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=table.columns)
            writer.writeheader()
            writer.writerows(table.records)

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"
