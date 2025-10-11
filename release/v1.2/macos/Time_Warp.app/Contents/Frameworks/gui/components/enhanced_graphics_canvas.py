#!/usr/bin/env python3
"""
Enhanced Graphics Canvas for Time_Warp IDE
Improved turtle graphics with zoom, export, and grid features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import turtle
import io
from PIL import Image, ImageDraw
from typing import Optional, Tuple
import math


class EnhancedGraphicsCanvas:
    """Enhanced graphics canvas with zoom, export, and grid features"""
    
    def __init__(self, parent_widget, width: int = 800, height: int = 600):
        self.parent = parent_widget
        self.canvas_width = width
        self.canvas_height = height
        self.zoom_level = 1.0
        self.show_grid = False
        self.grid_size = 20
        
        self.setup_ui()
        self.setup_turtle()
        
    def setup_ui(self):
        """Setup the graphics canvas UI"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Graphics controls
        ttk.Label(toolbar_frame, text="🎨 Graphics Canvas", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(toolbar_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Zoom controls
        ttk.Label(toolbar_frame, text="Zoom:").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            toolbar_frame,
            text="➖",
            width=3,
            command=self.zoom_out
        ).pack(side=tk.LEFT, padx=1)
        
        self.zoom_label = ttk.Label(toolbar_frame, text="100%", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar_frame,
            text="➕",
            width=3,
            command=self.zoom_in
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            toolbar_frame,
            text="🔍",
            width=3,
            command=self.zoom_fit
        ).pack(side=tk.LEFT, padx=5)
        
        # Grid toggle
        self.grid_var = tk.BooleanVar()
        grid_check = ttk.Checkbutton(
            toolbar_frame,
            text="Grid",
            variable=self.grid_var,
            command=self.toggle_grid
        )
        grid_check.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(toolbar_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Canvas controls
        ttk.Button(
            toolbar_frame,
            text="🗑️",
            width=3,
            command=self.clear_canvas
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            toolbar_frame,
            text="💾",
            width=3,
            command=self.export_canvas
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            toolbar_frame,
            text="🏠",
            width=3,
            command=self.center_turtle
        ).pack(side=tk.LEFT, padx=1)
        
        # Status bar
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.position_label = ttk.Label(status_frame, text="(0, 0)", relief=tk.SUNKEN, width=15)
        self.position_label.pack(side=tk.RIGHT)
        
        # Canvas frame with scrollbars
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create turtle canvas
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            scrollregion=(0, 0, self.canvas_width, self.canvas_height)
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
    def setup_turtle(self):
        """Setup turtle graphics"""
        # Create turtle screen using the canvas
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor('white')
        
        # Create turtle
        self.turtle = turtle.RawTurtle(self.screen)
        self.turtle.speed(6)
        self.turtle.shape('turtle')
        self.turtle.color('green')
        
        # Draw initial grid if enabled
        if self.show_grid:
            self.draw_grid()
            
    def zoom_in(self):
        """Zoom in on canvas"""
        if self.zoom_level < 3.0:
            self.zoom_level *= 1.2
            self.apply_zoom()
            
    def zoom_out(self):
        """Zoom out on canvas"""
        if self.zoom_level > 0.3:
            self.zoom_level /= 1.2
            self.apply_zoom()
            
    def zoom_fit(self):
        """Reset zoom to fit canvas"""
        self.zoom_level = 1.0
        self.apply_zoom()
        
    def apply_zoom(self):
        """Apply current zoom level to canvas"""
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
        # Scale canvas
        scale_factor = self.zoom_level
        new_width = int(self.canvas_width * scale_factor)
        new_height = int(self.canvas_height * scale_factor)
        
        # Update scroll region
        self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
        
        # Scale all canvas items
        self.canvas.scale('all', self.canvas_width//2, self.canvas_height//2, scale_factor / (self.zoom_level / scale_factor if hasattr(self, '_last_zoom') else 1.0), scale_factor / (self.zoom_level / scale_factor if hasattr(self, '_last_zoom') else 1.0))
        
        self._last_zoom = scale_factor
        
        # Redraw grid if enabled
        if self.show_grid:
            self.draw_grid()
            
    def toggle_grid(self):
        """Toggle coordinate grid display"""
        self.show_grid = self.grid_var.get()
        if self.show_grid:
            self.draw_grid()
        else:
            self.canvas.delete('grid')
            
    def draw_grid(self):
        """Draw coordinate grid on canvas"""
        # Clear existing grid
        self.canvas.delete('grid')
        
        if not self.show_grid:
            return
            
        # Calculate grid parameters
        grid_size = int(self.grid_size * self.zoom_level)
        width = int(self.canvas_width * self.zoom_level)
        height = int(self.canvas_height * self.zoom_level)
        
        # Draw vertical lines
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height, fill='lightgray', tags='grid')
            
        # Draw horizontal lines
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y, fill='lightgray', tags='grid')
            
        # Draw axes
        center_x = width // 2
        center_y = height // 2
        
        # X-axis
        self.canvas.create_line(0, center_y, width, center_y, fill='gray', width=2, tags='grid')
        # Y-axis
        self.canvas.create_line(center_x, 0, center_x, height, fill='gray', width=2, tags='grid')
        
        # Add coordinate labels
        for x in range(-width//2, width//2, grid_size):
            if x != 0:
                canvas_x = center_x + x
                if 0 <= canvas_x <= width:
                    self.canvas.create_text(
                        canvas_x, center_y + 15, 
                        text=str(int(x/self.zoom_level)), 
                        fill='gray', 
                        font=('Arial', 8),
                        tags='grid'
                    )
                    
        for y in range(-height//2, height//2, grid_size):
            if y != 0:
                canvas_y = center_y - y  # Flip Y coordinate
                if 0 <= canvas_y <= height:
                    self.canvas.create_text(
                        center_x - 15, canvas_y, 
                        text=str(int(y/self.zoom_level)), 
                        fill='gray', 
                        font=('Arial', 8),
                        tags='grid'
                    )
                    
    def clear_canvas(self):
        """Clear the graphics canvas"""
        self.canvas.delete('all')
        self.screen.clear()
        if self.show_grid:
            self.draw_grid()
        self.update_status("Canvas cleared")
        
    def center_turtle(self):
        """Move turtle to center of canvas"""
        self.turtle.penup()
        self.turtle.home()
        self.turtle.pendown()
        self.update_status("Turtle centered")
        
    def export_canvas(self):
        """Export canvas as image"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("SVG files", "*.svg"),
                ("PostScript files", "*.ps"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            if file_path.lower().endswith('.svg'):
                self.export_svg(file_path)
            elif file_path.lower().endswith('.ps'):
                self.export_postscript(file_path)
            else:
                self.export_png(file_path)
                
            self.update_status(f"Exported to {file_path}")
            messagebox.showinfo("Export Complete", f"Canvas exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export canvas:\n{str(e)}")
            
    def export_png(self, file_path: str):
        """Export canvas as PNG image"""
        # Get canvas bounds
        x1, y1, x2, y2 = self.canvas.bbox('all')
        if x1 is None:
            # Empty canvas
            x1, y1, x2, y2 = 0, 0, self.canvas_width, self.canvas_height
            
        width = int(x2 - x1)
        height = int(y2 - y1)
        
        # Create image
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Draw canvas items (simplified)
        # This is a basic implementation - for full fidelity, consider using tkinter's postscript export
        for item in self.canvas.find_all():
            if 'grid' not in self.canvas.gettags(item):
                coords = self.canvas.coords(item)
                item_type = self.canvas.type(item)
                
                if item_type == 'line' and len(coords) >= 4:
                    # Adjust coordinates
                    adj_coords = [(coords[i] - x1, coords[i+1] - y1) for i in range(0, len(coords), 2)]
                    if len(adj_coords) >= 2:
                        draw.line(adj_coords, fill='black', width=2)
                        
        image.save(file_path)
        
    def export_svg(self, file_path: str):
        """Export canvas as SVG"""
        # Simple SVG export
        x1, y1, x2, y2 = self.canvas.bbox('all')
        if x1 is None:
            x1, y1, x2, y2 = 0, 0, self.canvas_width, self.canvas_height
            
        width = int(x2 - x1)
        height = int(y2 - y1)
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
<rect width="100%" height="100%" fill="white"/>
'''
        
        # Add canvas items as SVG elements
        for item in self.canvas.find_all():
            if 'grid' not in self.canvas.gettags(item):
                coords = self.canvas.coords(item)
                item_type = self.canvas.type(item)
                
                if item_type == 'line' and len(coords) >= 4:
                    points = ' '.join([f"{coords[i]-x1},{coords[i+1]-y1}" for i in range(0, len(coords), 2)])
                    svg_content += f'<polyline points="{points}" stroke="black" stroke-width="2" fill="none"/>\n'
                    
        svg_content += '</svg>'
        
        with open(file_path, 'w') as f:
            f.write(svg_content)
            
    def export_postscript(self, file_path: str):
        """Export canvas as PostScript"""
        self.canvas.postscript(file=file_path)
        
    def on_canvas_click(self, event):
        """Handle canvas click"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to turtle coordinates
        turtle_x = canvas_x - self.canvas_width // 2
        turtle_y = self.canvas_height // 2 - canvas_y
        
        self.update_position(turtle_x, turtle_y)
        
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        self.on_canvas_click(event)
        
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def on_mouse_move(self, event):
        """Handle mouse movement for position display"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Convert to turtle coordinates
        turtle_x = int(canvas_x - self.canvas_width // 2)
        turtle_y = int(self.canvas_height // 2 - canvas_y)
        
        self.position_label.config(text=f"({turtle_x}, {turtle_y})")
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
        # Clear status after 3 seconds
        self.frame.after(3000, lambda: self.status_label.config(text="Ready"))
        
    def update_position(self, x: float, y: float):
        """Update position display"""
        self.position_label.config(text=f"({int(x)}, {int(y)})")
        
    def get_turtle(self) -> turtle.RawTurtle:
        """Get the turtle object"""
        return self.turtle
        
    def get_screen(self) -> turtle.TurtleScreen:
        """Get the turtle screen object"""
        return self.screen
        
    def get_canvas(self) -> tk.Canvas:
        """Get the canvas object"""
        return self.canvas
    
    def apply_theme(self, colors):
        """Apply theme colors to graphics canvas"""
        try:
            # Apply theme to canvas
            self.canvas.configure(
                bg=colors["bg_primary"],
                highlightcolor=colors["accent"],
                highlightbackground=colors["border"]
            )
            
            # Apply theme to turtle screen
            self.screen.bgcolor(colors["bg_primary"])
            
            # Update main frame background
            self.frame.configure(style="Modern.TFrame")
            
            # Update status bar
            self.status_label.configure(
                background=colors["bg_secondary"],
                foreground=colors["text_primary"]
            )
            self.position_label.configure(
                background=colors["bg_secondary"],
                foreground=colors["text_primary"]
            )
            
        except Exception as e:
            print(f"⚠️ EnhancedGraphicsCanvas theme error: {e}")