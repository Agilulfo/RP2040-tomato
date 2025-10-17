from usr_button import LONG_PRESSED, SHORT_PRESSED
from tasks import Blinker, get_runner, get_task_registry
from colors import BLUE, GREEN


STATE_MACHINE = None


def get_state_machine():
    global STATE_MACHINE
    if STATE_MACHINE is None:
        STATE_MACHINE = StateMachine()
        STATE_MACHINE.start_from(states[WAITING])
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


# STATES

WAITING = "waiting"


class WaitingState:
    def handle_event(self, event):
        if event == SHORT_PRESSED:
            return (states[TOMATO_READY], None)
        return None

    def enter(self, _options):
        pass

    def exit(self):
        pass


TOMATO_READY = "tomato_ready"


class TomatoReadyState:
    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[WAITING], None)
        elif event == SHORT_PRESSED:
            return (states[PAUSE_READY], None)
        return None

    def enter(self, _options):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(GREEN)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


PAUSE_READY = "pause_ready"


class PauseReadyState:
    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[WAITING], None)
        elif event == SHORT_PRESSED:
            return (states[TOMATO_READY], None)
        return None

    def enter(self, _options):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(BLUE)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


states = {
    WAITING: WaitingState(),
    TOMATO_READY: TomatoReadyState(),
    PAUSE_READY: PauseReadyState(),
}
