import json
import logging
import math
import os
import time
from typing import List

import requests

from coinmarketCapApi import CoinmarketCapApi
from csv_strings import CSVStrings
from local_data import LocalData
from singleton import Singleton


@Singleton
class CurrencyHandler:
    def __init__(self, static=False):
        self.all_currencies_with_data = None

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("CurrencyHandler instantiated")

        self.coinmarketcapAPI: CoinmarketCapApi = CoinmarketCapApi(static=static)

        self.data_path: str = LocalData.FINANCIAL_DATA_PATH

        self.basic_currency_data = self.load_basic_currency_data()
        self.all_currency_names = self.load_all_currency_names()

    def get_all_currency_names_where_data_is_available(self, size_limit=math.inf) -> List[str]:
        if self.all_currencies_with_data is not None:
            if len(self.all_currencies_with_data) <= size_limit:
                return self.all_currencies_with_data
            else:
                return self.all_currencies_with_data[:size_limit]

        else:
            self.all_currencies_with_data = []
            for index, filename in enumerate(os.listdir(self.data_path)):
                if not os.path.isdir(os.path.join(self.data_path, filename)):
                    self.all_currencies_with_data.append(filename.split(".")[0])

            if len(self.all_currencies_with_data) <= size_limit:
                return self.all_currencies_with_data
            else:
                return self.all_currencies_with_data[:size_limit]

    def get_basic_currency_data(self, currency):
        if currency in self.basic_currency_data:
            return self.basic_currency_data[currency]
        else:
            time.sleep(1)
            path = ("https://" + LocalData.COIN_MARKET_CAP_GRAPH_API_URL + "/currencies/{}/").format(currency)
            response = requests.request("GET", path)

            if response.status_code == 404:
                self.logger.info("Currency {} not listed anymore".format(currency))
                self.basic_currency_data[currency] = None
            else:
                data = json.loads(response.text)
                datapoints = data[CSVStrings.PRICE_USD_STRING]

                self.basic_currency_data[currency] = {"start_date": datapoints[0][0]}
            self.save_basic_currency_data()
            return self.basic_currency_data[currency]

    def load_basic_currency_data(self) -> dict:
        filename: str = "basic-currency-data.json"
        file_path: str = os.path.join(LocalData.CURRENCY_HANDLER_PATH, filename)
        if os.path.isfile(file_path):
            with open(file_path) as file:
                return json.load(file)

        return dict()

    def save_basic_currency_data(self) -> None:
        filename: str = "basic-currency-data.json"
        file_path: str = os.path.join(LocalData.CURRENCY_HANDLER_PATH, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)

        with open(file_path, "w") as file:
            json.dump(self.basic_currency_data, file)

    def save_all_currency_names_data(self) -> None:
        filename: str = "all-currency-names.json"
        file_path: str = os.path.join(LocalData.CURRENCY_HANDLER_PATH, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)

        with open(file_path, "w") as file:
            json.dump(self.all_currency_names, file)

    def load_all_currency_names(self) -> dict:
        filename: str = "basic-currency-data.json"
        file_path: str = os.path.join(LocalData.CURRENCY_HANDLER_PATH, filename)

        if os.path.isfile(file_path):
            with open(file_path) as file:
                return json.load(file)

        return dict()

    def get_all_currency_names(self) -> List[str]:
        currencies: list = self.get_all_currency_names_where_data_is_available()

        additional: list = self.coinmarketcapAPI.get_all_currencies()

        for currency in additional:
            if currency["id"] in currencies:
                pass
            else:
                currencies.append(currency["id"])

        currencies.reverse()
        to_remove = list()
        for currency in currencies:
            if LocalData.LAST_DATA_FOR_DOWNLOAD - 1000 * 3600 * 24 * 3 < self.get_basic_currency_data(currency)[
                "start_date"]:
                to_remove.append(currency)

        for currency in to_remove:
            currencies.remove(currency)

        self.all_currency_names = currencies
        self.save_all_currency_names_data()

        return sorted(self.all_currency_names)
