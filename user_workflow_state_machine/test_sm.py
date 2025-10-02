from user_workflow_state_machine.workflow_sm import UserWorkflowStateMachine
from user_workflow_state_machine.state import TerminalState


class MockHandlers:
    def on_process_entry(self):
        print("Processing entry state...")

    def on_process_authenticate(self):
        print("Processing authentication...")

    def on_process_browsing(self):
        print("Processing browsing...")

    def on_process_unauthenticated(self):
        print("Processing unauthenticated state...")

    def on_process_terminal(self):
        print("Processing terminal state...")

    def on_process_view_product(self):
        print("Processing view product state...")

    def on_process_add_to_cart(self):
        print("Processing add to cart...")

    def on_process_remove_from_cart(self):
        print("Processing remove from cart...")


def test_uasm():
    sm = UserWorkflowStateMachine(handlers=MockHandlers())
    out_state = sm.handle()

    assert isinstance(out_state, TerminalState)
