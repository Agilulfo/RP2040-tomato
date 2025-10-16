from machine import Pin
from neopixel import NeoPixel

# The RGB LED on the YD-RP2040 is commonly on GPIO 23.
RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25
NUM_PIXELS = 1  # Only one LED on the board

# Initialize the NeoPixel object
np = NeoPixel(Pin(RGB_PIN, Pin.OUT), NUM_PIXELS)

# Initialize blue LED
blue_led = Pin(LED_PIN, Pin.OUT)

# Set the color for the first (and only) pixel
# Colors are (Red, Green, Blue) with values from 0-255
RED = (10, 0, 0)
GREEN = (0, 5, 0)
BLUE = (0, 0, 10)
OFF = (0, 0, 0)

colors = [("red", RED), ("green", GREEN), ("blue", BLUE)]


PRESSED = 1
RELEASED = 0


class UsrButton:
    def __init__(self, gpio):
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
        self.previous_status = self.pin.value()

    def released(self):
        current_status = self.pin.value()
        pressed = self.previous_status == PRESSED and current_status == RELEASED
        self.previous_status = current_status
        return pressed


def loop():
    button = UsrButton(BTN_PIN)
    index = 0
    set_color(OFF)
    while True:
        if button.released():
            index = (index + 1) % 3
            text, numerical = colors[index]
            set_color(numerical)
            blue_led.toggle()
            print(text)


def set_color(value):
    np[0] = value
    np.write()


if __name__ == "__main__":
    loop()
