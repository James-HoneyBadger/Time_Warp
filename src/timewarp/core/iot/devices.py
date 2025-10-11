"""
IoT Device Management System
Smart home and IoT device integration for Time_Warp.
"""

import time
import random
import json
from datetime import datetime


class IoTDevice:
    """Base class for IoT devices"""

    def __init__(self, device_id, device_type, ip_address=None):
        self.device_id = device_id
        self.device_type = device_type
        self.ip_address = ip_address
        self.connected = False
        self.last_data = {}
        self.properties = {}

    def connect(self):
        """Connect to the IoT device"""
        # Simulate connection
        self.connected = True
        return True

    def disconnect(self):
        """Disconnect from the IoT device"""
        self.connected = False

    def send_command(self, command, params=None):
        """Send command to IoT device"""
        if not self.connected:
            return {"error": "Device not connected"}
        # Simulate command response
        return {"status": "ok", "command": command, "params": params}

    def read_data(self):
        """Read current data from device"""
        if not self.connected:
            return None
        # Simulate device data based on type
        if self.device_type == "temperature":
            self.last_data = {
                "temperature": round(random.uniform(18.0, 25.0), 1),
                "timestamp": time.time(),
            }
        elif self.device_type == "humidity":
            self.last_data = {
                "humidity": round(random.uniform(40.0, 70.0), 1),
                "timestamp": time.time(),
            }
        elif self.device_type == "light":
            self.last_data = {
                "brightness": random.randint(0, 100),
                "timestamp": time.time(),
            }
        elif self.device_type == "motion":
            self.last_data = {
                "motion_detected": random.choice([True, False]),
                "timestamp": time.time(),
            }
        elif self.device_type == "camera":
            self.last_data = {
                "recording": random.choice([True, False]),
                "timestamp": time.time(),
            }
        return self.last_data


class IoTDeviceManager:
    """Advanced IoT Device Management System"""

    def __init__(self):
        self.devices = {}
        self.device_groups = {}
        self.automation_rules = []
        self.data_history = {}
        self.discovery_enabled = False

    def discover_devices(self, network_range="192.168.1.0/24"):
        """Discover IoT devices on the network"""
        # Simulate device discovery
        discovered = [
            {
                "id": "temp_01",
                "type": "temperature",
                "ip": "192.168.1.101",
                "name": "Living Room Temp",
            },
            {
                "id": "humid_01",
                "type": "humidity",
                "ip": "192.168.1.102",
                "name": "Kitchen Humidity",
            },
            {
                "id": "light_01",
                "type": "light",
                "ip": "192.168.1.103",
                "name": "Bedroom Light",
            },
            {
                "id": "motion_01",
                "type": "motion",
                "ip": "192.168.1.104",
                "name": "Hallway Motion",
            },
            {
                "id": "cam_01",
                "type": "camera",
                "ip": "192.168.1.105",
                "name": "Front Door Camera",
            },
        ]

        for dev_info in discovered:
            device = IoTDevice(dev_info["id"], dev_info["type"], dev_info["ip"])
            device.properties["name"] = dev_info["name"]
            self.devices[dev_info["id"]] = device

        return len(discovered)

    def add_device(self, device_id, device_type, ip_address=None, properties=None):
        """Manually add an IoT device"""
        device = IoTDevice(device_id, device_type, ip_address)
        if properties:
            device.properties.update(properties)
        self.devices[device_id] = device
        return device

    def connect_device(self, device_id):
        """Connect to a specific device"""
        if device_id in self.devices:
            return self.devices[device_id].connect()
        return False

    def connect_all(self):
        """Connect to all discovered devices"""
        connected = 0
        for device in self.devices.values():
            if device.connect():
                connected += 1
        return connected

    def get_device_data(self, device_id):
        """Get current data from a device"""
        if device_id in self.devices:
            data = self.devices[device_id].read_data()
            if data:
                # Store in history
                if device_id not in self.data_history:
                    self.data_history[device_id] = []
                self.data_history[device_id].append(data)
                # Keep only recent history
                if len(self.data_history[device_id]) > 1000:
                    self.data_history[device_id] = self.data_history[device_id][-1000:]
            return data
        return None

    def get_all_data(self):
        """Get data from all connected devices"""
        all_data = {}
        for device_id in self.devices:
            data = self.get_device_data(device_id)
            if data:
                all_data[device_id] = data
        return all_data

    def create_device_group(self, group_name, device_ids):
        """Create a group of devices for batch operations"""
        self.device_groups[group_name] = device_ids

    def control_group(self, group_name, command, params=None):
        """Send command to all devices in a group"""
        if group_name not in self.device_groups:
            return {"error": "Group not found"}

        results = {}
        for device_id in self.device_groups[group_name]:
            if device_id in self.devices:
                result = self.devices[device_id].send_command(command, params)
                results[device_id] = result
        return results

    def add_automation_rule(self, rule_name, condition, action):
        """Add automation rule (trigger -> action)"""
        rule = {
            "name": rule_name,
            "condition": condition,  # e.g., {"device": "motion_01", "property": "motion_detected", "value": True}
            "action": action,  # e.g., {"device": "light_01", "command": "turn_on"}
            "enabled": True,
        }
        self.automation_rules.append(rule)

    def check_automation_rules(self):
        """Check and execute automation rules"""
        for rule in self.automation_rules:
            if not rule["enabled"]:
                continue

            # Check condition
            condition = rule["condition"]
            device_id = condition.get("device")
            if device_id in self.devices:
                data = self.devices[device_id].last_data
                property_name = condition.get("property")
                expected_value = condition.get("value")

                if property_name in data and data[property_name] == expected_value:
                    # Execute action
                    action = rule["action"]
                    target_device = action.get("device")
                    command = action.get("command")
                    params = action.get("params")

                    if target_device in self.devices:
                        self.devices[target_device].send_command(command, params)
                        print(f"🏠 Automation: {rule['name']} triggered")


class SmartHomeHub:
    """Smart Home Management Hub"""

    def __init__(self):
        self.iot_manager = IoTDeviceManager()
        self.scenes = {}
        self.schedules = []
        self.security_mode = False
        self.energy_monitoring = {}

    def create_scene(self, scene_name, device_settings):
        """Create a scene with specific device settings"""
        self.scenes[scene_name] = device_settings

    def activate_scene(self, scene_name):
        """Activate a predefined scene"""
        if scene_name not in self.scenes:
            return False

        scene = self.scenes[scene_name]
        for device_id, settings in scene.items():
            if device_id in self.iot_manager.devices:
                for command, params in settings.items():
                    self.iot_manager.devices[device_id].send_command(command, params)

        print(f"🏠 Scene '{scene_name}' activated")
        return True

    def set_security_mode(self, enabled):
        """Enable/disable security mode"""
        self.security_mode = enabled

        # Configure security devices
        for device in self.iot_manager.devices.values():
            if device.device_type in ["motion", "camera", "door"]:
                command = "enable_security" if enabled else "disable_security"
                device.send_command(command)

        print(f"🔒 Security mode: {'ON' if enabled else 'OFF'}")

    def get_energy_usage(self):
        """Get energy usage data"""
        # Simulate energy monitoring
        usage = {}
        for device_id, device in self.iot_manager.devices.items():
            if device.device_type in ["light", "appliance"]:
                usage[device_id] = {
                    "current_power": random.uniform(5, 100),  # Watts
                    "daily_usage": random.uniform(0.5, 10),  # kWh
                    "cost": random.uniform(0.05, 1.0),  # USD
                }
        return usage

    def optimize_energy(self):
        """Optimize energy usage across devices"""
        usage = self.get_energy_usage()
        optimizations = []

        for device_id, stats in usage.items():
            if stats["current_power"] > 50:  # High power usage
                optimizations.append(
                    {
                        "device": device_id,
                        "suggestion": "Consider dimming or scheduling",
                        "potential_savings": stats["current_power"] * 0.3,
                    }
                )

        return optimizations


class SensorNetwork:
    """Environmental Sensor Network Management"""

    def __init__(self):
        self.sensors = {}
        self.data_streams = {}
        self.alerts = []
        self.thresholds = {}

    def add_sensor(self, sensor_id, sensor_type, location, calibration=None):
        """Add a sensor to the network"""
        sensor = {
            "id": sensor_id,
            "type": sensor_type,
            "location": location,
            "calibration": calibration or {"offset": 0, "scale": 1},
            "status": "active",
            "last_reading": None,
            "last_update": None,
        }
        self.sensors[sensor_id] = sensor
        self.data_streams[sensor_id] = []

    def read_sensor(self, sensor_id):
        """Read data from a specific sensor"""
        if sensor_id not in self.sensors:
            return None

        sensor = self.sensors[sensor_id]

        # Simulate sensor readings based on type
        if sensor["type"] == "temperature":
            raw_value = random.uniform(15, 30)
        elif sensor["type"] == "humidity":
            raw_value = random.uniform(30, 80)
        elif sensor["type"] == "pressure":
            raw_value = random.uniform(990, 1030)
        elif sensor["type"] == "co2":
            raw_value = random.uniform(300, 1000)
        elif sensor["type"] == "light":
            raw_value = random.uniform(0, 10000)
        else:
            raw_value = random.uniform(0, 100)

        # Apply calibration
        calibrated_value = (raw_value + sensor["calibration"]["offset"]) * sensor[
            "calibration"
        ]["scale"]

        reading = {
            "sensor_id": sensor_id,
            "value": round(calibrated_value, 2),
            "timestamp": time.time(),
            "location": sensor["location"],
            "type": sensor["type"],
        }

        # Store reading
        self.data_streams[sensor_id].append(reading)
        sensor["last_reading"] = reading
        sensor["last_update"] = time.time()

        # Check alerts
        self.check_sensor_alerts(sensor_id, calibrated_value)

        return reading

    def read_all_sensors(self):
        """Read data from all active sensors"""
        readings = {}
        for sensor_id in self.sensors:
            if self.sensors[sensor_id]["status"] == "active":
                readings[sensor_id] = self.read_sensor(sensor_id)
        return readings

    def set_alert_threshold(self, sensor_id, min_value=None, max_value=None):
        """Set alert thresholds for a sensor"""
        self.thresholds[sensor_id] = {"min": min_value, "max": max_value}

    def check_sensor_alerts(self, sensor_id, value):
        """Check if sensor value triggers alerts"""
        if sensor_id not in self.thresholds:
            return

        threshold = self.thresholds[sensor_id]

        if threshold["min"] is not None and value < threshold["min"]:
            alert = {
                "sensor_id": sensor_id,
                "type": "low_threshold",
                "value": value,
                "threshold": threshold["min"],
                "timestamp": time.time(),
            }
            self.alerts.append(alert)
            print(
                f"🚨 Alert: {sensor_id} below threshold ({value} < {threshold['min']})"
            )

        if threshold["max"] is not None and value > threshold["max"]:
            alert = {
                "sensor_id": sensor_id,
                "type": "high_threshold",
                "value": value,
                "threshold": threshold["max"],
                "timestamp": time.time(),
            }
            self.alerts.append(alert)
            print(
                f"🚨 Alert: {sensor_id} above threshold ({value} > {threshold['max']})"
            )

    def get_sensor_statistics(self, sensor_id, hours=24):
        """Get statistics for a sensor over time period"""
        if sensor_id not in self.data_streams:
            return None

        data = self.data_streams[sensor_id]
        cutoff_time = time.time() - (hours * 3600)
        recent_data = [
            reading for reading in data if reading["timestamp"] > cutoff_time
        ]

        if not recent_data:
            return None

        values = [reading["value"] for reading in recent_data]

        return {
            "sensor_id": sensor_id,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
        }
