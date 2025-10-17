from colors import OFF
from time import ticks_ms
from ticks import ticks_delta

RUNNER = None
TASK_REGISTRY = None


def get_runner():
    global RUNNER
    if RUNNER is None:
        RUNNER = Runner()
    return RUNNER


def get_task_registry():
    global TASK_REGISTRY
    if TASK_REGISTRY is None:
        TASK_REGISTRY = TaskRegistry()
    return TASK_REGISTRY


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
        # Necessary to avoid circula import
        from state_machine import get_state_machine
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
    TASK_NAME = "blinker"

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
