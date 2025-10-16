from machine import Pin
from neopixel import NeoPixel

# The RGB LED on the YD-RP2040 is commonly on GPIO 23.
RGB_PIN = 23
NUM_PIXELS = 1  # Only one LED on the board

# Initialize the NeoPixel object
np = NeoPixel(Pin(RGB_PIN, Pin.OUT), NUM_PIXELS)

# Initialize usr button
usr_btn = Pin(24, Pin.IN, Pin.PULL_UP)

# Initialize blue LED
blue_led = Pin(25, Pin.OUT)

# Set the color for the first (and only) pixel
# Colors are (Red, Green, Blue) with values from 0-255
RED = (10, 0, 0)
GREEN = (0, 5, 0)
BLUE = (0, 0, 10)
OFF = (0, 0, 0)

colors = [("red", RED), ("green", GREEN), ("blue", BLUE)]


PRESSED = 1
RELEASED = 0


def loop():
    index = 0
    previous = RELEASED
    set_color(OFF)
    while True:
        current = usr_btn.value()
        if previous == PRESSED and current == RELEASED:
            index = (index + 1) % 3
            text, numerical = colors[index]
            set_color(numerical)
            blue_led.toggle()
            print(text)
        previous = current


def set_color(value):
    np[0] = value
    np.write()


if __name__ == "__main__":
    loop()
