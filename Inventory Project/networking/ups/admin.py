# In upsapp/admin.py
from django.contrib import admin
from .models import SNMP, History, Manual

admin.site.register(SNMP)
admin.site.register(History)
admin.site.register(Manual)
