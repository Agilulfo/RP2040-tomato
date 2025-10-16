from machine import Pin
from usr_button import UsrButton
from rgb_led import RGBled

# The RGB LED on the YD-RP2040 is commonly on GPIO 23.
RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25

# Initialize blue LED
blue_led = Pin(LED_PIN, Pin.OUT)

# Set the color for the first (and only) pixel
# Colors are (Red, Green, Blue) with values from 0-255
RED = (10, 0, 0)
GREEN = (0, 5, 0)
BLUE = (0, 0, 10)
OFF = (0, 0, 0)

colors = [("red", RED), ("green", GREEN), ("blue", BLUE)]

def loop():
    button = UsrButton(BTN_PIN)
    rgb_led = RGBled(RGB_PIN)
    index = 0
    rgb_led.set_color(OFF)
    while True:
        if button.released():
            index = (index + 1) % 3
            text, numerical = colors[index]
            rgb_led.set_color(numerical)
            blue_led.toggle()
            print(text)


if __name__ == "__main__":
    loop()
