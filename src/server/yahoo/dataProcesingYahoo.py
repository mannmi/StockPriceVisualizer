import matplotlib.pyplot as plt
from datetime import timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from src.marketCheck.marketCheck import Markettimechecker
from src.server.yahoo.fetchYahoo import DataFetcher
from src.server.DatabaseManager.dataPorcesing import DataProcessor


def zoom(event):
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    zoom_factor = 1.2 if event.step > 0 else 1 / 1.2

    new_xlim = [(x - (x - xlim[0]) * zoom_factor) for x in xlim]
    new_ylim = [(y - (y - ylim[0]) * zoom_factor) for y in ylim]

    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    plt.draw()


def onselect(eclick, erelease):
    ax = plt.gca()
    ax.set_xlim(eclick.xdata, erelease.xdata)
    ax.set_ylim(eclick.ydata, erelease.ydata)
    plt.draw()


class DataProcessorYahoo(DataProcessor):
    def __init__(self, ticker, ticker_file_path):
        super().__init__(ticker,ticker_file_path)
        self.ticker = ticker
        self.tickerFilePath = ticker_file_path
        self.tickerList = self.read_all_tickers_from_file()
        self.all_data = []

    def process_data(self):
        market_checker = Markettimechecker()
        fetcher = DataFetcher(self.ticker)
        print(self.ticker)

        days_to_go_back, ticker_first_updated, ticker_last_updated = fetcher.fetch_active_period()
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

            #last_runer = False
            if days_pass_range != -1:
                remaining_days = days_pass_range - days_passed
                remain_day_test = remaining_days % fetch_days

                if days_pass_range < (days_passed + fetch_days + remain_day_test):
                    #last_runer = True
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

    # Example usage
    # data = pd.read_csv('your_data.csv')
    # fig_html = plot_data(data, period='1Y')  # Plot data for the last 1 year
    # fig_html = plot_data(data, period='2Y')  # Plot data for the last 2 years
    # fig_html = plot_data(data, period='all')  # Plot all available data

    def plot_data(self, data, period='all'):
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
        fig.add_trace(go.Bar(x=data.index, y=data['volume'], name='Volume'), row=2, col=1)

        # Update layout to enable zoom and pan
        fig.update_layout(title='Stock Data', xaxis_title='Time', yaxis_title='Price (USD)',
                          xaxis2_title='Time', yaxis2_title='Volume', showlegend=True)

        fig_html = fig.to_html()
        # Write the HTML to a file for debugging

        return fig_html
