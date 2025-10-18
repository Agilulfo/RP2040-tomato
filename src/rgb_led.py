from machine import Pin
from neopixel import NeoPixel

NUM_PIXELS = 1  # Only one LED on the board


class RGBled:
    R_SCALE = 625
    G_SCALE = 1250
    B_SCALE = 300

    def __init__(self, gpio):
        self.np = NeoPixel(Pin(gpio, Pin.OUT), NUM_PIXELS)

    def set_color(self, value_tuple, compensate=True):
        if compensate:
            value_tuple = self._compensate(value_tuple)

        self.np[0] = value_tuple
        self.np.write()

    """
    According to this datasheet:
    https://cdn-shop.adafruit.com/datasheets/WS2812.pdf
    WS2812 LEDS for the same value emit a different intensity of light
    with this function I'm trying to compensate to make colors more
    neutral
    """

    def _compensate(self, value_tuple):
        r, g, b = value_tuple

        minimum = min(self.R_SCALE, self.G_SCALE, self.B_SCALE)

        return (
            int(r * minimum / self.R_SCALE),
            int(g * minimum / self.G_SCALE),
            int(b * minimum / self.B_SCALE),
        )
