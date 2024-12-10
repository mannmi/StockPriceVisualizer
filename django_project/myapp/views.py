import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TickerSerializer
from src.server.DatabaseManager.runner import Runner
from src.server.yahoo.dataProcesingYahoo import DataProcessorYahoo
from src.server.yahoo.yahoo_db import Yahoo

class YahooRunner:
    def __init__(self, api_key_Load, docker_config, config_path, ticker_path):
        self.api_key_Load = api_key_Load
        self.docker_config = docker_config
        self.config_path = config_path
        self.ticker_file = ticker_path
        self.ticker_list = []

        self.runner = Runner(api_key_Load, docker_config, config_path)
        self.dataProcessor = DataProcessorYahoo("A", ticker_path)
        self.db_manager = Yahoo(docker_config, api_key_Load, ticker_path)

    def get_watched_list_all(self):
        tickers_list = self.db_manager.get_ticker_list()
        return tickers_list

    def update_watch_list(self, tickers):
        print(tickers)
        ticker_list = self.db_manager.get_ticker_list()
        self.db_manager.fetch_and_store_data(ticker_list, self.api_key_Load)

    def add_to_watch_list(self, tickers):
        self.db_manager.add_to_watcher_list(tickers)

    def remove_from_watch_list(self, tickers):
        self.db_manager.remove_from_watcher_list(tickers)

    def update_ticker_list(self):
        ticker = self.dataProcessor.fetch_all_tickers(self.api_key_Load)
        self.dataProcessor.store_all_tickers_file(ticker)
        self.dataProcessor.strip_empty_lines()

    def store_ticker_list(self, tickers):
        tickers_list = self.get_all_tickers_file()
        self.db_manager.fetch_and_store_symbol(tickers_list, self.api_key_Load)

    def get_all_tickers_file(self):
        self.ticker_list = self.dataProcessor.read_all_tickers_from_file()
        return self.ticker_list

    def get_tickers(self, watcher=True):
        self.ticker_list = self.db_manager.get_ticker_list(watcher)
        return self.ticker_list

    def load_data(self, tickers):
        all_data = self.db_manager.fetch_data_from_db(tickers)
        return all_data

    def plotGraph(self, all_data, chunk_size):
        self.dataProcessor.all_data = all_data
        return self.dataProcessor.plot_data(chunk_size)

    def get_tickers_from_variable(self):
        self.ticker_list = self.db_manager.ticker_list_Storage
        if self.ticker_list.empty:
            self.ticker_list = self.db_manager.get_ticker_list(False)
        return self.ticker_list

runner = YahooRunner(api_key_Load="Test key to load",
                     docker_config=r"C:\Users\mannnmi\CryptoPrediction\docker-compose.yml",
                     config_path=r"C:\Users\mannnmi\CryptoPrediction\config_loader\config.yml",
                     ticker_path=r"C:\Users\mannnmi\CryptoPrediction\src\server\listing_status.csv")

class GetTickers(APIView):
    def get(self, request):
        watcher = request.query_params.get('watcher', 'true').lower() == 'true'
        tickers_list = runner.get_tickers(watcher)
        return Response(tickers_list.to_dict(orient='records'))

class GetWatchedListAll(APIView):
    def get(self, request):
        tickers_list = runner.get_watched_list_all()
        return Response(tickers_list.to_dict(orient='records'))

class UpdateWatchList(APIView):
    def post(self, request):
        tickers = request.data.get('tickers')
        runner.update_watch_list(tickers)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class AddToWatchList(APIView):
    def post(self, request):
        tickers = request.data.get('tickers')
        runner.add_to_watch_list(tickers)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class RemoveFromWatchList(APIView):
    def post(self, request):
        tickers = request.data.get('tickers')
        runner.remove_from_watch_list(tickers)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class UpdateTickerList(APIView):
    def post(self, request):
        runner.update_ticker_list()
        return Response({'status': 'Ticker list updated'}, status=status.HTTP_200_OK)

class StoreTickerList(APIView):
    def post(self, request):
        tickers = request.data.get('tickers')
        runner.store_ticker_list(tickers)
        return Response({'status': 'Ticker list stored'}, status=status.HTTP_200_OK)

class GetAllTickersFile(APIView):
    def get(self, request):
        tickers_list = runner.get_all_tickers_file()
        return Response(tickers_list.to_dict(orient='records'))

class LoadData(APIView):
    def post(self, request):
        tickers = request.data.get('tickers')
        all_data = runner.load_data(tickers)
        return Response(all_data.to_dict(orient='records'))

class PlotGraph(APIView):
    def post(self, request):
        all_data = request.data.get('all_data')
        chunk_size = request.data.get('chunk_size', 1000)
        fig, config = runner.plotGraph(pd.DataFrame(all_data), chunk_size)
        return Response({'fig': fig, 'config': config})

class GetTickersFromVariable(APIView):
    def get(self, request):
        tickers_list = runner.get_tickers_from_variable()
        return Response(tickers_list.to_dict(orient='records'))