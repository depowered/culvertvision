import typer

from culvertvision.config import Settings
from culvertvision.data import boundaries, watersheds
from culvertvision.data.io_manager import LocalDatasetIOManager

app = typer.Typer()

IO_MANAGER = LocalDatasetIOManager(data_dir=Settings().DATA_DIR)


@app.command()
def make_boundaries() -> None:
    "Create the boundaries dataset."
    boundaries.make_dataset(IO_MANAGER)


@app.command()
def remove_boundaries() -> None:
    "Remove all files related to the boundaries dataset."
    boundaries.remove_dataset(IO_MANAGER)


@app.command()
def make_watersheds() -> None:
    "Create the watersheds dataset."
    watersheds.make_dataset(IO_MANAGER)


@app.command()
def remove_watersheds() -> None:
    "Remove all files related to the boundaries dataset."
    watersheds.remove_dataset(IO_MANAGER)


if __name__ == "__main__":
    app()
