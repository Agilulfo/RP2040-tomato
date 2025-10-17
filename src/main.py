from usr_button import UsrButton
from rgb_led import RGBled
from colors import OFF, GREEN
from time import sleep
from state_machine import get_state_machine
from tasks import Blinker, get_runner, get_task_registry

# GPIO mapping
RGB_PIN = 23
BTN_PIN = 24
LED_PIN = 25


def init_device():
    rgb = RGBled(RGB_PIN)
    button = UsrButton(BTN_PIN)
    return (rgb, button)


def main():
    rgb, button = init_device()

    # init sequence to allow
    # user to connect via serial port
    rgb.set_color(GREEN)
    sleep(1)
    rgb.set_color(OFF)

    # register basic tasks
    blinker = Blinker(rgb, GREEN, 500)
    task_registry = get_task_registry()
    task_registry.add(blinker, blinker.TASK_NAME)
    task_registry.add(button, button.TASK_NAME)

    # init runner
    runner = get_runner()
    runner.add_task(UsrButton.TASK_NAME)

    # init state machine
    # TODO: probably can be removed
    get_state_machine()
    while True:
        runner.run()


if __name__ == "__main__":
    main()
