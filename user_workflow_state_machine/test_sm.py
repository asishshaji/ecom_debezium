from user_workflow_state_machine.workflow_sm import UserWorkflowStateMachine
from user_workflow_state_machine.state import TerminalState


def test_uasm():
    sm = UserWorkflowStateMachine(
        on_process_entry=lambda: print("Processing entry state..."),
        on_process_authenticate=lambda: print("Processing authentication..."),
        on_process_browsing=lambda: print("Processing browsing..."),
        on_process_unauthenticated=lambda: print("Processing unauthenticated state..."),
        on_process_terminal=lambda: print("Processing terminal state..."),
        on_process_view_product=lambda: print("Processing view product state..."),
        on_process_add_to_cart=lambda: print("Processing add to cart"),
        on_process_remove_from_cart=lambda: print("Processing remove from cart"),
    )
    out_state = sm.handle()
    assert isinstance(out_state, TerminalState)
