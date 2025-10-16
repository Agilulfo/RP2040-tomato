from machine import Pin
from usr_button import UsrButton
from rgb_led import RGBled
from colors import ColorIterator, RGB

RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25

# Initialize blue LED
blue_led = Pin(LED_PIN, Pin.OUT)


def loop():
    button = UsrButton(BTN_PIN)
    rgb_led = RGBled(RGB_PIN)
    color_iterator = ColorIterator(RGB)
    while True:
        if button.released():
            text, numerical = next(color_iterator)
            rgb_led.set_color(numerical)
            blue_led.toggle()
            print(text)


if __name__ == "__main__":
    loop()
