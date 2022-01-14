import aiounittest

from botbuilder.core import TurnContext
from botbuilder.core.adapters import TestAdapter

from helpers.luis_helper import LuisHelper

from flight_booking_recognizer import FlightBookingRecognizer

from config import DefaultConfig


async def _test_LUIS_entity(phrase, expected, attribute):
    CONFIG = DefaultConfig()
    luis_recognizer = FlightBookingRecognizer(CONFIG)
    async def exec_LUIS(turn_context:TurnContext):
        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            luis_recognizer, turn_context
        )
        await turn_context.send_activity(getattr(luis_result, attribute))
        return luis_result

    adapter = TestAdapter(exec_LUIS)
    
    step = await adapter.send(phrase)
    await step.assert_reply(expected)
        
class LUIS_Test(aiounittest.AsyncTestCase):
    async def test_LUIS_intent(self):    
        CONFIG = DefaultConfig()
        luis_recognizer = FlightBookingRecognizer(CONFIG)
    
        async def exec_LUIS(turn_context:TurnContext):
            # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
            intent, luis_result = await LuisHelper.execute_luis_query(
                luis_recognizer, turn_context
            )
            await turn_context.send_activity(intent)
            return intent
    
        adapter = TestAdapter(exec_LUIS)
        step = await adapter.send("hello")
        await step.assert_reply("None")
    
        step = await adapter.send("i want to go to paris")
        await step.assert_reply("book")
    

    async def test_LUIS_entity_or_city(self):
        await _test_LUIS_entity("i want to go from paris to berlin the 2nd of September, 2022", "Paris", "origin")
    
    async def test_LUIS_entity_dest_city(self):
        await _test_LUIS_entity("i want to go from paris to berlin the 2nd of September, 2022", "Berlin", "destination")
        
    async def test_LUIS_entity_start_date(self):
        await _test_LUIS_entity("i want to go from paris to berlin the 2nd of September, 2022", "2022-09-02", "start_travel_date")
        
    async def test_LUIS_entity_end_date(self):
        await _test_LUIS_entity("i want to go from paris to berlin from the 2nd of september, 2022 and come back the 11/3/2022", "2022-11-03", "end_travel_date")
        
    async def test_LUIS_entity_budget(self):
        await _test_LUIS_entity("i want to go from paris to berlin the 2nd of September, 2022 with a budget of $800", "$ 800", "budget")
    