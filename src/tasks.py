from colors import OFF, GREEN, RED, hue_to_rgb
from time import ticks_ms, time
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


class Timer:
    TASK_NAME = "timer"
    FINISHED_EVENT = "finished"

    def __init__(self, rgb):
        self.rgb = rgb
        self.start_color = GREEN
        self.end_color = RED

    def run(self):
        now = time()
        if self.started_at is None:
            self.started_at = now
        elapsed = now - self.started_at
        if elapsed >= self.duration:
            return self.FINISHED_EVENT
        progress = elapsed / self.duration
        color = self.interpolate(progress)
        self.rgb.set_color(color)
        return None

    def reset(self, duration):
        self.duration = duration
        self.started_at = None
        self.rgb.set_color(OFF)

    def stop(self):
        self.reset(0)

    def interpolate(self, progress):
        AR, AG, AB = self.start_color
        BR, BG, BB = self.end_color

        CR = AR - (AR - BR) * progress
        CG = AG - (AG - BG) * progress
        CB = AB - (AB - BB) * progress
        return (int(CR), int(CG), int(CB))


class RunnerIndicator:
    TASK_NAME = "runner_indicator"
    PERIOD = 1000

    def __init__(self, led):
        self.led = led
        self.last_flip = ticks_ms()

    def run(self):
        current_ticks = ticks_ms()
        passed = ticks_delta(self.last_flip, current_ticks)
        if passed >= self.PERIOD / 2:
            self.led.toggle()
            self.last_flip = current_ticks
        return None


class HueLoop:
    TASK_NAME = "hue_loop"
    PERIOD = 5000

    def __init__(self, rgb):
        self.rgb = rgb

    def run(self):
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
