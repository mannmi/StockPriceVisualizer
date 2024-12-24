import pandas as pd
import requests

from src.logging.logging_config import logger
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.server.DatabaseManager.DatabaseManager import DatabaseManager

# Add the /app directory to sys.path

logger.info("MySQL Connector is installed and working!")


def fetch_all_tickers(api_key):
    """
    fetch all tickers from AlphaVantage
    Args:
        api_key: api key from AlphaVantage to fetch all tickers with

    Returns:

    """
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'LISTING_STATUS',
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.text

    # Save the CSV data to a file
    with open('../listing_status.csv', 'w') as file:
        file.write(data)

    # Load the CSV data into a DataFrame
    # df = pd.read_csv('../listing_status.csv')
    return data


class AlphaEvent(DatabaseManager):
    def __init__(self, docker_config, api_key):
        """
        Constructor for AlphaVantage
        Args:
            docker_config: the path to the docker config file
            api_key: the path to the api key file
        """
        super().__init__(docker_config, api_key)

    def store_data(self, ticker, df):
        """
        Store Ticker associated Data in DB
        Args:
            ticker: the ticker whose data will be stored
            df: the dataframe containing the stock data

        Returns: None

        """
        ticker_id = self.update_symbol(ticker)
        # store prices in database
        for index, row in df.iterrows():
            self.cursor.execute('''
            SELECT COUNT(*) FROM prices WHERE symbol_id = %s AND timestamp = %s
            ''', (ticker_id, index))
            count = self.cursor.fetchone()[0]
            if count == 0:
                self.cursor.execute('''
                INSERT INTO prices (symbol_id, timestamp, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                ticker_id, index, row['1. open'], row['2. high'], row['3. low'], row['4. close'], row['5. volume']))
        self.conn.commit()
        self.close()
        logger.info(f"Data for {ticker} has been stored in the database.")


    # Fetch and store data for multiple tickers
    def fetch_and_store_data(self, tickers, api_key):
        """
        Fetch and store all data from AlphaVantage in database
        Args:
            tickers: list of tickers
            api_key: the api key

        Returns:

        """
        url = 'https://www.alphavantage.co/query'
        # configAuth = Yml_Loader('./config.yml')

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
                logger.info(f"Response for {ticker}: {data}")

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
            except Exception as e:
                print(f"An error occurred for {ticker}: {e}")


# Example usage
# if __name__ == "__main__":
#     api_key = 'your_api_key_here'  # Replace with your actual API key
#     docker_config = '/app/docker-compose.yml'
#     config_path = "/app/config_loader/config.yml"
#     config = YmlLoader(docker_config)
#
#     db_manager = AlphaEvent(docker_config, config)
#
#     tickers = db_manager.fetch_all_tickers()
#
#     db_manager.fetch_and_store_data(tickers, api_key)
#
#     # # Create an interactive plot with Plotly
#     # fig = px.line(df, x=df.index, y='4. close', title=f'{ticker} Intraday Stock Prices')
#     # fig.update_layout(
#     #     xaxis_title='Time',
#     #     yaxis_title='Price (USD)',
#     #     hovermode='x unified'
#     # )
#     #
#     # # Show the plot
#     # fig.show()
