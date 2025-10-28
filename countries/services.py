import random
import requests
from decimal import Decimal
from django.utils import timezone
from .models import Country, RefreshStatus

def fetch_countries_data():
    """Fetch country info from REST Countries API."""
    url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        raise Exception(f"Could not fetch data from Countries API: {e}")

def fetch_exchange_rates(base_currency='USD'):
    """Fetch exchange rate data."""
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()
        data = res.json()
        return data.get('rates', {})
    except Exception as e:
        raise Exception(f"Could not fetch data from Exchange Rate API: {e}")

def refresh_countries_data():
    """Fetch, compute GDP, and update or insert countries."""
    countries_data = fetch_countries_data()
    exchange_rates = fetch_exchange_rates()

    total = 0
    for c in countries_data:
        name = c.get('name')
        capital = c.get('capital')
        region = c.get('region')
        population = c.get('population', 0)
        flag = c.get('flag')

        currencies = c.get('currencies', [])
        currency_code = None
        exchange_rate = None
        estimated_gdp = None

        if currencies:
            currency_code = currencies[0].get('code')
            exchange_rate = exchange_rates.get(currency_code)

            if exchange_rate:
                multiplier = random.randint(1000, 2000)
                try:
                    estimated_gdp = Decimal(population) * Decimal(multiplier) / Decimal(exchange_rate)
                except Exception:
                    estimated_gdp = None

        # Update or create (case-insensitive)
        Country.objects.update_or_create(
            name__iexact=name,
            defaults={
                'name': name,
                'capital': capital,
                'region': region,
                'population': population,
                'currency_code': currency_code,
                'exchange_rate': exchange_rate,
                'estimated_gdp': estimated_gdp,
                'flag_url': flag,
                'last_refreshed_at': timezone.now()
            }
        )
        total += 1

    # Update global refresh status
    RefreshStatus.objects.all().delete()
    RefreshStatus.objects.create(total_countries=total, last_refreshed_at=timezone.now())

    return {"message": f"Successfully refreshed {total} countries."}
