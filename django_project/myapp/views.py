import html
import json
import os
from io import StringIO

import pandas as pd
from IPython.core.display_functions import display
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tenacity import sleep

from myapp.serializers import TickerSerializer
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
        try:
            # Parse the incoming JSON data
            data = JSONParser().parse(request)
            row_dict = data.get('tickers', {})

            # Serialize the incoming data
            serializer = TickerSerializer(data=row_dict)
            serializer.is_valid(raise_exception=True)

            # Get the validated data
            validated_data = serializer.validated_data

            # Convert the validated data to a pandas Series
            tickers_series = pd.Series(validated_data)

            if tickers_series.empty:
                logger.error("Received empty series")
                return Response({"error": "Received empty DataFrame"}, status=status.HTTP_400_BAD_REQUEST)

            # Continue processing with `runner.load_data(tickers_df)`
            all_data = runner.load_data(tickers_series)
            # Return the DataFrame as a list of dictionaries
            return Response(all_data.to_dict(orient='records'))

        except Exception as e:
            logger.error(f"Error processing the request: {e}")
            return Response({"error": "Invalid data format or content"}, status=status.HTTP_400_BAD_REQUEST)


class PlotGraph(APIView):
    def post(self, request):
        try:
            # Get the data from the request
            all_data = request.data.get('all_data')
            chunk_size = request.data.get('chunk_size', 10)

            if not all_data:
                logger.error("No data provided.")
                return Response({"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Convert the list of dictionaries back to DataFrame
            all_data_df = pd.DataFrame(all_data)

            # Generate the plot HTML using the DataFrame
            fig_html = runner.plot_graph(all_data_df, chunk_size)

            if fig_html is None:
                logger.info("No data to plot.")
                return Response({"error": "No data to plot"}, status=status.HTTP_400_BAD_REQUEST)

            # Return the HTML string directly with proper content-type
            fig_html = html.escape(fig_html)
            return HttpResponse(fig_html, content_type='text/html')

        except Exception as e:
            logger.error(f"Error processing the request: {e}")
            return Response({"error": "Invalid data format or content"}, status=status.HTTP_400_BAD_REQUEST)


class GetTickersFromVariable(APIView):
    def get(self, request):
        tickers_list = runner.get_tickers_from_variable()
        return Response(tickers_list.to_dict(orient='records'))


class GetTickersFromDB(APIView):
    def get(self, request):
        tickers_list = runner.get_tickers_from_db()
        return Response(tickers_list.to_dict(orient='records'))
