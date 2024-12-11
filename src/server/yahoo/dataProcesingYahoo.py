import os
import sys

import matplotlib.pyplot as plt
from datetime import timedelta

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector  # Import RectangleSelector

from src.logging.logging_config import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/app/')))
from src.marketCheck.marketCheck import marketTimeChecker
from src.server.yahoo.fetchYahoo import DataFetcher
from src.server.DatabaseManager.dataPorcesing import DataProcessor


class DataProcessorYahoo(DataProcessor):
    def __init__(self, ticker, tickerFilePath):
        self.ticker = ticker
        self.tickerFilePath = tickerFilePath
        self.tickerList = self.read_all_tickers_from_file()
        self.all_data = []

    def process_data(self, start_date=0):
        #todo when it gose life only fetch historical data when the markets are "down"
        market_checker = marketTimeChecker()
        fetcher = DataFetcher(self.ticker)
        logger.info(self.ticker)


        days_to_go_back, ticker_first_updated, ticker_last_updated = fetcher.fetch_active_period(start_date)
        #logger.info("output=> ",start_date, days_to_go_back, ticker_first_updated, ticker_last_updated )
        if days_to_go_back == None and ticker_first_updated == None and ticker_last_updated == None:
            return None
        if days_to_go_back <= 0:
            logger.info("no changes detected")
            return
        days_to_go_back_total = days_to_go_back
        days_to_go_back = days_to_go_back_total

        local_time = market_checker.get_current_time()
        end_date = market_checker.convert_to_market_time(local_time)

        days_passed = 0
        while days_to_go_back > 0:
            if days_passed >= 60:
                interval = '1d'
                fetch_days = 30
                days_pass_range = -1
            elif days_passed >= 30:
                interval = '5m'
                fetch_days = 7
                days_pass_range = 60
            else:
                interval = '1m'
                fetch_days = 7
                days_pass_range = 30

            last_runer = False
            if days_pass_range != -1:
                remaining_days = days_pass_range - days_passed
                remain_day_test = remaining_days % fetch_days

                if days_pass_range < (days_passed + fetch_days + remain_day_test):
                    last_runer = True
                    fetch_days = remain_day_test

            start_date = end_date - timedelta(days=min(fetch_days, days_to_go_back))

            data = fetcher.fetch_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), interval)

            if data is not None:
                self.all_data.append(data)

            end_date = start_date
            days_to_go_back -= fetch_days
            days_passed = (days_to_go_back_total - days_to_go_back)

        combined_data = pd.concat(self.all_data, ignore_index=True)
        return combined_data

    def zoom(self, event):
        ax = plt.gca()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        zoom_factor = 1.2 if event.step > 0 else 1 / 1.2

        new_xlim = [(x - (x - xlim[0]) * zoom_factor) for x in xlim]
        new_ylim = [(y - (y - ylim[0]) * zoom_factor) for y in ylim]

        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        plt.draw()

    def onselect(self, eclick, erelease):
        ax = plt.gca()
        ax.set_xlim(eclick.xdata, erelease.xdata)
        ax.set_ylim(eclick.ydata, erelease.ydata)
        plt.draw()

    def plot_data(self, chunk_size=1000):
        if self.all_data.empty:
            logger.error("It's empty")
            return None, None

        logger.info(self.all_data)

        # Convert all timestamps to timezone-naive
        self.all_data['timestamp'] = pd.to_datetime(self.all_data['timestamp'])
        self.all_data.set_index('timestamp', inplace=True)
        self.all_data.index = self.all_data.index.tz_localize(None)

        # Initialize the plot
        fig = Figure()
        ax = fig.add_subplot(111)

        # Plot the entire dataset with a single label for each data type
        ax.plot(self.all_data.index, self.all_data['close'], label='Close')
        ax.plot(self.all_data.index, self.all_data['volume'], label='Volume')
        ax.plot(self.all_data.index, self.all_data['low'], label='Low')
        ax.plot(self.all_data.index, self.all_data['high'], label='High')
        ax.plot(self.all_data.index, self.all_data['open'], label='Open')

        # Update layout to enable zoom and pan
        ax.set_title('Closing Price')
        ax.set_xlabel('Time')
        ax.set_ylabel('Price (USD)')
        ax.legend()

        # Enable interactive features
        fig.tight_layout()
        fig.canvas.mpl_connect('scroll_event', self.zoom)

        # Add rectangle selector
        self.rs = RectangleSelector(ax, self.onselect, useblit=True,
                                    button=[1],  # Left mouse button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)

        return fig, None
    # def plot_data(self, chunk_size=1000):
    #     if self.all_data.empty:
    #         print("It's empty")
    #         return None, None
    #
    #     print(self.all_data)
    #
    #     # Convert all timestamps to timezone-naive
    #     self.all_data['timestamp'] = pd.to_datetime(self.all_data['timestamp'])
    #     self.all_data.set_index('timestamp', inplace=True)
    #     self.all_data.index = self.all_data.index.tz_localize(None)
    #
    #     # Initialize the plot
    #     fig = go.Figure()
    #     num_chunks = len(self.all_data) // chunk_size + 1
    #     for i in range(num_chunks):
    #         chunk = self.all_data.iloc[i * chunk_size:(i + 1) * chunk_size]
    #         if chunk.empty:
    #             continue
    #
    #         # Add the chunk to the plot
    #         fig.add_trace(go.Scatter(x=chunk.index, y=chunk['close'], mode='lines', name=f'Chunk {i + 1}'))
    #
    #     # Update layout to enable zoom and pan
    #     fig.update_layout(
    #         title='Closing Price',
    #         xaxis_title='Time',
    #         yaxis_title='Price (USD)',
    #         legend_title='Legend',
    #         hovermode='x unified',
    #         dragmode='zoom',  # Set the drag mode to 'zoom'
    #         modebar_add=['zoom', 'pan', 'resetScale2d']  # Add zoom and pan buttons to the mode bar
    #     )
    #
    #     # Configuration to enable scroll zoom
    #     config = {'scrollZoom': True}
    #
    #     return fig, config

    # def plot_data(self, chunk_size=1000):
    #     if self.all_data.empty:
    #         print("It's empty")
    #         return None
    #
    #     print(self.all_data)
    #
    #     # Convert all timestamps to timezone-naive
    #     self.all_data['timestamp'] = pd.to_datetime(self.all_data['timestamp'])
    #     self.all_data.set_index('timestamp', inplace=True)
    #     self.all_data.index = self.all_data.index.tz_localize(None)
    #
    #     # Prepare data chunks
    #     data_chunks = []
    #     num_chunks = len(self.all_data) // chunk_size + 1
    #     for i in range(num_chunks):
    #         chunk = self.all_data.iloc[i * chunk_size:(i + 1) * chunk_size]
    #         if chunk.empty:
    #             continue
    #         data_chunks.append({'x': chunk.index, 'y': chunk['close']})
    #
    #     return data_chunks
