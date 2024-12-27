import pandas as pd
import mysql.connector
from sqlalchemy import create_engine #todo migrate fully to sqlalchmy
from src.config_loader.configLoader import YmlLoader
from src.logging.logging_config import logger
from src.os_calls.basic_os_calls import is_running_in_docker


# Database Manager Class
def validate_symbol_data(symbol):
    """
    Validates that the symbol meets the requirements.

    Args:
        symbol: The symbol to validate.

    Returns:
        symbol_data: The validated symbol data if the symbol is valid.

    Raises:
        Exception: If the symbol does not meet the requirements.
    """

    # Ensure symbol is a Pandas Series
    if not isinstance(symbol, pd.Series):
        raise ValueError("symbol must be a Pandas Series")

    # Extract values from the Series
    symbol_data = symbol.to_dict()

    # Convert symbol to uppercase if needed
    if isinstance(symbol_data['symbol'], str):
        symbol_data['symbol'] = symbol_data['symbol'].upper()
    elif pd.isna(symbol_data['symbol']):
        raise ValueError("symbol must be a string or a pandas Series. Every ticker has an id")
    else:
        raise ValueError("symbol_data['symbol'] is not a string and not NaN")

    # Ensure all fields are not NaN before inserting into the database
    for key, value in symbol_data.items():
        if pd.isna(value):
            symbol_data[key] = None

    return symbol_data


class DatabaseManager:
    def __init__(self, docker_config, config):
        """
        Constructor of the DatabaseManager class.

        Manages various data sources (e.g., API, brokerage, etc.)

        Args:
            docker_config (str): Path to the docker configuration file.
            config (str): Path to the configuration file containing the API key.
        """

        if docker_config is None:
            raise ValueError("No Path provided")
        elif config is None:
            raise ValueError("No Path provided")

        # db_type = 'mysql+pymysql'
        # variable declaration :)
        cpath = docker_config
        print(cpath)
        self.docker_config = YmlLoader(cpath)
        print(self.docker_config.data)
        # self.docker_config = Yml_Loader(cpath)
        if self.docker_config.data is None:
            raise ValueError("Config not loaded Properly")
        logger.info(self.docker_config.data)

        db_conf = self.docker_config.data['services']['db']['environment']
        self.user = db_conf['MYSQL_USER']
        self.password = db_conf['MYSQL_PASSWORD']
        self.database = db_conf['MYSQL_DATABASE']

        if is_running_in_docker():
            self.host = "db"
        else:
            self.host = "127.0.0.1"

        host_port, container_port = self.docker_config.data['services']['db']['ports'][0].split(':')
        self.port = int(host_port)
        self.conn = None
        self.cursor = None
        self.setup_database()
        self.engine = create_engine(
            "mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=self.host, db=self.database, user=self.user,
                                                             pw=self.password))
        self.ticker_list_Storage = pd.DataFrame()

    def connect(self):
        """
        connect to the database
        Returns: None
        """
        if self.conn is None or not self.conn.is_connected():
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.conn.cursor()

    def fetch_data_from_db(self, symbol_id):
        """
        Fetches data from the database for a given ticker.
        Args:
            symbol_id:

        Returns:

        """
        if isinstance(symbol_id, pd.Series):
            logger.info("The object is a pandas Series.")
        elif isinstance(symbol_id, str):
            logger.info("The object is a String.")
            symbol_id = symbol_id["symbol"]

        logger.info("Fetching data from database {symbol_id}".format(symbol_id=symbol_id))
        self.connect()
        query = """
        SELECT timestamp, open, high, low, close, volume
        FROM prices
        WHERE symbol_id = %s
        ORDER BY timestamp
        """
        self.cursor.execute(query, (symbol_id["symbol"],))
        rows = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        # Write DataFrame to CSV
        df.to_csv('output.csv', index=False)

        return df

    def close(self):
        """
        closes the database connection
        Returns:

        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def setup_database(self):
        """
        setup the database Tables
        Returns: None

        """
        self.connect()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            symbol VARCHAR(10) PRIMARY KEY,
            name VARCHAR(1000) NULL,
            exchange VARCHAR(10),
            assetType VARCHAR(10),
            ipoDate DATE,
            delistingDate DATE NULL,
            status VARCHAR(10),
            watching BOOLEAN NOT NULL DEFAULT FALSE
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            symbol_id VARCHAR(10),
            timestamp DATETIME NOT NULL,
            open FLOAT NOT NULL,
            high FLOAT NOT NULL,
            low FLOAT NOT NULL,
            close FLOAT NOT NULL,
            volume INT NOT NULL,
            PRIMARY KEY(symbol_id,timestamp),
            FOREIGN KEY (symbol_id) REFERENCES symbols(symbol)
        )
        ''')
        self.conn.commit()
        self.close()
        logger.debug("Database setup complete.")

    def get_max_timestamp(self, symbol):
        """
        Get the max timestamp for a given ticker.
        When was the ticker last updated?
        Args:
            symbol: the symbol to get the max timestamp for.

        Returns:

        """
        self.connect()
        try:
            self.cursor.execute('''SELECT MAX(timestamp) AS max_timestamp
                                     FROM prices
                                     WHERE symbol_id = %s''', (symbol,))
            result = self.cursor.fetchone()

            logger.info(f"Query result: {result} for newest database date {symbol}")
        except Exception as e:
            logger.error(f"An error occurred in get_max_timestamp: {e}")
            result = 0  # Return 0 in case of error
        finally:
            self.close()

        # Check if result is None and set it to 0 if it is
        if result is None or result[0] is None:
            result = 0  # The data has not been added yet, we need to start from scratch
        else:
            result = result[0]

        return result

    def get_ticker_list(self, watcher_only=True):
        """
        get the ticker list from the database.
        Args:
            watcher_only:
                @True Get only the tickers/symbol on the watch list
                @False Get all the tickers/symbols in the database.

        Returns: The ticker list.

        """
        # result = []
        self.connect()
        try:
            if watcher_only:
                self.cursor.execute('''
                    SELECT symbol, name, exchange, assetType, ipoDate, delistingDate, status, watching
                    FROM symbols
                    WHERE watching = TRUE
                ''')
            else:
                self.cursor.execute('''
                     SELECT symbol, name, exchange, assetType, ipoDate, delistingDate, status, watching
                     FROM symbols
                ''')
            rows = self.cursor.fetchall()
            columns = ['symbol', 'name', 'exchange', 'assetType', 'ipoDate', 'delistingDate', 'status', 'watching']
            result = pd.DataFrame(rows, columns=columns)
            if not watcher_only:
                self.ticker_list_Storage = result
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            result = pd.DataFrame()  # Return an empty DataFrame in case of error
        finally:
            self.close()
        return result

    def add_to_watcher_list(self, symbol):
        """
        Add the symbol to the watcher list.
        Args:
            symbol: symbol to add to the watcher list.

        Returns:

        """
        self.connect()
        try:
            self.cursor.execute('''
                UPDATE symbols
                SET watching = TRUE
                WHERE symbol = %s;
            ''', (symbol,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"An error occurred get_watcher_list: {e}")
        finally:
            self.close()

    def remove_from_watcher_list(self, symbol):
        """
        Remove the symbol from the watcher list.
        Args:
            symbol: symbol to remove from the watcher list.

        Returns:

        """
        logger.info("remove from watcher list")
        self.connect()
        try:
            self.cursor.execute('''
                   UPDATE symbols
                   SET watching = FALSE
                   WHERE symbol = %s;
               ''', (symbol,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"An error occurred remove_from_watcher_list: {e}")
        finally:
            self.close()

    def update_symbol(self, symbol):
        """
        Update the symbol with new data if not exists then create a new ticker.
        (may have to be updated for when a ticker get unlisted and relisted with a new company)
        Args:
            symbol: symbol to update.

        Returns:

        """
        symbol_data = validate_symbol_data(symbol)

        try:
            self.connect()
            self.cursor.execute('SELECT symbol FROM symbols WHERE symbol = %s', (symbol_data['symbol'],))
            result = self.cursor.fetchone()

            if result:
                self.cursor.execute('''
                        UPDATE symbols
                        SET name = %s,
                            exchange = %s,
                            assetType = %s,
                            ipoDate = %s,
                            delistingDate = %s,
                            status = %s
                        WHERE symbol = %s;
                    ''', (
                    symbol_data['name'],
                    symbol_data['exchange'],
                    symbol_data['assetType'],
                    symbol_data['ipoDate'],
                    symbol_data['delistingDate'],
                    symbol_data['status'],
                    symbol_data['symbol']  # The symbol to identify the record to update
                ))
                self.conn.commit()

            else:
                self.cursor.execute('''
                    INSERT INTO symbols (symbol, name, exchange, assetType, ipoDate, delistingDate, status, watching)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    symbol_data['symbol'],
                    symbol_data['name'],
                    symbol_data['exchange'],
                    symbol_data['assetType'],
                    symbol_data['ipoDate'],
                    symbol_data['delistingDate'],
                    symbol_data['status'],
                    False  # Default value for 'watching'
                ))
                self.conn.commit()
                result = self.cursor.fetchone()[0]

        finally:
            self.close()

        return result

    def store_symbol(self, symbol):
        """
        store symbol in the database. Validate the symbol To check if valid.
        Args:
            symbol: symbol to be store in the database.

        Returns: the symbol name 

        """
        symbol_data = validate_symbol_data(symbol)

        try:
            self.connect()
            self.cursor.execute('SELECT symbol FROM symbols WHERE symbol = %s', (symbol_data['symbol'],))
            result = self.cursor.fetchone()

            if result:
                symbol_id = result[0]
            else:
                self.cursor.execute('''
                    INSERT INTO symbols (symbol, name, exchange, assetType, ipoDate, delistingDate, status, watching)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    symbol_data['symbol'],
                    symbol_data['name'],
                    symbol_data['exchange'],
                    symbol_data['assetType'],
                    symbol_data['ipoDate'],
                    symbol_data['delistingDate'],
                    symbol_data['status'],
                    False  # Default value for 'watching'
                ))
                self.conn.commit()
                symbol_id = symbol_data['symbol']
        finally:
            self.close()

        return symbol_id
