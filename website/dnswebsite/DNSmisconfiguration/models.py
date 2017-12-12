from django.db import models


class AddressURL(models.Model):
    url_address = models.CharField(max_length=256)


class AddressIP(models.Model):
    url = models.ForeignKey(AddressURL, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=256)
    misconfigured = models.BooleanField()
