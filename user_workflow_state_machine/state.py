from abc import abstractmethod
from abc import ABC
from typing import Type


class StateInterface(ABC):
    def __init__(self, next_states=None, on_process=None):
        self.next_states: list[Type["StateInterface"]] = next_states or []
        self.on_process = on_process


class EntryState(StateInterface):
    pass


class AuthenticatedState(StateInterface):
    pass


class BrowsingState(StateInterface):
    pass


class ViewProductState(StateInterface):
    pass


class AddToCartState(StateInterface):
    pass


class RemoveFromCart(StateInterface):
    pass


class UnauthenticatedState(StateInterface):
    pass


class TerminalState(StateInterface):
    pass
