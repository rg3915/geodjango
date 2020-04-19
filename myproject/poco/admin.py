from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Poco


@admin.register(Poco)
class PocoAdmin(LeafletGeoAdmin):
    pass
