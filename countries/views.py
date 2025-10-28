from django.shortcuts import render

# Create your views here.
import io
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from django.db.models import F
from .models import Country, RefreshStatus
from .serializers import CountrySerializer
from .services import fetch_country_data
import os

CACHE_DIR = "cache"
SUMMARY_IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")


class RefreshCountriesView(APIView):
    """POST /countries/refresh — Fetch and cache data"""

    def post(self, request):
        try:
            countries_data = fetch_country_data()
            # Delete and repopulate database
            Country.objects.all().delete()
            for data in countries_data:
                Country.objects.create(**data)

            # Update refresh status
            status_obj, _ = RefreshStatus.objects.get_or_create(id=1)
            status_obj.last_refreshed_at = datetime.utcnow()
            status_obj.total_countries = Country.objects.count()
            status_obj.save()

            # Generate summary image
            self.generate_summary_image()

            return JsonResponse(
                {"message": "Countries refreshed successfully."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return JsonResponse(
                {"error": "Failed to refresh countries", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_summary_image(self):
        """Create summary image with top 5 countries by GDP"""
        os.makedirs(CACHE_DIR, exist_ok=True)
        img = Image.new("RGB", (600, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        title = "Country Summary"
        draw.text((20, 20), title, fill="black")

        # Top 5 countries by GDP
        top_countries = Country.objects.order_by(F('estimated_gdp').desc())[:5]
        y = 60
        for c in top_countries:
            draw.text((20, y), f"{c.name}: {round(c.estimated_gdp, 2)}", fill="blue")
            y += 30

        # Footer
        total = Country.objects.count()
        draw.text((20, 280), f"Total: {total}", fill="black")
        draw.text((20, 310), f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", fill="gray")

        img.save(SUMMARY_IMAGE_PATH)


class CountryListView(generics.ListAPIView):
    """GET /countries — supports filtering and sorting"""
    serializer_class = CountrySerializer

    def get_queryset(self):
        qs = Country.objects.all()
        region = self.request.GET.get("region")
        currency = self.request.GET.get("currency")
        sort = self.request.GET.get("sort")

        if region:
            qs = qs.filter(region__iexact=region)
        if currency:
            qs = qs.filter(currency_code__iexact=currency)
        if sort:
            if sort == "gdp_desc":
                qs = qs.order_by(F("estimated_gdp").desc(nulls_last=True))
            elif sort == "gdp_asc":
                qs = qs.order_by(F("estimated_gdp").asc(nulls_last=True))
        return qs


class CountryDetailView(APIView):
    """GET /countries/:name and DELETE /countries/:name"""

    def get(self, request, name):
        country = get_object_or_404(Country, name__iexact=name)
        return JsonResponse(CountrySerializer(country).data, safe=False)

    def delete(self, request, name):
        country = Country.objects.filter(name__iexact=name).first()
        if not country:
            return JsonResponse({"error": "Country not found"}, status=404)
        country.delete()
        return JsonResponse({"message": f"{name} deleted successfully."})


class StatusView(APIView):
    """GET /status — Show total countries and last refresh"""
    def get(self, request):
        status_obj = RefreshStatus.objects.first()
        if not status_obj:
            return JsonResponse({"total_countries": 0, "last_refreshed_at": None})
        return JsonResponse({
            "total_countries": status_obj.total_countries,
            "last_refreshed_at": status_obj.last_refreshed_at
        })


class SummaryImageView(APIView):
    """GET /countries/image — Serve summary image"""
    def get(self, request):
        if not os.path.exists(SUMMARY_IMAGE_PATH):
            return JsonResponse({"error": "Summary image not found"}, status=404)
        return FileResponse(open(SUMMARY_IMAGE_PATH, "rb"), content_type="image/png")
