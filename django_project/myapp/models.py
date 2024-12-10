from django.db import models


# Create your models here.
class Symbol(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=1000, null=True)
    exchange = models.CharField(max_length=10)
    assetType = models.CharField(max_length=10)
    ipoDate = models.DateField()
    delistingDate = models.DateField(null=True)
    status = models.CharField(max_length=10)
    watching = models.BooleanField(default=False)


class Price(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.IntegerField()

    class Meta:
        unique_together = ('symbol', 'timestamp')
