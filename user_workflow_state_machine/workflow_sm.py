from .state import (
    StateInterface,
    AuthenticatedState,
    BrowsingState,
    RemoveFromCart,
    UnauthenticatedState,
    TerminalState,
    EntryState,
    ViewProductState,
    AddToCartState,
)
from collections import deque
import random
import uuid


class UserWorkflowStateMachine:
    def __init__(self, handlers):
        self.state_mappings = {
            EntryState: {
                "states": [AuthenticatedState],
                "on_process": getattr(handlers, "on_process_entry", None),
            },
            AuthenticatedState: {
                "states": [BrowsingState],
                "on_process": getattr(handlers, "on_process_authenticate", None),
            },
            BrowsingState: {
                "states": [
                    BrowsingState,
                    ViewProductState,
                    UnauthenticatedState,
                ],
                "on_process": getattr(handlers, "on_process_browsing", None),
            },
            ViewProductState: {
                "states": [
                    BrowsingState,
                    ViewProductState,
                    UnauthenticatedState,
                    AddToCartState,
                    RemoveFromCart,
                ],
                "on_process": getattr(handlers, "on_process_view_product", None),
            },
            AddToCartState: {
                "states": [
                    BrowsingState,
                    ViewProductState,
                    UnauthenticatedState,
                    RemoveFromCart,
                ],
                "on_process": getattr(handlers, "on_process_add_to_cart", None),
            },
            RemoveFromCart: {
                "states": [
                    BrowsingState,
                    UnauthenticatedState,
                ],
                "on_process": getattr(handlers, "on_process_remove_from_cart", None),
            },
            UnauthenticatedState: {
                "states": [TerminalState],
                "on_process": getattr(handlers, "on_process_unauthenticated", None),
            },
            TerminalState: {
                "states": [],
                "on_process": getattr(handlers, "on_process_terminal", None),
            },
        }

    async def handle(self) -> StateInterface:
        # used for propagation
        self.context_id = uuid.uuid4()

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
                await state_obj.on_process(self.context_id)
                break
            await state_obj.on_process(self.context_id)
            next_states = [
                state_objs_mapper[state.__name__] for state in state_obj.next_states
            ]
            queue.extend(random.choices(next_states))

        return state_obj
