import os
import pandas as pd
import requests
from src.logging.logging_config import logger


def fetch_all_tickers(api_key):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'LISTING_STATUS',
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.text
    # Load the CSV data into a DataFrame
    # df = pd.read_csv('../listing_status.csv')
    return data


class DataProcessor:
    def __init__(self, ticker,ticker_file_path):
        """
        Deals with data, this is the base class for the different data sources.
        Args:
            ticker: start ticker symbol (deprecated ?)
            ticker_file_path: path to the ticker data file
        """
        self.ticker = ticker
        self.ticker_file_path = ticker_file_path
        self.tickerList = self.read_all_tickers_from_file()
        self.all_data = []


    def store_all_tickers_file(self, symbol):
        """
        Store the ticker data file
        Args:
            symbol: symbols to store in the ticker file

        Returns:

        """
        # Save the CSV data to a file
        with open(self.ticker_file_path, 'w') as file:
            file.write(symbol)

    def read_all_tickers_from_file(self):
        """
        Read the ticker data file
        Returns: the ticker data file

        """
        file_path = self.ticker_file_path
        if os.path.getsize(file_path) == 0:
            logger.debug("The file is empty.")
            exit()
        else:
            #data = pd.read_csv(file_path)
            logger.info("Data read successfully.")

        # Save the CSV data to a file
        with open(file_path, 'r') as file:
            content = file.read()
            logger.info("File content:\n", content)
            data = pd.read_csv(file_path)
        return data

    def strip_empty_lines(self):
        """
        strip empty lines from the ticker data file
        (Had a bug where there are empty lines in the file)
        Returns: None

        """
        file_path = self.ticker_file_path
        if os.path.getsize(file_path) == 0:
            logger.debug("The file is empty.")
        else:
            #data = pd.read_csv(file_path)
            logger.info("Data read successfully.")

        with open(file_path, 'r') as file:
            lines = file.readlines()

        with open(file_path, 'w') as file:
            for line in lines:
                if line.strip():  # This checks if the line is not empty
                    file.write(line)

