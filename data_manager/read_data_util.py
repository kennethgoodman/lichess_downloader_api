from typing import List, Union, TextIO
import os
import datetime
import logging

# define top level module logger
logger = logging.getLogger(__name__)

class ReadManager:
    def __init__(self, year: int, month: int):
        self.year: int = year
        self.month: int = month
        self.dt = datetime.datetime(year=self.year, month=self.month, day=1)
        self.f: Union[TextIO, None] = None  # file object

    @staticmethod
    def get_file_list() -> List[str]:
        return os.listdir('data')

    def has_data(self) -> bool:
        return self.get_path() is not None

    def get_path(self) -> Union[str, None]:
        try:
            for fl in self.get_file_list():
                if self.dt.strftime("%Y-%m") in fl:
                    return os.path.join('data', fl)
        except FileNotFoundError:
            logger.warning("couldn't find file list folder")
            return None
        return None

    def __enter__(self):
        self.f = open(self.get_path())
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.f is not None:
            self.f.close()
