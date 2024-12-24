from rest_framework import serializers

class TickerSerializer(serializers.Serializer):
    """
    Serializer for Ticker model
    """
    symbol = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=100, allow_null=True, required=False)
    exchange = serializers.CharField(max_length=10)
    assetType = serializers.CharField(max_length=10)
    ipoDate = serializers.DateField()
    delistingDate = serializers.DateField(allow_null=True, required=False)
    status = serializers.CharField(max_length=10)
    watching = serializers.BooleanField()
