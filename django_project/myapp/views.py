import html
import os
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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

#doxygen was ai generated on this fiel


def test_logging_view(request):
    """
    @brief Test logging view.

    @param request The django request object.

    @return The test logging view as an HTML response.
    """
    # Get the current log level of the logger
    log_level = logging.getLevelName(logger.getEffectiveLevel())
    logger_name = logger.name
    logger.info('This is a test log message')
    context = {'log_level': log_level, 'logger_name': logger_name}
    return render(request, 'test_logging.html', context)


class GetLoger(APIView):
    """
    @brief API view to test the logger.
    """

    def get(self, request):
        """
        @brief Handles GET requests to test the logger.

        @param request The django request object.

        @return The response from the test_logging_view function.
        """
        logger = logging.getLogger(__name__)
        return test_logging_view(request)


class GetTickers(APIView):
    """
    @brief API view to get tickers.
    """

    def get(self, request):
        """
        @brief Handles GET requests to retrieve tickers.

        @param request The django request object.

        @return A response containing the tickers list.
        """
        watcher = request.query_params.get('watcher', 'true').lower() == 'true'
        tickers_list = runner.get_tickers(watcher)
        return Response(tickers_list.to_dict(orient='records'))


class GetWatchedListAll(APIView):
    """
    @brief API view to get the entire watched ticker list.
    """

    def get(self, request):
        """
        @brief Handles GET requests to retrieve the entire watched ticker list.

        @param request The django request object.

        @return A response containing the watched tickers list.
        """
        tickers_list = runner.get_watched_list_all()
        return Response(tickers_list.to_dict(orient='records'))


class UpdateWatchList(APIView):
    """
    @brief API view to update the watch list.
    """

    def post(self, request):
        """
        @brief Handles POST requests to update the watch list.

        @param request The django request object.

        @return A response indicating the success of the operation.
        """
        tickers = request.data.get('tickers')
        runner.update_watch_list(tickers)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class AddToWatchList(APIView):
    """
    @brief API view to add tickers to the watch list.
    """

    def post(self, request):
        """
        @brief Handles POST requests to add tickers to the watch list.

        @param request The django request object.

        @return A response indicating the success of the operation.
        """
        tickers = request.data.get('tickers')
        runner.add_to_watch_list(tickers)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class RemoveFromWatchList(APIView):
    """
    @brief API view to remove tickers from the watch list.
    """

    def post(self, request):
        """
        @brief Handles POST requests to remove tickers from the watch list.

        @param request The django request object.

        @return A response indicating the success of the operation.
        """
        tickers = request.data.get('tickers')
        runner.remove_from_watch_list(tickers)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class UpdateTickerList(APIView):
    """
    @brief API view to update the ticker list.
    """

    def post(self, request):
        """
        @brief Handles POST requests to update the ticker list.

        @param request The django request object.

        @return A response indicating the ticker list has been updated.
        """
        runner.update_ticker_list()
        return Response({'status': 'Ticker list updated'}, status=status.HTTP_200_OK)


class StoreTickerList(APIView):
    """
    @brief API view to store the ticker list.
    """

    def post(self, request):
        """
        @brief Handles POST requests to store the ticker list.

        @param request The django request object.

        @return A response indicating the ticker list has been stored.
        """
        tickers = request.data.get('tickers')
        runner.store_ticker_list(tickers)
        return Response({'status': 'Ticker list stored'}, status=status.HTTP_200_OK)


class GetAllTickersFile(APIView):
    """
    @brief API view to get all tickers from the file.
    """

    def get(self, request):
        """
        @brief Handles GET requests to retrieve all tickers from the file.

        @param request The django request object.

        @return A response containing the tickers list.
        """
        tickers_list = runner.get_all_tickers_file()
        return Response(tickers_list.to_dict(orient='records'))


class LoadData(APIView):
    """
    @brief API view to load data for the provided tickers.
    """

    def post(self, request):
        """
        @brief Handles POST requests to load data for the provided tickers.

        @param request The django request object.

        @return A response containing the loaded data, or an error message if the data is invalid.
        """
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


class PlotGraphData(APIView):
    """
    @brief API view to plot graph data.
    """

    def post(self, request):
        """
        @brief Handles POST requests to plot graph data.

        @param request The django request object.

        @return A response containing the plot HTML or an error message if the data is invalid.
        """
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


class PlotGraphTicker(APIView):
    """
    @brief API view to plot graph data for tickers.
    """

    def post(self, request):
        """
        @brief Handles POST requests to plot graph data for tickers.

        @param request The django request object.

        @return A response containing the plot HTML or an error message if the data is invalid.
        """
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
    """
    @brief API view to get tickers from the variable.
    """

    def get(self, request):
        """
        @brief Handles GET requests to retrieve tickers from the variable.

        @param request The django request object.

        @return A response containing the tickers list.
        """
        tickers_list = runner.get_tickers_from_variable()
        return Response(tickers_list.to_dict(orient='records'))


class GetTickersFromDB(APIView):
    """
    @brief API view to get tickers from the database.
    """

    def get(self, request):
        """
        @brief Handles GET requests to retrieve tickers from the database.

        @param request The django request object.

        @return A response containing the tickers list.
        """
        tickers_list = runner.get_tickers_from_db()
        return Response(tickers_list.to_dict(orient='records'))
