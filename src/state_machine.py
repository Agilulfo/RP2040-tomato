import asyncio
from time import ticks_ms

from colors import BLUE, GREEN, OFF, hue_to_rgb
from pwm_led import DimmedLED
from tasks import Blinker, Breather, Timer, get_runner, get_task_registry
from ticks import ticks_delta
from usr_button import LONG_PRESSED, SHORT_PRESSED

STATE_MACHINE = None
TIMER_OVER_COLOR = (255, 0, 0)
LED_PIN = 25

work_indicator = DimmedLED(LED_PIN)


def get_state_machine():
    global STATE_MACHINE
    if STATE_MACHINE is None:
        STATE_MACHINE = StateMachine()
        STATE_MACHINE.start_from(states[WaitingState.ID])
    return STATE_MACHINE


class StateMachine:
    def __init__(self, rgb_led):
        self.rgb_led = rgb_led

    async def run(self):
        print("running state machine")
        current_state = WaitingState(self.rgb_led)
        await current_state.run()


class WaitingState:
    PERIOD = 5000

    def __init__(self, rgb_led):
        self.rgb = rgb_led

    async def run(self):
        self.reset()
        try:
            while True:
                self.run_color()
                await asyncio.sleep_ms(2)
        except asyncio.CancelledError:
            self.stop()

    def run_color(self):
        now = ticks_ms()
        if self.cycle_started_at is None:
            self.cycle_started_at = now
        elapsed = ticks_delta(self.cycle_started_at, now)
        if elapsed > self.PERIOD:
            self.cycle_started_at = now
            elapsed = 0

        angle = elapsed / self.PERIOD * 360
        color = hue_to_rgb(angle)
        self.rgb.set_color(color)

        return None

    def reset(self):
        self.cycle_started_at = None
        self.rgb.set_color(OFF)

    def stop(self):
        self.reset()


class WorkReadyState:
    ID = "work_ready"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[WorkRunningState.ID]
        elif event == SHORT_PRESSED:
            return states[BreakReadyState.ID]
        return None

    def enter(self):
        breather = get_task_registry().get(Breather.TASK_NAME)
        breather.reset(BLUE)
        get_runner().add_task(breather.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Breather.TASK_NAME)


class BreakReadyState:
    ID = "break_ready"

    def handle_event(self, event):
        if event == LONG_PRESSED:
            return states[BreakRunningState.ID]
        elif event == SHORT_PRESSED:
            return states[WorkReadyState.ID]
        return None

    def enter(self):
        breather = get_task_registry().get(Breather.TASK_NAME)
        breather.reset(GREEN)
        get_runner().add_task(breather.TASK_NAME)

    def exit(self):
        get_runner().remove_task(Breather.TASK_NAME)


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
        work_indicator.on()

    def exit(self):
        get_runner().remove_task(Timer.TASK_NAME)
        work_indicator.off()


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
        work_indicator.on()

    def exit(self):
        get_runner().remove_task(Blinker.TASK_NAME)
        work_indicator.off()


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
    WorkReadyState.ID: WorkReadyState(),
    BreakReadyState.ID: BreakReadyState(),
    BreakRunningState.ID: BreakRunningState(),
    WorkRunningState.ID: WorkRunningState(),
    WorkOverState.ID: WorkOverState(),
    BreakOverState.ID: BreakOverState(),
}
