import requests
from typing import List, Tuple
import datetime
import bz2
import os
import shutil
import hashlib
from functools import partial
from enum import Enum
import logging
import time

# define top level module logger
logger = logging.getLogger(__name__)


def get_file_list() -> List[str]:
    return requests.get("https://database.lichess.org/standard/list.txt").text.split("\n")


def get_file_for_(year: int, month: int):
    now = datetime.datetime.today()
    first_day_of_month = now.replace(day=1)
    last_day_with_data = first_day_of_month - datetime.timedelta(days=1)
    first_day_with_data = datetime.datetime(year=2013, month=1, day=1)
    assert first_day_with_data <= datetime.datetime(year=year, month=month, day=1) <= last_day_with_data, \
        "not in range with data"
    dt = datetime.datetime(year=year, month=month, day=1)
    for fl in get_file_list():
        if dt.strftime("%Y-%m") in fl:
            return fl
    raise ValueError("no data for date")


def _shutil_copyfileobj(r: requests.Response, raw_file_path: str):
    r.raw.read = partial(r.raw.read, decode_content=True)
    with open(raw_file_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f, length=8192)


def _iter_content(r: requests.Response, raw_file_path: str):
    with open(raw_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


class DOWNLOAD_ZIPPED_METHOD(Enum):
    SHUTIL_COPY_FILE_OBJ = _shutil_copyfileobj
    ITER_CONTEXT = _iter_content


def download_zipped_data(filename: str, method: DOWNLOAD_ZIPPED_METHOD):
    raw_file_path = os.path.join("raw_data", filename)
    url = "https://database.lichess.org/standard/" + filename
    logger.info(f"getting data for {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        logging.info(f"request successful!")
        if not os.path.exists("raw_data"):
            logger.info(f"raw_data folder didn't exist, creating it")
            os.makedirs("raw_data")
            logger.info(f"raw_data folder created")
        logger.info(f"downloading data into file using: {repr(method)}")
        method(r, raw_file_path)
    return raw_file_path


def get_checksum(path):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    hs = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hs.update(data)
    return hs.hexdigest()


def inc_download_and_unzip(year: int, month: int):
    start_time = time.time()
    expected_checksum, filename = get_checksum_and_filename(year, month)
    if not os.path.exists("data"):
        logger.info(f"data folder didn't exist, creating it")
        os.makedirs("data")
        logger.info(f"data folder created")
    new_data_filepath = os.path.join('data', filename.replace(".bz2", ""))
    url = "https://database.lichess.org/standard/" + filename
    logger.info(f"getting data for {url}")
    hs = hashlib.sha256()
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        logger.info(f"request successful! downloading data into file using: incremental method")
        dec = bz2.BZ2Decompressor()
        with open(new_data_filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                hs.update(chunk)
                rtn = dec.decompress(chunk)
                if dec.eof:
                    unused = dec.unused_data
                    dec = bz2.BZ2Decompressor()
                    if unused:
                        dec.decompress(unused)
                    f.write(rtn)
    if dec.unused_data != b'':
        logger.warning(f"some unused data not decompress: len = {len(dec.unused_data)}")
    logger.info(f"decompress done")
    assert expected_checksum == hs.hexdigest()
    end_time = time.time()
    logger.info(f"checksum successful: took {round(end_time - start_time, 0)}")


def decompress_data(raw_file_path: str, newfilepath: str):
    # BUF_SIZE is totally arbitrary, from a couple experiments
    BUF_SIZE = 4096 * (2 ** 4)  # 65,536 did best
    logger.info(f"decompressing to {newfilepath} in buf_size={BUF_SIZE}")
    s = time.time()
    with open(newfilepath, 'wb') as new_file, bz2.BZ2File(raw_file_path, 'rb') as file:
        for data in iter(lambda: file.read(BUF_SIZE), b''):
            new_file.write(data)
    e = time.time()
    total_time = round(e - s, 0)
    logger.info(f"decompressed data from {raw_file_path} to {newfilepath} using {BUF_SIZE} buffer size in {total_time} "
                f"seconds")


def download_data(year: int, month: int):
    # TODO, is it possible to do decompress chunks instead of saving them
    # this way we can possibly filter the data as we are downloading to save on storage
    expected_checksum, filename = get_checksum_and_filename(year, month)
    raw_file_path = download_zipped_data(filename, DOWNLOAD_ZIPPED_METHOD.ITER_CONTEXT)
    logger.info(f"downloaded zipped file={filename} to {raw_file_path}")
    actual_checksum = get_checksum(raw_file_path)
    if expected_checksum != actual_checksum:
        os.remove(raw_file_path)
        logger.info(f"removing {raw_file_path} checksum failed")
        raise AssertionError("checksum {} != hexdigest {}".format(expected_checksum, actual_checksum))
    logger.info("checksum passed")
    newfilepath = os.path.join('data', filename.replace(".bz2", ""))
    decompress_data(raw_file_path, newfilepath)
    os.remove(raw_file_path)
    logger.info(f"removing {raw_file_path}")


def get_checksums() -> dict:
    rtn = {}
    for line in requests.get("https://database.lichess.org/standard/sha256sums.txt").text.split("\n"):
        if line.strip() == "":
            continue
        checksum, filename = line.strip().split("  ")
        rtn[filename] = checksum
    return rtn


def get_checksum_and_filename(year: int, month: int) -> Tuple[str, str]:
    dt = datetime.datetime(year=year, month=month, day=1)
    for filename, checksum in get_checksums().items():
        if dt.strftime("%Y-%m") in filename:
            return checksum, filename
    raise ValueError("no data for date")
