import pandas as pd
import yfinance as yf

from src.logging.logging_config import logger
import yfinance as yf
from datetime import datetime


class DataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker

    def convert_timestamp_to_yfinance_format(self, timestamp):
        if timestamp == 0:
            return None
        # Convert to yfinance format (YYYY-MM-DD HH:MM:SS)
        yfinance_format = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return yfinance_format

    def fetch_active_period(self,start_date=0):
        # Fetch the historical data
        data = yf.Ticker(self.ticker).history(period='max')
        # Calculate the number of days the stock has been listed
        ticker_last_updated = data.index[-1]
        ticker_first_updated = data.index[0]
        listing_days = (data.index[-1] - data.index[0]).days
        print(f'{self.ticker} has been listed for {listing_days} days.')
        return listing_days, ticker_first_updated, ticker_last_updated

    # def fetch_active_period(self, start_date=0):
    #     # Fetch the historical data
    #
    #     # Convert start_date to a datetime object if it's not 0
    #     if start_date != 0:
    #         #start_date = self.convert_timestamp_to_yfinance_format(start_date)
    #         data = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    #     else:
    #         data = yf.Ticker(self.ticker).history(period='max')
    #
    #     if start_date != 0:
    #         # Convert the index of data to timezone-naive if necessary
    #         data.index = data.index.tz_localize(None)
    #         print("data.index " + str(type(data.index)))
    #         # Filter data to only include dates from start_date onwards
    #         data = data[data.index >= start_date]
    #
    #     # Check if the data is empty
    #     if data.empty:
    #         logger.info(f'No data available for {self.ticker} since {start_date}.')
    #         return None, None, None
    #
    #     # Calculate the number of minutes the stock has been listed
    #     ticker_last_updated = data.index[-1]
    #     ticker_first_updated = data.index[0]
    #     listing_minutes = (ticker_last_updated - ticker_first_updated).total_seconds() / 60
    #
    #     logger.info(f'{self.ticker} has been listed for {listing_minutes} minutes.')
    #     logger.info(f'{data.index} vs {start_date} time stamp.')
    #     return listing_minutes, ticker_first_updated, ticker_last_updated

    import yfinance as yf
    import pandas as pd

    def fetch_data(self, start_date, end_date, interval='1m'):
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {self.ticker} from {start_date} to {end_date}")
            data.reset_index(inplace=True)  # Add the date index as a column
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

    def fetch_data_less_precise(self, start_date, end_date, interval):
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {self.ticker} from {start_date} to {end_date}")
            data.reset_index(inplace=True)  # Add the date index as a column
            return data
        except Exception as e:
            logger.error(f"Error fetching less precise data: {e}")
            return None
