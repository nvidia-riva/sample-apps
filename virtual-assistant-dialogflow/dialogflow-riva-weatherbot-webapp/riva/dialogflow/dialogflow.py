# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import os
import sys
import grpc
import requests
from google.cloud import dialogflow

from config import dialogflow_config

# Default ASR parameters - Used in case config values not specified in the config.py file
VERBOSE = False

# Class to handle all Dialogflow operations
class DialogflowPipe(object):
    
    def __init__(self, user_conversation_index):
        if "PROJECT_ID" in dialogflow_config:
            self.project_id = dialogflow_config["PROJECT_ID"]
        else:
            print('[Dialogflow] ERROR: PROJECT_ID not found in dialogflow_config. Please provide the PROJECT_ID in dialogflow_config and restart the server to continue')
            os._exit(1)
        if "LANGUAGE_CODE" in dialogflow_config:
            self.language_code = dialogflow_config["LANGUAGE_CODE"]
        else:
            print('[Dialogflow] ERROR: LANGUAGE_CODE not found in dialogflow_config. Please provide the LANGUAGE_CODE in dialogflow_config and restart the server to continue')
            os._exit(1)
        self.verbose = dialogflow_config["VERBOSE"] if "VERBOSE" in dialogflow_config else VERBOSE        
        self.user_conversation_index = user_conversation_index
    
    # Function to call google dialogflow API with user input and conversation id. Returns the final text response
    def request_dialogflow_for_question(self, message):
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(self.project_id, self.user_conversation_index)
        text_input = dialogflow.TextInput(text=message, language_code=self.language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )
            if response and response.query_result:
                if response.query_result.fulfillment_text:
                    if self.verbose:
                        print("[Dialogflow] Request: {}".format(response.query_result.query_text))
                        print("[Dialogflow] Detected intent: {} (confidence: {})\n".format(
                                response.query_result.intent.display_name,
                                response.query_result.intent_detection_confidence,
                            )
                        )
                        print("[Dialogflow] Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
                    return response.query_result.fulfillment_text
                else:
                    print("[Dialogflow] ERROR: There was no response from Dialogflow")
                    return "There was no response from Dialogflow" 
            else:
                print("[Dialogflow] ERROR: There was an error while making Dialogflow API call. It didnt return response or response.query_result")
                return "There was an error while making Dialogflow API call." 
        except Exception as e:
            print("[Dialogflow] ERROR: There was an error while making Dialogflow API call. Here is the error: ", e)
            return "There was an error while making Dialogflow API call." 