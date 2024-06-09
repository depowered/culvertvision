import shlex
import subprocess
from enum import StrEnum
from pathlib import Path

from loguru import logger

from culvertvision.config import Settings
from culvertvision.data.utils import download_file

SOURCE_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GPKG/NHDPLUS_H_0704_HU4_GPKG.zip"


class Huc12Watersheds(StrEnum):
    DOWNLOADED = "raw/NHDPLUS_H_0704_HU4_GPKG.zip"
    EXTRACTED = "interim/huc_12_watersheds.gpkg"
    CLEANED = "processed/huc_12_watersheds.gpkg"

    def get_path(self, settings: Settings) -> Path:
        return settings.DATA_DIR / self.value


def download_watersheds(settings: Settings) -> Path:
    """Download the NHDPLUS dataset for the project location."""

    src = SOURCE_URL
    dst = Huc12Watersheds.DOWNLOADED.get_path(settings)

    if dst.exists():
        logger.info(f"Downloaded watersheds found at: {dst}")
        return dst

    logger.info(f"Downloading watersheds to: {dst}")
    return download_file(url=src, dst=dst)


def extract_watersheds(settings: Settings) -> Path:
    """Extract the WBHUC12 layer to its own geopackage."""

    src = Huc12Watersheds.DOWNLOADED.get_path(settings)
    dst = Huc12Watersheds.EXTRACTED.get_path(settings)

    if dst.exists():
        logger.info(f"Extracted watersheds found at: {dst}")
        return dst

    vsi_src = f"/vsizip/{src}/{src.stem}.gpkg"
    layer = "WBDHU12"

    cmd = f"ogr2ogr {dst} {vsi_src} {layer}"

    logger.info(f"Extracting WBHUC12 layer to: {dst}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst


def clean_watersheds(settings: Settings) -> Path:
    """Remove duplicates, reproject, and filter fields."""

    src = Huc12Watersheds.EXTRACTED.get_path(settings)
    dst = Huc12Watersheds.CLEANED.get_path(settings)

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


if __name__ == "__main__":
    settings = Settings()
    download_watersheds(settings)
    extract_watersheds(settings)
    clean_watersheds(settings)
