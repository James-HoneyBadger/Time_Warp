"""
Hardware Integration Module
Raspberry Pi GPIO control and sensor interfaces.
"""

import os
import time


class RPiController:
    """Raspberry Pi GPIO Controller with simulation fallback"""

    def __init__(self):
        self.gpio_available = False
        self.pin_states = {}
        self.GPIO = None

        # Try to import RPi.GPIO with comprehensive error handling
        try:
            # Direct import attempt - simpler and more reliable
            import RPi.GPIO as GPIO

            self.GPIO = GPIO
            self.gpio_available = True
            GPIO.setmode(GPIO.BCM)
            print("🤖 Hardware: Raspberry Pi GPIO initialized")
        except (ModuleNotFoundError, ImportError, Exception) as e:
            # RPi.GPIO not available or failed to initialize - use simulation mode
            self.GPIO = None
            self.gpio_available = False
            print(
                "🤖 Hardware: Raspberry Pi GPIO simulation mode (RPi.GPIO not available)"
            )
        # Continue in simulation mode if hardware not available

    def set_pin_mode(self, pin, mode):
        """Set pin as input or output"""
        if self.gpio_available and self.GPIO:
            try:
                if mode.upper() == "OUTPUT":
                    self.GPIO.setup(pin, self.GPIO.OUT)
                elif mode.upper() == "INPUT":
                    self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
                return True
            except Exception as e:
                print(f"Pin setup failed: {e}")
        else:
            self.pin_states[pin] = {"mode": mode, "value": 0}
            print(f"[SIM] Pin {pin} mode set to {mode}")
        return True  # Return True for simulation mode too

    def digital_write(self, pin, value):
        """Write digital value to pin"""
        if self.gpio_available and self.GPIO:
            try:
                self.GPIO.output(pin, self.GPIO.HIGH if value else self.GPIO.LOW)
                return True
            except Exception as e:
                print(f"Digital write failed: {e}")
        else:
            if pin in self.pin_states:
                self.pin_states[pin]["value"] = 1 if value else 0
                print(f"[SIM] Pin {pin} = {self.pin_states[pin]['value']}")
            else:
                self.pin_states[pin] = {"mode": "OUTPUT", "value": 1 if value else 0}
                print(f"[SIM] Pin {pin} = {self.pin_states[pin]['value']}")
        return True  # Return True for simulation mode too

    def digital_read(self, pin):
        """Read digital value from pin"""
        if self.gpio_available and self.GPIO:
            try:
                return self.GPIO.input(pin) == self.GPIO.HIGH
            except Exception as e:
                print(f"Digital read failed: {e}")
        else:
            return self.pin_states.get(pin, {"value": 0})["value"] == 1
        return False

    def cleanup(self):
        """Clean up GPIO resources"""
        if self.gpio_available and self.GPIO:
            try:
                self.GPIO.cleanup()
            except Exception as e:
                print(f"GPIO cleanup failed: {e}")


class SensorVisualizer:
    """Sensor Data Visualization for hardware interfaces"""

    def __init__(self, canvas):
        self.canvas = canvas
        self.data_history = {}
        self.max_history = 100
        self.chart_colors = ["red", "blue", "green", "orange", "purple"]

    def add_data_point(self, sensor_name, value):
        """Add sensor data point for visualization"""
        if sensor_name not in self.data_history:
            self.data_history[sensor_name] = []

        self.data_history[sensor_name].append(value)

        # Keep only max_history points
        if len(self.data_history[sensor_name]) > self.max_history:
            self.data_history[sensor_name].pop(0)

        self.update_chart()

    def update_chart(self):
        """Update the visualization chart"""
        if not self.canvas:
            return

        # Clear previous chart
        self.canvas.delete("sensor_chart")

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # Draw axes
        margin = 40
        chart_width = canvas_width - 2 * margin
        chart_height = canvas_height - 2 * margin

        # X-axis
        self.canvas.create_line(
            margin,
            canvas_height - margin,
            canvas_width - margin,
            canvas_height - margin,
            fill="black",
            tags="sensor_chart",
        )

        # Y-axis
        self.canvas.create_line(
            margin,
            margin,
            margin,
            canvas_height - margin,
            fill="black",
            tags="sensor_chart",
        )

        # Plot data for each sensor
        color_index = 0
        for sensor_name, data in self.data_history.items():
            if len(data) < 2:
                continue

            color = self.chart_colors[color_index % len(self.chart_colors)]
            color_index += 1

            # Find min/max for scaling
            min_val = min(data)
            max_val = max(data)
            val_range = max_val - min_val if max_val != min_val else 1

            points = []
            for i, value in enumerate(data):
                x = margin + (i / (len(data) - 1)) * chart_width
                y = (
                    canvas_height
                    - margin
                    - ((value - min_val) / val_range) * chart_height
                )
                points.extend([x, y])

            if len(points) >= 4:
                self.canvas.create_line(
                    *points, fill=color, width=2, tags="sensor_chart", smooth=True
                )

            # Add legend
            legend_y = margin + color_index * 20
            self.canvas.create_text(
                canvas_width - margin - 60,
                legend_y,
                text=sensor_name,
                fill=color,
                tags="sensor_chart",
            )


class GameController:
    """Game controller interface for hardware input"""

    def __init__(self):
        self.pygame_available = False
        self.joysticks = []
        self.button_states = {}

        try:
            import pygame

            pygame.init()
            pygame.joystick.init()
            self.pygame_available = True

            # Initialize joysticks
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.joysticks.append(joystick)
                print(f"🎮 Controller {i}: {joystick.get_name()}")

        except ImportError:
            print("🎮 Pygame not available - controller simulation mode")
        except Exception as e:
            print(f"🎮 Controller initialization failed: {e}")

    def get_button_state(self, controller_id, button_id):
        """Get button state (True/False)"""
        if not self.pygame_available or controller_id >= len(self.joysticks):
            # Simulation mode - return random state for demo
            import random

            return random.choice([True, False])

        try:
            joystick = self.joysticks[controller_id]
            return joystick.get_button(button_id) == 1
        except Exception:
            return False

    def get_axis_value(self, controller_id, axis_id):
        """Get analog stick/trigger value (-1.0 to 1.0)"""
        if not self.pygame_available or controller_id >= len(self.joysticks):
            # Simulation mode
            import random

            return random.uniform(-1.0, 1.0)

        try:
            joystick = self.joysticks[controller_id]
            return joystick.get_axis(axis_id)
        except Exception:
            return 0.0

    def update(self):
        """Update controller state (call regularly)"""
        if self.pygame_available:
            try:
                import pygame

                pygame.event.pump()
            except Exception:
                pass


class RobotInterface:
    """Basic robot control interface"""

    def __init__(self):
        self.motor_speeds = {"left": 0, "right": 0}
        self.servo_positions = {}
        self.sensor_values = {}
        self.serial_connection = None

    def connect_serial(self, port="/dev/ttyUSB0", baud_rate=9600):
        """Connect to robot via serial"""
        try:
            import serial

            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            print(f"🤖 Robot connected via {port}")
            return True
        except ImportError:
            print("🤖 PySerial not available - robot simulation mode")
            return False
        except Exception as e:
            print(f"🤖 Robot connection failed: {e}")
            return False

    def send_command(self, command):
        """Send command to robot"""
        if self.serial_connection:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                return True
            except Exception as e:
                print(f"🤖 Command send failed: {e}")
                return False
        else:
            print(f"🤖 [SIM] Robot command: {command}")
            return True

    def set_motor_speed(self, left_speed, right_speed):
        """Set motor speeds (-100 to 100)"""
        self.motor_speeds["left"] = max(-100, min(100, left_speed))
        self.motor_speeds["right"] = max(-100, min(100, right_speed))

        command = f"MOTOR,{self.motor_speeds['left']},{self.motor_speeds['right']}"
        return self.send_command(command)

    def set_servo_position(self, servo_id, position):
        """Set servo position (0-180 degrees)"""
        position = max(0, min(180, position))
        self.servo_positions[servo_id] = position

        command = f"SERVO,{servo_id},{position}"
        return self.send_command(command)

    def read_sensor(self, sensor_id):
        """Read sensor value"""
        if self.serial_connection:
            try:
                self.send_command(f"READ,{sensor_id}")
                response = self.serial_connection.readline().decode().strip()
                value = float(response)
                self.sensor_values[sensor_id] = value
                return value
            except Exception as e:
                print(f"🤖 Sensor read failed: {e}")
                return 0
        else:
            # Simulation mode - return random sensor data
            import random

            value = random.uniform(0, 100)
            self.sensor_values[sensor_id] = value
            return value

    def stop_all_motors(self):
        """Emergency stop all motors"""
        return self.set_motor_speed(0, 0)

    def disconnect(self):
        """Disconnect from robot"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            print("🤖 Robot disconnected")
