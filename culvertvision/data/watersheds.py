import shlex
import subprocess
from pathlib import Path

from loguru import logger

from culvertvision.data.io_manager import DatasetEnum, DatasetIOManager
from culvertvision.data.utils import download_file

SOURCE_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GPKG/NHDPLUS_H_0704_HU4_GPKG.zip"


class Huc12Watersheds(DatasetEnum):
    DOWNLOADED = "raw/NHDPLUS_H_0704_HU4_GPKG.zip"
    EXTRACTED = "interim/huc_12_watersheds.gpkg"
    CLEANED = "processed/huc_12_watersheds.gpkg"


def download_watersheds(io_manager: DatasetIOManager) -> Path:
    """Download the NHDPLUS dataset for the project location."""

    src = SOURCE_URL
    dst = io_manager.get_path(Huc12Watersheds.DOWNLOADED)

    if dst.exists():
        logger.info(f"Downloaded watersheds found at: {dst}")
        return dst

    logger.info(f"Downloading watersheds to: {dst}")
    return download_file(url=src, dst=dst)


def extract_watersheds(io_manager: DatasetIOManager) -> Path:
    """Extract the WBHUC12 layer to its own geopackage."""

    src = io_manager.get_path(Huc12Watersheds.DOWNLOADED)
    dst = io_manager.get_path(Huc12Watersheds.EXTRACTED)

    if dst.exists():
        logger.info(f"Extracted watersheds found at: {dst}")
        return dst

    vsi_src = f"/vsizip/{src}/{src.stem}.gpkg"
    layer = "WBDHU12"

    cmd = f"ogr2ogr {dst} {vsi_src} {layer}"

    logger.info(f"Extracting WBHUC12 layer to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def clean_watersheds(io_manager: DatasetIOManager) -> Path:
    """Remove duplicates, reproject, and filter fields."""

    src = io_manager.get_path(Huc12Watersheds.EXTRACTED)
    dst = io_manager.get_path(Huc12Watersheds.CLEANED)

    if dst.exists():
        logger.info(f"Cleaned watersheds found at: {dst}")
        return dst

    layer = "WBDHU12"

    cmd = f"""ogr2ogr \
                -t_srs EPSG:26915 \
                -sql 'SELECT DISTINCT HUC12 as huc12, Name as name, Shape as geom from {layer}' \
                -nln watersheds \
                {dst} {src}"""

    logger.info(f"Writing cleaned watershed boundaries to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def make_dataset(io_manager: DatasetIOManager) -> None:
    download_watersheds(io_manager)
    extract_watersheds(io_manager)
    clean_watersheds(io_manager)


def remove_dataset(io_manager: DatasetIOManager) -> None:
    for item in Huc12Watersheds:
        match item:
            case Huc12Watersheds.DOWNLOADED:
                continue  # Don't delete the source
            case _:
                file = io_manager.get_path(item)
                if file.exists():
                    logger.info(f"Deleting: {file}")
                    file.unlink()
