from typing import Tuple, Dict

import requests
from rest_framework import (
    views as rest_views,
    status as rest_status,
    exceptions as rest_exceptions,
    response as rest_response,
)

from django.conf import settings

from drizzly_bear.api.serializers import WeatherCheckSerializer


class WeatherCheck(rest_views.APIView):
    """
    Check the weather forecast for you location
    Takes user's IP address, or lat/long coordinates to fetch the weather forecast
    """

    serializer_class = WeatherCheckSerializer

    def get_serializer(self):
        return self.serializer_class(self.request.data, context={"request": self.request})

    @staticmethod
    def get_user_coordinates_from_ip(user_ip: str) -> Tuple[float, float]:
        """
        Get coordinates of a user from the IP address
        Args:
            user_ip (str) : IP address of the user

        Returns:
            latitude and longitude coordinates

        Raises:
            APIException
        """
        # the free service only allowed us to use HTTP urls
        location_api_url = f"http://api.ipstack.com/{user_ip}"
        location_api_response = requests.get(location_api_url, params={"access_key": settings.IP_TRACK_API_KEY})
        if location_api_response.status_code != rest_status.HTTP_200_OK:
            raise rest_exceptions.APIException("Location tracker API services are unavailable at the moment.")
        else:
            lat, long = location_api_response.json()["latitude"], location_api_response.json()["longitude"]
            return lat, long

    @staticmethod
    def get_weather_details(lat: float, long: float) -> Dict:
        """
        Get weather details for the given lat and long coordinates
        Args:
            lat (float) :  latitude coordinate
            long (float) : longitude coordinate
        Returns:
            dict of weather indicator params
        Raises:
            ApiException
        """
        # the free service only allowed us to use HTTP urls
        weather_api_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact"
        weather_api_response = requests.get(weather_api_url, params={"lat": str(lat), "lon": str(long)})
        if weather_api_response.status_code != rest_status.HTTP_200_OK:
            raise rest_exceptions.APIException("Weather tracker API services are unavailable at the moment.")
        else:
            # The data can be trimmed down based on API contract with the frontend dev
            return weather_api_response.json()

    def post(self):
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        request_payload = serializer.data
        if user_ip := request_payload.get("user_ip"):
            lat, long = self.get_user_coordinates_from_ip(user_ip)
        else:
            lat, long = request_payload["latitude"], request_payload["longitude"]
        weather_indicator_data = self.get_weather_details(lat, long)
        return rest_response.Response(status=rest_status.HTTP_200_OK, data=weather_indicator_data)
