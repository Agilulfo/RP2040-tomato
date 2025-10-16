from machine import Pin

PRESSED = 0
RELEASED = 1


class UsrButton:
    def __init__(self, gpio):
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
        self.previous_status = self.pin.value()

    def released(self):
        current_status = self.pin.value()
        pressed = self.previous_status == PRESSED and current_status == RELEASED
        self.previous_status = current_status
        return pressed
