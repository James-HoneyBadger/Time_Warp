"""
Timing utilities for Time_Warp
Handles delays, timers, and time-based events.
"""


class Timer:
    """Simple timer that triggers after a specified delay"""

    def __init__(self, delay_ms: int, label: str):
        self.delay = max(0, int(delay_ms))
        self.label = label
        self.t = 0
        self.done = False

    def step(self, dt):
        """Update the timer by dt milliseconds"""
        if self.done:
            return

        self.t += dt
        if self.t >= self.delay:
            self.done = True
