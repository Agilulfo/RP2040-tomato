from math import cos, pi
from time import ticks_ms, time

from colors import GREEN, OFF, RED, hue_to_rgb, interpolate
from ticks import ticks_delta


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

    def reset(self, color=None, compensate=True):
        self.compensate = compensate
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
            self.rgb.set_color(self.color, compensate=self.compensate)
            self.on = True

    def stop(self):
        self.reset()


class Timer:
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
        color = interpolate(self.start_color, self.end_color, progress)
        self.rgb.set_color(color)
        return None

    def reset(self, duration):
        self.duration = duration
        self.started_at = None
        self.rgb.set_color(OFF)

    def stop(self):
        self.reset(0)


class HueLoop:
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


class Breather:
    TASK_NAME = "breather"

    def __init__(self, rgb, color, period):
        self.rgb = rgb
        self.color = color
        self.period = period
        self.reset()

    def run(self):
        current_ticks = ticks_ms()
        passed = ticks_delta(self.cycle_start, current_ticks)
        if passed >= self.period:
            passed = 0
            self.cycle_start = current_ticks
        progress = passed / self.period
        self.rgb.set_color(self._compute_color(progress))
        return None

    def reset(self, color=None):
        if color:
            self.color = color
        self.rgb.set_color(OFF)
        self.cycle_start = ticks_ms()

    def _compute_color(self, linear_progress):
        start = OFF
        end = self.color
        curved_progress = 1 - ((cos(2 * pi * linear_progress) + 1) / 2)
        return interpolate(start, end, curved_progress)

    def stop(self):
        self.reset()
