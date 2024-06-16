import typer
from enum import StrEnum, auto

from culvertvision.config import Settings
from culvertvision.data import boundaries, watersheds, culverts
from culvertvision.data.io_manager import LocalDatasetIOManager

app = typer.Typer()

IO_MANAGER = LocalDatasetIOManager(data_dir=Settings().DATA_DIR)


class Action(StrEnum):
    CREATE = auto()
    REMOVE = auto()


@app.command()
def manage_boundaries(action: Action = Action.CREATE) -> None:
    "Create/remove the boundaries dataset."
    match action:
        case Action.CREATE:
            boundaries.make_dataset(IO_MANAGER)
        case Action.REMOVE:
            boundaries.remove_dataset(IO_MANAGER)


@app.command()
def manage_watersheds(action: Action = Action.CREATE) -> None:
    "Create/remove the watersheds dataset."
    match action:
        case Action.CREATE:
            watersheds.make_dataset(IO_MANAGER)
        case Action.REMOVE:
            watersheds.remove_dataset(IO_MANAGER)


@app.command()
def manage_culverts(action: Action = Action.CREATE) -> None:
    "Create/remove the culverts dataset."
    match action:
        case Action.CREATE:
            culverts.make_dataset(IO_MANAGER)
        case Action.REMOVE:
            culverts.remove_dataset(IO_MANAGER)


if __name__ == "__main__":
    app()
