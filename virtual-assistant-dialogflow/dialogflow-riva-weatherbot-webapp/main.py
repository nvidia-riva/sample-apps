# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import os, sys

root_folder = (os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(root_folder)

from config import client_config

if __name__ == '__main__':
    if client_config["CLIENT_APPLICATION"] == "WEBAPPLICATION":
        from client.webapplication.start_web_application import start_web_application
        start_web_application()