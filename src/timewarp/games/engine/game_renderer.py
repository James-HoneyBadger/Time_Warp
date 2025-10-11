"""
Game Renderer for Time_Warp Game Engine
Handles rendering of game objects to tkinter canvas.
"""


class GameRenderer:
    """Render game objects to canvas"""

    def __init__(self, canvas=None):
        self.canvas = canvas
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.debug_draw = False

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.camera_x) * self.zoom
        screen_y = (world_y - self.camera_y) * self.zoom
        return screen_x, screen_y

    def clear(self):
        """Clear the canvas"""
        if self.canvas:
            self.canvas.delete("game_object")

    def draw_object(self, obj):
        """Draw a game object"""
        if not self.canvas or not obj.visible:
            return

        screen_x, screen_y = self.world_to_screen(obj.position.x, obj.position.y)
        screen_w = obj.width * self.zoom
        screen_h = obj.height * self.zoom

        # Draw object rectangle
        rect_id = self.canvas.create_rectangle(
            screen_x,
            screen_y,
            screen_x + screen_w,
            screen_y + screen_h,
            fill=obj.color,
            outline="black",
            tags="game_object",
        )

        if self.debug_draw:
            # Draw velocity vector
            vel_scale = 2.0
            vel_end_x = (
                screen_x + obj.width / 2 + obj.velocity.x * vel_scale * self.zoom
            )
            vel_end_y = (
                screen_y + obj.height / 2 + obj.velocity.y * vel_scale * self.zoom
            )

            self.canvas.create_line(
                screen_x + obj.width / 2,
                screen_y + obj.height / 2,
                vel_end_x,
                vel_end_y,
                fill="red",
                width=2,
                tags="game_object",
            )

    def draw_static_object(self, static_obj):
        """Draw a static object (platform, wall, etc.)"""
        if not self.canvas:
            return

        screen_x, screen_y = self.world_to_screen(static_obj["x"], static_obj["y"])
        screen_w = static_obj["width"] * self.zoom
        screen_h = static_obj["height"] * self.zoom

        # Draw static object as a gray rectangle
        self.canvas.create_rectangle(
            screen_x,
            screen_y,
            screen_x + screen_w,
            screen_y + screen_h,
            fill="gray",
            outline="darkgray",
            tags="game_object",
        )

    def set_camera(self, x, y):
        """Set camera position"""
        self.camera_x = x
        self.camera_y = y

    def set_zoom(self, zoom):
        """Set zoom level"""
        self.zoom = max(0.1, min(10.0, zoom))  # Clamp between 0.1 and 10.0

    def toggle_debug_draw(self):
        """Toggle debug drawing mode"""
        self.debug_draw = not self.debug_draw
