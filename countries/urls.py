from django.urls import path
from .views import (
    RefreshCountriesView,
    CountryListView,
    CountryDetailView,
    StatusView,
    SummaryImageView
)

urlpatterns = [
    path("countries/refresh", RefreshCountriesView.as_view(), name="refresh_countries"),
    path("countries/image", SummaryImageView.as_view(), name="country_image"),
    path("countries", CountryListView.as_view(), name="list_countries"),
    path("countries/<str:name>", CountryDetailView.as_view(), name="country_detail"),
    path("status", StatusView.as_view(), name="status"),
]
