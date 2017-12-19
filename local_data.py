from datetime import datetime


class LocalData:
    FINANCIAL_DATA_PATH = "Z:\Google Drive\\01 - Studium\Bachelorarbeit\data\coinmarketcap-2017-10-08\\"

    EXTERNAL_PATH_RAW_DATA = "X:\\bachelor-thesis\\raw-data"
    EXTERNAL_PATH_COMPRESSED_DATA = "X:\\bachelor-thesis\\compressed-data"
    EXTERNAL_PATH_AGGREGATED_DATA = "X:\\bachelor-thesis\\final-aggregated-data"
    EXTERNAL_PATH_ADDITIONAL_DATA = "X:\\bachelor-thesis\\additional-data"

    FOLDER_COMPRESSED_DATA_ONLY_RAW_DATA = "only-with-raw-data"
    FOLDER_COMPRESSED_DATA_WITH_ADDITIONAL_DATA = "with-additional-data"

    LAST_DATA_FOR_DOWNLOAD: int = int(datetime.strptime("01.12.2017 10:00", "%d.%m.%Y %H:%M").timestamp() * 1e3)

    COIN_MARKET_CAP_GRAPH_API_URL = "graphs.coinmarketcap.com"
