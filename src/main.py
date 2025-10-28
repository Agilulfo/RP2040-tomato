import asyncio

from rgb_led import RGBled
from state_machine import StateMachine

# GPIO mapping
RGB_PIN = 23
BTN_PIN = 24


def main():
    rgb = RGBled(RGB_PIN)
    state_machine = StateMachine(rgb)
    asyncio.run(state_machine.run())


if __name__ == "__main__":
    main()
