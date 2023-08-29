# Weather Virtual Assistant Example

## Overview

The Virtual Assistant (VA) sample demonstrates how to use NVIDIA NeMo LLM along with Riva AI Services to build a simple but complete conversational AI application. It demonstrates receiving input via speech from the user, interpreting the query via an intention recognition and slot filling approach, leveraging the NeMo LLM to generate a natural sounding human-like response, and speaking this back to the user in a natural voice.

## Prerequisites

- This demo uses NVIDIA Riva to support Speech AI capabilities like Automatic Speech Recognition (ASR) and Text-to-Speech (TTS). To run NVIDIA Riva Speech AI services, please ensure you have the pre-requisites mentioned [here](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html#data-center).
- For running this sample application, you'll need: 
    - Access to the [OpenAI platform](https://platform.openai.com/). You will require your [OpenAI API key](https://platform.openai.com/account/api-keys) to access the service through the API in this sample application.
    - A Linux x86_64 environment with [pip](https://pypi.org/project/pip/) and Python 3.8+ installed.
    - The [weatherstack API access key](https://weatherstack.com/documentation). The VA uses weatherstack for weather fulfillment, that is when the weather intents are recognized, the real-time weather information is fetched from weatherstack. Sign up to the free tier of [weatherstack](https://weatherstack.com/), and get your API access key.
    - A microphone and speaker (for example, a Logitech H390 USB Computer Headset) to communicate with the app.


### Setup

1. Clone the NVIDIA Riva Sample Apps repo.

2. Enter the home directory of the Virtual Assistant ChatGPT sample app:
```bash
cd /path/to/sample-apps/virtual-assistant-chatgpt
```

3. Create and enable a Python [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment). For example:
```
python3 -m venv apps-env
source apps-env/bin/activate
```

After activating, checking the Python version should reveal the one you created the environment with. For example:
```
python3 --version
```
*Python 3.8.10*


4. Install the libraries necessary for the virtual assistant, including the Riva client library:
    1. Install the Riva client library.
		```
		pip install nvidia-riva-client
		```
	2. Install weatherbot web application dependencies. `requirements.txt` captures all Python dependencies needed for weatherbot web application.
        ```bash
        pip install -r requirements.txt # Tested with Python 3.8
        ```
    3. Install the OpenAI Client library
        ```bash
        pip install openai
        ```

### Running the demo
1.  Start the Riva Speech Server, if not already done. Follow the steps in the [Riva Quick Start Guide](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html). This will allow Speech AI capabilities which are required for the demo. **Note the IP & port** where the Riva server is running. By default it will run at IP:50051

2. Edit the configuration file [config.py](./config.py)
    1. In `riva_config` set:
        * The Riva speech server URL. This is the endpoint where the Riva services can be accessed.
        * The [weatherstack API access key](https://weatherstack.com/documentation). The VA uses weatherstack for weather fulfillment, that is when the weather intents are recognized, real-time weather information is fetched from weatherstack. Sign up to the free tier of [weatherstack](https://weatherstack.com/), and get your API access key.
    2. In `llm_config` set:
        * The OpenAI API Access key
        * (Optionally) you can also choose the GPT model to use. By default, 
        this is set to "gpt-3.5-turbo", but check out 
        https://platform.openai.com/docs/models for more options.

The code snippets will look like the example below.
```python3
riva_config = {
  "RIVA_SPEECH_API_URL": "<IP>:<PORT>", # Replace the IP & port with your hosted Riva endpoint
   ...
  "WEATHERSTACK_ACCESS_KEY": "<API_ACCESS_KEY>",  # Get your access key at - https://weatherstack.com/
   ...
}
...
llm_config = {
    ...
    "API_MODEL_NAME":"gpt-3.5-turbo",
    "API_KEY": "<OPENAI_API_ACCESS_KEY>" # Get your access key at https://platform.openai.com/account/api-keys
    ...
}
```

3. Run the virtual assistant application
```bash
python3 main.py
```

4. Open the browser to **https://IP:8009/rivaWeather**, where the IP is for the machine where the application is running. For instance, go to <https://127.0.0.1:8009/rivaWeather/> if the app is running in your local machine.

5. Speak to the virtual assistant through your microphone or type-in your text, asking a weather related query. To hear back text-to-speech audio of the LLM response, click on "Unmute System Speech" on the right bottom corner of the UI.

`NOTE:` To learn about the call to the LLM Service, please refer to the `query_llm` method in `riva_local/chatbot/stateDM/Util.py`.

## Sample Use Cases
It is possible to ask the bot the following types of questions:

* What is the weather in Berlin?

* What is the weather?
    * For which location?

* What’s the weather like in San Francisco tomorrow?
    * What about in California City?

* What is the temperature in Paris on Friday?

* How hot is it in Berlin today?

* Is it currently cold in San Francisco?

* Is it going to rain in Detroit tomorrow?

* How much rain in Seattle?

* Will it be sunny next week in Santa Clara?

* Is it cloudy today?

* Is it going to snow tomorrow in Milwaukee?

* How much snow is there in Toronto currently?

* How humid is it right now?

* What is the humidity in Miami?

* What's the humidity level in San Diego?

## Limitations
* The sample supports intents for weather, temperature, rain, humidity, sunny, cloudy and snowfall checks. It does not support general conversational queries or other domains.
* The sample supports only 1 slot for city.
* The sample supports up to four concurrent users. This restriction is because of the web framework (Flask and Flask-SocketIO) that is being used. The socket connection is to stream audio to (TTS) and from (ASR); you are unable to sustain more than four concurrent socket connections.
* The chatbot application is not optimized for low latency in the case of multiple concurrent users.
* Some erratic issues have been observed with the chatbot sample on the Firefox browser. The most common issue is the TTS output being taken in as input by ASR for certain microphone gain values.

## License
The [NVIDIA Riva License Agreement](https://developer.nvidia.com/riva/ga/license) is included with the product. Licenses are also available along with the model application zip file. By pulling and using the Riva SDK container, downloading models, or using the sample applications here, you accept the terms and conditions of these licenses. <br>
