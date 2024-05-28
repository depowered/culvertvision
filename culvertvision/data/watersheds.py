import shlex
import subprocess
from pathlib import Path

import requests
from loguru import logger
from pydantic import config

from culvertvision.config import StorageConfig

WATERSHEDS = {
    "raw": {
        "filename": "NHDPLUS_H_0704_HU4_GPKG.zip",
        "url": "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/VPU/Current/GPKG/NHDPLUS_H_0704_HU4_GPKG.zip",
    },
    "intermim": {"filename": "huc12_watersheds.gpq"},
}


def download_watersheds(config: StorageConfig) -> Path:
    url = WATERSHEDS["raw"]["url"]
    filename = WATERSHEDS["raw"]["filename"]
    output = config.data_dir / "raw" / filename

    if output.exists():
        logger.info(f"Skipping download: {output.name} already exists.")
        return output

    logger.info(f"Downloading raw watershed file: {filename}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        with open(output, "wb") as f:
            for chunk in r.iter_content(chunk_size=10 * 1024):
                f.write(chunk)

    return output


def extract_huc12_watersheds(config: StorageConfig) -> Path:
    zipfile = config.data_dir / "raw" / WATERSHEDS["raw"]["filename"]
    src_dataset = f"/vsizip/{zipfile}/{zipfile.stem}.gpkg"
    layer_name = "WBDHU12"

    dst_dataset = config.data_dir / "interim" / WATERSHEDS["intermim"]["filename"]
    dst_crs = "EPSG:26915"
    # Filter duplicate geometries and exclude unneeded fields
    sql = f"SELECT DISTINCT HUC12 as huc12, Name as name, Shape as geom from {layer_name}"

    if dst_dataset.exists():
        logger.info(f"Skipping extraction: {dst_dataset.name} already exists.")
        return dst_dataset

    cmd = f"""ogr2ogr \
                -f Parquet \
                -t_srs {dst_crs} \
                -sql '{sql}' \
                {dst_dataset} {src_dataset}"""

    logger.info(f"Extracting {layer_name} to {dst_dataset.name}")
    subprocess.run(shlex.split(cmd), check=True)

    return dst_dataset


if __name__ == "__main__":
    config = StorageConfig()
    download_watersheds(config)
    extract_huc12_watersheds(config)
