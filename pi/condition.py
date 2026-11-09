#!/usr/bin/env python3
# human-contributors: []; ai-contributors: [Claude]; status: "#ai-written"
"""Cycle the Inky pHAT through full-colour flushes to help rehabilitate stuck pixels.

Interrupt with Ctrl+C when done.
"""

import signal
import sys
import time

from inky import InkyPHAT
from PIL import Image

COLOUR = "red"
DELAY = 4  # seconds between frames — fast enough to condition, slow enough not to stress the panel

inky = InkyPHAT(COLOUR)
inky.set_border(inky.WHITE)

SEQUENCE = [inky.WHITE, inky.BLACK, inky.WHITE, inky.RED]
NAMES = {inky.WHITE: "WHITE", inky.BLACK: "BLACK", inky.RED: "RED"}


def flush(colour: int) -> None:
    img = Image.new("P", (inky.WIDTH, inky.HEIGHT), colour)
    inky.set_image(img)
    inky.show()


def handle_exit(sig, frame):
    print("\nInterrupted. Leaving display white.")
    flush(inky.WHITE)
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)

print(f"Conditioning display — Ctrl+C to stop and leave white.")
cycle = 0
while True:
    for colour in SEQUENCE:
        cycle += 1
        print(f"  cycle {cycle:4d}  {NAMES[colour]}")
        flush(colour)
        time.sleep(DELAY)
