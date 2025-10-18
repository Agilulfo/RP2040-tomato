import math

RED = (20, 0, 0)
GREEN = (0, 20, 0)
BLUE = (0, 0, 20)
OFF = (0, 0, 0)


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


# Got this from Gemini :-P
def hue_to_rgb(hue_angle: float) -> tuple[int, int, int]:
    """
    Converts a Hue angle (0-360 degrees) to an RGB tuple (0-255, 0-255, 0-255).

    This implementation assumes maximum Saturation (S=1.0) and mid-Lightness (L=0.5)
    to produce the most vibrant colors for the given hue.

    Args:
        hue_angle: The hue angle in degrees (0.0 to 360.0).

    Returns:
        A tuple (R, G, B) where each component is an integer from 0 to 255.
    """
    # Normalize Hue to be between 0 and 360
    H = hue_angle % 360

    # Assume maximum saturation and mid-lightness (for vibrant colors)
    S = 1.0
    L = 0.1  # this value seem to produce an acceptable brightness

    # Step 1: Calculate Chroma (C)
    # C = (1 - |2L - 1|) * S
    C = (1 - abs(2 * L - 1)) * S

    # Step 2: Calculate the Intermediate Value (X)
    # X = C * (1 - |(H / 60) mod 2 - 1|)
    # (H / 60) mod 2 calculates which of the six 60-degree sectors the hue falls into
    X = C * (1 - abs((H / 60.0) % 2 - 1))

    # Initialize R', G', B'
    R_prime, G_prime, B_prime = 0.0, 0.0, 0.0

    # Step 3: Map Hue Sector to (R', G', B')
    # Determine the sector (0 to 5)
    sector = math.floor(H / 60.0)

    if sector == 0:  # 0 <= H < 60 (Red -> Yellow)
        R_prime, G_prime, B_prime = C, X, 0
    elif sector == 1:  # 60 <= H < 120 (Yellow -> Green)
        R_prime, G_prime, B_prime = X, C, 0
    elif sector == 2:  # 120 <= H < 180 (Green -> Cyan)
        R_prime, G_prime, B_prime = 0, C, X
    elif sector == 3:  # 180 <= H < 240 (Cyan -> Blue)
        R_prime, G_prime, B_prime = 0, X, C
    elif sector == 4:  # 240 <= H < 300 (Blue -> Magenta)
        R_prime, G_prime, B_prime = X, 0, C
    elif sector == 5:  # 300 <= H < 360 (Magenta -> Red)
        R_prime, G_prime, B_prime = C, 0, X

    # Step 4: Add the Lightness Match (M)
    M = L - C / 2

    # Step 5: Final RGB Values (normalized 0-1) and scaled to 0-255
    R = (R_prime + M) * 255
    G = (G_prime + M) * 255
    B = (B_prime + M) * 255

    # Return as integer tuple
    return (int(round(R)), int(round(G)), int(round(B)))
