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

    def fetch_active_period(self, start_date=0):
        """
        Fetches the active period of the ticker since the start date.

        Args:
            start_date: The start date from which to fetch data (default is 0). Which is the max time, added to limit the time frame to reduced fetch time
                when the data has already been fetched.

        Returns:
            tuple: A tuple containing the number of minutes the stock has been listed,
                the first update timestamp, and the last update timestamp. Returns None if no data is available.
        """
        # Fetch the historical data

        # Convert start_date to a datetime object if it's not 0
        if start_date != 0:
            # start_date = self.convert_timestamp_to_yfinance_format(start_date)
            data = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        else:
            data = yf.Ticker(self.ticker).history(period='max')

        if start_date != 0:
            # Convert the index of data to timezone-naive if necessary
            data.index = data.index.tz_localize(None)
            print("data.index " + str(type(data.index)))
            # Filter data to only include dates from start_date onwards
            data = data[data.index >= start_date]

        # Check if the data is empty
        if data.empty:
            logger.info(f'No data available for {self.ticker} since {start_date}.')
            return None, None, None

        # Calculate the number of minutes the stock has been listed
        ticker_last_updated = data.index[-1]
        ticker_first_updated = data.index[0]
        listing_minutes = (ticker_last_updated - ticker_first_updated).total_seconds() / 60

        logger.info(f'{self.ticker} has been listed for {listing_minutes} minutes.')
        logger.info(f'{data.index} vs {start_date} time stamp.')
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
