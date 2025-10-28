import asyncio
from time import ticks_ms

from colors import BLUE, GREEN, OFF, hue_to_rgb
from pwm_led import DimmedLED
from tasks import Blinker, Breather, Timer, get_runner, get_task_registry
from ticks import ticks_delta
from usr_button import LONG_PRESSED, SHORT_PRESSED, ButtonListener

TIMER_OVER_COLOR = (255, 0, 0)
LED_PIN = 25

work_indicator = DimmedLED(LED_PIN)


class StateMachine:
    def __init__(self, rgb_led, button_pin):
        self.rgb_led = rgb_led
        self.button_pin = button_pin

    async def run(self):
        print("running state machine")

        # I wish I could create multiple events
        # and wait on the first event happening
        # micropython asyncio.wait() is not implemented
        # so I can only use one event that I need to share
        event = asyncio.Event()

        # This task should never stop
        button_listener = ButtonListener(self.button_pin, event)
        asyncio.create_task(button_listener.run())

        # init states
        waiting_state = WaitingState(self.rgb_led)
        work_ready_state = WorkReadyState(self.rgb_led)
        break_ready_state = BreakReadyState(self.rgb_led)

        # link states
        waiting_state.set_next(work_ready_state)
        work_ready_state.set_next(break_ready_state)
        break_ready_state.set_next(work_ready_state)

        # init state machine
        current_state = waiting_state
        current_task = asyncio.create_task(current_state.run())

        # run loop
        while True:
            await event.wait()

            event_type = event.type
            event.type = None

            next_state = current_state.handle_event(event_type)

            if next_state:
                current_task.cancel()
                current_state = next_state
                current_task = asyncio.create_task(next_state.run())

            event.clear()


class WaitingState:
    PERIOD = 5000

    def __init__(self, rgb_led):
        self.rgb = rgb_led

    def set_next(self, state):
        self.next = state

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

    def handle_event(self, event_type):
        if event_type == SHORT_PRESSED:
            return self.next
        else:
            return None


class WorkReadyState:
    def __init__(self, rgb_led):
        self.rgb = rgb_led
        self.breather = Breather(rgb_led, BLUE, 1000)

    def set_next(self, state):
        self.next = state

    async def run(self):
        self.task = asyncio.current_task()
        try:
            while True:
                self.breather.run()
                await asyncio.sleep_ms(20)
        except asyncio.CancelledError:
            self.breather.stop()

    def handle_event(self, event_type):
        if event_type == LONG_PRESSED:
            return None
        elif event_type == SHORT_PRESSED:
            return self.next
        return None


class BreakReadyState:
    def __init__(self, rgb_led):
        self.rgb = rgb_led
        self.breather = Breather(rgb_led, GREEN, 1000)

    def set_next(self, state):
        self.next = state

    async def run(self):
        self.task = asyncio.current_task()
        try:
            while True:
                self.breather.run()
                await asyncio.sleep_ms(20)
        except asyncio.CancelledError:
            self.breather.stop()

    def handle_event(self, event_type):
        if event_type == LONG_PRESSED:
            return None
        elif event_type == SHORT_PRESSED:
            return self.next
        return None

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


states = {
}
