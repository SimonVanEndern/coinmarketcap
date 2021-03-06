import logging

from finance_data_import.currency_handler import CurrencyHandler

from compressed_raw_data.currency_compressor import CurrencyCompressor


class SimplifyRawData:
    def __init__(self):
        self.currency_handler = CurrencyHandler.Instance()

    def compress_data(self, last_time):
        logging.info("{} Compressing data for all currencies".format(self.__class__.__name__))

        for currency_name in self.currency_handler.get_all_currency_names():
            CurrencyCompressor(currency_name, last_time)
