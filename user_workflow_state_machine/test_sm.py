from user_workflow_state_machine.workflow_sm import UserWorkflowStateMachine
from user_workflow_state_machine.state import TerminalState


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
    sm = UserWorkflowStateMachine(
        on_process_entry=_on_process_entry,
        on_process_authenticate=_on_process_authenticate,
        on_process_browsing=_on_process_browsing,
        on_process_unauthenticated=_on_process_unauthenticated,
        on_process_terminal=_on_process_terminal,
    )
    out_state = sm.handle()
    assert isinstance(out_state, TerminalState)
