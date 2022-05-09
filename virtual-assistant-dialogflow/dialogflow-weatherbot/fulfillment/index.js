// ==============================================================================
// Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
//
// The License information can be found under the "License" section of the
// README.md file.
// ==============================================================================

'use strict';

// Get your access key at - https://weatherstack.com/ and enter it here
const weatherstack_APIkey = '';

const host = 'api.weatherstack.com';
const partial_path = '/current?access_key='+ weatherstack_APIkey +'&query=';

const http = require('http');
const functions = require('firebase-functions');

function is_xxxing(xxx_val, condition) {
	if (condition.toLowerCase().search(xxx_val)!=-1) {
		return true;
	}
    return false;
}

function xxx(xxx_val, response) {
    if (is_xxxing(xxx_val, response.condition)) {
        return `In ${response.city}, it is currently ${xxx_val}.`;
    } else {
        return `In ${response.city}, it is currently not ${xxx_val}.`;
    }
}

function xxxfall(xxx_val, response) {
    if (is_xxxing(xxx_val, response.condition)) {
        return `In ${response.city}, it is currently ${xxx_val}ing.`;
    } else {
        return `In ${response.city}, it is currently not ${xxx_val}ing.`;
    }
}

function is_windy(response) {
    if (response.wind_mph <= 10) {
        return `In ${response.city}, it is currently not windy.""".`;
    } else if (response.wind_mph > 10 && response.wind_mph <= 22) {
        return `In ${response.city}, it is currently breezy.`;
    } else {
        return `In ${response.city}, it is currently quite windy.`;
    }
}

function cloudyFulfillment(response) {
	let fulfillment_text = xxx('cloudy', response);
	return fulfillment_text;
}

function humidityFulfillment(response) {
	let fulfillment_text = `The humidity is ${response['humidity']} percent in ${response['city']} at the moment`;
	return fulfillment_text;
}

function rainfallFulfillment(response) {
	let fulfillment_text = `The precipitation is ${response['precip']} inches in ${response['city']} at the moment.`;
	return fulfillment_text;
}

function snowFulfillment(response) {
	let fulfillment_text = xxxfall('snow', response);
	return fulfillment_text;
}

function sunnyFulfillment(response) {
	let fulfillment_text = xxx('sunny', response);
	return fulfillment_text;
}

function temperatureFulfillment(response) {
	let fulfillment_text = `It is ${response['temperature_c']} degree celsius in ${response['city']} at the moment.`;
	return fulfillment_text;
}

function weatherFulfillment(response) {
	let fulfillment_text = `It is ${response['condition']} in ${response['city']} at the moment. The temperature is ${response['temperature_c']} degrees, the humidity is ${response['humidity']} percent and the wind speed is ${response['wind_mph']} miles per hour.`;
	return fulfillment_text;
}

function windyFulfillment(response) {
	let fulfillment_text = `${is_windy(response)} The wind speed is ${response['wind_mph']} miles per hour.`;
	return fulfillment_text;
}

function intent_outputfunction_mapping_fcn() {
	let intent_outputfunction_mapping = {};
	intent_outputfunction_mapping['cloudy'] = cloudyFulfillment;
	intent_outputfunction_mapping['cloudy - custom'] = cloudyFulfillment;
	intent_outputfunction_mapping['humidity'] = humidityFulfillment;
	intent_outputfunction_mapping['humidity - custom'] = humidityFulfillment;
	intent_outputfunction_mapping['rainfall'] = rainfallFulfillment;
	intent_outputfunction_mapping['rainfall - custom'] = rainfallFulfillment;
	intent_outputfunction_mapping['snow'] = snowFulfillment;
	intent_outputfunction_mapping['snow - custom'] = snowFulfillment;
	intent_outputfunction_mapping['sunny'] = sunnyFulfillment;
	intent_outputfunction_mapping['sunny - custom'] = sunnyFulfillment;
	intent_outputfunction_mapping['temperature'] = temperatureFulfillment;
	intent_outputfunction_mapping['temperature - custom'] = temperatureFulfillment;
	intent_outputfunction_mapping['weather'] = weatherFulfillment;
	intent_outputfunction_mapping['weather - custom'] = weatherFulfillment;
	intent_outputfunction_mapping['windy'] = windyFulfillment;
	intent_outputfunction_mapping['windy - custom'] = windyFulfillment;
	return intent_outputfunction_mapping;
}  

const intent_outputfunction_mapping = intent_outputfunction_mapping_fcn();


exports.dialogflowFirebaseFulfillment = functions.https.onRequest((req, res) => {
  // Get the city and date from the request
  let detected_intent = req.body.queryResult.intent.displayName;
  let city = null;
  if ('geo-city1' in req.body.queryResult.parameters) {
	  city = req.body.queryResult.parameters['geo-city1']; // city is a required param
  }
  if (city) {
	  if (weatherstack_APIkey) {
		  // Call the weather API
		  callWeatherApi(city).then((apiOutput) => {
			  let fulfillment_text = null;
			  if (detected_intent in intent_outputfunction_mapping) {
				  fulfillment_text = intent_outputfunction_mapping[detected_intent](apiOutput);   
			  } else {
				  fulfillment_text = "Fulfillment not found for intent " + detected_intent;
			  }
			  res.json({ 'fulfillmentText': fulfillment_text });
		  }).catch(() => {
		    res.json({ 'fulfillmentText': `Exception occurred while requesting Weather Stack API.` });
		  });
	  } else {
		  res.json({ 'fulfillmentText': `The Weather stack API key is not set in line 7. Please set the API key.` });
		  console.log(`ERROR: The Weather stack API key is not set in line 7. Please set the API key.`);
	  }
  } else {
	  res.json({ 'fulfillmentText': `For which location?` });
  }
  
});

function parseAPIResponse(api_response) {
	let response = {};
    response.success = true;
    response.country = api_response['location']['country'];
    response.city = api_response['location']['name'];
    response.condition = api_response['current']['weather_descriptions'][0];
    response.temperature_c = api_response['current']['temperature'];
    response.humidity = api_response['current']['humidity'];
    response.wind_mph = api_response['current']['wind_speed'];
    response.precip = api_response['current']['precip'];
    return response;
}

function callWeatherApi (city) {
  return new Promise((resolve, reject) => {
    // Create the path for the HTTP request to get the weather
    let path = partial_path + encodeURIComponent(city);
    console.log('API Request: ' + host + path);

    // Make the HTTP request to get the weather
    http.get({host: host, path: path}, (res) => {
      let body = ''; // var to store the response chunks
      res.on('data', (d) => { body += d; }); // store each response chunk
      res.on('end', () => {
    	let api_response = JSON.parse(body);
    	let output = null;
    	if ('success' in api_response && api_response.success == false) {
    		output = "There was an Error in getting response from Weather Stack API. City might not be valid or Check your connection to weatherstack.com";
    	    console.log("[Dialogflow Fulfillment] ERROR: There was an Error in getting response from Weather Stack API. City might not be valid or Check your connection to weatherstack.com. Here is the response from Weather Stack API: " + api_response);
    	} else {
    		output = parseAPIResponse(api_response);
    		// console.log(output);
    	}
    	resolve(output);
      });
      res.on('error', (error) => {
    	console.log("[Dialogflow Fulfillment] ERROR: Exception occurred while requesting Weather Stack API: "+error);
        reject();
      });
    });
  });
}