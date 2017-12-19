import logging
import os

from currency_handler import CurrencyHandler
from raw_data.coinmarketcap_importer import CoinMarketCapGraphAPIImporter


class RawDataImporter:
    def __init__(self, last_date_for_download=1512118800000, path="/"):
        self.path = path
        self.path_raw_data = os.path.join(path, "raw-data")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ch = CurrencyHandler.Instance()
        self.coinmarketcap_importer = CoinMarketCapGraphAPIImporter()

        self.last_timestamp = last_date_for_download

    def download_all_data(self):
        currencies = self.ch.get_all_currency_names()

        for currency in currencies:
            self.logger.info("Start - Downloading currency:{}".format(currency))
            self.coinmarketcap_importer.request_currency(currency, self.last_timestamp)
            self.logger.info("End - Downloading currency:{}".format(currency))

        # Mark currency download until last_date as finished
        open(os.path.join(self.path_raw_data, "ready" + str(self.last_timestamp)), "w").close()
        self.logger.info("Finished downloading currencies until {}".format(self.last_timestamp))
