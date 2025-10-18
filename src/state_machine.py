from usr_button import LONG_PRESSED, SHORT_PRESSED
from tasks import Blinker, get_runner, get_task_registry, Timer, HueLoop
from colors import BLUE, GREEN


STATE_MACHINE = None
TIMER_OVER_COLOR = (255, 0, 0)


def get_state_machine():
    global STATE_MACHINE
    if STATE_MACHINE is None:
        STATE_MACHINE = StateMachine()
        STATE_MACHINE.start_from(states[WaitingState.ID])
    return STATE_MACHINE


class StateMachine:
    def start_from(self, state):
        self.current_state = state
        state.enter()

    def handle_events(self, events):
        for event in events:
            next_state = self.current_state.handle_event(event)
            if next_state:
                self.current_state.exit()
                next_state.enter()
                self.current_state = next_state


class WaitingState:
    ID = "waiting"

    def handle_event(self, event):
        if event == SHORT_PRESSED:
            return states[WorkReadyState.ID]
        return None

    def enter(self):
        looper = get_task_registry().get(HueLoop.TASK_NAME)
        looper.reset()
        get_runner().add_task(HueLoop.TASK_NAME)

    def exit(self):
        get_runner().remove_task(HueLoop.TASK_NAME)


class WorkReadyState:
    ID = "work_ready"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[WorkRunningState.ID]
        elif event == SHORT_PRESSED:
            return states[BreakReadyState.ID]
        return None

    def enter(self):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(BLUE)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


class BreakReadyState:
    ID = "break_ready"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[BreakRunningState.ID]
        elif event == SHORT_PRESSED:
            return states[WorkReadyState.ID]
        return None

    def enter(self):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(GREEN)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


class WorkRunningState:
    ID = "work_running"
    # WORK_DURATION = 20  # DEBUG amount
    WORK_DURATION = 60 * 25  # 25 minutes

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[WaitingState.ID]
        elif event == Timer.FINISHED_EVENT:
            return states[WorkOverState.ID]
        return None

    def enter(self):
        timer = get_task_registry().get(Timer.TASK_NAME)
        timer.reset(self.WORK_DURATION)
        get_runner().add_task(timer.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Timer.TASK_NAME)


class BreakRunningState:
    ID = "break_running"
    # TIMER_DURATION = 10  # DEBUG amount
    TIMER_DURATION = 60 * 5  # 5 minutes

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[WaitingState.ID]
        elif event == Timer.FINISHED_EVENT:
            return states[BreakOverState.ID]
        return None

    def enter(self):
        timer = get_task_registry().get(Timer.TASK_NAME)
        timer.reset(self.TIMER_DURATION)
        get_runner().add_task(timer.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Timer.TASK_NAME)


class WorkOverState:
    ID = "work_over_state"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[WaitingState.ID]
        elif event == SHORT_PRESSED:
            return states[BreakRunningState.ID]
        return None

    def enter(self):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(TIMER_OVER_COLOR, compensate=False)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


class BreakOverState:
    ID = "break_over_state"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[WaitingState.ID]
        elif event == SHORT_PRESSED:
            return states[WorkRunningState.ID]
        return None

    def enter(self):
        blinker = get_task_registry().get(Blinker.TASK_NAME)
        blinker.reset(TIMER_OVER_COLOR, compensate=False)
        get_runner().add_task(Blinker.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)


states = {
    WaitingState.ID: WaitingState(),
    WorkReadyState.ID: WorkReadyState(),
    BreakReadyState.ID: BreakReadyState(),
    BreakRunningState.ID: BreakRunningState(),
    WorkRunningState.ID: WorkRunningState(),
    WorkOverState.ID: WorkOverState(),
    BreakOverState.ID: WorkOverState(),
}
