import riva.client
# from config import riva_config, nlp_config
from pprint import pprint

# QA api-endpoint
# QA_API_ENDPOINT = nlp_config["QA_API_ENDPOINT"]
# enable_qa = riva_config["ENABLE_QA"]
# verbose = riva_config["VERBOSE"]

# auth = riva.client.Auth(uri=riva_config["RIVA_SPEECH_API_URL"])
auth = riva.client.Auth(uri='localhost:50051')
riva_nlp = riva.client.NLPService(auth)

def get_intent(resp, entities):
    if hasattr(resp, 'intent'):
        entities['intent'] = resp.intent.class_name


def get_slots(resp, entities):
    entities['payload'] = dict()            
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
            if cl == "location":
                entities['location'] = entity["value"]
            else:    
                entities['payload'][cl] = entity["value"]
            break


def get_riva_output(text, verbose=True, enable_qa=False):
    # Submit an AnalyzeIntent request. We do not provide a domain with the query, so a domain
    # classifier is run first, and based on the inferred value from the domain classifier,
    # the query is run through the appropriate intent/slot classifier
    # Note: the detected domain is also returned in the response.
    try:
        # The <domain_name> is appended to "riva_intent_" to look for a model "riva_intent_<domain_name>"
        # So the model "riva_intent_<domain_name>" needs to be preloaded in riva server.
        # In this case the domain is weather and the model being used is "riva_intent_weather-misc".
        options = riva.client.AnalyzeIntentOptions(lang='en-US', domain='weather')
        
        resp: AnalyzeIntentResponse = riva_nlp.analyze_intent(text, options)
    
    except Exception as inst:
        # An exception occurred
        print("[Riva NLU] Error during NLU request")
        return {'riva_error': 'riva_error'}
    entities = {}
    get_intent(resp, entities)
    get_slots(resp, entities)
    if 'location' not in entities:
        if verbose:
            print(f"[Riva NLU] Did not find any location in the string: {text}\n"
                    "[Riva NLU] Checking again using NER model")
        try:
            model_name = "riva_ner"
            resp_ner: TokenClassResponse = riva_nlp.classify_tokens(text, model_name)
        except Exception as inst:
            # An exception occurred
            print("[Riva NLU] Error during NLU request (riva_ner)")
            return {'riva_error': 'riva_error'}

        if verbose:
            print(f"[Riva NLU] NER response results: \n {resp_ner.results[0].results}\n")
            print("[Riva NLU] Location Entities:")
        loc_count = 0
        for result in resp_ner.results[0].results:
            if result.label[0].class_name == "LOC":
                if verbose:
                    print(f"[Riva NLU] Location found: {result.token}") # Flow unhandled for multiple location input
                loc_count += 1
                entities['location'] = result.token
        if loc_count == 0:
            if verbose:
                print("[Riva NLU] No location found in string using NER LOC")
                print("[Riva NLU] Checking response domain")
            if resp.domain.class_name == "nomatch.none":
                # as a final resort try QA API
                if enable_qa == "true":
                    if verbose:
                        print("[Riva NLU] Checking using QA API")
                    riva_misty_profile = requests.get(nlp_config["RIVA_MISTY_PROFILE"]).text # Live pull from Cloud
                    qa_resp = get_qa_answer(riva_misty_profile, text, p_threshold)
                    if not qa_resp['result'] == '':
                        if verbose:
                            print("[Riva NLU] received qa result")
                        entities['intent'] = 'qa_answer'
                        entities['answer_span'] = qa_resp['result']
                        entities['query'] = text
                    else:
                        entities['intent'] = 'riva_error'
                else:
                    entities['intent'] = 'riva_error'
    if verbose:
        print("[Riva NLU] This is what entities contain: ", entities)
    return entities

text = "What is the chance of rain at 4:00 pm on Saturday in Berkeley?"
entities = get_riva_output(text)
# pprint(entities)
