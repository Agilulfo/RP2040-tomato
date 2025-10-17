# YD-RP2040-based Tomato Timer

A minimalist timer for the [Pomodoro Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique).

I haven't had this much fun developing this little thing in a long time!

Building a little standalone device that can sit on my desk and track my work time has been on my bucket list for a while, so I'm incredibly happy I've finally done it. Being able to run MicroPython on this chip is a blessing.

## Implementation Notes

This device has to be able to do multiple things at the same time:
 - Keep an eye on the button to detect when it gets pressed.
 - Keep track of the time passed.
 - Change the LED color to indicate the different statuses.

As far as I know, there are a few options to achieve multitasking on microcontrollers.

Often, interrupts based on timers or other sources are used to momentarily interrupt the program execution and run some other piece of logic.

MicroPython allows binding some methods/functions to interrupts too, and it also supports [asyncio](https.docs.micropython.org/en/latest/library/asyncio.html).

Of course, I've opted for reinventing the wheel and challenging myself with the task of building a rudimentary event loop capable of running multiple tasks at the same time.

IT WORKS! ..Nothing too fancy..

Just a 'runner' keeping track of a few 'tasks' that do something and then immediately return.

The tasks can generate events that are then sent to a 'state machine' that decides how to react to each event based on the current state.

## TODO

There are a few things here and there to polish and refactor, but all the functionalities I wanted to implement are completed and working correctly.

I would love to rewrite the whole code using the asyncio library.
