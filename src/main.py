from usr_button import UsrButton, LONG_PRESSED, SHORT_PRESSED
from rgb_led import RGBled
from colors import OFF, GREEN, BLUE

RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25

WAITING = "waiting"
SELECTED = "selected"
RUNNING = "running"
DONE = "done"


def loop():
    rgb = RGBled(RGB_PIN)
    rgb.set_color(OFF)

    button = UsrButton(BTN_PIN)
    state = WAITING

    while True:
        check_event(button, rgb)
        do(state)


def do(state):
    if state == WAITING:
        do_blink()
    elif state == SELECTED:
        do_selected()


def check_event(button, rgb):
    detected_event = button.run()
    if detected_event == LONG_PRESSED:
        rgb.set_color(GREEN)
    elif detected_event == SHORT_PRESSED:
        rgb.set_color(BLUE)


def do_blink():
    pass


def do_selected():
    pass


if __name__ == "__main__":
    loop()
