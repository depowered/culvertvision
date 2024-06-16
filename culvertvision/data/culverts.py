import shlex
import subprocess
from pathlib import Path

from loguru import logger

from culvertvision.data.io_manager import DatasetEnum, DatasetIOManager


class Culverts(DatasetEnum):
    SOURCE = "external/source_goodhue_culvert_lines.shp.zip"
    EXTRACTED = "interim/culverts.gpkg"
    CLEANED = "processed/culverts.gpkg"


def extract_culverts(io_manager: DatasetIOManager) -> Path:
    """Extract the culverts from the zipped shapefile source."""

    src = io_manager.get_path(Culverts.SOURCE)
    dst = io_manager.get_path(Culverts.EXTRACTED)

    if dst.exists():
        logger.info(f"Extracted culverts found at : {dst}")

    vsi_src = f"/vsizip/{src}"
    layer = "GoodhueCountyCulvertLines"

    cmd = f"ogr2ogr {dst} {vsi_src} {layer}"

    logger.info(f"Extracting {layer} layer to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)


def clean_culverts(io_manager: DatasetIOManager) -> None:
    """Reproject and filter fields."""

    src = io_manager.get_path(Culverts.EXTRACTED)
    dst = io_manager.get_path(Culverts.CLEANED)

    if dst.exists():
        logger.info(f"Cleaned culverts found at: {dst}")
        return dst

    layer = "GoodhueCountyCulvertLines"

    cmd = f"""ogr2ogr \
        -t_srs EPSG:26915 \
        -sql 'SELECT fid, geom from {layer}' \
        -nln culverts \
        {dst} {src}"""

    logger.info(f"Writing cleaned culverts to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def make_dataset(io_manager: DatasetIOManager) -> None:
    extract_culverts(io_manager)
    clean_culverts(io_manager)


def remove_dataset(io_manager: DatasetIOManager) -> None:
    for item in Culverts:
        match item:
            case Culverts.SOURCE:
                continue  # Don't delete the source
            case _:
                file = io_manager.get_path(item)
                if file.exists():
                    logger.info(f"Deleting: {file}")
                    file.unlink()
