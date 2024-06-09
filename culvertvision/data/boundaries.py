import shlex
import subprocess
from enum import StrEnum
from pathlib import Path

from loguru import logger

from culvertvision.config import Settings
from culvertvision.data.utils import download_file

SOURCE_URL = "https://resources.gisdata.mn.gov/pub/gdrs/data/pub/us_mn_state_dnr/bdry_counties_in_minnesota/gpkg_bdry_counties_in_minnesota.zip"


class CountyBoundaries(StrEnum):
    DOWNLOADED = "raw/gpkg_bdry_counties_in_minnesota.zip"
    EXTRACTED = "interim/county_boundaries.gpkg"
    CLEANED = "processed/county_boundaries.gpkg"

    def get_path(self, settings: Settings) -> Path:
        return settings.DATA_DIR / self.value


def download_boundaries(settings: Settings) -> Path:
    """Download a dataset of MN county boundaries."""

    src = SOURCE_URL
    dst = CountyBoundaries.DOWNLOADED.get_path(settings)

    if dst.exists():
        logger.info(f"Downloaded county boundaries found at: {dst}")
        return dst

    logger.info(f"Downloading county boundaries to: {dst}")
    return download_file(url=src, dst=dst)


def extract_boundaries(settings: Settings) -> Path:
    """Extract the mn_county_boundaries_multipart layer from the zipped geopackage."""

    src = CountyBoundaries.DOWNLOADED.get_path(settings)
    dst = CountyBoundaries.EXTRACTED.get_path(settings)

    if dst.exists():
        logger.info(f"Extracted county boundaries found at: {dst}")
        return dst

    vsi_src = f"/vsizip/{src}/bdry_counties_in_minnesota.gpkg"
    layer = "mn_county_boundaries_multipart"

    cmd = f"ogr2ogr {dst} {vsi_src} {layer}"

    logger.info(f"Extracting mn_county_boundaries_multipart layer to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def clean_boundaries(settings: Settings) -> Path:
    """Remove duplicates, reproject, and filter fields."""

    src = CountyBoundaries.EXTRACTED.get_path(settings)
    dst = CountyBoundaries.CLEANED.get_path(settings)

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



if __name__ == "__main__":
    settings = Settings()
    download_boundaries(settings)
    extract_boundaries(settings)
    clean_boundaries(settings)
