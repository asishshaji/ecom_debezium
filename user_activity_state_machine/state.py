from abc import ABC
from typing import Type


class StateInterface(ABC):
    def __init__(self, next_states=None, on_process=None):
        self.next_states: list[Type["StateInterface"]] = next_states or []
        self.on_process = on_process


class EntryState(StateInterface):
    def __init__(self, next_states, on_process):
        super().__init__(next_states, on_process)


class AuthenticatedState(StateInterface):
    def __init__(self, next_states, on_process):
        super().__init__(next_states, on_process)


class BrowsingState(StateInterface):
    def __init__(self, next_states, on_process):
        super().__init__(next_states, on_process)


class UnauthenticatedState(StateInterface):
    def __init__(self, next_states, on_process):
        super().__init__(next_states, on_process)


class TerminalState(StateInterface):
    def __init__(self, next_states, on_process):
        super().__init__(next_states, on_process)
