import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

import requests

from src.logging.logging_config import logger
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/app/src/')))
from src.marketCheck.marketCheck import marketTimeChecker
from src.server.yahoo.fetchYahoo import DataFetcher


class DataProcessor:
    def __init__(self, ticker):
        self.ticker = ticker
        self.tickerFilePath = "/app/server/listing_status.csv"
        self.tickerList = self.read_all_tickers_from_file()
        self.all_data = []


    # no api on yaho to do this :)
    def fetch_all_tickers(self, api_key):
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

    def store_all_tickers_file(self, symbol):
        # Save the CSV data to a file
        with open(self.tickerFilePath, 'w') as file:
            file.write(symbol)

    def read_all_tickers_from_file(self):
        file_path = self.tickerFilePath
        if os.path.getsize(file_path) == 0:
            logger.debug("The file is empty.")
            exit()
        else:
            data = pd.read_csv(file_path)
            logger.info("Data read successfully.")

        # Save the CSV data to a file
        with open(file_path, 'r') as file:
            content = file.read()
            logger.info("File content:\n", content)
            data = pd.read_csv(file_path)
        return data

    def strip_empty_lines(self):
        file_path = self.tickerFilePath
        if os.path.getsize(file_path) == 0:
            logger.debug("The file is empty.")
        else:
            data = pd.read_csv(file_path)
            logger.info("Data read successfully.")

        with open(file_path, 'r') as file:
            lines = file.readlines()

        with open(file_path, 'w') as file:
            for line in lines:
                if line.strip():  # This checks if the line is not empty
                    file.write(line)



    def plot_data(self, data, period='all'):
        if self.all_data:
            # Convert all timestamps to timezone-naive
            for i in range(len(self.all_data)):
                self.all_data[i].index = self.all_data[i].index.tz_localize(None)

            combined_data = pd.concat([data for data in self.all_data if data is not None]).sort_index()

            plt.figure(figsize=(15, 7))
            plt.plot(combined_data['Close'], label=f'{self.ticker} Closing Price')
            plt.title(f'{self.ticker} Closing Price')
            plt.xlabel('Time')
            plt.ylabel('Price (USD)')
            plt.legend()
            plt.grid(True)
            plt.show()
        else:
            logger.info("No data to plot. Data Procesing")
