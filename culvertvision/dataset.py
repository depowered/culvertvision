from enum import StrEnum, auto

import typer

from culvertvision.config import Settings
from culvertvision.data import boundaries, culverts, dem_index, watersheds
from culvertvision.data.io_manager import LocalDatasetIOManager

app = typer.Typer()

IO_MANAGER = LocalDatasetIOManager(data_dir=Settings().DATA_DIR)


class Dataset(StrEnum):
    BOUNDARIES = auto()
    WATERSHEDS = auto()
    CULVERTS = auto()
    DEM_INDEX = auto()


@app.command()
def create(datasets: list[Dataset]) -> None:
    "Create one or more datasets."
    for ds in datasets:
        match ds:
            case Dataset.BOUNDARIES:
                boundaries.make_dataset(IO_MANAGER)
            case Dataset.WATERSHEDS:
                watersheds.make_dataset(IO_MANAGER)
            case Dataset.CULVERTS:
                culverts.make_dataset(IO_MANAGER)
            case Dataset.DEM_INDEX:
                dem_index.make_dataset(IO_MANAGER)


@app.command()
def remove(datasets: list[Dataset]) -> None:
    "Remove one or more datasets."
    for ds in datasets:
        match ds:
            case Dataset.BOUNDARIES:
                boundaries.remove_dataset(IO_MANAGER)
            case Dataset.WATERSHEDS:
                watersheds.remove_dataset(IO_MANAGER)
            case Dataset.CULVERTS:
                culverts.remove_dataset(IO_MANAGER)
            case Dataset.DEM_INDEX:
                dem_index.remove_dataset(IO_MANAGER)


if __name__ == "__main__":
    app()
