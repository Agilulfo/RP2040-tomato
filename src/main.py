from usr_button import UsrButton, LONG_PRESSED, SHORT_PRESSED
from rgb_led import RGBled
from colors import OFF, GREEN, BLUE
from ticks import ticks_delta
from time import ticks_ms, sleep

# GPIO mapping
RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25

# task names
BUTTON = "button"
BLINKER = "blinker"


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
        blinker = get_task_registry().get(BLINKER)
        blinker.reset(GREEN)
        get_runner().add_task(BLINKER)

    def exit(self):
        get_runner().remove_task(BLINKER)


PAUSE_READY = "pause_ready"


class PauseReadyState:
    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[WAITING], None)
        elif event == SHORT_PRESSED:
            return (states[TOMATO_READY], None)
        return None

    def enter(self, _options):
        blinker = get_task_registry().get(BLINKER)
        blinker.reset(BLUE)
        get_runner().add_task(BLINKER)

    def exit(self):
        get_runner().remove_task(BLINKER)


# TASKS INFRASTRUCTURE


class Runner:
    def __init__(self):
        self.tasks = set()

    def add_task(self, name):
        self.tasks.add(name)

    def remove_task(self, name):
        task = get_task_registry().get(name)
        task.stop()
        self.tasks.remove(name)

    def run(self):
        events = []
        for task_name in self.tasks:
            task = get_task_registry().get(task_name)
            event = task.run()
            if event:
                events.append(event)
        get_state_machine().handle_events(events)


class TaskRegistry:
    def __init__(self):
        self.register = dict()

    def add(self, task, name):
        self.register[name] = task

    def get(self, name):
        return self.register.get(name, None)


# TASKS


class Blinker:
    def __init__(self, rgb, color, period):
        self.rgb = rgb
        self.color = color
        self.period = period
        self.reset()

    def run(self):
        current_ticks = ticks_ms()
        passed = ticks_delta(self.last_flip, current_ticks)
        if passed >= self.period / 2:
            self._toggle()
            self.last_flip = current_ticks
        return None

    def reset(self, color=None):
        if color:
            self.color = color
        self.rgb.set_color(OFF)
        self.on = False
        self.last_flip = ticks_ms()

    def _toggle(self):
        if self.on:
            self.rgb.set_color(OFF)
            self.on = False
        else:
            self.rgb.set_color(self.color)
            self.on = True

    def stop(self):
        self.reset()


# INITIALIZATION

# Global shared states
states = {
    WAITING: WaitingState(),
    TOMATO_READY: TomatoReadyState(),
    PAUSE_READY: PauseReadyState(),
}

RUNNER = None
TASK_REGISTRY = None
STATE_MACHINE = None


def get_runner():
    global RUNNER
    if RUNNER is None:
        RUNNER = Runner()
    return RUNNER


def get_state_machine():
    global STATE_MACHINE
    if STATE_MACHINE is None:
        STATE_MACHINE = StateMachine()
    return STATE_MACHINE


def get_task_registry():
    global TASK_REGISTRY
    if TASK_REGISTRY is None:
        TASK_REGISTRY = TaskRegistry()
    return TASK_REGISTRY


def init_device():
    rgb = RGBled(RGB_PIN)
    button = UsrButton(BTN_PIN)
    return (rgb, button)


def main():
    rgb, button = init_device()

    # init sequence to allow
    # user to connect via serial port
    rgb.set_color(GREEN)
    sleep(4)
    rgb.set_color(OFF)

    # register basic tasks
    blinker = Blinker(rgb, GREEN, 500)
    task_registry = get_task_registry()
    task_registry.add(blinker, BLINKER)
    task_registry.add(button, BUTTON)

    # init runner
    runner = get_runner()
    runner.add_task(BUTTON)

    # init state machine
    get_state_machine().start_from(states[WAITING])
    while True:
        runner.run()


if __name__ == "__main__":
    main()
