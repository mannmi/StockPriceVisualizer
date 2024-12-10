import yfinance as yf

class DataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker

    def fetch_active_period(self):
        # Fetch the historical data
        data = yf.Ticker(self.ticker).history(period='max')
        # Calculate the number of days the stock has been listed
        ticker_last_updated = data.index[-1]
        ticker_first_updated = data.index[0]
        listing_days = (data.index[-1] - data.index[0]).days
        print(f'{self.ticker} has been listed for {listing_days} days.')
        return listing_days, ticker_first_updated, ticker_last_updated

    def fetch_data(self, start_date, end_date, interval='1m'):
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {self.ticker} from {start_date} to {end_date}")
            data.reset_index(inplace=True)  # Add the date index as a column
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def fetch_data_less_precise(self, start_date, end_date, interval):
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {self.ticker} from {start_date} to {end_date}")
            data.reset_index(inplace=True)  # Add the date index as a column
            return data
        except Exception as e:
            print(f"Error fetching less precise data: {e}")
            return None