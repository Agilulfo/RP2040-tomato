import asyncio
from time import sleep_ms, ticks_ms

from ticks import ticks_delta

PRESSED = 0
RELEASED = 1

SHORT_PRESSED = "short"
LONG_PRESSED = "long"

DURATION_TRESHOLD = 300


class ButtonListener:
    def __init__(self, pin):
        self.pin = pin
        sleep_ms(100)
        self.previous_status = self.pin.value()

    def _detect_transition(self):
        current_status = self.pin.value()
        detected = None
        if self.previous_status != current_status:
            if current_status == RELEASED:
                current_tick = ticks_ms()
                duration = ticks_delta(self.pressed_at, current_tick)
                if duration < DURATION_TRESHOLD:
                    detected = SHORT_PRESSED
                else:
                    detected = LONG_PRESSED
            else:
                self.pressed_at = ticks_ms()
        self.previous_status = current_status
        return detected

    async def run(self):
        while True:
            transition = self._detect_transition()
            if transition:
                print(f"detected {transition}")
            await asyncio.sleep_ms(10)
