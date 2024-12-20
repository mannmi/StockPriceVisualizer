import os
import pandas as pd
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src.logging.logging_config import logger
import src.os_calls.basic_os_calls as os_calls
from src.server.yahoo.Yahoorunner import Yahoorunner
import logging


if os_calls.is_running_in_docker():
    cpathRoot = os.path.abspath("/app/")

else:
    cpathRoot = os.path.abspath("")

api_key_Load = "Test key to load"
docker_config = cpathRoot + "/docker-compose.yml"
config_path = cpathRoot + "/config_loader/config.yml"
tickerFilePath = cpathRoot + "/src/server/listing_status.csv"
runner = Yahoorunner(api_key_Load, docker_config, config_path, tickerFilePath)




def test_logging_view(request):
    # Get the current log level of the logger
    log_level = logging.getLevelName(logger.getEffectiveLevel())
    logger_name = logger.name
    logger.info('This is a test log message')
    context = {'log_level': log_level, 'logger_name': logger_name}
    return render(request, 'test_logging.html', context)

class GetLoger(APIView):
    def get(self, request):
        logger = logging.getLogger(__name__)
        return test_logging_view(request)


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
        chunk_size = request.data.get('chunk_size', 10)

        all_data = runner.load_data(request)
        fig_html = runner.plot_graph(all_data, chunk_size=10)

        if fig_html is None:
            logger.info("No data to plot.")
            logger.debug(fig_html)
            return

        html = runner.plot_graph(pd.DataFrame(all_data), chunk_size)
        return Response({'fig': html})


class GetTickersFromVariable(APIView):
    def get(self, request):
        tickers_list = runner.get_tickers_from_variable()
        return Response(tickers_list.to_dict(orient='records'))


class GetTickersFromDB(APIView):
    def get(self, request):
        tickers_list = runner.get_tickers_from_db()
        return Response(tickers_list.to_dict(orient='records'))
