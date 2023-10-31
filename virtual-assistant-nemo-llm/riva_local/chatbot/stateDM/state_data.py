# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

# This is used for finding the state to transition to based on intent
# We've added the misspelled intent weather.temprature because that intent is 
# misspelled in <riva_model_loc>/models/riva_intent_weather/1/intent_labels.csv
# To clarify further, the problem is in the outputs of the intent slot model, 
# not in the sample apps or the Riva Client Python module
intent_transitions = {
    'rivaWeather': {
        'weather.qa_answer': 'checkWeatherLocation',
        'weather.weather': 'checkWeatherLocation',
        'context.weather': 'checkWeatherLocation',
        'weather.temperature': 'checkWeatherLocation',
        'weather.temprature': 'checkWeatherLocation', # Intentional misspelling for debugging
        'weather.sunny': 'checkWeatherLocation',
        'weather.cloudy': 'checkWeatherLocation',
        'weather.snow': 'checkWeatherLocation',
        'weather.rainfall': 'checkWeatherLocation',
        'weather.snow_yes_no': 'checkWeatherLocation',
        'weather.rainfall_yes_no': 'checkWeatherLocation',
        'weather.temperature_yes_no': 'checkWeatherLocation',
        'weather.humidity': 'checkWeatherLocation',
        'weather.humidity_yes_no': 'checkWeatherLocation',
        'navigation.startnavigationpoi': 'checkWeatherLocation',
        'navigation.geteta': 'checkWeatherLocation',
        'navigation.showdirection': 'checkWeatherLocation',
        'riva_error': 'error',
        'navigation.showmappoi': 'error',
        'nomatch.none': 'error'
    }
}