# Virtual Assistant (with Rasa)

This Virtual Assistant (with Rasa) sample application demonstrates the integration of Rasa and the Riva Speech Service in the form
of a weather chatbot web application. This sample is available in two options:

**Option 1:** Riva ASR + Riva TTS + Riva NLP + Rasa dialog manager

**Option 2:** Riva ASR + Riva TTS + Rasa NLU + Rasa dialog manager

To learn more about Rasa, follow [this link](https://rasa.com/).

## Demo Video

To see how the Riva weather chatbot service works, the demo video can be found [here](https://youtu.be/YCuilEpmlFI).

## Implementation

At a high-level, the integration takes advantage of the native API support of Rasa and gRPC support of Riva. The Weatherbot Client
coordinates the workflow with Riva Services and Rasa, then interacts with the end-user via a web UI.

- Container 1: Riva AI Services

  > - Exposes Speech Services (ASR/NLP/TTS) over gRPC endpoints
  > - Needs a GPU

- Container 2: Riva Samples' Riva-Rasa Chatbot

  > - Functionality
  >
  >   > - Exposes Rasa functionality over API endpoints. Responsible for dialog management with Rasa as well as NLP with Riva or
  >   >   NLU with Rasa
  >   > - Contains the Weatherbot Client application (web UI and web service)
  >
  > - Rasa
  >
  >   > - Up to two instances
  >   >
  >   >   > 1. Rasa Server
  >   >   > 2. Rasa Action (if applicable)
  >   >
  >   > - Does not need GPUs but can be deployed on GPUs for performance
  >
  > - Weatherbot Client
  >
  >   > - Includes the Riva Python library installed
  >   > - Communicates with Riva AI Services and Rasa over gRPC and REST API endpoints respectively
  >   > - Pipelines ASR, NLP, TTS, and dialog manager functionalities
  >   > - Does not need GPUs

### Architecture

```{image} img/riva-nlp.png
:alt: Riva ASR + Riva TTS + Riva NLP + Rasa dialog manager
:width: 800
```

```{image} img/rasa-nlu.png
:alt: Riva ASR + Riva TTS + Rasa NLU + Rasa dialog manager
:width: 800
```

### Code Structure

This section shows the high-level code structure of the Weatherbot Client (in Riva Samples' Riva-Rasa Chatbot).

- `asr.py`

  > - This file contains the functionality to make the gRPC call to Riva ASR, using the Riva Python Client libraries, with the
  >   audio snippet, and returns the text transcript.
  > - ASR is used in streaming mode

- `rasa.py`

  > - This file contains the functionality to make an API call to Rasa, with the user input and sender ID, and returns a text
  >   response obtained by processing the Rasa response object.

- `tts.py` and `tts\_stream.py`

  > - These files contain the functionality to make the gRPC call to Riva TTS, using the Riva Python Client libraries, with a
  >   text snippet, and returns the corresponding audio speech.
  > - TTS can be used in either `Batch` or `Streaming` mode, depending on whether `tts.py` or `tts\_stream.py` is used. This
  >   can be set by changing the import statements in lines 12 and 13 in `virtual-assistant-rasa/rasa-riva-weatherbot-webapp/riva/chatbot/chatbot.py`.

- `chatbot.py`

  > - This file contains the `Chatbot` class which is responsible for pipelining all the ASR, TTS, and Rasa operations.
  >
  > - Creates one instance of the `Chatbot` class per conversation.
  >
  > - Pipeline is as follows:
  >
  >   > - ASR is used in `Streaming` mode, therefore, it's a background operation. By default, we are listening to the audio of
  >   >   the user who is speaking into the microphone.
  >   > - ASR calls Rasa with the transcribed text either automatically when the user stops talking (when the `AutoSubmit` flag is
  >   >   enabled) or when the **Submit** button is hit.
  >   > - When called, Rasa internally calls Riva NLP or Rasa NLU with the transcribed text to fetch the intents and slots which
  >   >   is then used by the Rasa dialog manager to get the final response text. The response text is returned.
  >   > - TTS is automatically called with Rasa's response text, if `System Speech` is not muted.
  >   > - TTS gets the audio snippet and plays it back to the user on the speakers.

(rasa-network-configuration)=

## Requirements and Setup

### Requirements:  
1. Python 3.6.9  

### Setup:  

1. Enter directory:  
``cd sample-apps/virtual-assistant-rasa``  

2. Create parent directory for all venvs:  
``mkdir pythonenvs``  
  
3. Install rasa venv libraries:  
``python3 -m venv pythonenvs/rasa``  
``. pythonenvs/rasa/bin/activate``  
``pip3 install -U pip``  
``pip3 install -r requirements_rasa.txt``  
``deactivate``  

4. Install client venv libraries:  
``python3 -m venv pythonenvs/client``  
``. pythonenvs/client/bin/activate``
``pip3 install -U pip``  
	4.1. Install Riva client libraries:  
		``cd /home/nsrihari/Riva/QSG/``  
		``cd riva_quickstart_v2.0.0``  
		``pip install riva_api-2.0.0-py3-none-any.whl``  
	4.2. Install other libraries  
	``pip3 install -r requirements_client.txt``
``deactivate``


## Running the Demo

1. Start the Riva Speech Server. Follow the steps in the {ref}`quick_start_guide`.
2. Clone Riva Sample Apps repo:
`` git clone https://github.com/nvidia-riva/sample-apps.git``
``cd sample-apps/virtual-assistant-rasa``

3. Modify the API endpoint setting:
There are two locations in the code base that have to be configured for inter-service communication:

1. `rasa-weatherbot/endpoints.yml`

   ```
   # uncomment and populate the section below
   action_endpoint:
       url: "http://[rasa server host IP]:5055/webhook"
   ```

   For example:

   ```
   # uncomment and populate the section below
   action_endpoint:
       url: "http://10.20.30.40:5055/webhook"
   ```

2. `config.py`

   ```
   # uncomment and populate the section below
   riva_config = {
       ...
       "RIVA_SPEECH_API_URL": "[riva speech service host IP]:50051",
       ...
   }

   # uncomment and populate the section below
   rasa_config = {
       ...
       "RASA_API_URL": "[rasa server host IP]:5005",
       ...
   }
   ```

   In the case where one is using `localhost` the `[rasa server host IP]` must be set to the local machine's IP, instead
   of `localhost`.

   If the Riva Service, Rasa server, and the Weatherbot Client are all running on the same machine, it would be:

   ```
   # uncomment and populate the section below
   riva_config = {
       ...
       "RIVA_SPEECH_API_URL": "10.20.30.40:50051",
       ...

   # uncomment and populate the section below
   rasa_config = {
       ...
       "RASA_API_URL": "10.20.30.40:5005",
       ...
   ```

   If the Riva Service runs on a GPU that is supported by a remote machine, and Rasa and the Weatherbot Client are running on a
   local machine, it would be:

   ```
   # uncomment and populate the section below
   riva_config = {
       ...
       "RIVA_SPEECH_API_URL": "10.20.30.40:50051",
       ...

   # uncomment and populate the section below
   rasa_config = {
       ...
       "RASA_API_URL": "20.40.60.80:5005",
       ...
   ```
3. Start the Rasa Action server.

      1. Open the `config.py` script. In the dictionary on the right side of the `riva_config` variable, update the `WEATHERSTACK_ACCESS_KEY` field with your Weatherstack API key.  A new Weatherstack API key can be obtained [here](https://weatherstack.com/).

      2. Activate the Rasa Python environment.

         ```
         . pythonenvs/rasa/bin/activate
         ```

      3. Navigate to the `rasa-weatherbot` directory.

         ```
         cd rasa-weatherbot
         ```

      4. Run the Rasa Action server.

         ```
         rasa run actions --actions actions
         ```

4. Start the Rasa server in a different terminal.

      1. Activate the Rasa Python environment.

         ```
         . pythonenvs/rasa/bin/activate
         ```

      2. Navigate to the `rasa-weatherbot` directory.

         ```
         cd rasa-weatherbot
         ```

      3. Run the Rasa training.

         - For Riva NLP: Train the Rasa Core model.

           ```
           rasa train -c config/config_rivanlp.yml \
               -d domain/domain_rivanlp.yml \
               --out models/models_rivanlp/ \
               --data data/nlu_rivanlp.yml \
               data/rules_rivanlp.yml \
               data/stories_rivanlp.yml
           ```

         - For Rasa NLU: Train the Rasa NLU and Rasa Core models.

           ```
           rasa train -c config/config_rasanlp.yml \
               -d domain/domain_rasanlp.yml \
               --out models/models_rasanlp/ \
               --data data/nlu_rasanlp.yml \
               data/rules_rasanlp.yml data/stories_rasanlp.yml
           ```

      4. Run the Rasa server.

         - For Riva NLP.

           ```
           rasa run -m models/models_rivanlp/ --enable-api \
               --log-file out.log --endpoints endpoints.yml
           ```

         - For Rasa NLU.

           ```
           rasa run -m models/models_rasanlp/ --enable-api \
               --log-file out.log --endpoints endpoints.yml
           ```

5. Start the Riva Chatbot server.

      1. Activate the Chatbot Client Python environment.

         ```
         . pythonenvs/client/bin/activate
         ```

      2. Navigate to the `rasa-riva-weatherbot-webapp` directory.

         ```
         cd rasa-riva-weatherbot-webapp
         ```

      3. Starting the Chatbot Client server.

         ```
         python3 main.py
         ```

        4. Open the web UI on a web browser.

        ```
        https://[riva chatbot server host IP]:5555/rivaWeather
        ```

        For example:

        ```
        [https://0.0.0.0:5555/rivaWeather](https://0.0.0.0:5555/rivaWeather)
        ```

## Sample Conversations

### Rasa NLU: Sample 1

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** How's the weather?

**Virtual Assistant:** For which location?

**User:** In Seattle.

**Virtual Assistant:** It is Haze, Smoke in Seattle at the moment. The temperature is 31 degrees, the humidity is 30 percent and the
wind speed is 20 miles per hour.

### Rasa NLU: Sample 2

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** How's the weather in Paris?

**Virtual Assistant:** It is Clear in Paris at the moment. The temperature is 20 degrees, the humidity is 73 percent and the wind
speed is 9 miles per hour.

### Rasa NLU: Sample 3

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** hi

**Virtual Assistant:** Hey! How are you?

**User:** who are you?

**Virtual Assistant:** I am a bot, powered by Rasa.

### Rasa NLU: Sample 4

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** Good Morning

**Virtual Assistant:** Hey! How are you?

**User:** I am doing great

**Virtual Assistant:** Great, carry on!

**User:** See you around

**Virtual Assistant:** Bye

### Riva NLP: Sample 1

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** How's the weather?

**Virtual Assistant:** For which location?

**User:** In Seattle.

**Virtual Assistant:** It is Haze, Smoke in Seattle at the moment. The temperature is 31 degrees, the humidity is 30 percent and the
wind speed is 20 miles per hour.

### Riva NLP: Sample 2

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** How's the weather in Paris?

**Virtual Assistant:** It is Clear in Paris at the moment. The temperature is 20 degrees, the humidity is 73 percent and the wind
speed is 9 miles per hour.

### Riva NLP: Sample 3

**Virtual Assistant:** Hi, welcome to RIVA weather service. How can I help you?

**User:** Is it raining in Austin?

**Virtual Assistant:** The precipitation is 0.4 inches in Austin at the moment.

**User:** What is the temperature in Toronto today?

**Virtual Assistant:** It is 4 degree celsius in Toronto at the moment.

## Limitations

- The provided samples are not complete virtual assistants, but are intended as simple examples of how to build basic task-oriented
  chatbots with Riva.  Consequently, the intent classifier and slot filling models have been trained with small amounts of data
  and are not expected to be highly accurate.
- The Rasa virtual assistant sample supports intents for weather, temperature, rain, humidity, sunny, cloudy and snowfall checks. It
  does not support general conversational queries or other domains.
- Both the Riva NLP and Rasa NLU samples support only 1 slot for city. Neither takes into account the day associated with the query.
- Although the Rasa servers and the chatbot servers can be hosted on different machines, the provided code does not support
  independent scaling of the servers.
- These samples support up to four concurrent users. This restriction is not because of Riva, but because of the web framework
  (Flask and Flask-ScoketIO) that is being used. The socket connection to stream audio to (TTS) and from (ASR) the user is unable to
  sustain more than four concurrent socket connections.
- The Rasa virtual assistant is not optimized for low latency in case of multiple concurrent users.
- Some erratic issues have been observed with the Rasa sample on the Firefox browser.  The most common issue is the TTS output being
  taken in as input by ASR for certain microphone gain values.

## License

For applicable licenses, refer to the {ref}`license` section.
