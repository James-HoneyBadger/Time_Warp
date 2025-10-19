"""
Animation utilities for Time_Warp
Handles tweening and smooth transitions.
"""

# Easing functions for smooth animations
EASE = {
    "linear": lambda t: t,
    "quadOut": lambda t: 1 - (1 - t) * (1 - t),
    "quadIn": lambda t: t * t,
    "smooth": lambda t: t * t * (3 - 2 * t),
}


class Tween:
    """Smooth transition between two values over time"""

    def __init__(
        self,
        store: dict,
        key: str,
        a: float,
        b: float,
        dur_ms: int,
        ease: str = "linear",
    ):
        self.store = store
        self.key = key
        self.a = float(a)
        self.b = float(b)
        self.dur = max(1, int(dur_ms))
        self.t = 0
        self.ease = EASE.get(ease, EASE["linear"])
        self.done = False

    def step(self, dt):
        """Update the tween by dt milliseconds"""
        if self.done:
            return

        self.t += dt
        u = min(1.0, self.t / self.dur)
        k = self.ease(u)
        self.store[self.key] = self.a + (self.b - self.a) * k

        if self.t >= self.dur:
            self.store[self.key] = self.b
            self.done = True
