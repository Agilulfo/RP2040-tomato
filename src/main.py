from colors import OFF
from rgb_led import RGBled
from tasks import (
    Blinker,
    Breather,
    HueLoop,
    Timer,
    get_runner,
    get_task_registry,
)
from usr_button import UsrButton

# GPIO mapping
RGB_PIN = 23
BTN_PIN = 24


def main():
    rgb = RGBled(RGB_PIN)
    button = UsrButton(BTN_PIN)

    # register basic tasks
    blinker = Blinker(rgb, OFF, 500)
    breather = Breather(rgb, OFF, 2000)
    timer = Timer(rgb)
    hue_loop = HueLoop(rgb)

    task_registry = get_task_registry()
    task_registry.add(blinker, blinker.TASK_NAME)
    task_registry.add(breather, breather.TASK_NAME)
    task_registry.add(button, button.TASK_NAME)
    task_registry.add(timer, timer.TASK_NAME)
    task_registry.add(hue_loop, hue_loop.TASK_NAME)

    # init runner
    runner = get_runner()
    runner.add_task(UsrButton.TASK_NAME)

    while True:
        runner.run()


if __name__ == "__main__":
    main()
