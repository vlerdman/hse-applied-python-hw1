import requests
import datetime
import asyncio
import aiohttp

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}

class WeatherService:
    def __init__(self):
        self.url = WEATHER_API_URL
        self.cur_weather = None
        self.cur_city = None
        self.timestamp = None
        self.resp_code = 500
    
    async def fetch_weather(self, city, api_key):
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                self.resp_code = response.status
                if response.status == 200:
                    data = await response.json()
                    self.cur_weather = data['main']['temp']
                    self.cur_city = city
                    self.timestamp = data['dt']
                elif response.status == 401:
                    self.cur_weather = await response.json()
        
    def get_weather(self):
        return self.resp_code, self.cur_weather, self.cur_city
    
    def get_season(self):
        date = datetime.datetime.fromtimestamp(self.timestamp)
        return month_to_season[date.month]
