#!/usr/bin/env python3
"""
Hardware Controller Plugin for Time_Warp IDE
Professional hardware interface tool with GPIO control, sensor management,
device automation, and Raspberry Pi integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import sys
import os
from typing import Dict, Any, List, Optional

# Import the base framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.framework import ToolPlugin


class HardwareControllerPlugin(ToolPlugin):
    """Hardware controller tool plugin"""

    def __init__(self, ide_instance, framework):
        super().__init__(ide_instance, framework)

        # Plugin metadata
        self.name = "Hardware Controller"
        self.version = "1.0.0"
        self.author = "Time_Warp IDE Team"
        self.description = "Professional hardware interface tool with GPIO control, sensor management, device automation, and Raspberry Pi integration"
        self.category = "hardware"

        # Hardware state
        self.hardware_state = {
            "gpio_pins": {},
            "sensors": {},
            "devices": {},
            "automation_rules": [],
        }

        # UI references
        self._tool_window = None
        self.gpio_buttons = {}
        self.gpio_states = {}
        self.selected_pin_var = None
        self.pin_mode_var = None
        self.pin_value_var = None
        self.sensors_tree = None
        self.devices_tree = None
        self.rules_listbox = None

    def initialize(self) -> bool:
        """Initialize the hardware controller plugin"""
        try:
            # Subscribe to relevant events
            self.subscribe_event("interpreter_ready", self._on_interpreter_ready)
            self.subscribe_event("hardware_event", self._on_hardware_event)

            # Initialize GPIO states (40 pins for Raspberry Pi)
            for pin_num in range(1, 41):
                self.gpio_states[pin_num] = {
                    "mode": "input",
                    "value": 0,
                    "enabled": False,
                }

            return True
        except Exception as e:
            print(f"Error initializing Hardware Controller: {e}")
            return False

    def activate(self) -> bool:
        """Activate the hardware controller"""
        try:
            # Add menu item
            self.add_menu_item(
                "Tools", "🔌 Hardware Controller", self.show_tool_dialog, "Ctrl+Shift+H"
            )

            # Add toolbar item
            self.add_toolbar_item(
                "🔌 Hardware", self.show_tool_dialog, tooltip="Open Hardware Controller"
            )

            return True
        except Exception as e:
            print(f"Error activating Hardware Controller: {e}")
            return False

    def deactivate(self) -> bool:
        """Deactivate the hardware controller"""
        try:
            # Close hardware controller window if open
            if self._tool_window:
                self._tool_window.destroy()
                self._tool_window = None

            return True
        except Exception as e:
            print(f"Error deactivating Hardware Controller: {e}")
            return False

    def create_ui(self, parent_widget) -> tk.Widget:
        """Create the hardware controller UI"""
        try:
            # Main container
            main_frame = ttk.Frame(parent_widget)

            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                header_frame, text="🔌 Hardware Controller", font=("Arial", 16, "bold")
            ).pack(side=tk.LEFT)

            ttk.Button(
                header_frame, text="🔄 Refresh All", command=self._refresh_all_hardware
            ).pack(side=tk.RIGHT, padx=5)

            # Create notebook for different hardware aspects
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Setup tabs
            self._setup_gpio_tab(notebook)
            self._setup_sensors_tab(notebook)
            self._setup_devices_tab(notebook)
            self._setup_automation_tab(notebook)

            return main_frame

        except Exception as e:
            print(f"Error creating hardware controller UI: {e}")
            return ttk.Label(
                parent_widget, text=f"Error creating hardware controller UI: {e}"
            )

    def _setup_gpio_tab(self, notebook):
        """Setup GPIO pins control tab"""
        gpio_frame = ttk.Frame(notebook)
        notebook.add(gpio_frame, text="📌 GPIO Pins")

        # GPIO Pin Grid
        pin_frame = ttk.LabelFrame(gpio_frame, text="GPIO Pin Control")
        pin_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Pin grid canvas
        canvas = tk.Canvas(pin_frame, width=400, height=300, bg="white")
        canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Draw GPIO pin layout (40 pins for Raspberry Pi)
        for i in range(40):
            row = i // 2
            col = i % 2
            x = 50 + col * 150
            y = 30 + row * 12

            pin_num = i + 1
            pin_color = self._get_gpio_pin_color(pin_num)

            # Pin rectangle
            rect_id = canvas.create_rectangle(
                x, y, x + 80, y + 10, fill=pin_color, outline="black"
            )
            text_id = canvas.create_text(
                x + 40, y + 5, text=f"Pin {pin_num}", font=("Arial", 7)
            )

            # Bind click events
            canvas.tag_bind(
                rect_id, "<Button-1>", lambda e, p=pin_num: self._toggle_gpio_pin(p)
            )
            canvas.tag_bind(
                text_id, "<Button-1>", lambda e, p=pin_num: self._toggle_gpio_pin(p)
            )

        # Control panel
        control_frame = ttk.LabelFrame(gpio_frame, text="Pin Control")
        control_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=5, pady=5)

        ttk.Label(control_frame, text="Selected Pin:").pack(pady=5)
        self.selected_pin_var = tk.StringVar(value="None")
        ttk.Label(
            control_frame,
            textvariable=self.selected_pin_var,
            font=("Arial", 12, "bold"),
        ).pack(pady=5)

        # Pin mode
        ttk.Label(control_frame, text="Mode:").pack(pady=(10, 0))
        self.pin_mode_var = tk.StringVar(value="input")
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(pady=5)
        ttk.Radiobutton(
            mode_frame,
            text="Input",
            variable=self.pin_mode_var,
            value="input",
            command=self._update_pin_mode,
        ).pack()
        ttk.Radiobutton(
            mode_frame,
            text="Output",
            variable=self.pin_mode_var,
            value="output",
            command=self._update_pin_mode,
        ).pack()

        # Pin value for output mode
        ttk.Label(control_frame, text="Output Value:").pack(pady=(10, 0))
        self.pin_value_var = tk.StringVar(value="0")
        value_frame = ttk.Frame(control_frame)
        value_frame.pack(pady=5)
        ttk.Radiobutton(
            value_frame,
            text="LOW (0)",
            variable=self.pin_value_var,
            value="0",
            command=self._update_pin_value,
        ).pack()
        ttk.Radiobutton(
            value_frame,
            text="HIGH (1)",
            variable=self.pin_value_var,
            value="1",
            command=self._update_pin_value,
        ).pack()

        # Control buttons
        ttk.Button(control_frame, text="📖 Read Pin", command=self._read_gpio_pin).pack(
            pady=5, fill=tk.X
        )
        ttk.Button(
            control_frame, text="✏️ Write Pin", command=self._write_gpio_pin
        ).pack(pady=5, fill=tk.X)
        ttk.Button(
            control_frame, text="🔄 Reset All", command=self._reset_all_gpio
        ).pack(pady=5, fill=tk.X)

    def _setup_sensors_tab(self, notebook):
        """Setup sensors monitoring tab"""
        sensors_frame = ttk.Frame(notebook)
        notebook.add(sensors_frame, text="🌡️ Sensors")

        # Sensor list
        sensors_list_frame = ttk.LabelFrame(sensors_frame, text="Connected Sensors")
        sensors_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sensors treeview
        columns = ("Sensor", "Type", "Pin", "Value", "Unit", "Status")
        self.sensors_tree = ttk.Treeview(
            sensors_list_frame, columns=columns, show="headings", height=12
        )

        for col in columns:
            self.sensors_tree.heading(col, text=col)
            self.sensors_tree.column(col, width=100)

        self.sensors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        sensor_scroll = ttk.Scrollbar(
            sensors_list_frame, orient=tk.VERTICAL, command=self.sensors_tree.yview
        )
        self.sensors_tree.config(yscrollcommand=sensor_scroll.set)
        sensor_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Add default sensors
        self._populate_default_sensors()

        # Sensor controls
        sensor_controls = ttk.Frame(sensors_frame)
        sensor_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            sensor_controls, text="➕ Add Sensor", command=self._add_sensor
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            sensor_controls, text="❌ Remove Sensor", command=self._remove_sensor
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            sensor_controls, text="🔄 Refresh Data", command=self._refresh_sensor_data
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            sensor_controls,
            text="📊 Start Monitoring",
            command=self._start_sensor_monitoring,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            sensor_controls,
            text="⏹️ Stop Monitoring",
            command=self._stop_sensor_monitoring,
        ).pack(side=tk.LEFT, padx=2)

    def _setup_devices_tab(self, notebook):
        """Setup device control tab"""
        devices_frame = ttk.Frame(notebook)
        notebook.add(devices_frame, text="🔧 Devices")

        # Device list
        devices_list_frame = ttk.LabelFrame(devices_frame, text="Connected Devices")
        devices_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Devices treeview
        columns = ("Device", "Type", "Interface", "Status", "Actions")
        self.devices_tree = ttk.Treeview(
            devices_list_frame, columns=columns, show="headings", height=10
        )

        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=120)

        self.devices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        device_scroll = ttk.Scrollbar(
            devices_list_frame, orient=tk.VERTICAL, command=self.devices_tree.yview
        )
        self.devices_tree.config(yscrollcommand=device_scroll.set)
        device_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Add default devices
        self._populate_default_devices()

        # Device controls
        device_controls = ttk.Frame(devices_frame)
        device_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            device_controls, text="🔧 Control Device", command=self._control_device
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            device_controls, text="📋 Device Info", command=self._show_device_info
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            device_controls, text="⚙️ Configure", command=self._configure_device
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            device_controls, text="🔄 Scan Devices", command=self._scan_devices
        ).pack(side=tk.LEFT, padx=2)

    def _setup_automation_tab(self, notebook):
        """Setup automation rules tab"""
        automation_frame = ttk.Frame(notebook)
        notebook.add(automation_frame, text="🤖 Automation")

        # Automation rules
        rules_frame = ttk.LabelFrame(automation_frame, text="Automation Rules")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Rules listbox
        self.rules_listbox = tk.Listbox(rules_frame, font=("Consolas", 10))
        self.rules_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        rules_scroll = ttk.Scrollbar(
            rules_frame, orient=tk.VERTICAL, command=self.rules_listbox.yview
        )
        self.rules_listbox.config(yscrollcommand=rules_scroll.set)
        rules_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Add sample rules
        self._populate_sample_automation_rules()

        # Rule controls
        rule_controls = ttk.Frame(automation_frame)
        rule_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            rule_controls, text="➕ Add Rule", command=self._add_automation_rule
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            rule_controls, text="✏️ Edit Rule", command=self._edit_automation_rule
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            rule_controls, text="❌ Delete Rule", command=self._delete_automation_rule
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            rule_controls, text="▶️ Start Automation", command=self._start_automation
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            rule_controls, text="⏹️ Stop Automation", command=self._stop_automation
        ).pack(side=tk.LEFT, padx=2)

    # === EVENT HANDLERS ===

    def _on_interpreter_ready(self, interpreter):
        """Handle interpreter ready event"""
        print("Hardware Controller: Interpreter ready for hardware integration")

    def _on_hardware_event(self, event_type, data):
        """Handle hardware-specific events"""
        print(f"Hardware Controller: Received {event_type} event with data: {data}")

    # === GPIO METHODS ===

    def _get_gpio_pin_color(self, pin_num):
        """Get color for GPIO pin based on function"""
        # Standard Raspberry Pi GPIO colors
        power_pins = [2, 4]  # 5V
        ground_pins = [6, 9, 14, 20, 25, 30, 34, 39]  # Ground

        if pin_num in power_pins:
            return "#FF6B6B"  # Red for power
        elif pin_num in ground_pins:
            return "#4ECDC4"  # Cyan for ground
        else:
            return "#95E1D3"  # Light green for GPIO

    def _toggle_gpio_pin(self, pin_num):
        """Toggle GPIO pin selection"""
        self.selected_pin_var.set(f"Pin {pin_num}")
        pin_state = self.gpio_states.get(pin_num, {})
        self.pin_mode_var.set(pin_state.get("mode", "input"))
        self.pin_value_var.set(str(pin_state.get("value", 0)))

    def _update_pin_mode(self):
        """Update selected pin mode"""
        pin_num = self._get_selected_pin_number()
        if pin_num:
            self.gpio_states[pin_num]["mode"] = self.pin_mode_var.get()
            messagebox.showinfo(
                "Pin Mode", f"Pin {pin_num} set to {self.pin_mode_var.get()} mode"
            )
            self.emit_event("gpio_pin_mode_changed", pin_num, self.pin_mode_var.get())

    def _update_pin_value(self):
        """Update selected pin output value"""
        pin_num = self._get_selected_pin_number()
        if pin_num and self.gpio_states[pin_num]["mode"] == "output":
            self.gpio_states[pin_num]["value"] = int(self.pin_value_var.get())
            messagebox.showinfo(
                "Pin Value", f"Pin {pin_num} output set to {self.pin_value_var.get()}"
            )
            self.emit_event(
                "gpio_pin_value_changed", pin_num, int(self.pin_value_var.get())
            )

    def _get_selected_pin_number(self):
        """Get currently selected pin number"""
        pin_text = self.selected_pin_var.get()
        if pin_text != "None":
            return int(pin_text.split()[1])
        return None

    def _read_gpio_pin(self):
        """Read value from GPIO pin"""
        pin_num = self._get_selected_pin_number()
        if pin_num:
            # Simulate reading pin value
            value = random.randint(0, 1)
            self.gpio_states[pin_num]["value"] = value
            messagebox.showinfo("Pin Read", f"Pin {pin_num} value: {value}")
            self.emit_event("gpio_pin_read", pin_num, value)
        else:
            messagebox.showwarning("No Pin Selected", "Please select a pin first")

    def _write_gpio_pin(self):
        """Write value to GPIO pin"""
        pin_num = self._get_selected_pin_number()
        if pin_num:
            if self.gpio_states[pin_num]["mode"] == "output":
                value = int(self.pin_value_var.get())
                self.gpio_states[pin_num]["value"] = value
                messagebox.showinfo("Pin Write", f"Pin {pin_num} set to {value}")
                self.emit_event("gpio_pin_write", pin_num, value)
            else:
                messagebox.showwarning(
                    "Pin Mode", "Pin must be in output mode to write"
                )
        else:
            messagebox.showwarning("No Pin Selected", "Please select a pin first")

    def _reset_all_gpio(self):
        """Reset all GPIO pins"""
        if messagebox.askyesno("Reset GPIO", "Reset all GPIO pins to default state?"):
            for pin_num in self.gpio_states:
                self.gpio_states[pin_num] = {
                    "mode": "input",
                    "value": 0,
                    "enabled": False,
                }
            messagebox.showinfo("GPIO Reset", "All GPIO pins reset to default state")
            self.emit_event("gpio_reset_all")

    # === SENSOR METHODS ===

    def _populate_default_sensors(self):
        """Populate sensors tree with default sensors"""
        default_sensors = [
            ("Temperature", "DHT22", "Pin 4", "22.5", "°C", "Active"),
            ("Humidity", "DHT22", "Pin 4", "65.0", "%", "Active"),
            ("Distance", "HC-SR04", "Pin 18", "15.2", "cm", "Active"),
            ("Light", "LDR", "Pin 26", "450", "lux", "Active"),
            ("Motion", "PIR", "Pin 23", "0", "detected", "Standby"),
        ]

        for sensor in default_sensors:
            self.sensors_tree.insert("", "end", values=sensor)

    def _add_sensor(self):
        """Add a new sensor"""
        dialog = tk.Toplevel(self._tool_window)
        dialog.title("➕ Add Sensor")
        dialog.geometry("400x300")
        dialog.transient(self._tool_window)
        dialog.grab_set()

        # Sensor configuration
        ttk.Label(dialog, text="Sensor Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).pack(pady=5)

        ttk.Label(dialog, text="Sensor Type:").pack(pady=5)
        type_var = tk.StringVar(value="DHT22")
        type_combo = ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=["DHT22", "DS18B20", "BMP280", "HC-SR04", "PIR", "LDR"],
        )
        type_combo.pack(pady=5)

        ttk.Label(dialog, text="GPIO Pin:").pack(pady=5)
        pin_var = tk.StringVar(value="Pin 4")
        pin_combo = ttk.Combobox(
            dialog, textvariable=pin_var, values=[f"Pin {i}" for i in range(1, 41)]
        )
        pin_combo.pack(pady=5)

        def create_sensor():
            self.sensors_tree.insert(
                "",
                "end",
                values=(
                    name_var.get(),
                    type_var.get(),
                    pin_var.get(),
                    "0.0",
                    "units",
                    "Ready",
                ),
            )
            messagebox.showinfo(
                "Sensor Added", f"Sensor '{name_var.get()}' added successfully"
            )
            self.emit_event(
                "sensor_added", name_var.get(), type_var.get(), pin_var.get()
            )
            dialog.destroy()

        ttk.Button(dialog, text="✅ Add", command=create_sensor).pack(pady=20)
        ttk.Button(dialog, text="❌ Cancel", command=dialog.destroy).pack()

    def _remove_sensor(self):
        """Remove selected sensor"""
        selection = self.sensors_tree.selection()
        if selection:
            item = self.sensors_tree.item(selection[0])
            sensor_name = item["values"][0]
            self.sensors_tree.delete(selection[0])
            messagebox.showinfo("Sensor Removed", "Sensor removed successfully")
            self.emit_event("sensor_removed", sensor_name)
        else:
            messagebox.showwarning("No Selection", "Please select a sensor to remove")

    def _refresh_sensor_data(self):
        """Refresh sensor data"""
        for item in self.sensors_tree.get_children():
            values = list(self.sensors_tree.item(item)["values"])
            sensor_type = values[1]

            # Simulate sensor readings based on type
            if sensor_type == "DHT22":
                if "Temperature" in values[0]:
                    values[3] = f"{random.uniform(20, 30):.1f}"
                elif "Humidity" in values[0]:
                    values[3] = f"{random.uniform(40, 80):.1f}"
            elif sensor_type == "HC-SR04":
                values[3] = f"{random.uniform(5, 50):.1f}"
            elif sensor_type == "LDR":
                values[3] = f"{random.randint(100, 800)}"
            elif sensor_type == "PIR":
                values[3] = str(random.randint(0, 1))

            self.sensors_tree.item(item, values=values)

        messagebox.showinfo("Sensors", "Sensor data refreshed")
        self.emit_event("sensors_refreshed")

    def _start_sensor_monitoring(self):
        """Start continuous sensor monitoring"""
        messagebox.showinfo(
            "Monitoring",
            "Sensor monitoring started\\n\\nData will be logged continuously",
        )
        self.emit_event("sensor_monitoring_started")

    def _stop_sensor_monitoring(self):
        """Stop sensor monitoring"""
        messagebox.showinfo("Monitoring", "Sensor monitoring stopped")
        self.emit_event("sensor_monitoring_stopped")

    # === DEVICE METHODS ===

    def _populate_default_devices(self):
        """Populate devices tree with default devices"""
        default_devices = [
            ("LED Strip", "WS2812B", "GPIO 18", "Off", "Control"),
            ("Servo Motor", "SG90", "GPIO 12", "Position 90°", "Control"),
            ("Buzzer", "Active", "GPIO 13", "Silent", "Control"),
            ("Relay Module", "5V", "GPIO 21", "Open", "Control"),
            ("Display", "LCD 16x2", "I2C", "Ready", "Update"),
        ]

        for device in default_devices:
            self.devices_tree.insert("", "end", values=device)

    def _control_device(self):
        """Control selected device"""
        selection = self.devices_tree.selection()
        if selection:
            item = self.devices_tree.item(selection[0])
            device_name = item["values"][0]
            device_type = item["values"][1]

            # Create device control dialog
            control_dialog = tk.Toplevel(self._tool_window)
            control_dialog.title(f"🔧 Control {device_name}")
            control_dialog.geometry("300x200")
            control_dialog.transient(self._tool_window)
            control_dialog.grab_set()

            ttk.Label(
                control_dialog,
                text=f"Device: {device_name}",
                font=("Arial", 12, "bold"),
            ).pack(pady=10)
            ttk.Label(control_dialog, text=f"Type: {device_type}").pack()

            if "LED" in device_name:
                ttk.Button(
                    control_dialog,
                    text="💡 Turn On",
                    command=lambda: self._device_action(device_name, "on"),
                ).pack(pady=5)
                ttk.Button(
                    control_dialog,
                    text="🌑 Turn Off",
                    command=lambda: self._device_action(device_name, "off"),
                ).pack(pady=5)
            elif "Servo" in device_name:
                ttk.Button(
                    control_dialog,
                    text="↪️ Position 0°",
                    command=lambda: self._device_action(device_name, "pos_0"),
                ).pack(pady=5)
                ttk.Button(
                    control_dialog,
                    text="↩️ Position 180°",
                    command=lambda: self._device_action(device_name, "pos_180"),
                ).pack(pady=5)
            elif "Buzzer" in device_name:
                ttk.Button(
                    control_dialog,
                    text="🔊 Beep",
                    command=lambda: self._device_action(device_name, "beep"),
                ).pack(pady=5)
            elif "Relay" in device_name:
                ttk.Button(
                    control_dialog,
                    text="🔴 Close",
                    command=lambda: self._device_action(device_name, "close"),
                ).pack(pady=5)
                ttk.Button(
                    control_dialog,
                    text="🟢 Open",
                    command=lambda: self._device_action(device_name, "open"),
                ).pack(pady=5)

            ttk.Button(
                control_dialog, text="✅ Close", command=control_dialog.destroy
            ).pack(pady=10)

    def _device_action(self, device_name, action):
        """Perform action on device"""
        messagebox.showinfo("Device Action", f"Performed '{action}' on {device_name}")
        self.emit_event("device_action", device_name, action)

    def _show_device_info(self):
        """Show device information"""
        selection = self.devices_tree.selection()
        if selection:
            item = self.devices_tree.item(selection[0])
            device_info = f"""Device Information:
            
Name: {item['values'][0]}
Type: {item['values'][1]}
Interface: {item['values'][2]}
Status: {item['values'][3]}
Actions: {item['values'][4]}

Technical Details:
- Voltage: 3.3V/5V compatible
- Current Draw: Low power
- Communication: Digital/Analog
- Control Method: GPIO/I2C/SPI"""

            messagebox.showinfo("Device Information", device_info)

    def _configure_device(self):
        """Configure selected device"""
        selection = self.devices_tree.selection()
        if selection:
            device_name = self.devices_tree.item(selection[0])["values"][0]
            messagebox.showinfo(
                "Device Configuration", f"Opening configuration for {device_name}"
            )

    def _scan_devices(self):
        """Scan for connected devices"""
        messagebox.showinfo(
            "Device Scan", "Scanning for connected devices...\\n\\nFound 5 devices"
        )
        self.emit_event("devices_scanned")

    # === AUTOMATION METHODS ===

    def _populate_sample_automation_rules(self):
        """Populate automation rules with samples"""
        sample_rules = [
            "IF temperature > 25°C THEN turn_on(fan)",
            "IF motion_detected THEN turn_on(lights) FOR 10min",
            "IF light_level < 100 THEN dim_lights(50%)",
            "IF button_pressed THEN toggle(relay)",
            "EVERY 1hour DO read_all_sensors()",
        ]

        for rule in sample_rules:
            self.rules_listbox.insert(tk.END, rule)

    def _add_automation_rule(self):
        """Add new automation rule"""
        rule = simpledialog.askstring("Add Rule", "Enter automation rule:")
        if rule:
            self.rules_listbox.insert(tk.END, rule)
            messagebox.showinfo("Rule Added", "Automation rule added successfully")
            self.emit_event("automation_rule_added", rule)

    def _edit_automation_rule(self):
        """Edit selected automation rule"""
        selection = self.rules_listbox.curselection()
        if selection:
            current_rule = self.rules_listbox.get(selection[0])
            new_rule = simpledialog.askstring(
                "Edit Rule", "Edit automation rule:", initialvalue=current_rule
            )
            if new_rule:
                self.rules_listbox.delete(selection[0])
                self.rules_listbox.insert(selection[0], new_rule)
                messagebox.showinfo(
                    "Rule Updated", "Automation rule updated successfully"
                )
                self.emit_event("automation_rule_edited", current_rule, new_rule)

    def _delete_automation_rule(self):
        """Delete selected automation rule"""
        selection = self.rules_listbox.curselection()
        if selection:
            rule = self.rules_listbox.get(selection[0])
            self.rules_listbox.delete(selection[0])
            messagebox.showinfo("Rule Deleted", "Automation rule deleted successfully")
            self.emit_event("automation_rule_deleted", rule)

    def _start_automation(self):
        """Start automation engine"""
        messagebox.showinfo(
            "Automation", "Automation engine started\\n\\nRules are now active"
        )
        self.emit_event("automation_started")

    def _stop_automation(self):
        """Stop automation engine"""
        messagebox.showinfo("Automation", "Automation engine stopped")
        self.emit_event("automation_stopped")

    # === UTILITY METHODS ===

    def _refresh_all_hardware(self):
        """Refresh all hardware data"""
        self._refresh_sensor_data()
        messagebox.showinfo("Hardware Controller", "All hardware data refreshed")


# Plugin entry point - this will be imported by the plugin system
TimeWarpPlugin = HardwareControllerPlugin
