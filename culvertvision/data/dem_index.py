from pathlib import Path

import geopandas
import pandas as pd
from geopandas import GeoDataFrame
from loguru import logger

from culvertvision.data.io_manager import DatasetEnum, DatasetIOManager
from culvertvision.data.utils import download_file

OPR_DOWNLOAD_LINKS_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/Projects/MN_GoodhueCounty_2020_A20/MN_GoodhueCo_1_2020/0_file_download_links.txt"
OPR_INDEX_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/MN_GoodhueCounty_2020_A20/MN_GoodhueCo_1_2020/spatial_metadata/USGS/opr_index.gpkg"


class LinksList(DatasetEnum):
    DOWNLOADED = "raw/opr_download_links.txt"


class DemIndex(DatasetEnum):
    DOWNLOADED = "raw/opr_index.gpkg"
    CLEANED = "interim/dem_index.gpkg"
    JOINED = "processed/dem_index.gpkg"


def download_links_textfile(io_manager: DatasetIOManager) -> Path:
    """Download text file with links to all OPR DEMs in the LiDAR project."""

    src = OPR_DOWNLOAD_LINKS_URL
    dst = io_manager.get_path(LinksList.DOWNLOADED)

    if dst.exists():
        logger.info(f"Downloaded links textfile found at: {dst}")
        return dst

    logger.info(f"Downloading links textfile to: {dst}")
    return download_file(url=src, dst=dst)


def download_dem_index(io_manager: DatasetIOManager) -> Path:
    """Download the index geopackage of OPR TIFs."""

    src = OPR_INDEX_URL
    dst = io_manager.get_path(DemIndex.DOWNLOADED)

    if dst.exists():
        logger.info(f"Downloaded OPR index found at: {dst}")
        return dst

    logger.info(f"Downloading OPR index to: {dst}")
    return download_file(url=src, dst=dst)


def clean_dem_index(io_manager: DatasetIOManager) -> Path:
    """Reproject and filter fields."""

    src = io_manager.get_path(DemIndex.DOWNLOADED)
    dst = io_manager.get_path(DemIndex.CLEANED)

    if dst.exists():
        logger.info(f"Cleaned DEM index found at: {dst}")
        return dst

    logger.info(f"Writing cleaned DEM index to: {dst}")
    gdf: GeoDataFrame = geopandas.read_file(filename=src)
    gdf["id"] = gdf["location"].apply(lambda x: Path(x).stem)
    gdf = gdf.filter(["id", "geometry"], axis="columns")
    gdf = gdf.to_crs(crs="EPSG:26915")
    gdf.to_file(filename=dst)


def join_dem_index(io_manager: DatasetIOManager) -> Path:
    """Join download URLs to features in the DEM index."""

    src = io_manager.get_path(DemIndex.CLEANED)
    dst = io_manager.get_path(DemIndex.JOINED)

    if dst.exists():
        logger.info(f"Joined DEM index found at: {dst}")
        return dst

    logger.info(f"Writing joined DEM index to: {dst}")

    # Prepare the URLs for joining by extracting an ID (TIF name)
    df = pd.read_csv(io_manager.get_path(LinksList.DOWNLOADED), names=["url"])
    df["id"] = df["url"].str.extract(r"(\d+).tif")

    gdf: GeoDataFrame = geopandas.read_file(filename=src)
    gdf = gdf.merge(right=df, how="left", on="id")
    gdf.to_file(filename=dst)


def make_dataset(io_manager: DatasetIOManager) -> None:
    download_links_textfile(io_manager)
    download_dem_index(io_manager)
    clean_dem_index(io_manager)
    join_dem_index(io_manager)


def remove_dataset(io_manager: DatasetIOManager) -> None:
    for item in DemIndex:
        match item:
            case DemIndex.DOWNLOADED:
                continue  # Don't delete the source
            case _:
                file = io_manager.get_path(item)
                if file.exists():
                    logger.info(f"Deleting: {file}")
                    file.unlink()
