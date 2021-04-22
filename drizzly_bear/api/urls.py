from django.conf.urls import url

from drizzly_bear.api.views import WeatherCheck as weather_check_view

urlpatterns = [
    url(r"^weather-check/", weather_check_view, name='weather_check'),
]