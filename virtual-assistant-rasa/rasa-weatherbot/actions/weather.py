# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import requests
from config import riva_config

'''
typical api_response format
{'request': {'type': 'City', 'query': 'London, United Kingdom', 'language': 'en', 'unit': 'm'},
'location': {'name': 'London', 'country': 'United Kingdom', 'region': 'City of London, Greater London',
'lat': '51.517', 'lon': '-0.106', 'timezone_id': 'Europe/London', 'localtime': '2019-12-10 22:16',
'localtime_epoch': 1576016160, 'utc_offset': '0.0'}, 'current': {'observation_time': '10:16 PM',
'temperature': 10, 'weather_code': 296, 'weather_icons': ['https://assets.weatherstack.com/images/wsymbols01_png_64/wsymbol_0033_cloudy_with_light_rain_night.png'],
'weather_descriptions': ['Light Rain'], 'wind_speed': 24, 'wind_degree': 260, 'wind_dir': 'W', 'pressure': 1006,
'precip': 1.4, 'humidity': 82, 'cloudcover': 0, 'feelslike': 7, 'uv_index': 1, 'visibility': 10, 'is_day': 'no'}}
'''

weather_service_url = 'http://api.weatherstack.com/current'
weather_stack_key = riva_config["WEATHERSTACK_ACCESS_KEY"] if "WEATHERSTACK_ACCESS_KEY" in riva_config else None

class Weather:
    def __init__(self):
        self.service_url = weather_service_url
        self.access_key = weather_stack_key

    @staticmethod
    def is_xxxing(xxx, condition):
        return xxx in condition.lower()

    def xxx(self, xxx, location, response):
        if self.is_xxxing(xxx, response['condition']):
            return """In {}, it is currently {}.""".format(response['city'], xxx)
        else:
            return """In {}, it is currently not {}.""".format(response['city'], xxx)

    def xxxfall(self, xxx, location, response):
        if self.is_xxxing(xxx, response['condition']):
            return """In {}, it is currently {}ing.""".format(location, xxx)
        else:
            return """In {}, it is currently not {}ing.""".format(location, xxx)

    def is_windy(self, location, response):
        if response['wind_mph'] <= 10:
            return """In {}, it is currently not windy.""".format(location)
        elif response['wind_mph'] > 10 and response['wind_mph'] <= 22:
            return """In {}, it is currently breezy.""".format(location)
        else:
            return """In {}, it is currently quite windy.""".format(location)

    def query_weather(self, location):
        response = {}
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            if not self.access_key:
                response['success'] = False
                response['error_message'] = "The Weather stack API key is not set in your configuration. Please set the API key in the config file"
                print("[Rasa Actions] ERROR: The Weather stack API key is not set in your configuration. Please set the API key in the config file")
                return response
            
            api_result = requests.get(self.service_url, params)
            api_response = api_result.json()

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                response['error_message'] = "There was an Error in getting response from Weather Stack API. City might not be valid or Check your connection to weatherstack.com"
                print("[Rasa Actions] ERROR: There was an Error in getting response from Weather Stack API. City might not be valid or Check your connection to weatherstack.com. Here is the response from Weather Stack API: ", api_response)
                return response

            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = api_response['current']['temperature']
            response['humidity'] = api_response['current']['humidity']
            response['wind_mph'] = api_response['current']['wind_speed']
            response['precip'] = api_response['current']['precip']
            return response
        except Exception as e:
            response['success'] = False
            response['error_message'] = "Exception occurred while requesting Weather Stack API"
            print("[Rasa Actions] ERROR: Exception occurred while requesting Weather Stack API: ", e)
            return response