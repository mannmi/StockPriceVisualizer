import math
import time
from datetime import timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from src.marketCheck.marketCheck import Markettimechecker
from src.os_calls.basic_os_calls import get_root_path
from src.server.yahoo.fetchYahoo import DataFetcher
from src.server.DatabaseManager.dataPorcesing import DataProcessor


class DataProcessorYahoo(DataProcessor):
    def __init__(self, ticker, ticker_file_path):
        """
        data processor for Yahoo data Deals with Data Processing
        Args:
            ticker: inital ticker symbol (deprecated)
            ticker_file_path: path to file containing ticker symbols
        """
        super().__init__(ticker, ticker_file_path)
        self.ticker = ticker
        self.tickerFilePath = ticker_file_path
        self.tickerList = self.read_all_tickers_from_file()
        self.all_data = []

    def process_data(self,startDate=None, endDate=None):
        """
        fetch data from Yahoo API (todo rewrite to take ticker as argument ?)
        Returns: Data for the ticker

        """
        market_checker = Markettimechecker()
        fetcher = DataFetcher(self.ticker)
        print(self.ticker)

        minutes_to_go_back, ticker_first_updated, ticker_last_updated = fetcher.fetch_active_period(startDate)
        minutes_to_go_back_total = minutes_to_go_back
        # minutes_to_go_back = minutes_to_go_back_total

        if minutes_to_go_back ==0:
            return None

        local_time = market_checker.get_current_time()
        end_date = market_checker.convert_to_market_time(local_time)

        days_passed = 0
        minutes_in_day = 60 * 24
        while minutes_to_go_back > 0:
            print(minutes_to_go_back)
            if days_passed >= 60:
                interval = '1d'
                fetch_days = 30
                subtract_minutes = 30 * minutes_in_day
                days_pass_range = -1
            elif days_passed >= 30:
                interval = '5m'
                fetch_days = 7
                subtract_minutes = 7 * minutes_in_day
                days_pass_range = 60
            else:
                interval = '1m'
                fetch_days = 7
                subtract_minutes = 7 * minutes_in_day
                days_pass_range = 30

            # last_runer = False
            if days_pass_range != -1:
                remaining_days = days_pass_range - days_passed
                remain_day_test = remaining_days % fetch_days

                if days_pass_range < (days_passed + fetch_days + remain_day_test):
                    # last_runer = True
                    fetch_days = remain_day_test

            start_date = end_date - timedelta(days=min(fetch_days, minutes_to_go_back))

            #This schould now also fetch todays data
            data = fetcher.fetch_data(start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'), interval)

            if data is not None:
                self.all_data.append(data)

            end_date = start_date
            minutes_to_go_back -= subtract_minutes
            days_passed = math.ceil((minutes_to_go_back_total - minutes_to_go_back) / minutes_in_day)
            print(days_passed)

        combined_data = pd.concat(self.all_data, ignore_index=True)
        return combined_data



    def plot_data(self, data, period='all'):
        """

        Args:
            data: data to plot
            period: period to plot

        Returns:
            html of the data

        Example:
            @code python
             fig_html = plot_data(data, period='1Y')  # Plot data for the last 1 year
             fig_html = plot_data(data, period='2Y')  # Plot data for the last 2 years
             fig_html = plot_data(data, period='all')  # Plot all available data
            @endcode

        """
        if data.empty:
            print("It's empty")
            return None

        print(data)

        # Convert all timestamps to timezone-naive
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.set_index('timestamp', inplace=True)
        data.index = data.index.tz_localize(None)

        # Filter data based on the specified period
        if period and period != 'all':
            data = data.last(period)

        # Create subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1, subplot_titles=('Price', 'Volume'))

        # Add traces for price data
        fig.add_trace(go.Scatter(x=data.index, y=data['close'], mode='lines', name='Close'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['low'], mode='lines', name='Low'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['high'], mode='lines', name='High'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['open'], mode='lines', name='Open'), row=1, col=1)

        # Add trace for volume data
        fig.add_trace(go.Scatter(x=data.index, y=data['volume'], name='Volume'), row=2, col=1)

        # Update layout to enable zoom and pan
        fig.update_layout(title='Stock Data', xaxis_title='Time', yaxis_title='Price (USD)',
                          xaxis2_title='Time', yaxis2_title='Volume', showlegend=True)

        fig_html = fig.to_html()
        # Write the HTML to a file for debugging

        return fig_html
