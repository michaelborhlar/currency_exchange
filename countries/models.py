from django.db import models
from django.utils import timezone
# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=4, blank=True, null=True)
    estimated_gdp = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    flag_url = models.URLField(blank=True, null=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class RefreshStatus(models.Model):
    total_countries = models.IntegerField(default=0)
    last_refreshed_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"Refreshed on {self.last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S')}"


    class Meta:
        verbose_name = "Refresh Status"
        verbose_name_plural = "Refresh Status"