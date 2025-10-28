import asyncio

from colors import BLUE, GREEN
from pwm_led import DimmedLED
from tasks import Blinker, Breather, Timer, HueLoop
from usr_button import LONG_PRESSED, SHORT_PRESSED, ButtonListener

TIMER_OVER_COLOR = (255, 0, 0)
LED_PIN = 25


class StateMachine:
    def __init__(self, rgb_led, button_pin):
        self.rgb_led = rgb_led
        self.button_pin = button_pin
        self.work_indicator = DimmedLED(LED_PIN)

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
        work_kwargs = {"work_led": self.work_indicator}

        waiting_state = WaitingState(self.rgb_led)
        work_ready_state = TimerReadyState(self.rgb_led, BLUE)
        break_ready_state = TimerReadyState(self.rgb_led, GREEN)
        work_running_state = TimerRunningState(
            self.rgb_led, event, is_work=True, **work_kwargs
        )
        break_running_state = TimerRunningState(self.rgb_led, event)
        work_over_state = TimerOverState(self.rgb_led, **work_kwargs)
        break_over_state = TimerOverState(self.rgb_led)

        # link states
        waiting_state.set_next(work_ready_state)
        work_ready_state.set_next(break_ready_state, work_running_state)
        break_ready_state.set_next(work_ready_state, break_running_state)
        work_running_state.set_next(waiting_state, work_over_state)
        break_running_state.set_next(waiting_state, break_over_state)
        work_over_state.set_next(break_running_state, waiting_state)
        break_over_state.set_next(work_running_state, waiting_state)

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
        self.hue_loop = HueLoop(rgb_led)

    def set_next(self, state):
        self.next = state

    async def run(self):
        self.hue_loop.reset()
        try:
            while True:
                self.hue_loop.run()
                await asyncio.sleep_ms(2)
        except asyncio.CancelledError:
            self.hue_loop.stop()

    def handle_event(self, event_type):
        if event_type == SHORT_PRESSED:
            return self.next
        else:
            return None


class TimerReadyState:
    def __init__(self, rgb_led, color):
        self.breather = Breather(rgb_led, color, 1000)

    def set_next(self, next_short, next_long):
        self.next_short = next_short
        self.next_long = next_long

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
            return self.next_long
        elif event_type == SHORT_PRESSED:
            return self.next_short
        return None


class TimerRunningState:
    def __init__(self, rgb_led, event, is_work=False, work_led=None):
        self.event = event
        self.timer = Timer(rgb_led)
        self.work_led = work_led
        # if is_work:
        #     self.duration = 60 * 25  # 25 minutes
        # else:
        #     self.duration = 60 * 5  # 5 minutes
        if is_work:
            self.duration = 10
        else:
            self.duration = 5

    def set_next(self, next_long, next_finished):
        self.next_finished = next_finished
        self.next_long = next_long

    async def run(self):
        self.timer.reset(self.duration)
        if self.work_led:
            self.work_led.on()
        try:
            while True:
                event_type = self.timer.run()
                if event_type:
                    self.event.type = event_type
                    self.event.set()
                await asyncio.sleep_ms(500)
        except asyncio.CancelledError:
            self.timer.stop()
            if self.work_led:
                self.work_led.off()

    def handle_event(self, event_type):
        if event_type == LONG_PRESSED:
            return self.next_long
        elif event_type == self.timer.FINISHED_EVENT:
            return self.next_finished
        return None


class TimerOverState:
    def __init__(self, rgb_led, work_led=None):
        self.rgb = rgb_led
        self.blinker = Blinker(rgb_led, TIMER_OVER_COLOR, 1000)
        self.blinker.reset(compensate=False)
        self.work_led = work_led

    def set_next(self, next_short, next_long):
        self.next_short = next_short
        self.next_long = next_long

    async def run(self):
        if self.work_led:
            self.work_led.on()
        try:
            while True:
                self.blinker.run()
                await asyncio.sleep_ms(20)
        except asyncio.CancelledError:
            self.blinker.stop()
            if self.work_led:
                self.work_led.off()

    def handle_event(self, event_type):
        if event_type == LONG_PRESSED:
            return self.next_long
        elif event_type == SHORT_PRESSED:
            return self.next_short
        return None
