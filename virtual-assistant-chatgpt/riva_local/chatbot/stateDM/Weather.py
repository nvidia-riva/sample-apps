# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from riva_local.chatbot.stateDM.state import State
from riva_local.chatbot.stateDM.Util import WeatherService, query_llm, llm_weather_intents


DEFAULT_MESSAGE = "Unfortunately the weather service is not available at this time. Check your connection to weatherstack.com, set a different API key in your configuration or else try again later."


class Weather(State):
    def __init__(self, bot, uid):
        super(Weather, self).__init__("Weather", bot, uid)
        self.next_state = None

    # # NOTE: weather forecast and weather historical are paid options in weatherstack
    # # forecast and historical methods here return the current data only for now.

    def run(self, request_data):
        ws = WeatherService()

        # Extract time information
        if 'weatherforecastdaily' in request_data['context']['payload']:
            timeinfo =  request_data['context']['payload']['weatherforecastdaily']
        elif 'weathertime' in request_data['context']['payload']:
            timeinfo =  request_data['context']['payload']['weathertime']
        else:
            timeinfo = "Today" # Default

        # Convert LLM Model intents to strings that LLM can understand
        if request_data['context']['intent'] in llm_weather_intents:
            response = {}
            ws.query_weather(request_data['context']['location'], response)

            # Query the LLM service to paraphrase the weather-data to a natural sounding response
            if response['success']:
                message = query_llm(intent=llm_weather_intents[request_data['context']['intent']], 
                                timeinfo=timeinfo,
                                weather_data=response)
            else:
                message = DEFAULT_MESSAGE
        else:
                # TODO: Add support for small talk
                message = "Sorry, I did not understand the query."

        request_data['context'].update({'weather_status': message})

        # Update the response text with the weather status
        request_data.update({'response':
                             self.construct_message(request_data, message)})