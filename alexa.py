import psycopg2
import json
import collections
import datetime
import sys
import numpy as np
import ast

from extractdata import *

class alexa_skill:

    def speak_populardestinations(self,list_destinations):
        session_attributes = {}
        card_title = "Popularity"
        reprompt_text = ""
        should_end_session = True

        dest_String = ",".join(list_destinations)

        speech_output = "The most popular destinations are " + dest_String

        return self.build_response(session_attributes, self.build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    def build_speechlet_response(self,title, output, reprompt_text, should_end_session):
        return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
        }

    def build_response(self,session_attributes, speechlet_response):
        return {
            "version": "1.0",
            "sessionAttributes": session_attributes,
            "response": speechlet_response
        }

def __init__(self):
        print ("in init")
