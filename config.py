#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "a54c942f-acda-4428-9021-473a593b70ee")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "wau7Q~~gHGKdFRQHID1g1pWvvmyirzsq-ZGWd")
    LUIS_APP_ID = os.environ.get("LuisAppId", "4298d232-9a94-4f16-946a-1027d351324c")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "54013f61d4224fbebad640b96592ec3d")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "68be6074-0632-4076-b87a-a3a83f47f6e3"
    )
