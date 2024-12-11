import os
import sys

from src.logging.logging_config import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/app/')))

from src.server.DatabaseManager.runner import Runner
from src.server.yahoo.dataProcesingYahoo import DataProcessorYahoo
from src.server.yahoo.yahoo_db import Yahoo


# from server.backup.fetch_data import ticker


class yahooRunner(Runner):
    def __init__(self, api_key_Load, docker_config, config_path, ticker_path):
        self.api_key_Load = api_key_Load  # Replace with your actual API key
        self.docker_config = docker_config
        self.config_path = config_path
        self.ticker_file = ticker_path  # "/app/server/listing_status.csv"
        self.ticker_list = []
        # no need to load evry time the new list :)

        super().__init__(api_key_Load, docker_config, config_path)
        self.dataProcessor = DataProcessorYahoo("A", ticker_path)
        self.db_manager = (Yahoo(docker_config, api_key_Load, ticker_path))

    def get_watched_list_all(self):
        tickers_list = self.db_manager.get_ticker_list()
        return tickers_list

    def full_update_watch_list(self, tickers):
        #print("todo")
        ticker_list = self.db_manager.get_ticker_list()
        self.db_manager.fetch_and_store_data(ticker_list, self.api_key_Load)

    def update_watch_list(self, tickers):
        ticker_list = self.db_manager.get_ticker_list()
        self.db_manager.fetch_and_store_data(ticker_list, self.api_key_Load)

    def add_to_watch_list(self, tickers):
        logger.info("add_to_watch_list")
        self.db_manager.add_to_watcher_list(tickers)

    def remove_from_watch_list(self, tickers):
        logger.info("remove_from_watch_list")
        self.db_manager.remove_from_watcher_list(tickers)

    def update_ticker_list(self):
        ticker = self.dataProcessor.fetch_all_tickers(self.api_key_Load)
        self.dataProcessor.store_all_tickers_file(ticker)
        self.dataProcessor.strip_empty_lines()

    def store_ticker_list(self, tickers):
        tickers_list = self.get_all_tickers_file()
        logger.info(tickers_list)
        # todo remove this line ? not realy used at the moment with yahoo
        self.db_manager.fetch_and_store_symbol(tickers_list, self.api_key_Load)

    def get_all_tickers_file(self):
        self.ticker_list = self.dataProcessor.read_all_tickers_from_file()
        return self.ticker_list

    def get_tickers(self, watcher=True):
        self.ticker_list = self.db_manager.get_ticker_list(watcher)
        return self.ticker_list

    def load_data(self,tickers):
        all_data = self.db_manager.fetch_data_from_db(tickers)
        return all_data

    def plotGraph(self,all_data,chunk_size):
        self.dataProcessor.all_data = all_data
        return self.dataProcessor.plot_data(chunk_size)

    def get_tickers_from_variable(self):
        self.ticker_list = self.db_manager.ticker_list_Storage
        if self.ticker_list.empty:
             self.ticker_list = self.db_manager.get_ticker_list(False)
             logger.debug("It was empty")
        return self.ticker_list

    def get_tickers_from_db(self):
        self.ticker_list = self.db_manager.get_ticker_list(False)
        return self.ticker_list


# Example usage
if __name__ == "__main__":
    logger.info("yahooRunner")
