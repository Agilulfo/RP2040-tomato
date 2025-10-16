# YD-RP2040 micro python led blinker

A simple program that uses the onboard features to get started with this platform

## about YD-RP2040 board

the [YD-RP2040][YD-RP2040] is a RP-2040 based board that is:

 - cheap
 - offer a rgb led
 - offer a reset button
 - offer a power led indicator
 - offer a usr button
 - has an USB C connector

 it is prefect to get started

### GPIO23 RGB WS2812 LED

GPIO23 pin can be used to control the onboard RGB WS2812 LED.

if you want to use this feature you have to bridge the [R68 pads](https://forum.arduino.cc/t/yd-rp2040-built-in-w2812/1062726) (I'm not sure if an actual resistor need to be used but a ball of melted tin is doing the job)

the led can be controlled with the [NeoPixel](https://docs.micropython.org/en/latest/rp2/quickref.html#neopixel-and-apa106-driver) driver.

### GPIO24 usr button

a button is connected to GPIO24

### GPIO25 blue led

the board offers a simple led connected to the GPIO25 pin


## Usage

### flash  micropython

follow instructions in [here][micropython RP2040]. (I've used the pico firmware, and it seems to work fine)

in short:

1. connect board to usb while pressing the boot button
2. drop micropython fw on the controller


### use REPL

you can access the REPL via usb serial

#### using screen

after you figure which serial port is being usded (dmesg is your friend)

```
screen /dev/ttyACM0 115200
```
exit screen by pressing  "ctrl+a" and immediatelly "\"

#### using mpremote

simply run

```
mpremote
```

similarly to screen, exit by pressing  "ctrl+a" and immediatelly "\"

### flash your python script

```
mpremote fs cp main.py :main.py
```

this command works similarly to the bash cp (you can rename files while moving them)

[YD-RP2040]: https://circuitpython.org/board/vcc_gnd_yd_rp2040/
[micropython RP2040]: https://www.raspberrypi.com/documentation/microcontrollers/micropython.html
[RP2040]: https://www.raspberrypi.com/products/rp2040/
