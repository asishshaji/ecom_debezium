from state import EntryState
from state import StateInterface
from state import UnauthenticatedState
from action import Action


class UASM:
    def __init__(self):
        self.state: StateInterface = EntryState()

    def handle(self):
        while not isinstance(self.state, UnauthenticatedState):
            self.state = self.state.next_state(action=Action.LOGIN)

        self.state.next_state(action = None)
