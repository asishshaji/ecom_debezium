from .state import StateInterface, AuthenticatedState, BrowsingState, UnauthenticatedState, TerminalState, EntryState
from collections import deque
import random


class UserWorkflowStateMachine:
    def __init__(
        self,
        on_process_entry=None,
        on_process_authenticate=None,
        on_process_browsing=None,
        on_process_unauthenticated=None,
        on_process_terminal=None,
    ):
        self.state_mappings = {
            EntryState: {
                "states": [AuthenticatedState],
                "on_process": on_process_entry,
            },
            AuthenticatedState: {
                "states": [BrowsingState],
                "on_process": on_process_authenticate,
            },
            BrowsingState: {
                "states": [BrowsingState, UnauthenticatedState],
                "on_process": on_process_browsing,
            },
            UnauthenticatedState: {
                "states": [TerminalState],
                "on_process": on_process_unauthenticated,
            },
            TerminalState: {
                "states": [],
                "on_process": None,
            },
        }

    def handle(self) -> StateInterface:
        state_objs_mapper = {}
        for state, info in self.state_mappings.items():
            state_objs_mapper[state.__name__] = state(
                next_states=info["states"], on_process=info["on_process"]
            )

        start_state_obj = state_objs_mapper[EntryState.__name__]

        queue = deque([start_state_obj])
        state_obj = None

        # bfs traversal
        while queue:
            state_obj = queue.popleft()
            # sentinal
            if isinstance(state_obj, TerminalState):
                break
            state_obj.on_process()
            next_states = [
                state_objs_mapper[state.__name__] for state in state_obj.next_states
            ]
            queue.extend(random.choices(next_states))

        return state_obj
