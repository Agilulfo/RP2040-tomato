from usr_button import UsrButton, LONG_PRESSED, SHORT_PRESSED
from rgb_led import RGBled
from colors import OFF, GREEN, BLUE
from ticks import ticks_delta
from time import ticks_ms, sleep

# GPIO mapping
RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25

# state names
WAITING = "waiting"
BLINKING = "blinking"

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
                next_state.enter(options)
                self.current_state = next_state


# STATES


class WaitingState:
    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[BLINKING], {"color": GREEN})
        elif event == SHORT_PRESSED:
            return (states[BLINKING], {"color": BLUE})
        return None

    def enter(self, _options):
        # MAYBE think later what should happen here
        # should I insert the tasks for listening button
        # presses in here?
        pass


class BlinkingState:
    def handle_event(self, event):
        if event == LONG_PRESSED:
            return (states[BLINKING], {"color": GREEN})
        elif event == SHORT_PRESSED:
            return (states[BLINKING], {"color": BLUE})
        return None

    def enter(self, options):
        blinker = task_registry.get(BLINKER)
        blinker.reset(options["color"])
        runner.add_task(BLINKER)

    def exit(self):
        # maybe reset blinker task?
        # it is done anyway in the enter
        # so for the time being no
        runner.remove_task(BLINKER)
        # this should remove the task from the runner pausing the blinking


# TASKS INFRASTRUCTURE


class Runner:
    def __init__(self, state_machine):
        self.tasks = set()
        self.state_machine = state_machine

    def add_task(self, name):
        self.tasks.add(name)

    def remove_task(self, name):
        task = self.tasks.discard(name)
        if task:
            task.stop()

    def run(self):
        events = []
        for task_name in self.tasks:
            task = task_registry.get(task_name)
            event = task.run()
            if event:
                events.append(event)
        self.state_machine.handle_events(events)


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
states = {WAITING: WaitingState(), BLINKING: BlinkingState()}
task_registry = TaskRegistry()
state_machine = StateMachine()
runner = Runner(state_machine)


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
    task_registry.add(blinker, BLINKER)
    task_registry.add(button, BUTTON)

    # init runner
    runner.add_task(BUTTON)

    # init state machine
    state_machine.start_from(states[WAITING])
    while True:
        runner.run()


if __name__ == "__main__":
    main()
