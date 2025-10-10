"""
Physics Engine for Time_Warp Games
2D physics simulation with collision detection and response.
"""

from .game_objects import Vector2D


class PhysicsEngine:
    """2D Physics engine for game objects"""

    def __init__(self):
        self.gravity = Vector2D(0, 9.8 * 60)  # 60 pixels = 1 meter, earth gravity
        self.world_bounds = {"width": 800, "height": 600}
        self.objects = []
        self.collision_pairs = []
        self.static_objects = []  # Platforms, walls, etc.

    def add_object(self, obj):
        """Add object to physics simulation"""
        if obj not in self.objects:
            self.objects.append(obj)

    def remove_object(self, obj):
        """Remove object from physics simulation"""
        if obj in self.objects:
            self.objects.remove(obj)

    def add_static_object(self, x, y, width, height):
        """Add static collision object (platform, wall)"""
        static_obj = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "left": x,
            "right": x + width,
            "top": y,
            "bottom": y + height,
        }
        self.static_objects.append(static_obj)
        return static_obj

    def check_collision_with_static(self, obj):
        """Check collision with static objects"""
        bounds = obj.get_bounds()
        collisions = []

        for static in self.static_objects:
            if not (
                bounds["right"] < static["left"]
                or bounds["left"] > static["right"]
                or bounds["bottom"] < static["top"]
                or bounds["top"] > static["bottom"]
            ):
                collisions.append(static)

        return collisions

    def resolve_collision_with_static(self, obj, static):
        """Resolve collision between object and static object"""
        bounds = obj.get_bounds()

        # Calculate overlap on each axis
        overlap_x = min(
            bounds["right"] - static["left"], static["right"] - bounds["left"]
        )
        overlap_y = min(
            bounds["bottom"] - static["top"], static["bottom"] - bounds["top"]
        )

        # Resolve collision on the axis with smallest overlap
        if overlap_x < overlap_y:
            # Horizontal collision
            if bounds["center_x"] < static["x"] + static["width"] / 2:
                # Object is to the left of static
                obj.position.x = static["left"] - obj.width
                if obj.velocity.x > 0:
                    obj.velocity.x = -obj.velocity.x * obj.bounce
            else:
                # Object is to the right of static
                obj.position.x = static["right"]
                if obj.velocity.x < 0:
                    obj.velocity.x = -obj.velocity.x * obj.bounce
        else:
            # Vertical collision
            if bounds["center_y"] < static["y"] + static["height"] / 2:
                # Object is above static (landing on top)
                obj.position.y = static["top"] - obj.height
                obj.on_ground = True
                if obj.velocity.y > 0:
                    obj.velocity.y = -obj.velocity.y * obj.bounce
            else:
                # Object is below static (hitting from below)
                obj.position.y = static["bottom"]
                if obj.velocity.y < 0:
                    obj.velocity.y = -obj.velocity.y * obj.bounce

    def check_world_bounds(self, obj):
        """Check and resolve collision with world boundaries"""
        bounds = obj.get_bounds()

        # Left boundary
        if bounds["left"] < 0:
            obj.position.x = 0
            if obj.velocity.x < 0:
                obj.velocity.x = -obj.velocity.x * obj.bounce

        # Right boundary
        if bounds["right"] > self.world_bounds["width"]:
            obj.position.x = self.world_bounds["width"] - obj.width
            if obj.velocity.x > 0:
                obj.velocity.x = -obj.velocity.x * obj.bounce

        # Top boundary
        if bounds["top"] < 0:
            obj.position.y = 0
            if obj.velocity.y < 0:
                obj.velocity.y = -obj.velocity.y * obj.bounce

        # Bottom boundary
        if bounds["bottom"] > self.world_bounds["height"]:
            obj.position.y = self.world_bounds["height"] - obj.height
            obj.on_ground = True
            if obj.velocity.y > 0:
                obj.velocity.y = -obj.velocity.y * obj.bounce

    def step(self, dt):
        """Step physics simulation forward"""
        for obj in self.objects:
            if not obj.active:
                continue

            # Reset ground state
            obj.on_ground = False

            # Apply gravity
            gravity_force = Vector2D(
                self.gravity.x * obj.gravity_scale, self.gravity.y * obj.gravity_scale
            )
            obj.apply_force(gravity_force)

            # Update physics
            obj.update(dt)

            # Check collisions with static objects
            collisions = self.check_collision_with_static(obj)
            for static in collisions:
                self.resolve_collision_with_static(obj, static)

            # Check world boundaries
            self.check_world_bounds(obj)

    def check_collision(self, obj1, obj2):
        """Check collision between two objects"""
        # Simple AABB collision detection
        obj1_left = obj1.position.x
        obj1_right = obj1.position.x + obj1.width
        obj1_top = obj1.position.y
        obj1_bottom = obj1.position.y + obj1.height

        obj2_left = obj2.position.x
        obj2_right = obj2.position.x + obj2.width
        obj2_top = obj2.position.y
        obj2_bottom = obj2.position.y + obj2.height

        # Check for overlap
        return (
            obj1_left < obj2_right
            and obj1_right > obj2_left
            and obj1_top < obj2_bottom
            and obj1_bottom > obj2_top
        )
