from user_activity_state_machine.uasm import UASM
from user_activity_state_machine.state import TerminalState


def _on_process_authenticate():
    print("Processing authentication...")


def _on_process_browsing():
    print("Processing browsing...")


def _on_process_unauthenticated():
    print("Processing unauthenticated state...")


def _on_process_terminal():
    print("Processing terminal state...")


def _on_process_entry():
    print("Processing entry state...")


def test_uasm():
    uasm = UASM(
        on_process_entry=_on_process_entry,
        on_process_authenticate=_on_process_authenticate,
        on_process_browsing=_on_process_browsing,
        on_process_unauthenticated=_on_process_unauthenticated,
        on_process_terminal=_on_process_terminal,
    )
    out_state = uasm.handle()
    assert isinstance(out_state, TerminalState)
