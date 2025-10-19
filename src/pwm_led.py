from machine import PWM, Pin


class DimmedLED:
    def __init__(self, gpio):
        frequency = 500
        self.pwm = PWM(Pin(gpio), frequency)
        self.set_level(10)
        self.off()

    """
    for simplicity this code
    suports 17 levels [0, 16]
    """

    def set_level(self, level):
        self.level = level

    def on(self):
        self.pwm.duty_u16(__class__.level_to_duty(self.level))
        self.is_on = True

    def off(self):
        self.pwm.duty_u16(__class__.level_to_duty(0))
        self.is_on = False

    def toggle(self):
        if self.is_on:
            self.off()
        else:
            self.on()

    def level_to_duty(level):
        return (1 << level) - 1
