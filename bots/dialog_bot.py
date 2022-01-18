# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Implements bot Activity handler."""

from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    UserState,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
    Severity
)
from botbuilder.dialogs import Dialog, DialogExtensions, DialogInstance, DialogState
from booking_details import BookingDetails
from helpers.dialog_helper import DialogHelper

def _get_diag_object(dialog, myTexts):
    if hasattr(dialog, 'state'):
        if("options" in dialog.state.keys()):
            if(dialog.state["options"] is not None):
                if(hasattr(dialog.state["options"], "prompt")):
                    myTexts.append("Bot: "+dialog.state["options"].prompt.text)
                # elif(isinstance(dialog.state["options"], BookingDetails)):
                #     dialogs = ["User: "+user_dialog for user_dialog in dialog.state["options"].dialogs]
                #     myTexts.extend(dialogs)
        else:
            for key in dialog.state.keys():
                if hasattr(dialog.state[key], 'dialog_stack'):
                    for diag in dialog.state[key].dialog_stack: # this is a dialogInstance that can contain a state
                        _get_diag_object(diag, myTexts)                        
    return
    
class DialogBot(ActivityHandler):
    """Main activity handler for the bot."""

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
        telemetry_client: BotTelemetryClient,
    ):
        if conversation_state is None:
            raise Exception(
                "[DialogBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        self.telemetry_client = telemetry_client
        
    async def on_message_activity(self, turn_context: TurnContext):
        turn_context.responses.append("user: "+turn_context.activity.text.lower())
        await DialogExtensions.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )
        responses = []
        _get_diag_object(turn_context.turn_state["Internal.ConversationState"], responses)
        responses = [resp.lower() for resp in responses]
        turn_context.responses.extend(responses)
        # Save any state changes that might have occured during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        if(not hasattr(self.conversation_state, "responses")):
            self.conversation_state.responses = turn_context.responses
        else:
            self.conversation_state.responses.extend(turn_context.responses)
        if("user: no" in self.conversation_state.responses):
            self.telemetry_client.track_trace(name="not-understood-trace",
                                              properties={"log":"\n".join(self.conversation_state.responses[-1])},
                                              severity=Severity.error)
            self.conversation_state.responses = [self.conversation_state.responses[-1],]
        await self.user_state.save_changes(turn_context, False)

    @property
    def telemetry_client(self) -> BotTelemetryClient:
        """
        Gets the telemetry client for logging events.
        """
        return self._telemetry_client

    # pylint:disable=attribute-defined-outside-init
    @telemetry_client.setter
    def telemetry_client(self, value: BotTelemetryClient) -> None:
        """
        Sets the telemetry client for logging events.
        """
        if value is None:
            self._telemetry_client = NullTelemetryClient()
        else:
            self._telemetry_client = value
