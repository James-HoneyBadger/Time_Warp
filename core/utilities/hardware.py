"""
Hardware integration utilities for Time_Warp
Handles Arduino, GPIO, and sensor interfacing.
"""


class ArduinoController:
    """Arduino/Serial Communication controller"""

    def __init__(self):
        self.connection = None
        self.port = None
        self.baud_rate = 9600
        self.connected = False

    def connect(self, port="/dev/ttyUSB0", baud_rate=9600):
        """Connect to Arduino via serial port"""
        try:
            import serial

            self.connection = serial.Serial(port, baud_rate, timeout=1)
            self.port = port
            self.baud_rate = baud_rate
            self.connected = True
            return True
        except ImportError:
            print("PySerial not installed. Install with: pip install pyserial")
            return False
        except Exception as e:
            print(f"Arduino connection failed: {e}")
            return False

    def send_command(self, command):
        """Send command to Arduino"""
        if self.connected and self.connection:
            try:
                self.connection.write(f"{command}\\n".encode())
                return True
            except Exception as e:
                print(f"Send failed: {e}")
                return False
        return False

    def read_sensor(self):
        """Read sensor data from Arduino"""
        if self.connected and self.connection:
            try:
                if self.connection.in_waiting > 0:
                    data = self.connection.readline().decode().strip()
                    return data
            except Exception as e:
                print(f"Read failed: {e}")
        return None

    def disconnect(self):
        """Disconnect from Arduino"""
        if self.connection:
            self.connection.close()
            self.connected = False
