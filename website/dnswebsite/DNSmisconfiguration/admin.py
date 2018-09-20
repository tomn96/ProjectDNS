from django.contrib import admin

from .models import Server, AddressIPv4, AddressIPv6, KnownNameServer

admin.site.register(AddressURL)
admin.site.register(AddressIP)
