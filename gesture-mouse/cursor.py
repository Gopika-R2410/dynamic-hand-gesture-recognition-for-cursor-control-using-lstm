"""Cursor movement, pinch-to-click/drag, and built-in scroll mode (no recording needed)."""
import math
import sys
import numpy as np
import pyautogui
from smoothing import OneEuro

pyautogui.FAILSAFE = False  # use Q/Esc or the lock gesture to stop
pyautogui.PAUSE = 0


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def _finger_up(lm, tip, pip):
    """Finger counts as extended if its tip is clearly farther from the wrist than its middle joint."""
    return _dist(lm[0], lm[tip]) > _dist(lm[0], lm[pip]) * 1.15


class CursorController:
    def __init__(self, margin=0.2, press=0.30, release_gap=0.12):
        self.margin = margin
        self.press = press              # pinch ratio below this = mouse down (adjust with + / -)
        self.release_gap = release_gap  # must open this much more to release (hysteresis)
        self.sw, self.sh = pyautogui.size()
        self.fx = OneEuro()
        self.fy = OneEuro()
        self.pinched = False
        self.mode = "cursor"            # shown on screen: cursor / scroll
        self.ratio = 0.0                # live pinch value, shown on screen
        # scroll speed (Mac uses much smaller units)
        self.scroll_speed = 20 if sys.platform == "darwin" else 200

    def update(self, lm):
        hand_size = _dist(lm[0], lm[9]) or 1e-6
        self.ratio = _dist(lm[4], lm[8]) / hand_size

        index_up = _finger_up(lm, 8, 6)
        middle_up = _finger_up(lm, 12, 10)
        ring_up = _finger_up(lm, 16, 14)
        pinky_up = _finger_up(lm, 20, 18)

        # ---------- SCROLL MODE: peace sign (index + middle up, ring + pinky down) ----------
        if index_up and middle_up and not ring_up and not pinky_up and not self.pinched:
            self.mode = "scroll"
            m = self.margin
            y = float(np.clip((lm[9].y - m) / (1 - 2 * m), 0, 1))
            offset = y - 0.5                     # hand high = scroll up, hand low = scroll down
            if abs(offset) > 0.12:               # dead zone in the middle
                pyautogui.scroll(int(-offset * self.scroll_speed))
            return

        # ---------- CURSOR + PINCH ----------
        self.mode = "cursor"
        closing = self.ratio < (self.press + 0.15) and not self.pinched
        if not closing:  # freeze cursor while fingers close so the click lands where you aimed
            m = self.margin
            x = np.clip((lm[8].x - m) / (1 - 2 * m), 0, 1)
            y = np.clip((lm[8].y - m) / (1 - 2 * m), 0, 1)
            px = min(self.fx(x) * self.sw, self.sw - 1)
            py = min(self.fy(y) * self.sh, self.sh - 1)
            pyautogui.moveTo(px, py)

        if not self.pinched and self.ratio < self.press:
            self.pinched = True
            pyautogui.mouseDown()
        elif self.pinched and self.ratio > self.press + self.release_gap:
            self.pinched = False
            pyautogui.mouseUp()

    def release(self):
        if self.pinched:
            self.pinched = False
            pyautogui.mouseUp()
