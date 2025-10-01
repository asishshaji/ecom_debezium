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
import random
import time


class StateInterface(ABC):
    def __init__(self, next_states=None):
        self.next_states: list[Type["StateInterface"]] = next_states or []

    @abstractmethod
    def _on_process(self):
        pass

    @abstractmethod
    def next_state(self, action: Action):
        # based on the action, return the next state
        pass


class EntryState(StateInterface):
    def __init__(self):
        super().__init__([AuthenticatedState])

    def _on_process(self):
        print("Entry state")

    def next_state(self, action: Action) -> StateInterface:
        self._on_process()
        return random.choice(self.next_states)()


class AuthenticatedState(StateInterface):
    def __init__(self):
        super().__init__([BrowsingState])

    def _on_process(self):
        print("authenticating user")
        time.sleep(2)

    def next_state(self, action: Action) -> StateInterface:
        self._on_process()
        return random.choice(self.next_states)()


class BrowsingState(StateInterface):
    def __init__(self):
        super().__init__([BrowsingState, UnauthenticatedState])

    def _on_process(self):
        print("user is browsing")
        time.sleep(1)

    def next_state(self, action: Action) -> StateInterface:
        self._on_process()
        return random.choice(self.next_states)()


class UnauthenticatedState(StateInterface):
    def __init__(self):
        super().__init__([TerminalState])

    def _on_process(self):
        print("user is logging out")

    def next_state(self, action: Action) -> StateInterface:
        self._on_process()
        return random.choice(self.next_states)()


class TerminalState(StateInterface):
    def __init__(self):
        super().__init__([])

    def _on_process(self):
        print("Reached terminal state. Exiting.")

    def next_state(self, action: Action) -> StateInterface:
        return self
