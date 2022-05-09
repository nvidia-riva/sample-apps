# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import requests
import os, sys
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

root_folder = (os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.path.pardir,
                                                 os.path.pardir)))
sys.path.append(root_folder)

from actions.weather import Weather

class ActionWeather(Action):

    def name(self) -> Text:
        return "action_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather() # Weather service
        response = ws.query_weather(city)
        
        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []

        t = "It is {} in {} at the moment. The temperature is {} degrees, the humidity is {} percent and the wind speed is {} miles per hour.".format(
            response['condition'], response['city'], response['temperature_c'], response['humidity'], response['wind_mph'])
        dispatcher.utter_message(text=t)

        return []


class ActionTemperature(Action):

    def name(self) -> Text:
        return "action_temperature"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather() # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []

        t = "It is {} degree celsius in {} at the moment.".format(
            response['temperature_c'], response['city'])
        dispatcher.utter_message(text=t)

        return []


class ActionRainfall(Action):

    def name(self) -> Text:
        return "action_rainfall"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather()  # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []

        t = "The precipitation is {} inches in {} at the moment.".format(
            response['precip'], response['city'])
        dispatcher.utter_message(text=t)

        return []


class ActionSunny(Action):

    def name(self) -> Text:
        return "action_sunny"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather()  # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []

        t = ws.xxx('sunny', city, response)
        dispatcher.utter_message(text=t)

        return []


class ActionCloudy(Action):

    def name(self) -> Text:
        return "action_cloudy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather()  # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []
        
        t = ws.xxx('cloudy', city, response)
        dispatcher.utter_message(text=t)

        return []


class ActionHumidity(Action):

    def name(self) -> Text:
        return "action_humidity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather()  # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []
        
        t = "The humidity is {} percent in {} at the moment".format(
            response['humidity'], response['city'])
        dispatcher.utter_message(text=t)

        return []


class ActionWindy(Action):

    def name(self) -> Text:
        return "action_windy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather()  # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []
        
        t = "{} The wind speed is {} miles per hour.".format(
            ws.is_windy(city, response), response['wind_mph'])
        dispatcher.utter_message(text=t)

        return []

class ActionSnow(Action):

    def name(self) -> Text:
        return "action_snow"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            # This situation is never supposed to happen with good training
            print("[Rasa Actions] ERROR: City not found to find weather")
            dispatcher.utter_message(text="City not found to find weather")
            return []

        ws = Weather()  # Weather service
        response = ws.query_weather(city)

        if 'success' in response and response['success'] == False:
            dispatcher.utter_message(text=response['error_message'])
            return []
        
        t = ws.xxxfall('snow', city, response)
        dispatcher.utter_message(text=t)

        return []
