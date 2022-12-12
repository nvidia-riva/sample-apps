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

from config import rasa_config

# Default ASR parameters - Used in case config values not specified in the config.py file
VERBOSE = False

# Class to handle all RASA operations
class RASAPipe(object):
    
    def __init__(self, user_conversation_index):
        if "RASA_API_URL" in rasa_config:
            self.messagesurl = rasa_config["RASA_API_URL"] + "/webhooks/rest/webhook"
        else:
            print('[RASA] ERROR: RASA_API_URL not found in rasa_config. Please provide the RASA_API_URL in rasa_config and restart the server to continue')
            os._exit(1)
        self.verbose = rasa_config["VERBOSE"] if "VERBOSE" in rasa_config else VERBOSE        
        self.user_conversation_index = user_conversation_index
    
    # Function to process the response object returned by rasa, to get the final text response
    def process_rasa_response(self, rasa_response):
        rasa_response_text = rasa_response[len(rasa_response)-1]['text']
        return rasa_response_text
    
    # Function to call rasa API with user input and conversation id. Returns the final text response
    def request_rasa_for_question(self, message):
        rasa_requestdata = {"message": message, "sender": self.user_conversation_index}
        if self.verbose:
            print("[Rasa/Riva NLP + RASA DM] Request: "+str(rasa_requestdata))
        x = requests.post(self.messagesurl, json = rasa_requestdata)
        rasa_response = x.json()
        processed_rasa_response = self.process_rasa_response(rasa_response)
        if self.verbose:
            print("[Rasa/Riva NLP + RASA DM] Raw Response: "+str(rasa_response))
            print("[Rasa/Riva NLP + RASA DM] Processed Response: "+str(processed_rasa_response))
        return processed_rasa_response