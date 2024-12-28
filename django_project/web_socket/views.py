from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# class TriggerFunctionView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Notify WebSocket consumers
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'group_name',
#             {
#                 'type': 'trigger_function',
#                 'message': 'Trigger function in PyQt'
#             }
#         )
#         return Response({"status": "Function triggered"}, status=200)
#
#     def trigger_function(self, event):
#         message = event['message']
#         # Logic for triggering the function

# views.py

from django.shortcuts import render

def websocket_trigger_view(request):
    return render(request, 'websocket_trigger.html')

# todo switch to yml
type_list = ["ticker_update"]
context = ["Watch_List","all_tickers_file","all_tickers_variable","all_tickers_db"]

def trigger_event_update(event_type, affected_data):
    channel_layer = get_channel_layer()
    event_data = {
        'type': 'event_update',
        'event_type': event_type,
        'affected_data': affected_data
    }
    async_to_sync(channel_layer.group_send)('event_group', {
        'type': 'send_event_update',
        'event_data': event_data
    })

#test caller
#trigger_event_update('ticker_update', {'ticker': 'AAPL'})

