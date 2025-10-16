# Set the color for the first (and only) pixel
# Colors are (Red, Green, Blue) with values from 0-255
RED = (10, 0, 0)
GREEN = (0, 5, 0)
BLUE = (0, 0, 10)
OFF = (0, 0, 0)

PRIMARIES = [("red", RED), ("green", GREEN), ("blue", BLUE)]


class ColorIterator:
    def __init__(self, colors):
        self.colors = colors
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        color = self.colors[self.index]
        self.index = (self.index + 1) % len(self.colors)
        return color
