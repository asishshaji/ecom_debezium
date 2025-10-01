from state import (
    StateInterface,
    BrowsingState,
    AuthenticatedState,
    UnauthenticatedState,
)
from action import Action


class UASM:
    def __init__(self):
        self.state: StateInterface = UnauthenticatedState

    def handle(self, action: Action):
        pass
