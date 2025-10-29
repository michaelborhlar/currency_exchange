import os
from datetime import datetime
from PIL import Image, ImageDraw
from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from django.db.models import F
from .models import Country, RefreshStatus
from .serializers import CountrySerializer
from .services import refresh_countries_data

CACHE_DIR = "cache"
SUMMARY_IMAGE_PATH = os.path.join(CACHE_DIR, "summary.png")


class RefreshCountriesView(APIView):
    """POST /countries/refresh — Fetch and cache data"""
    def post(self, request):
        try:
            result = refresh_countries_data()
            self.generate_summary_image()
            return JsonResponse(result, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "Failed to refresh countries", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_summary_image(self):
        """Create summary image with top 5 countries by estimated GDP"""
        os.makedirs(CACHE_DIR, exist_ok=True)
        img = Image.new("RGB", (600, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        draw.text((20, 20), "Country Summary", fill="black")

        top_countries = Country.objects.order_by(F('estimated_gdp').desc())[:5]
        y = 60
        for c in top_countries:
            draw.text((20, y), f"{c.name}: {round(c.estimated_gdp or 0, 2)}", fill="blue")
            y += 30

        total = Country.objects.count()
        draw.text((20, 280), f"Total: {total}", fill="black")
        draw.text((20, 310), f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", fill="gray")

        img.save(SUMMARY_IMAGE_PATH)


class CountryListView(generics.ListAPIView):
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
        if sort == "gdp_desc":
            qs = qs.order_by('-estimated_gdp')   # descending numeric order
        elif sort == "gdp_asc":
            qs = qs.order_by('estimated_gdp')

        return qs

class CountryDetailView(APIView):
    def get(self, request, name):
        try:
            country = Country.objects.get(name__iexact=name)
            return JsonResponse(CountrySerializer(country).data, safe=False)
        except Country.DoesNotExist:
            return JsonResponse({"error": "Country not found"}, status=404)

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


# countries/views.py - SummaryImageView
class SummaryImageView(APIView):
    def get(self, request):
        if not os.path.exists(SUMMARY_IMAGE_PATH):
            return JsonResponse({"error": "Summary image not found"}, status=404)
        return FileResponse(open(SUMMARY_IMAGE_PATH, "rb"), content_type="image/png", status=200)
