from django.db import models


class Server(models.Model):
    host_name = models.CharField(primary_key=True, max_length=256, default="")
    description = models.CharField(max_length=512, default="")
    original_domain = models.CharField(max_length=256, default="")

    def __str__(self):
        return str(self.host_name)


class AddressIPv4(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(protocol='IPv4')

    def __str__(self):
        return str(self.ip_address) + " (" + str(self.server.host_name) + ")"


class AddressIPv6(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(protocol='IPv6')

    def __str__(self):
        return str(self.ip_address) + " (" + str(self.server.host_name) + ")"


class KnownNameServer(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    domain = models.CharField(max_length=512, default="")
    known_server = models.CharField(max_length=256, default="")

    def __str__(self):
        return "(" + str(self.server.host_name) + ", " + str(self.domain) + ") --> " + str(self.known_server)


class RootDNSServers(models.Model):
    host_name = models.CharField(primary_key=True, max_length=256, default="")
    ipv4_address = models.GenericIPAddressField(protocol='IPv4')
    ipv6_address = models.GenericIPAddressField(protocol='IPv6')
    description = models.CharField(max_length=512, default="")


class StoredDict(models.Model):
    pickle_dict = models.BinaryField()
