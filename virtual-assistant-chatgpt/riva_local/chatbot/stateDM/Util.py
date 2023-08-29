# ==============================================================================
# Copyright (c) 2020-2022, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import requests
import datetime

import openai
import random

try:
    import inflect
except ImportError:
    print("[Riva DM] Import Error: Import inflect failed!")
    raise ImportError

from config import riva_config, llm_config, LLM_PROMPT_DEFAULT

p = inflect.engine()

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

# Mapping of intents detected by the Intent & Slot Model to simple intent strings
# that the Large Language Model can understand
llm_weather_intents = {
    "weather.weather":"Weather",
    "context.weather":"Weather",
    "weather.temperature":"Temperature",
    "weather.temperature_yes_no":"Temperature",
    "weather.rainfall_yes_no":"Rain",
    "weather.rainfall":"Rain",
    "weather.snow_yes_no":"Snow",
    "weather.snow":"Snow",
    "weather.cloudy":"Cloudy",
    "weather.sunny":"Sunny",
    "weather.humidity":"Humidity",
    "weather.humidity_yes_no":"Humidity",
}

LLM_ERROR_RESPONSE="Sorry, I could not connect to the LLM Service. Please check the configurations again."

def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0

    try:
        for word in textnum.split():
            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0

    except Exception as e:
        print(e)
        # If an Illegal word is detected, ignore the whole weathertime
        return 0

    return result + current


class WeatherService:

    def __init__(self):
        self.access_key = riva_config["WEATHERSTACK_ACCESS_KEY"]
        self.days_of_week = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
        self.weekend = 'weekend'

    def time_to_days(self, context):
        if riva_config['VERBOSE']:
            print('[Riva Weather] Time info from the query:', context['payload'])
        ctxtime = False
        if 'weatherforecastdaily' in context['payload']:
            ctxtime = context['payload']['weatherforecastdaily'].lower()
        if 'weathertime' in context['payload']:
            ctxtime = context['payload']['weathertime'].lower()
            if ctxtime == "week":
                if 'weatherforecastdaily' in context['payload']:
                    ctxtime = context['payload']['weatherforecastdaily'].lower() + " " + ctxtime
                else:
                    ctxtime = False
        if 'day_of_week' in context['payload']:
            ctxtime = context['payload']['day_of_week'].lower()
        if ctxtime:
            context['time'] = ctxtime
            if 'now' in ctxtime:
                return 0
            elif 'tomorrow' in ctxtime:
                return 1
            elif 'next week' in ctxtime:
                return 7
            elif 'yesterday' in ctxtime:
                return -1
            elif 'last week' in ctxtime:
                return -7
            elif ctxtime in self.days_of_week:
                diff = self.days_of_week[ctxtime] - datetime.datetime.today().weekday()
                if diff<0:
                    diff+=7
                return diff
            elif self.weekend in ctxtime:
                context['time'] = 'during the weekend'
                return self.days_of_week['sunday'] - datetime.datetime.today().weekday()
            elif 'weathertime' in context['payload']:
                if not isinstance(context['payload']['weathertime'], int):
                    q = text2int(context['payload']['weathertime'])
                else:
                    q = context['payload']['weathertime']
                context['time'] = "in {} {}".format(context['payload']['weathertime'], ctxtime)
                if 'week' in ctxtime:
                    return q*7
                elif 'days' in ctxtime:
                    return q
        return 0

    def query_weather(self, location, response):
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            api_result = requests.get('http://api.weatherstack.com/current', params)
            api_response = api_result.json()
            if riva_config['VERBOSE']:
                print("[Riva Weather] Weather API Response: " + str(api_response))

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                return

            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = api_response['current']['temperature']
            response['temperature_c_int'] = api_response['current']['temperature']
            response['humidity'] = api_response['current']['humidity']
            response['wind_mph'] = api_response['current']['wind_speed']
            response['precip'] = api_response['current']['precip']
        except:
            response['success'] = False

    def query_weather_forecast(self, location, day, response):
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            api_result = requests.get('http://api.weatherstack.com/current', params)
            api_response = api_result.json()

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                return
            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = p.number_to_words(api_response['current']['temperature'])
            response['temperature_c_int'] = api_response['current']['temperature']
            response['humidity'] = p.number_to_words(api_response['current']['humidity'])
            response['wind_mph'] = p.number_to_words(api_response['current']['wind_speed'])
        except:
            response['success'] = False

    def query_weather_historical(self, location, day, response):
        params = {
            'access_key': self.access_key,
            'query': location
        }
        try:
            api_result = requests.get('http://api.weatherstack.com/current', params)
            api_response = api_result.json()

            if 'success' in api_response and api_response['success'] == False:
                response['success'] = False
                return

            response['success'] = True
            response['country'] = api_response['location']['country']
            response['city'] = api_response['location']['name']
            response['condition'] = api_response['current']['weather_descriptions'][0]
            response['temperature_c'] = p.number_to_words(api_response['current']['temperature'])
            response['temperature_c_int'] = api_response['current']['temperature']
            response['humidity'] = p.number_to_words(api_response['current']['humidity'])
            response['wind_mph'] = p.number_to_words(api_response['current']['wind_speed'])

        except:
            response['success'] = False

def query_llm(intent, timeinfo, weather_data):
    """
    This function prompts the LLM service to paraphrase real-time weather data to a natural sounding human-like response.

    Args:
    intent: The intent of the user query determined by the Intent & Slot model. For ex. weather, rain, snow, temperature, humidity etc.
    timeinfo: The time of the weather request.
    weather_data: The response of the fulfillment service that contains real-time weather information.

    Returns:
        The weather response paraphrased by the LLM service.
    """

    # Default error response
    llm_response = LLM_ERROR_RESPONSE

    # Step 1: Set the OpenAI API key
    openai.api_key = llm_config["API_KEY"]

    # Real-time weather data is string formatted into a query
    # which will be added to a few examples of paraphrasing weather data when querying the service.
    query ='\n\nIntent: {intent}\nCondition: {condition}\nPlace: {city}\nTime: {time}\nTemperature: {temperature} C\nHumidity: {humidity} percent\nWind Speed: {wind_speed} mph\n\nMisty:'.format(intent=intent, condition=weather_data["condition"], city=weather_data["city"], time=timeinfo, temperature=weather_data["temperature_c"], humidity=weather_data["humidity"], wind_speed=weather_data["wind_mph"])

    if llm_config["VERBOSE"]:
        print("Query to LLM Service:", LLM_PROMPT_DEFAULT+query)

    try:
        # Step 2: Call the LLM service to generate a completion.
        # The query with real-time weather data is added to the few-shot prompt in LLM_PROMPT_DEFAULT (refer <BASE DIR>/config.py)
        # The description and ranges of various parameters are present in the API reference: (https://llm.ngc.nvidia.com/openapi/api-reference
        
        response = openai.ChatCompletion.create(
            model=llm_config["API_MODEL_NAME"],
            messages=[{"role": "system", "content": LLM_PROMPT_DEFAULT}, {"role": "user", "content": query}],
            temperature=llm_config["TEMPERATURE"], # this is the degree of randomness of the model's output
            top_p=llm_config["TOP_P"],
            n=1,
            stop=llm_config["STOP_WORDS"], # stop words
            max_tokens=llm_config["TOKENS_TO_GENERATE"], # tokens to generate
            presence_penalty=llm_config["PRESENCE_PENALTY"], # \in [-2.0, 2.0] Is this kind of the opposite of the beam search diversity rate?
            frequency_penalty=llm_config["REPETITION_PENALTY"], # \in [-2.0, 2.0] as opposed to [1.0, 2.0] as in nemollm repetition_penalty
        )
        llm_response = response.choices[0].message["content"]
        if llm_response.startswith("Misty: "):
            llm_response = llm_response[7:]


        if llm_config["VERBOSE"]:
            print("Response from LLM Service:", llm_response)
    except Exception as e:
        print(e)


    return llm_response
