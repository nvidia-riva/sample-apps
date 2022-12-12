# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from riva.chatbot.chatbot import ChatBot
from config import riva_config

# Default ASR parameters - Used in case config values not specified in the config.py file
VERBOSE = False

verbose = riva_config["VERBOSE"] if "VERBOSE" in riva_config else VERBOSE 

userbots = {}
user_conversation_cnt = 0


def create_chatbot(user_conversation_index, sio):
    if user_conversation_index not in userbots:
        userbots[user_conversation_index] = ChatBot(user_conversation_index,
                                                                verbose=verbose)
        userbots[user_conversation_index].start_asr(sio)
        if verbose:
            print(f'[Riva Chatbot] [{user_conversation_index}] Chatbot Created')


def get_new_user_conversation_index():
    global user_conversation_cnt
    user_conversation_cnt += 1
    user_conversation_index = user_conversation_cnt
    return str(user_conversation_index)


def get_chatbot(user_conversation_index):
    if user_conversation_index in userbots:
        return userbots[user_conversation_index]
    else:
        return None
