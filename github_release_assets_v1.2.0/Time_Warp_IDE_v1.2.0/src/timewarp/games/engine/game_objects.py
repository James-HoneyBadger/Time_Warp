"""
Game Objects for Time_Warp Game Engine
Base classes for game entities with physics properties.
"""


# Need to import Vector2D from the core physics
# For now using a simple implementation
class Vector2D:
    """2D Vector class for physics calculations"""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __repr__(self):
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"

    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5

    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        return (self - other).magnitude()


class GameObject:
    """Base game object with physics properties"""

    def __init__(self, x=0, y=0, width=32, height=32):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
        self.width = width
        self.height = height
        self.mass = 1.0
        self.bounce = 0.8  # Restitution coefficient
        self.friction = 0.98
        self.gravity_scale = 1.0
        self.active = True
        self.visible = True
        self.color = "blue"
        self.sprite_data = None
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.last_animation_time = 0
        self.collision_layer = 0
        self.collision_mask = 1
        self.on_ground = False
        self.obj_type = "default"

    def get_bounds(self):
        """Get bounding rectangle"""
        return {
            "left": self.position.x,
            "right": self.position.x + self.width,
            "top": self.position.y,
            "bottom": self.position.y + self.height,
            "center_x": self.position.x + self.width / 2,
            "center_y": self.position.y + self.height / 2,
        }

    def overlaps(self, other):
        """Check if this object overlaps with another"""
        bounds1 = self.get_bounds()
        bounds2 = other.get_bounds()

        return not (
            bounds1["right"] < bounds2["left"]
            or bounds1["left"] > bounds2["right"]
            or bounds1["bottom"] < bounds2["top"]
            or bounds1["top"] > bounds2["bottom"]
        )

    def apply_force(self, force):
        """Apply force to object (F = ma, so a = F/m)"""
        # Ensure force is a Vector2D
        if not isinstance(force, Vector2D):
            force = (
                Vector2D(force, 0)
                if isinstance(force, (int, float))
                else Vector2D(0, 0)
            )
        # Calculate acceleration from force (a = F/m)
        acceleration_delta = Vector2D(force.x / self.mass, force.y / self.mass)
        self.acceleration.x += acceleration_delta.x
        self.acceleration.y += acceleration_delta.y

    def update(self, dt):
        """Update object physics"""
        if not self.active:
            return

        # Apply acceleration to velocity
        self.velocity.x += self.acceleration.x * dt
        self.velocity.y += self.acceleration.y * dt

        # Apply friction
        self.velocity.x *= self.friction
        self.velocity.y *= self.friction

        # Apply velocity to position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt

        # Reset acceleration for next frame
        self.acceleration.x = 0
        self.acceleration.y = 0
