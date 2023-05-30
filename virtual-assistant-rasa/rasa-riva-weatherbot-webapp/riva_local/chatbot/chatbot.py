# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import time

from riva_local.asr.asr import ASRPipe
from riva_local.rasa.rasa import RASAPipe
# from riva_local.tts.tts import TTSPipe
from riva_local.tts.tts_stream import TTSPipe

class ChatBot(object):
    """ Class Implementing all the features of the chatbot"""

    def __init__(self, user_conversation_index, verbose=False):
        self.id = user_conversation_index
        self.asr = ASRPipe()
        self.rasa = RASAPipe(user_conversation_index)
        self.tts = TTSPipe()
        self.thread_asr = None
        self.pause_asr_flag = False
        self.enableTTS = False
        self.verbose = verbose

    def server_asr(self):
        if self.verbose:
            print(f'[Riva Chatbot] [{self.id }] Starting chatbot ASR server task')
        self.asr.main_asr()

    def start_asr(self, sio):
        self.thread_asr = sio.start_background_task(self.server_asr)
        if self.verbose:
            print(f'[Riva Chatbot] [{self.id }] ASR background task started')

    def wait(self):
        self.thread_asr.join()
        if self.verbose:
            print(f'[Riva Chatbot] [{self.id }] ASR background task terminated')
            
    def empty_asr_buffer(self):
        self.asr.empty_asr_buffer()
        if self.verbose:
            print(f'[Riva Chatbot] [{self.id }] ASR buffer cleared')
        
    # Function to fill the asr buffer with audio snippets
    def asr_fill_buffer(self, audio_in):
        if not self.pause_asr_flag:
            self.asr.fill_buffer(audio_in)
        
    # Function to get asr'ed text transcript  
    def get_asr_transcript(self):
        return self.asr.get_transcript()
    
    def pause_asr(self):
        self.pause_asr_flag = True
        
    def unpause_asr(self, on):
        if on == "REQUEST_COMPLETE" and not self.enableTTS:
            self.pause_asr_flag = False
            if self.verbose:
                print(f'[Riva Chatbot] [{self.id }] ASR successfully unpaused for Request Complete')
            return True
        elif on == "TTS_END":
            self.reset_current_tts_duration()
            self.pause_asr_flag = False
            if self.verbose:
                print(f'[Riva Chatbot] [{self.id}] ASR successfully unpaused for TTS End')
            return True
    
    def pause_wait_unpause_asr(self):
            self.pause_asr_flag = True
            time.sleep(1) # Wait till riva has completed tts operation
            time.sleep(self.get_current_tts_duration()+2) # Added the 2 extra seconds to account for the flush audio in tts
            self.reset_current_tts_duration()
            self.pause_asr_flag = False
            
    # Function to pipeline rasa and tts functionality
    def rasa_tts_pipeline(self, text):
        # Request rasa for response with user input and sender id
        response_text = self.rasa.request_rasa_for_question(text)
        if len(response_text) and self.enableTTS == True:
            # Fill tts buffer with rasa response text, if enableTTS is set to True
            self.tts_fill_buffer(response_text)
        return response_text
            
    def start_tts(self):
        self.enableTTS = True
        if self.verbose:
            print(f'[Riva Chatbot] [{self.id }] TTS Enabled')
        
    def stop_tts(self):
        self.enableTTS = False
        if self.verbose:
            print(f'[Riva Chatbot] [{self.id }] TTS Disabled')
            
    def get_tts_speaking_flag(self):
        return self.tts.tts_speaking
    
    def get_current_tts_duration(self):
        return self.tts.get_current_tts_duration()
    
    def reset_current_tts_duration(self):
        self.tts.reset_current_tts_duration()        
            
    # Function to fill the tts buffer with text
    def tts_fill_buffer(self, response_text):
        if self.enableTTS:
            if self.verbose:
                print(f'[Riva Chatbot] [{self.id }] Client speak: ', response_text)
            self.tts.fill_buffer(response_text)
        
    # Function to get audio from tts  
    def get_tts_speech(self):
        return self.tts.get_speech()