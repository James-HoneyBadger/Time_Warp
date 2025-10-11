"""
Particle system utilities for Time_Warp
Handles particle effects and visual effects.
"""


class Particle:
    """Individual particle with position, velocity, and lifetime"""

    def __init__(self, x, y, vx, vy, life_ms, color="#ffaa33", size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life_ms
        self.color = color
        self.size = size

    def step(self, dt):
        """Update particle position and lifetime"""
        self.x += self.vx * (dt / 1000.0)
        self.y += self.vy * (dt / 1000.0)
        self.vy -= 30 * (dt / 1000.0)  # Simple gravity
        self.life -= dt
