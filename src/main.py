import asyncio

from rgb_led import RGBled
from machine import Pin
from state_machine import StateMachine

# GPIO mapping
RGB_PIN = 23
BTN_PIN = 24


def main():
    rgb = RGBled(RGB_PIN)
    button_pin = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
    state_machine = StateMachine(rgb, button_pin)
    asyncio.run(state_machine.run())


if __name__ == "__main__":
    main()
