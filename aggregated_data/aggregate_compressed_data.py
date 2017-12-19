from finance_data_import.currency_handler import CurrencyHandler

from aggregated_data.currency_aggregator import CurrencyAggregator


class ReduceSimplifiedData:
    def __init__(self):
        self.currency_handler = CurrencyHandler.Instance()

    def aggregate_compressed_data(self, last_time: int, interval: int):
        for currency in self.currency_handler.get_all_currency_names():
            CurrencyAggregator(currency, last_time, interval).run()
