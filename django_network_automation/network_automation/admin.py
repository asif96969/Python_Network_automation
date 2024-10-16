from django.contrib import admin
from .models import Device, NetworkConnection

admin.site.register(Device)
admin.site.register(NetworkConnection)

