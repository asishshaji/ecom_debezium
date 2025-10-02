import pytest

from user_workflow_state_machine.workflow_sm import UserWorkflowStateMachine
from user_workflow_state_machine.state import TerminalState


class MockHandlers:
    async def on_process_entry(self, _):
        print("Processing entry state...")

    async def on_process_authenticate(self, _):
        print("Processing authentication...")

    async def on_process_browsing(self, _):
        print("Processing browsing...")

    async def on_process_unauthenticated(self, _):
        print("Processing unauthenticated state...")

    async def on_process_terminal(self, _):
        print("Processing terminal state...")

    async def on_process_view_product(self, _):
        print("Processing view product state...")

    async def on_process_add_to_cart(self, _):
        print("Processing add to cart...")

    async def on_process_remove_from_cart(self, _):
        print("Processing remove from cart...")


@pytest.mark.asyncio
async def test_uasm():
    sm = UserWorkflowStateMachine(handlers=MockHandlers())
    out_state = await sm.handle()

    assert isinstance(out_state, TerminalState)
