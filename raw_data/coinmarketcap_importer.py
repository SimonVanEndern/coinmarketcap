import csv
import json
import logging
import os.path
import time

import requests

from csv_strings import CSVStrings
from currency_handler import CurrencyHandler
from local_data import LocalData


def check_data_already_downloaded(currency, start, end, save_path):
    filename = str(start) + "-" + str(end) + ".csv"
    return os.path.isfile(os.path.join(save_path, currency, filename))


class CoinMarketCapGraphAPIImporter:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.raw_data_path = LocalData.EXTERNAL_PATH_RAW_DATA
        self.save_path_additional_data = LocalData.EXTERNAL_PATH_ADDITIONAL_DATA

        self.ch = CurrencyHandler.Instance()

    def request_currency(self, currency, last_date_for_download):
        if os.path.isfile(os.path.join(self.raw_data_path, currency, "ready" + str(last_date_for_download))):
            self.logger.info("All currencies until {} already downloaded".format(last_date_for_download))
            return

        start_date_of_currency = self.ch.get_basic_currency_data(currency)["start_date"]

        if last_date_for_download < start_date_of_currency:
            return

        if not os.path.isdir(os.path.join(self.raw_data_path, currency)):
            os.mkdir(os.path.join(self.raw_data_path, currency))

        self.request_data_monthly(currency, start_date_of_currency, last_date_for_download)

        # Mark currency as completely downloaded for this timestamp
        open(os.path.join(self.raw_data_path, currency, "ready" + str(last_date_for_download)), "w").close()

    def request_data_monthly(self, currency, first_date, last_date):
        span_month = 29 * 24 * 60 * 60 * 1000

        dates = list(range(first_date, last_date, span_month))
        dates = list(map(lambda x: [x, x + span_month], dates))
        dates[len(dates) - 1][1] = last_date

        for date_tuple in dates:
            data = self.request_data(currency, date_tuple[0], date_tuple[1], self.raw_data_path)
            self.save_data(data, currency, date_tuple[0], date_tuple[1], self.raw_data_path)

    def request_data(self, currency, start, end, save_path):
        if check_data_already_downloaded(currency, start, end, save_path):
            return None

        print("Sleeping for 1 secs to circumvent DOS Protection denials")
        time.sleep(1)

        path = (
            "https://" + LocalData.COIN_MARKET_CAP_GRAPH_API_URL + "/currencies/{}/{}/{}/".format(currency, start, end))
        self.logger.info("Start: Downloading from " + path)
        response = requests.request("GET", path)
        self.logger.info("End: Downloading from " + path)

        if response.status_code != 200:
            self.logger.warning("No results: {}".format(path))
        else:
            return json.loads(response.text)

    def save_data(self, data, currency, start, end, path):
        if data is None:
            self.logger.info("Currency {} from {} to {} already downloaded".format(currency, start, end))
            return

        if len(data[CSVStrings.PRICE_USD_STRING]) == 2:
            self.logger.info("Currency {} from {} to {} has no additional data".format(currency, start, end))

        self.logger.info(
            "saved data from {} to {} --> {} entries".format(start, end, len(data[CSVStrings.PRICE_USD_STRING])))
        if len(data[CSVStrings.PRICE_USD_STRING]) < 800:
            self.logger.warning(
                "For {} to {} we only got {} entries".format(start, end, len(data[CSVStrings.PRICE_USD_STRING])))

        filename = str(start) + "-" + str(end) + ".csv"
        if not os.path.isdir(os.path.join(path, currency)):
            os.mkdir(os.path.join(path, currency))

        csv_data = self.convert_json_to_csv_data(data)

        with open(os.path.join(path, currency, filename), "w") as file:
            writer = csv.writer(file, delimiter=",", lineterminator="\n")
            writer.writerow(("Timestamp", "USD", "BTC", "Volume", "Market_cap"))
            for row in csv_data:
                writer.writerow(list(row))

    def request_additional_data(self, currency, time_span_tuples):
        for time_span in time_span_tuples:
            data = self.request_data(currency, time_span[0], time_span[1], self.save_path_additional_data)
            self.save_data(data, currency, time_span[0], time_span[1], self.save_path_additional_data)

        if os.path.isdir(os.path.join(self.save_path_additional_data, currency)):
            open(os.path.join(self.save_path_additional_data, currency,
                              "ready" + str(LocalData.LAST_DATA_FOR_DOWNLOAD)), "w").close()

    def convert_json_to_csv_data(self, data):

        market_cap = list(data[CSVStrings.MARKET_CAP_STRING])
        timestamps = list(list(zip(market_cap))[0])
        market_cap = list(list(zip(market_cap))[1])

        price_usd = list(data[CSVStrings.PRICE_USD_STRING])
        price_usd = list(list(zip(price_usd))[1])

        price_btc = list(data[CSVStrings.PRICE_BTC_STRING])
        price_btc = list(list(zip(price_btc))[1])

        volume_usd = list(data[CSVStrings.VOLUME_STRING])
        volume_usd = list(list(zip(volume_usd))[1])

        return zip(timestamps, price_usd, price_btc, volume_usd, market_cap)
