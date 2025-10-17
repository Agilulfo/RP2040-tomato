from time import ticks_add

TICKS_MAX = ticks_add(0, -1)


def ticks_delta(start, end):
    if start <= end:
        return end - start
    else:
        return TICKS_MAX - start + end
