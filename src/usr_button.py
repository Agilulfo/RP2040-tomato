from machine import Pin
from time import ticks_ms, ticks_add, sleep_ms

PRESSED = 0
RELEASED = 1

SHORT_PRESSED = "short"
LONG_PRESSED = "long"

DURATION_TRESHOLD = 300

TICKS_MAX = ticks_add(0, -1)


class UsrButton:
    def __init__(self, gpio):
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
        # reading immediatelly cause issue, wait a little
        sleep_ms(100)
        self.previous_status = self.pin.value()

    def _detect_transition(self):
        current_status = self.pin.value()
        detected = None
        if self.previous_status != current_status:
            if current_status == RELEASED:
                current_tick = ticks_ms()
                duration = self._press_duration(current_tick)
                print(f"the duration was {TICKS_MAX} - {duration}")
                if duration < DURATION_TRESHOLD:
                    detected = SHORT_PRESSED
                else:
                    detected = LONG_PRESSED
            else:
                self.pressed_at = ticks_ms()
        self.previous_status = current_status
        return detected

    def _press_duration(self, end_tick):
        if self.pressed_at <= end_tick:
            return end_tick - self.pressed_at
        else:
            return TICKS_MAX - self.pressed_at + end_tick

    def run(self):
        transition = self._detect_transition()
        return transition
