# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import riva_api.riva_nlp_pb2 as rnlp
import riva_api.riva_nlp_pb2_grpc as rnlp_srv

import grpc
from config import riva_config, rivanlp_config
import requests
import json

channel = grpc.insecure_channel(riva_config["RIVA_SPEECH_API_URL"])
riva_nlp = rnlp_srv.RivaLanguageUnderstandingStub(channel)

# The default intent object for specifying the city
SPECIFY_CITY_INTENT = { 'value': "specify_city", 'confidence': 1 }
NLU_FALLBACK_INTENT = { 'value': "nlu_fallback", 'confidence': 1 }

# Default NLP parameters - Used in case config values not specified in the config.py file
VERBOSE = False 
NLU_FALLBACK_THRESHOLD = 0.3

verbose = rivanlp_config["VERBOSE"] if "VERBOSE" in rivanlp_config else VERBOSE
nlu_fallback_threshold = rivanlp_config["NLU_FALLBACK_THRESHOLD"] if "NLU_FALLBACK_THRESHOLD" in rivanlp_config else NLU_FALLBACK_THRESHOLD


def get_intent_rnlp(resp, result):
    if hasattr(resp, 'intent') and (hasattr(resp, 'domain') and resp.domain.class_name != "nomatch.none"):
        result['intent'] = { 'value': resp.intent.class_name, 'confidence': resp.intent.score }
        parentclassintent_index = result['intent']['value'].find(".")
        if parentclassintent_index != -1:
            result['intent']['value'] = result['intent']['value'].replace(".", "__", 1)


def set_nlu_fallback_intent(result):
    if not result['intent'] or result['intent']['confidence'] < nlu_fallback_threshold:
        result['intent'] = NLU_FALLBACK_INTENT
        if verbose:
            print("[Riva NLU] Intent set to ", NLU_FALLBACK_INTENT)


def get_entities_rnlp(resp, result):
    location_found_flag = False
    all_entities_class = {}
    all_entities = []
    if hasattr(resp, 'slots'):
        for i in range(len(resp.slots)):
            slot_class = resp.slots[i].label[0].class_name.replace("\r", "")
            token = resp.slots[i].token.replace("?", "").replace(",", "").replace(".", "").replace("[SEP]", "").strip()
            score = resp.slots[i].label[0].score
            if slot_class and token:
                if slot_class == 'weatherplace' or slot_class == 'destinationplace':
                    entity = { "value": token,
                                "confidence": score,
                                "entity": "location" }
                    location_found_flag = True
                else:
                    entity = { "value": token,
                                "confidence": score,
                                "entity": slot_class }
                all_entities_class[entity["entity"]] = 1
                all_entities.append(entity)
    for cl in all_entities_class:
        partial_entities = list(filter(lambda x: x["entity"] == cl, all_entities))
        partial_entities.sort(reverse=True, key=lambda x: x["confidence"])
        for entity in partial_entities: 
            if entity["value"] != "[SEP]":
                result['entities'].append(entity)
                break
    return location_found_flag
                

def get_entities_rcnlp(resp, result):
    location_found_flag = False
    for current_result in resp.results[0].results:
        if current_result.label[0].class_name == "LOC":
            if verbose:
                print(f"[Riva NLU] Location found: {current_result.token}") # Flow unhandled for multiple location input
            entity = { "value": current_result.token,
                        "confidence": current_result.label[0].score,
                        "entity": "location" }
            location_found_flag = True
            result['entities'].append(entity)
    return location_found_flag


def get_riva_output(text):
    # Submit an AnalyzeIntentRequest. We do not provide a domain with the query, so a domain
    # classifier is run first, and based on the inferred value from the domain classifier,
    # the query is run through the appropriate intent/slot classifier
    # Note: the detected domain is also returned in the response.
    result = {'intent': None, 'entities': []}
    try:
        req = rnlp.AnalyzeIntentRequest()
        req.query = str(text)
        # The <domain_name> is appended to "riva_intent_" to look for a model "riva_intent_<domain_name>"
        # So the model "riva_intent_<domain_name>" needs to be preloaded in riva server.
        # In this case the domain is weather and the model being used is "riva_intent_weather-misc".
        req.options.domain = "weather"
        resp = riva_nlp.AnalyzeIntent(req)
    except Exception as inst:
        # An exception occurred
        print("[Riva NLU] ERROR: Error during NLU request: " + str(inst))
        return {"error": 'Riva_NLU_Error', "error_message": str(inst)}
    get_intent_rnlp(resp, result)
    location_found_flag = get_entities_rnlp(resp, result)
    if not location_found_flag:
        if verbose:
            print(f"[Riva NLU] Did not find any location in the string: {text}\n"
                    "[Riva NLU] Checking again using NER model")
        try:
            req = rnlp.TokenClassRequest()
            req.model.model_name = "riva_ner"
            req.text.append(text)
            resp_ner = riva_nlp.ClassifyTokens(req)
        except Exception as inst:
            # An exception occurred
            print("[Riva NLU] ERROR: Error during NLU request (riva_ner): " + str(inst))
            return {"error": 'Riva_NLU_Error', "error_message": str(inst)}
        if verbose:
            print(f"[Riva NLU] NER response results: \n {resp_ner.results[0].results}\n")
            print("[Riva NLU] Location Entities:")
        location_found_flag = get_entities_rcnlp(resp_ner, result)
        if location_found_flag:
            if not result['intent']:
                result['intent'] = SPECIFY_CITY_INTENT
                if verbose:
                    print("[Riva NLU] Intent set to ", SPECIFY_CITY_INTENT)
        else:
            if verbose:
                print("[Riva NLU] No location found in string using NER LOC")
    set_nlu_fallback_intent(result)
    if verbose:
        print("[Riva NLU] Final Riva NLU Output: ", result)
    return result


def get_intent_and_entities(text):
    return get_riva_output(text)
