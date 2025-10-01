from .state import StateInterface
from .state import EntryState
from .state import TerminalState
from .action import Action


class UASM:
    def __init__(self):
        self.state: StateInterface = EntryState()

    def handle(self) -> StateInterface:
        while not isinstance(self.state, TerminalState):
            self.state = self.state.next_state(action=Action.LOGIN)
        return self.state
