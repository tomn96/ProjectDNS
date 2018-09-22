from django.contrib import admin

from .models import Server, AddressIPv4, AddressIPv6, KnownNameServer, RootDNSServers, StoredDict


class IPv4Inline(admin.TabularInline):
    model = AddressIPv4
    extra = 0


class IPv6Inline(admin.TabularInline):
    model = AddressIPv6
    extra = 0


class KnownNameServerInline(admin.StackedInline):
    model = KnownNameServer
    extra = 0


class ServerAdmin(admin.ModelAdmin):
    list_display = ('host_name', 'description')
    search_fields = ['host_name']
    inlines = (IPv4Inline, IPv6Inline, KnownNameServerInline)
    ordering = ('host_name', )


admin.site.register(Server, ServerAdmin)

admin.site.register(AddressIPv4)
admin.site.register(AddressIPv6)
admin.site.register(KnownNameServer)
admin.site.register(RootDNSServers)
admin.site.register(StoredDict)
