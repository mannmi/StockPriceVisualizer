import requests
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from DatabaseManager import fetch_and_store_data
from src.logging.logging_config import logger
from src.server.DatabaseManager import DatabaseManager

# # Fetch data from Alpha Vantage
# url = 'https://www.alphavantage.co/query'
# params = {
#     'function': 'TIME_SERIES_INTRADAY',
#     'symbol': 'IBM',
#     'interval': '1min',
#     'apikey': 'YOUR_API_KEY'
# }
# response = requests.get(url, params=params)
# data = response.json()
#
# # Process the data
# time_series = data['Time Series (1min)']
# df = pd.DataFrame.from_dict(time_series, orient='index')
# df = df.astype(float)
# df.index = pd.to_datetime(df.index)
#
# # Create an interactive plot with Plotly
# fig = px.line(df, x=df.index, y='4. close', title='IBM Intraday Stock Prices')
# fig.update_layout(
#     xaxis_title='Time',
#     yaxis_title='Price (USD)',
#     hovermode='x unified'
# )
#
# # Show the plot
# fig.show()

# Example usage
tickers = ['IBM', 'AAPL', 'GOOGL']
trade_api = '/app/config_loader/config.yml'
config = '/app/docker-compose.yml'
DatabaseManager = DatabaseManager(config)
DatabaseManager.fetch_and_store_data(tickers,trade_api)

while True:
    logger.info("yesterday")
