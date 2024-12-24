from src.logging.logging_config import logger
from src.server.DatabaseManager.dataPorcesing import fetch_all_tickers
from src.server.DatabaseManager.runner import Runner
from src.server.yahoo.dataProcesingYahoo import DataProcessorYahoo
from src.server.yahoo.yahoo_db import Yahoo


class Yahoorunner(Runner):
    """
    Yahoorunner class for managing Yahoo financial data.

    This class inherits from the Runner class and manages data processing and
    database interactions for Yahoo financial data.
    """

    def __init__(self, api_key_load, docker_config, config_path, ticker_path):
        """
        Initializes the Yahoorunner instance.

        Args:
            api_key_load (str): The API key for accessing the data.
            docker_config (str): Path to the Docker configuration file.
            config_path (str): Path to the configuration file containing API keys.
            ticker_path (str): Path to the ticker file.

        """
        self.api_key_Load = api_key_load  # Replace with your actual API key
        self.docker_config = docker_config
        self.config_path = config_path
        self.ticker_file = ticker_path  # "/app/server/listing_status.csv"
        self.ticker_list = []
        # no need to load every time the new list :)

        super().__init__(api_key_load, docker_config, config_path)
        self.dataProcessor = DataProcessorYahoo("A", ticker_path)
        self.db_manager = Yahoo(docker_config, api_key_load, ticker_path)

    def get_watched_list_all(self):
        """
        Retrieves the entire watched ticker list.

        Returns:
            list: A list of all watched tickers.
        """
        tickers_list = self.db_manager.get_ticker_list()
        return tickers_list

    def full_update_watch_list(self, tickers):
        """
        Fully updates the watch list with new tickers.

        Args:
            tickers (list): List of tickers to update.
        """
        ticker_list = self.db_manager.get_ticker_list()
        self.db_manager.fetch_and_store_data(ticker_list, self.api_key_Load)

    def update_watch_list(self, tickers):
        """
        Updates the watch list with the provided tickers.

        Args:
            tickers (list): List of tickers to update.
        """
        ticker_list = self.db_manager.get_ticker_list()
        self.db_manager.fetch_and_store_data(ticker_list, self.api_key_Load)

    def add_to_watch_list(self, tickers):
        """
        Adds tickers to the watch list.

        Args:
            tickers (list): List of tickers to add.
        """
        logger.info("add_to_watch_list")
        self.db_manager.add_to_watcher_list(tickers)

    def remove_from_watch_list(self, tickers):
        """
        Removes tickers from the watch list.

        Args:
            tickers (list): List of tickers to remove.
        """
        logger.info("remove_from_watch_list")
        self.db_manager.remove_from_watcher_list(tickers)

    def update_ticker_list(self):
        """
        Updates the ticker list by fetching all tickers.
        """
        ticker = fetch_all_tickers(self.api_key_Load)
        self.dataProcessor.store_all_tickers_file(ticker)
        self.dataProcessor.strip_empty_lines()

    def store_ticker_list(self, tickers):
        """
        Stores the provided ticker list.

        Args:
            tickers (list): List of tickers to store.
        """
        tickers_list = self.get_all_tickers_file()
        logger.info(tickers_list)
        self.db_manager.fetch_and_store_symbol(tickers_list, self.api_key_Load)

    def get_all_tickers_file(self):
        """
        Retrieves all tickers from the file.

        Returns:
            list: A list of all tickers from the file.
        """
        self.ticker_list = self.dataProcessor.read_all_tickers_from_file()
        return self.ticker_list

    def get_tickers(self, watcher=True):
        """
        Retrieves the tickers from the database.

        Args:
            watcher (bool): If True, retrieves the watched tickers, otherwise all tickers.

        Returns:
            list: A list of tickers.
        """
        self.ticker_list = self.db_manager.get_ticker_list(watcher)
        return self.ticker_list

    def load_data(self, tickers):
        """
        Loads data for the provided tickers from the database.

        Args:
            tickers (list): List of tickers to load data for.

        Returns:
            DataFrame: DataFrame containing the data for the provided tickers.
        """
        all_data = self.db_manager.fetch_data_from_db(tickers)
        return all_data

    def plot_graph(self, all_data, chunk_size):
        """
        Plots the data for the provided tickers.

        Args:
            all_data (DataFrame): DataFrame containing all data to plot.
            chunk_size (int): The size of each data chunk to plot.

        Returns:
            Figure: A matplotlib figure object with the plotted data.
        """
        return self.dataProcessor.plot_data(all_data)

    def get_tickers_from_variable(self):
        """
        Retrieves the tickers from the class variable, falling back to the database if necessary.

        Returns:
            list: A list of tickers.
        """
        self.ticker_list = self.db_manager.ticker_list_Storage
        if self.ticker_list.empty:
            self.ticker_list = self.db_manager.get_ticker_list(False)
            logger.debug("It was empty")
        return self.ticker_list

    def get_tickers_from_db(self):
        """
        Retrieves the tickers directly from the database.

        Returns:
            list: A list of tickers.
        """
        self.ticker_list = self.db_manager.get_ticker_list(False)
        return self.ticker_list


# Example usage
if __name__ == "__main__":
    logger.info("yahooRunner")
