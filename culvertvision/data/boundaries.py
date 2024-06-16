import shlex
import subprocess
from pathlib import Path

from loguru import logger

from culvertvision.data.io_manager import DatasetEnum, DatasetIOManager
from culvertvision.data.utils import download_file

SOURCE_URL = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/bdry_counties_in_minnesota/gpkg_bdry_counties_in_minnesota.zip"


class CountyBoundaries(DatasetEnum):
    DOWNLOADED = "raw/gpkg_bdry_counties_in_minnesota.zip"
    EXTRACTED = "interim/county_boundaries.gpkg"
    CLEANED = "processed/county_boundaries.gpkg"


def download_boundaries(io_manager: DatasetIOManager) -> Path:
    """Download a dataset of MN county boundaries."""

    src = SOURCE_URL
    dst = io_manager.get_path(CountyBoundaries.DOWNLOADED)

    if dst.exists():
        logger.info(f"Downloaded county boundaries found at: {dst}")
        return dst

    logger.info(f"Downloading county boundaries to: {dst}")
    return download_file(url=src, dst=dst)


def extract_boundaries(io_manager: DatasetIOManager) -> Path:
    """Extract the mn_county_boundaries_multipart layer from the zipped geopackage."""

    src = io_manager.get_path(CountyBoundaries.DOWNLOADED)
    dst = io_manager.get_path(CountyBoundaries.EXTRACTED)

    if dst.exists():
        logger.info(f"Extracted county boundaries found at: {dst}")
        return dst

    vsi_src = f"/vsizip/{src}/bdry_counties_in_minnesota.gpkg"
    layer = "mn_county_boundaries_multipart"

    cmd = f"ogr2ogr {dst} {vsi_src} {layer}"

    logger.info(f"Extracting mn_county_boundaries_multipart layer to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def clean_boundaries(io_manager: DatasetIOManager) -> Path:
    """Remove duplicates, reproject, and filter fields."""

    src = io_manager.get_path(CountyBoundaries.EXTRACTED)
    dst = io_manager.get_path(CountyBoundaries.CLEANED)

    if dst.exists():
        logger.info(f"Cleaned county boundaries found at: {dst}")
        return dst

    layer = "mn_county_boundaries_multipart"

    cmd = f"""ogr2ogr \
                -t_srs EPSG:26915 \
                -sql 'SELECT COUNTYNAME as name, Shape as geom from {layer}' \
                -nln counties \
                {dst} {src}"""

    logger.info(f"Writing cleaned county boundaries to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def make_dataset(io_manager: DatasetIOManager) -> None:
    download_boundaries(io_manager)
    extract_boundaries(io_manager)
    clean_boundaries(io_manager)


def remove_dataset(io_manager: DatasetIOManager) -> None:
    for item in CountyBoundaries:
        match item:
            case CountyBoundaries.DOWNLOADED:
                continue  # Don't delete the source
            case _:
                file = io_manager.get_path(item)
                if file.exists():
                    logger.info(f"Deleting: {file}")
                    file.unlink()
