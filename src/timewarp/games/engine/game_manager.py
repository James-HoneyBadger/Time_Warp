"""
Game Manager for Time_Warp Game Engine
Main game management system with game loop and object management.
"""

from .physics import PhysicsEngine
from .game_renderer import GameRenderer
from .game_objects import GameObject, Vector2D


class GameManager:
    """Main game management system"""

    def __init__(self, canvas=None):
        self.canvas = canvas
        self.physics = PhysicsEngine()
        self.physics_engine = self.physics  # Alias for compatibility
        self.renderer = GameRenderer(canvas) if canvas else None
        self.game_objects = {}  # name -> object mapping
        self.objects = self.game_objects  # Alias for compatibility
        self.running = False
        self.last_time = 0
        self.fps = 60
        self.frame_time = 1000 / self.fps  # milliseconds
        self.output_callback = None
        self.game_loop_id = None
        self.input_keys = set()
        self.mouse_pos = Vector2D(0, 0)
        self.mouse_pressed = False

        # Game statistics
        self.frame_count = 0
        self.total_time = 0

        # Initialize physics world
        self.physics.world_bounds = {
            "width": canvas.winfo_reqwidth() if canvas else 800,
            "height": canvas.winfo_reqheight() if canvas else 600,
        }

    def set_output_callback(self, callback):
        """Set callback for game messages"""
        self.output_callback = callback

    def log_game_message(self, message):
        """Log game-related messages"""
        if self.output_callback:
            self.output_callback(f"🎮 Game: {message}")
        else:
            print(f"🎮 Game: {message}")

    def create_object(self, name, obj_type, x, y, width=32, height=32, color="blue"):
        """Create a new game object"""
        obj = GameObject(x, y, width, height)
        obj.color = color
        obj.obj_type = obj_type  # Store object type
        self.game_objects[name] = obj
        self.physics.add_object(obj)
        return True

    def get_object(self, name):
        """Get game object by name"""
        return self.game_objects.get(name)

    def remove_object(self, name):
        """Remove game object"""
        if name in self.game_objects:
            obj = self.game_objects[name]
            self.physics.remove_object(obj)
            del self.game_objects[name]

    def create_platform(self, x, y, width, height):
        """Create a static platform"""
        return self.physics.add_static_object(x, y, width, height)

    def apply_force_to_object(self, name, fx, fy):
        """Apply force to named object"""
        obj = self.get_object(name)
        if obj:
            obj.apply_force(Vector2D(fx, fy))

    def set_object_velocity(self, name, vx, vy):
        """Set object velocity directly"""
        obj = self.get_object(name)
        if obj:
            obj.velocity = Vector2D(vx, vy)

    def move_object(self, name, x, y):
        """Move object to specific position"""
        obj = self.get_object(name)
        if obj:
            obj.position = Vector2D(x, y)

    def start_game_loop(self):
        """Start the game loop"""
        if not self.running and self.canvas:
            self.running = True
            self.last_time = self.canvas.tk.call("clock", "milliseconds")
            self._game_loop()

    def stop_game_loop(self):
        """Stop the game loop"""
        self.running = False
        if self.game_loop_id and self.canvas:
            self.canvas.after_cancel(self.game_loop_id)

    def _game_loop(self):
        """Main game loop"""
        if not self.running or not self.canvas:
            return

        current_time = self.canvas.tk.call("clock", "milliseconds")
        dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
        dt = min(dt, 1.0 / 30.0)  # Cap at 30 FPS minimum to prevent large jumps

        # Update physics
        self.physics.step(dt)

        # Render everything
        if self.renderer:
            self.renderer.clear()

            # Draw static objects
            for static_obj in self.physics.static_objects:
                self.renderer.draw_static_object(static_obj)

            # Draw game objects
            for obj in self.game_objects.values():
                self.renderer.draw_object(obj)

        # Update statistics
        self.frame_count += 1
        self.total_time += dt

        self.last_time = current_time

        # Schedule next frame
        self.game_loop_id = self.canvas.after(int(self.frame_time), self._game_loop)

    def get_object_info(self, name):
        """Get object information for debugging"""
        obj = self.get_object(name)
        if obj:
            return {
                "position": (obj.position.x, obj.position.y),
                "velocity": (obj.velocity.x, obj.velocity.y),
                "on_ground": obj.on_ground,
                "active": obj.active,
                "bounds": obj.get_bounds(),
            }
        return None

    def reset_world(self):
        """Reset the game world"""
        self.stop_game_loop()
        self.game_objects.clear()
        self.physics.objects.clear()
        self.physics.static_objects.clear()
        if self.renderer:
            self.renderer.clear()
        self.frame_count = 0
        self.total_time = 0

    def render_scene(self, canvas_name=None):
        """Render the current game scene"""
        if not self.renderer:
            return False

        try:
            self.renderer.clear()

            # Draw all game objects
            for obj in self.game_objects.values():
                self.renderer.draw_object(obj)

            # Draw static objects
            for static_obj in self.physics.static_objects:
                self.renderer.draw_static_object(static_obj)

            return True
        except Exception as e:
            print(f"Render error: {e}")
            return False
