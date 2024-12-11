from django.urls import path

from .views import GetTickers, GetWatchedListAll, UpdateWatchList, AddToWatchList, RemoveFromWatchList, \
    UpdateTickerList, StoreTickerList, GetAllTickersFile, LoadData, PlotGraph, GetTickersFromVariable, GetTickersFromDB, \
    GetLoger

urlpatterns = [
    path('get_tickers/', GetTickers.as_view(), name='get_tickers'),
    path('get_watched_list_all/', GetWatchedListAll.as_view(), name='get_watched_list_all'),
    path('update_watch_list/', UpdateWatchList.as_view(), name='update_watch_list'),
    path('add_to_watch_list/', AddToWatchList.as_view(), name='add_to_watch_list'),
    path('remove_from_watch_list/', RemoveFromWatchList.as_view(), name='remove_from_watch_list'),
    path('update_ticker_list/', UpdateTickerList.as_view(), name='update_ticker_list'),
    path('store_ticker_list/', StoreTickerList.as_view(), name='store_ticker_list'),
    path('get_all_tickers_file/', GetAllTickersFile.as_view(), name='get_all_tickers_file'),
    path('load_data/', LoadData.as_view(), name='load_data'),
    path('plot_graph/', PlotGraph.as_view(), name='plot_graph'),
    path('get_tickers_from_variable/', GetTickersFromVariable.as_view(), name='get_tickers_from_variable'),
    path('get_tickers_from_db/', GetTickersFromDB.as_view(), name='get_tickers_from_db'),
    path('test-logging/', GetLoger.as_view(), name='test_logging_view'),


]