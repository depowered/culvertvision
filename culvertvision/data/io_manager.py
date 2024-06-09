from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol


class DatasetEnum(StrEnum):
    pass


class DatasetIOManager(Protocol):
    def get_path(self, dataset: DatasetEnum) -> Path: ...


@dataclass
class LocalDatasetIOManager:
    data_dir: Path

    def get_path(self, dataset: DatasetEnum) -> Path:
        return self.data_dir / dataset.value
