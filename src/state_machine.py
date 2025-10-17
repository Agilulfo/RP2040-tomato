from usr_button import LONG_PRESSED, SHORT_PRESSED
from tasks import Blinker, get_runner, get_task_registry
from colors import BLUE, GREEN


STATE_MACHINE = None


def get_state_machine():
    global STATE_MACHINE
    if STATE_MACHINE is None:
        STATE_MACHINE = StateMachine()
        STATE_MACHINE.start_from(states[WaitingState.ID])
    return STATE_MACHINE


class StateMachine:
    def start_from(self, state):
        self.current_state = state
        state.enter(None)

    def handle_events(self, events):
        for event in events:
            transition = self.current_state.handle_event(event)
            if transition:
                (next_state, options) = transition
                self.current_state.exit()
                next_state.enter(options)
                self.current_state = next_state


class WaitingState:
    ID = "waiting"

    def handle_event(self, event):
        if event == SHORT_PRESSED:
            return (states[TomatoReadyState.ID], None)
        return None

    def enter(self, _options):
        pass

    def exit(self):
        pass


class TomatoReadyState:
    ID = "tomato_ready"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[WaitingState.ID], None)
        elif event == SHORT_PRESSED:
            return (states[PauseReadyState.ID], None)
        return None

    def enter(self, _options):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(GREEN)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


class PauseReadyState:
    ID = "pause_ready"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[WaitingState.ID], None)
        elif event == SHORT_PRESSED:
            return (states[TomatoReadyState.ID], None)
        return None

    def enter(self, _options):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(BLUE)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


states = {
    WaitingState.ID: WaitingState(),
    TomatoReadyState.ID: TomatoReadyState(),
    PauseReadyState.ID: PauseReadyState(),
}
