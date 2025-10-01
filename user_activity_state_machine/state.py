# AUTHENTICATED = "AUTHENTICATED"
# BROWSING = "BROWSING"
# ORDER_PLACED = "ORDER_PLACED"
# CHECKOUT = "CHECKOUT"
# ORDER_PLACED = "ORDER_PLACED"
# CANCELLED = "CANCELLED"
# UNAUTHENTICATED = "UNAUTHENTICATED"

from action import Action
from abc import ABC
from abc import abstractmethod
from typing import Type


class StateInterface(ABC):
    def __init__(self):
        self.next_states: list[Type["StateInterface"]] = []

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def next_state(self, action: Action):
        # based on the action, return the next state
        pass


class AuthenticatedState(StateInterface):
    def __init__(self):
        super.__init__()
        self.next_states : list[StateInterface] = [BrowsingState]

    def process(self):
        pass

    def next_state(self, action: Action) -> StateInterface:
        pass


class BrowsingState(StateInterface):
    def __init__(self):
        super.__init__()
        self.next_states : list[StateInterface] = [BrowsingState, UnauthenticatedState]

    def process(self):
        pass

    def next_state(self, action: Action) -> StateInterface:
        pass


class UnauthenticatedState(StateInterface):
    def __init__(self):
        super.__init__()
        self.next_states : list[StateInterface] = [AuthenticatedState]

    def process(self):
        pass

    def next_state(self, action: Action) -> StateInterface:
        pass
