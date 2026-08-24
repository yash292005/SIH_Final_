from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/weather/", views.weather_api, name="weather_api"),
]
