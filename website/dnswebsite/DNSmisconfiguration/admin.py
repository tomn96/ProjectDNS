from django.contrib import admin

from .models import Server, AddressIPv4, AddressIPv6, KnownNameServer

admin.site.register(Server)
admin.site.register(AddressIPv4)
admin.site.register(AddressIPv6)
admin.site.register(KnownNameServer)
