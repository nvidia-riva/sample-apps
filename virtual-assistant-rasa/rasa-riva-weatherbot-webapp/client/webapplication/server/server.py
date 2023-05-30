# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

from __future__ import division

import uuid
import time
import logging
from flask import Flask, jsonify, send_from_directory, Response, request
from flask_cors import CORS
from flask import stream_with_context
from flask_socketio import SocketIO, emit
from os.path import dirname, abspath, join, isdir
from os import listdir
from engineio.payload import Payload

from config import client_config
from riva_local.chatbot.chatbots_multiconversations_management import create_chatbot, get_new_user_conversation_index, get_chatbot

''' Flask Initialization 
'''
app = Flask(__name__)
cors = CORS(app)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
Payload.max_decode_packets = 500  # https://github.com/miguelgrinberg/python-engineio/issues/142
sio = SocketIO(app, logger=False)
verbose = client_config['VERBOSE']
VA_INIT_MESSAGE = "Hi, welcome to RIVA weather service. How can I help you?"

# Methods to show client
@app.route('/rivaWeather/')
def get_bot1():
    return send_from_directory("../ui/", "index.html")

@app.route('/rivaWeather/<file>', defaults={'path': ''})
@app.route('/rivaWeather/<path:path>/<file>')
def get_bot2(path, file):
    return send_from_directory("../ui/" + path, file)


@app.route('/get_new_user_conversation_index')
def get_newuser_conversation_index():
    return get_new_user_conversation_index()

# Audio source for TTS
@app.route('/audio/<int:user_conversation_index>/<int:post_id>')
def audio(user_conversation_index, post_id):
    if verbose:
        print(f'[Client Server] [{user_conversation_index}] audio speak: {post_id}')
    currentChatbot = get_chatbot(user_conversation_index)
    return Response(currentChatbot.get_tts_speech())

# Handles ASR audio transcript output
@app.route('/stream/<int:user_conversation_index>')
def stream(user_conversation_index):
    @stream_with_context
    def audio_stream():
        currentChatbot = get_chatbot(user_conversation_index)
        if currentChatbot:
            asr_transcript = currentChatbot.get_asr_transcript()
            for t in asr_transcript:
                yield t
        params = {'response': "Audio Works"}
        return params
    return Response(audio_stream(), mimetype="text/event-stream")


# Used for sending messages to the bot
@app.route( "/init", methods=['POST'])
def init():
    try:
        user_conversation_index = request.json['user_conversation_index']
    except KeyError:
        return jsonify(ok=False, message="Missing parameters.")
    try:
        create_chatbot(user_conversation_index, sio)  
        return jsonify(ok=True, messages=[VA_INIT_MESSAGE], debug=client_config["DEBUG"])
    except Exception as e:  # Error in execution
        print("[Client Server] " + str(e))
        return jsonify(ok=False, message="Error during execution.")
    

# Used for sending messages to the bot
@app.route( "/", methods=['POST'])
def get_input():
    try:
        text = request.json['text']
        bot = request.json['bot'].lower()
        user_conversation_index = request.json['user_conversation_index']
    except KeyError:
        return jsonify(ok=False, message="Missing parameters.")
    if user_conversation_index:
        create_chatbot(user_conversation_index, sio)
        currentChatBot = get_chatbot(user_conversation_index)
        try:
            response_text = currentChatBot.rasa_tts_pipeline(text)    
            if verbose:
                print(f"[Client Server] [{user_conversation_index}] Response from RASA/Riva NLP and RASA DM: {response_text}")
            return jsonify(ok=True, messages=[response_text], debug=client_config["DEBUG"])
        except Exception as e:  # Error in execution
            print("[Client Server] " + str(e))
            return jsonify(ok=False, message="Error during execution.")
    else:
        print("[Client Server] user_conversation_index not found")
        return jsonify(ok=False, message="user_conversation_index not found")


# Writes audio data to ASR buffer
@sio.on('audio_in', namespace='/')
def receive_remote_audio(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.asr_fill_buffer(data["audio"])


@sio.on('start_tts', namespace='/')
def start_tts(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.start_tts()


@sio.on('stop_tts', namespace='/')
def stop_tts(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.stop_tts()


@sio.on('pause_asr', namespace='/')
def pauseASR(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        if verbose:
            print(f"[Client Server] [{data['user_conversation_index']}] Pausing ASR requests.")
        currentChatbot.pause_asr()
        

@sio.on('unpause_asr', namespace='/')
def unpauseASR(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        if verbose:
            print(f"[Client Server] [{data['user_conversation_index']}] Attempt at Unpausing ASR requests on {data['on']}.")
        unpause_asr_successful_flag = currentChatbot.unpause_asr(data["on"])
        if unpause_asr_successful_flag == True:
            emit('onCompleteOf_unpause_asr', {'user_conversation_index': data["user_conversation_index"]}, broadcast=False)


@sio.on('pause_wait_unpause_asr', namespace='/')
def pause_wait_unpause_asr(data):
    currentChatbot = get_chatbot(data["user_conversation_index"])
    if currentChatbot:
        currentChatbot.pause_wait_unpause_asr()
        emit('onCompleteOf_unpause_asr',  {'user_conversation_index': data["user_conversation_index"]}, broadcast=False)


@sio.on("connect", namespace="/")
def connect():
    if verbose:
        print('[Client Server] Client connected')


@sio.on("disconnect", namespace="/")
def disconnect():
    if verbose:
        print('[Client Server] Client disconnected')
