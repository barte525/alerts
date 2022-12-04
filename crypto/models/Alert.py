from django.db import models


class Alert(models.Model):
    origin_asset_name = models.CharField(max_length=30)
    alert_value = models.FloatField(null=False)
    email = models.EmailField(null=False, max_length=254)
    currency = models.CharField(max_length=30)
    alert_when_increases = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    on_email = models.BooleanField(default=True)








