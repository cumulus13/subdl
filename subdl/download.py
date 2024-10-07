"""
A rudimentary URL downloader (like wget or curl) to demonstrate Rich progress bars.
"""

from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os.path
import sys
from typing import Iterable
from urllib.request import urlopen, Request
import urllib.parse

from rich.progress import (
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    Progress,
    TaskID,
)


progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


def copy_url(task_id: TaskID, url: str, path: str, data: dict = {}, cookies: str = None) -> None:
    """create dataPost"""
    dataPost = urllib.parse.urlencode(data).encode('utf-8')
    """create Request object"""
    request = Request(url, data = dataPost)
    """Add cookies """
    if cookies: request.add_header('Cookie', cookies)
    """Copy data from a url to a local file."""
    response = urlopen(request)
    # This will break if the response doesn't contain content length
    progress.update(task_id, total=int(response.info()["Content-length"]))
    with open(path, "wb") as dest_file:
        progress.start_task(task_id)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            progress.update(task_id, advance=len(data))


def download(urls: Iterable[str], dest_dir: str, saveas: None, cookie: str = None, postData: dict = {}):
    """Download multuple files to the given directory."""
    with progress:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for url in urls:
                if not saveas:
                    filename = url.split("/")[-1]
                else:
                    filename = saveas
                dest_path = os.path.join(dest_dir, filename)
                task_id = progress.add_task("download", filename=filename, start=False)
                pool.submit(copy_url, task_id, url, dest_path, postData, cookie)


if __name__ == "__main__":
    # Try with https://releases.ubuntu.com/20.04/ubuntu-20.04.1-desktop-amd64.iso
    if sys.argv[1:]:
        download(sys.argv[1:], "./")
    else:
        print("Usage:\n\tpython downloader.py URL1 URL2 URL3 (etc)")
