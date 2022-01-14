# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from recognizers_date_time import recognize_datetime
from recognizers_text import Culture
from datatypes_date_time.timex import Timex

from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "book"
    CANCEL = "Cancel"
    NONE_INTENT = "None"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)

def _find_datetime(recognizer_result, date_label):
    recognizer_result.entities[date_label][0]
    return

class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "dst_city", []
                )
                if len(to_entities) > 0:
                    dst_city = to_entities[0]["text"].capitalize()
                    if "dst_city" in recognizer_result.entities.keys():
                        result.destination = dst_city
                    else:
                        result.unsupported_airports.append(dst_city)

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "or_city", []
                )
                if len(from_entities) > 0:
                    or_city = from_entities[0]["text"].capitalize()
                    if "or_city" in recognizer_result.entities.keys():
                        result.origin = or_city
                    else:
                        result.unsupported_airports.append(or_city)
                        
                        
                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "budget", []
                )
                if len(from_entities) > 0:
                    result.budget = from_entities[0]["text"].capitalize()

                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                date_entities = recognizer_result.entities.get("str_date", [])
                result.start_travel_date = None
                if len(date_entities)>0:
                    timex = recognize_datetime(date_entities[0], Culture.English)[0].resolution["values"][0]["timex"]
                    if timex:
                        datetime = timex.split("T")[0]
                        # We have a Date we just need to check it is unambiguous.
                        if "definite" in Timex(timex).types:
                            result.start_travel_date = datetime
                
                date_entities = recognizer_result.entities.get("end_date", [])
                result.end_travel_date = None
                if len(date_entities)>0:
                    timex = recognize_datetime(date_entities[0], Culture.English)[0].resolution["values"][0]["timex"]
                    if timex:
                        datetime = timex.split("T")[0]
                        # We have a Date we just need to check it is unambiguous.
                        if "definite" in Timex(timex).types:
                            result.end_travel_date = datetime

        except Exception as exception:
            print(exception)

        return intent, result
