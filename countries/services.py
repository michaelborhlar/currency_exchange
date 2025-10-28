import random
import requests
from decimal import Decimal
from django.utils import timezone
from .models import Country, RefreshStatus


def fetch_country_data():
    """Fetch country info from REST Countries API."""
    url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    try:
        res = requests.get(url, timeout=100)
        res.raise_for_status()
        data = res.json()
        print(f"[INFO] ✅ Fetched {len(data)} countries from REST Countries API")
        return data
    except Exception as e:
        print(f"[ERROR] ❌ Could not fetch data from API: {e}")
        raise Exception(f"Could not fetch country data: {e}")



def fetch_exchange_rates(base_currency='USD'):
    """Fetch exchange rate data from open.er-api.com."""
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()
        data = res.json()
        rates = data.get('rates', {})
        print(f"[INFO] ✅ Fetched {len(rates)} exchange rates")
        return rates
    except Exception as e:
        print(f"[ERROR] ❌ Could not fetch exchange rate data: {e}")
        return {}


def refresh_countries_data():
    """
    Fetch all country data, compute estimated GDP,
    and update/insert into database.
    """
    countries_data = fetch_country_data()
    if not countries_data:
        raise Exception("No data returned from REST Countries API.")

    exchange_rates = fetch_exchange_rates()
    total = 0

    for c in countries_data:
        try:
            name = c.get('name')
            if not name:
                continue

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

            # Save or update country
            Country.objects.update_or_create(
                name=name,
                defaults={
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

        except Exception as e:
            print(f"[ERROR] ❌ Could not process country {c.get('name')}: {e}")

    # Update refresh status
    RefreshStatus.objects.all().delete()
    RefreshStatus.objects.create(total_countries=total, last_refreshed_at=timezone.now())

    print(f"[SUCCESS] 🎯 Refreshed and saved {total} countries.")
    return {"message": f"Successfully refreshed {total} countries."}
