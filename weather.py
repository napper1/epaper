import os
from datetime import datetime

import requests

from constants import WEATHER_FORECAST_JSON


class WeatherClient(object):
    last_update = None
    weather_json = {}

    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.latitude = os.getenv("LATITUDE")
        self.longitude = os.getenv("LONGITUDE")
        self.exclude = "minutely,hourly"

    def get_current(self):
        """
        Get current forecast
        """
        url = (
            f"{self.base_url}/weather?q=Sydney,NSW,au&units=metric&appid={self.api_key}"
        )
        r = requests.get(url)
        return r.json()

    def get_forecast(self):
        """
        Return hourly forecast
        """
        url = f"{self.base_url}/forecast?q=Sydney,NSW,au&units=metric&appid={self.api_key}"
        response = requests.get(url)
        if response.ok:
            return response.json()
        return {}

    def get_daily_forecast(self):
        """
        https://openweathermap.org/api/one-call-api
        Supports: current, minutely. hourly. daily, alerts all in one JSON
        These can be excluded.
        """
        diff_minutes = None
        if self.last_update:
            difference = datetime.now() - self.last_update
            diff_minutes = difference.total_seconds() / 60
        if diff_minutes is None or diff_minutes > 60:
            # call API
            pass
            # url = f"{self.base_url}/onecall?lat={self.latitude}&lon={self.longitude}&exclude={self.exclude}&units=metric&appid={self.api_key}"
            # response = requests.get(url)
            # if response.ok:
            #     return response.json()
            # self.weather_json = response.json()
            # return {}
            self.last_update = datetime.now()
        else:
            # use the last saved
            # return self.weather_json
            pass
        return WEATHER_FORECAST_JSON

    def get_weather_forecast_list(self):
        """
        Parse forecast JSON into a list of days consisting of day temperature, weather type, and day name.
        """
        weather = self.get_daily_forecast()
        forecast = []
        # Add current weather as first forecast item
        current_weather_temp = int(weather["current"]["temp"])
        current_weather_type = weather["current"]["weather"][0][
            "main"
        ]  # Rain / Sunny / etc
        week_day = datetime.utcfromtimestamp(weather["current"]["dt"])
        current_weather = {
            "temp": str(current_weather_temp),
            "type": current_weather_type,
            "day": week_day.strftime("%a"),
        }
        forecast.append(current_weather)
        # Add daily forecast for the next 7 days
        weather_daily = weather["daily"]
        # Remove today's weather since we have it in current weather
        del weather_daily[0]
        for day in weather["daily"]:
            week_day = datetime.utcfromtimestamp(day["dt"])
            temp = int(day["temp"]["day"])
            weather_type = day["weather"][0]["main"]
            weather = {
                "temp": str(temp),
                "type": weather_type,
                "day": week_day.strftime("%a"),
                "date": str(week_day),
            }
            forecast.append(weather)
        return forecast
