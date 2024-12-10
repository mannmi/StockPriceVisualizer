import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/app/')))
from marketCheck.marketCheck import marketTimeChecker
from server.yahoo.fetchYahoo import DataFetcher


class DataProcessorAlphaVantage:
    def __init__(self, ticker):
        self.ticker = ticker
        self.tickerList = self.read_all_tickers_from_file()
        self.all_data = []


    #todo update to support more granulair fetch (this has to be done later
    #   see how it was implemneted in fetchYahoo.py
    def process_data(self,tickers):
        url = 'https://www.alphavantage.co/query'
        configAuth = Yml_Loader('./config.yml')

        if not tickers:
            raise ValueError("The list of tickers is empty. Please provide at least one ticker symbol.")

        for ticker in tickers:
            try:
                params = {
                    'function': 'TIME_SERIES_INTRADAY',
                    'symbol': ticker,
                    'interval': '1min',
                    'apikey': api_key  # Add the API key here
                }
                response = requests.get(url, params=params)
                data = response.json()

                # Debugging: Print the response to check its structure
                print(f"Response for {ticker}: {data}")

                # Check if 'Time Series (1min)' is in the response
                # If not then this may be one of the error messages :)
                if 'Time Series (1min)' in data:
                    time_series = data['Time Series (1min)']
                    df = pd.DataFrame.from_dict(time_series, orient='index')
                    df = df.astype(float)
                    df.index = pd.to_datetime(df.index)

                    # Store data in the database
                    self.store_data(ticker, df)
                else:
                    # Handle different types of errors
                    if 'Note' in data:
                        print(f"Note for {ticker}: {data['Note']}")
                    elif 'Error Message' in data:
                        print(f"Error for {ticker}: {data['Error Message']}")
                    else:
                        print(f"Unexpected response for {ticker}: {data}")

