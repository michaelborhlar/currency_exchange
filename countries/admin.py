from django.contrib import admin
from .models import Country, RefreshStatus
# Register your models here.

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "population", "currency_code", "exchange_rate", "estimated_gdp", "last_refreshed_at")
    search_fields = ("name", "region", "currency_code")


@admin.register(RefreshStatus)
class RefreshStatusAdmin(admin.ModelAdmin):
    list_display = ("total_countries", "last_refreshed_at")