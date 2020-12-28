from data_manager.read_data_util import ReadManager
from data_manager.download_data_utils import inc_download_and_unzip


class Manager(ReadManager):
    def __init__(self, year: int, month: int):
        super().__init__(year, month)
        if not self.has_data():
            inc_download_and_unzip(year, month)
            # download_data(year, month)
