from datetime import datetime
from src.logging.logging_config import logger
import yfinance as yf


def convert_timestamp_to_yfinance_format(timestamp):
    """
    Converts a timestamp to the yfinance format (YYYY-MM-DD HH:MM:SS).

    Args:
        timestamp: The timestamp to convert.

    Returns:
        str: A string formatted as 'YYYY-MM-DD HH:MM:SS' if the timestamp is not 0, otherwise None.
    """
    if timestamp == 0:
        return None
    # Convert to yfinance format (YYYY-MM-DD HH:MM:SS)
    yfinance_format = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return yfinance_format


class DataFetcher:
    """
    A class to fetch financial data for a given ticker.

    Args:
        ticker: The ticker symbol to fetch data for.
    """

    def __init__(self, ticker):
        """
        Initializes the DataFetcher instance.

        Args:
            ticker: The ticker symbol to fetch data for.
        """
        self.ticker = ticker

    def fetch_active_period(self, start_date=None):
        """
        Fetches the active period of the ticker since the start date.

        Args:
            start_date: The start date from which to fetch data (default is None).
                        If None, fetches data from the first available date.

        Returns:
            tuple: A tuple containing the number of minutes the stock has been listed,
                   the first update timestamp, and the last update timestamp. Returns None if no data is available.
        """
        # Fetch the historical data for the ticker
        data = yf.Ticker(self.ticker).history(period='max')

        # If a start_date is provided, convert it to a datetime object
        if start_date is not None:

            # Convert the index of data to timezone-naive if necessary
            data.index = data.index.tz_localize(None)

            # Filter data to only include dates from start_date onwards
            data = data[data.index >= start_date]

        # Print the date from which the data is actually being fetched
        if not data.empty:
            actual_start_date = data.index[0]
            logger.info(f'Data is being fetched from {actual_start_date}')
        else:
            logger.info(f'No data available for {self.ticker} since {start_date}')
            return None, None, None

        # Check if the data is empty
        if data.empty:
            logger.info(f'No data available for {self.ticker} since {start_date}.')
            return None, None, None

        # Calculate the number of minutes the stock has been listed
        ticker_first_updated = data.index[0]
        ticker_last_updated = data.index[-1]
        listing_minutes = (ticker_last_updated - ticker_first_updated).total_seconds() / 60

        logger.info(f'{self.ticker} has been listed for {listing_minutes} minutes.')
        logger.info(f'First update: {ticker_first_updated}, Last update: {ticker_last_updated}')
        return listing_minutes, ticker_first_updated, ticker_last_updated

    def fetch_data(self, start_date, end_date, interval='1m'):

        """
        Fetches historical data for the ticker within a specified date range and interval.

        Args:
            start_date: The start date for the data fetch.
            end_date: The end date for the data fetch.
            interval: The data interval (default is '1m').

        Returns:
            DataFrame: A DataFrame containing the fetched data. Returns None if an error occurs.
        """
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {self.ticker} from {start_date} to {end_date}")
            data.reset_index(inplace=True)  # Add the date index as a column
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
