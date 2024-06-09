from pathlib import Path

import requests


def download_file(url: str, dst: Path) -> Path:
    if dst.exists():
        return dst

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        dst.parent.mkdir(exist_ok=True, parents=True)

        with open(dst, "wb") as f:
            for chunk in r.iter_content(chunk_size=10 * 1024):
                f.write(chunk)

    return dst
