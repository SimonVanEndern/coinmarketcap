import logging
import os

from aggregated_data.aggregate_compressed_data import ReduceSimplifiedData
from compressed_raw_data.compress_raw_data import SimplifyRawData
from raw_data.raw_data_importer import RawDataImporter


class MainDataImporter:
    logging.basicConfig(level=logging.INFO)

    def __init__(self, path="/", last_date_for_download=1512118800000):
        self.path = path
        self.path_raw_data = os.path.join(path, "raw-data")

        self.raw_data_downloader = RawDataImporter()
        self.raw_data_simplifier = SimplifyRawData()
        self.raw_data_converter = ReduceSimplifiedData()

        self.last_time = last_date_for_download
        self.interval = 24  # hours

    def run(self):
        self.raw_data_downloader.download_all_data()
        self.raw_data_simplifier.compress_data(self.last_time)
        self.raw_data_converter.aggregate_compressed_data(self.last_time, self.interval)


MainDataImporter().run()
