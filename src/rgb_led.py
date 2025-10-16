from machine import Pin
from neopixel import NeoPixel


NUM_PIXELS = 1  # Only one LED on the board


class RGBled:
    def __init__(self, gpio):
        self.np = NeoPixel(Pin(gpio, Pin.OUT), NUM_PIXELS)

    def set_color(self, value_tuple):
        self.np[0] = value_tuple
        self.np.write()
