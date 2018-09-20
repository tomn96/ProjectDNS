from django.db import models


class Server(models.Model):
    host_name = models.CharField(primary_key=True, max_length=256, default="")
    description = models.CharField(max_length=512, default="")
    original_domain = models.CharField(max_length=256, default="")


class AddressIPv4(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(protocol='IPv4')


class AddressIPv6(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(protocol='IPv6')


class KnownNameServer(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    domain = models.CharField(max_length=512, default="")
    known_server = models.CharField(max_length=256, default="")

    class Meta:
        unique_together = (('server', 'domain'),)
