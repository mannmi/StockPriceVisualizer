from rest_framework import serializers

class TickerSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=100)
    exchange = serializers.CharField(max_length=10)
    assetType = serializers.CharField(max_length=10)
    ipoDate = serializers.DateField()
    delistingDate = serializers.DateField()
    status = serializers.CharField(max_length=10)
    watching = serializers.BooleanField()