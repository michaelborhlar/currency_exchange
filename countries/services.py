# countries/services.py
import random
import requests
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.utils import timezone
from .models import Country, RefreshStatus

def fetch_country_data():
    url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    try:
        res = requests.get(url, timeout=60)
        res.raise_for_status()
        data = res.json()
        print(f"[INFO] ✅ Fetched {len(data)} countries from REST Countries API")
        return data
    except Exception as e:
        print(f"[ERROR] ❌ Could not fetch data from API: {e}")
        raise Exception(f"Could not fetch country data: {e}")

def fetch_exchange_rates(base_currency='USD'):
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        data = res.json()
        rates = data.get('rates', {}) or {}
        print(f"[INFO] ✅ Fetched {len(rates)} exchange rates")
        # convert rates values to Decimal
        rates_dec = {}
        for k, v in rates.items():
            try:
                rates_dec[k] = Decimal(str(v))
            except (InvalidOperation, TypeError):
                continue
        return rates_dec
    except Exception as e:
        print(f"[ERROR] ❌ Could not fetch exchange rate data: {e}")
        return {}

def refresh_countries_data():
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
            population = c.get('population') or 0
            # ensure population is int
            try:
                population = int(population)
            except (ValueError, TypeError):
                population = 0

            flag = c.get('flag') or c.get('flags')  # v2 vs v3 fallback

            currencies = c.get('currencies') or []
            currency_code = None
            exchange_rate = None
            estimated_gdp = None

            if currencies and isinstance(currencies, list) and currencies:
                currency_code = currencies[0].get('code')
                if currency_code:
                    exchange_rate = exchange_rates.get(currency_code)

            # compute estimated_gdp only if we have an exchange_rate (Decimal)
            if exchange_rate:
                multiplier = random.randint(1000, 2000)
                try:
                    # Decimal math for precision
                    estimated_gdp = (Decimal(population) * Decimal(multiplier) / exchange_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                except Exception:
                    estimated_gdp = None

            Country.objects.update_or_create(
                name=name,
                defaults={
                    'capital': capital,
                    'region': region,
                    'population': population,
                    'currency_code': currency_code,
                    'exchange_rate': float(exchange_rate) if exchange_rate is not None else None,
                    'estimated_gdp': estimated_gdp,
                    'flag_url': flag,
                    'last_refreshed_at': timezone.now()
                }
            )
            total += 1

        except Exception as e:
            print(f"[ERROR] ❌ Could not process country {c.get('name')}: {e}")

    RefreshStatus.objects.all().delete()
    RefreshStatus.objects.create(total_countries=total, last_refreshed_at=timezone.now())
    print(f"[SUCCESS] 🎯 Refreshed and saved {total} countries.")
    return {"message": f"Successfully refreshed {total} countries."}