from user_activity_state_machine.uasm import UASM
from user_activity_state_machine.state import TerminalState


def test_uasm():
    uasm = UASM()
    out_state = uasm.handle()
    assert isinstance(out_state, TerminalState)
