import os
import sys
import pandas as pd
from numpy.f2py.auxfuncs import throw_error

# config.yml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/app/')))
from src.server.DatabaseManager.DatabaseManager import DatabaseManager
from src.config_loader.configLoader import Yml_Loader
from src.server.yahoo.dataProcesingYahoo import DataProcessorYahoo
from src.os_calls.basic_os_calls import clear

print("MySQL Connector is installed and working!")


class Yahoo(DatabaseManager):
    def __init__(self, docker_config, api_key, tickerFilePath):
        super().__init__(docker_config, api_key)
        self.tickerFilePath = tickerFilePath

    def store_data(self, symbol, df):
        self.store_symbol(symbol)

        self.connect()
        # Check if the symbol exists
        self.cursor.execute('SELECT symbol FROM symbols WHERE symbol = %s', (symbol["symbol"],))
        result = self.cursor.fetchone()

        if result:
            symbol_id = result[0]
        else:
            self.cursor.execute('INSERT INTO symbols (symbol, status) VALUES (%s, FALSE)', (symbol,))
            self.conn.commit()
            symbol_id = self.cursor.lastrowid

        symbol = str(symbol)  # Ensure symbol is a string

        # Print column names to verify 'Datetime' exists
        print("Columns in DataFrame:", df.columns)

        # Ensure Datetime column is in datetime format
        if ('Datetime', '') in df.columns:
            df[('Datetime', '')] = pd.to_datetime(df[('Datetime', '')], errors='coerce')
            df = df.dropna(subset=[('Datetime', '')])  # Drop rows where conversion failed

            df = df.dropna(subset=[col for col in df.columns if col != ('Datetime', '')])

            for index, row in df.iterrows():
                datetime_value = row[('Datetime', '')].strftime('%Y-%m-%d %H:%M:%S')
                # chatgbt generated fix
                open_value = row[('Open', 'A')].item() if isinstance(row[('Open', 'A')], pd.Series) else row[
                    ('Open', 'A')]
                high_value = row[('High', 'A')].item() if isinstance(row[('High', 'A')], pd.Series) else row[
                    ('High', 'A')]
                low_value = row[('Low', 'A')].item() if isinstance(row[('Low', 'A')], pd.Series) else row[('Low', 'A')]
                close_value = row[('Close', 'A')].item() if isinstance(row[('Close', 'A')], pd.Series) else row[
                    ('Close', 'A')]
                volume_value = row[('Volume', 'A')].item() if isinstance(row[('Volume', 'A')], pd.Series) else row[
                    ('Volume', 'A')]
                # end of chatgbt generated fix

                print(type(datetime_value), datetime_value)
                print(type(open_value), open_value)
                print(type(high_value), high_value)
                print(type(low_value), low_value)
                print(type(close_value), close_value)
                print(type(volume_value), volume_value)

                self.cursor.execute('''
                    SELECT COUNT(*) FROM prices WHERE symbol_id = %s AND timestamp = %s
                ''', (symbol_id, datetime_value))
                count = self.cursor.fetchone()[0]
                print("yes")

                if count == 0:
                    self.cursor.execute('''
                        INSERT INTO prices (symbol_id, timestamp, open, high, low, close, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        symbol_id, datetime_value, open_value, high_value, low_value, close_value, volume_value
                    ))

            self.conn.commit()
        else:
            print("Error: 'Datetime' column not found in DataFrame")

        self.close()
        print(f"Data for {symbol} has been stored in the database.")

    # Fetch and store data for multiple tickers
    def fetch_and_store_symbol(self, tickers, api_key):
        configAuth = Yml_Loader('./config.yml')

        if tickers.empty:
            raise ValueError("The list of tickers is empty. Please provide at least one ticker symbol.")

        for index, ticker in tickers.iterrows():
            try:
                self.update_symbol(ticker)
            except Exception as e:
                print(f"An error occurred for {ticker}: {e}")

    def fetch_and_store_data(self, tickers, api_key):
        try:
            watcher_list = self.get_ticker_list()
        except Exception as e:
            print(f"An error occurred : {e}")

        if tickers.empty:
            raise ValueError("The list of tickers is empty. Please provide at least one ticker symbol.")

        DataProcessorVar = DataProcessorYahoo(tickers, self.tickerFilePath)
        for index, ticker in watcher_list.iterrows():
            DataProcessorVar.ticker = ticker["symbol"]
            data_store = DataProcessorVar.process_data()
            print(data_store.columns.tolist())
            self.store_data(ticker, data_store)


# Example usage
if __name__ == "__main__":
    api_key_Load = 'your_api_key_here'  # Replace with your actual API key
    docker_config = '/app/docker-compose.yml'
    config_path = "/app/config_loader/config.yml"
    tickerFilePath = "/app/server/listing_status.csv"
    config = Yml_Loader(docker_config)

    dataProcessor = DataProcessorYahoo("A", tickerFilePath)
    dataProcessor.strip_empty_lines()

    tickers_list = dataProcessor.read_all_tickers_from_file()



    # print(tickers_list[0])
    for index, ticker in tickers_list.iterrows():
        print(type(ticker))
        print(ticker)

    # print(tickers_list)

    # if tickers_list.empty:
    #     print("The DataFrame is empty.")
    #     exit()

    # print(tickers_list)
    db_manager = (Yahoo(docker_config, config, tickerFilePath))
    # #db_manager.fetch_and_store_symbol(tickers_list, api_key_Load)
    # db_manager.add_to_watcher_list("AMD")
    # db_manager.add_to_watcher_list("A")

    #tickers_list = db_manager.get_ticker_list()
    db_manager.fetch_and_store_symbol(tickers_list,0)

    db_manager.fetch_and_store_data(tickers_list, api_key_Load)
