from django.contrib import admin

from .models import AddressURL, AddressIP

admin.site.register(AddressURL)
admin.site.register(AddressIP)
