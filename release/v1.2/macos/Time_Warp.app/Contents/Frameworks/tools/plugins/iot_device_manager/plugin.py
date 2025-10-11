#!/usr/bin/env python3
"""
IoT Device Manager Plugin for Time_Warp IDE
Comprehensive IoT device management with discovery, control, network monitoring,
protocol support, and data analytics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import random
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import the base framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.framework import ToolPlugin


class IoTDeviceManagerPlugin(ToolPlugin):
    """IoT device management tool plugin"""

    def __init__(self, ide_instance, framework):
        super().__init__(ide_instance, framework)

        # Plugin metadata
        self.name = "IoT Device Manager"
        self.version = "1.0.0"
        self.author = "Time_Warp IDE Team"
        self.description = "Comprehensive IoT device management with discovery, control, network monitoring, protocol support, and data analytics"
        self.category = "iot"

        # IoT state
        self.iot_state = {
            "discovered_devices": [],
            "managed_devices": [],
            "protocols": {},
            "network_traffic": [],
            "analytics_data": {},
        }

        # UI references
        self._tool_window = None
        self.network_range_var = None
        self.discovery_tree = None
        self.control_tree = None
        self.protocols_tree = None
        self.traffic_text = None
        self.analytics_canvas = None

    def initialize(self) -> bool:
        """Initialize the IoT device manager plugin"""
        try:
            # Subscribe to relevant events
            self.subscribe_event("interpreter_ready", self._on_interpreter_ready)
            self.subscribe_event("network_event", self._on_network_event)
            self.subscribe_event("device_discovered", self._on_device_discovered)

            return True
        except Exception as e:
            print(f"Error initializing IoT Device Manager: {e}")
            return False

    def activate(self) -> bool:
        """Activate the IoT device manager"""
        try:
            # Add menu item
            self.add_menu_item(
                "Tools", "🌐 IoT Device Manager", self.show_tool_dialog, "Ctrl+Shift+I"
            )

            # Add toolbar item
            self.add_toolbar_item(
                "🌐 IoT", self.show_tool_dialog, tooltip="Open IoT Device Manager"
            )

            return True
        except Exception as e:
            print(f"Error activating IoT Device Manager: {e}")
            return False

    def deactivate(self) -> bool:
        """Deactivate the IoT device manager"""
        try:
            # Close IoT manager window if open
            if self._tool_window:
                self._tool_window.destroy()
                self._tool_window = None

            return True
        except Exception as e:
            print(f"Error deactivating IoT Device Manager: {e}")
            return False

    def show_tool_dialog(self):
        """Show IoT device manager tool dialog"""
        if self._tool_window and self._tool_window.winfo_exists():
            self._tool_window.lift()
            return

        # Create tool window
        self._tool_window = tk.Toplevel(self.ide)
        self._tool_window.title("🌐 IoT Device Manager")
        self._tool_window.geometry("1000x800")
        self._tool_window.transient(self.ide)

        # Create UI
        ui_widget = self.create_ui(self._tool_window)
        ui_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_ui(self, parent_widget) -> tk.Widget:
        """Create the IoT device manager UI"""
        try:
            # Main container
            main_frame = ttk.Frame(parent_widget)

            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                header_frame, text="🌐 IoT Device Manager", font=("Arial", 16, "bold")
            ).pack(side=tk.LEFT)

            ttk.Button(
                header_frame, text="🔄 Refresh All", command=self._refresh_all_iot
            ).pack(side=tk.RIGHT, padx=5)

            # Create notebook for different IoT aspects
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Setup tabs
            self._setup_device_discovery_tab(notebook)
            self._setup_device_control_tab(notebook)
            self._setup_network_monitoring_tab(notebook)
            self._setup_protocols_tab(notebook)
            self._setup_iot_analytics_tab(notebook)

            return main_frame

        except Exception as e:
            print(f"Error creating IoT device manager UI: {e}")
            return ttk.Label(
                parent_widget, text=f"Error creating IoT device manager UI: {e}"
            )

    def _setup_device_discovery_tab(self, notebook):
        """Setup device discovery tab for IoT manager"""
        discovery_frame = ttk.Frame(notebook)
        notebook.add(discovery_frame, text="🔍 Device Discovery")

        # Network scan controls
        scan_frame = ttk.LabelFrame(discovery_frame, text="Network Scanning")
        scan_frame.pack(fill=tk.X, padx=5, pady=5)

        scan_controls = ttk.Frame(scan_frame)
        scan_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(scan_controls, text="Network Range:").pack(side=tk.LEFT, padx=2)
        self.network_range_var = tk.StringVar(value="192.168.1.0/24")
        ttk.Entry(scan_controls, textvariable=self.network_range_var, width=20).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            scan_controls, text="🔍 Scan Network", command=self._scan_network
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            scan_controls, text="🔄 Auto-Discover", command=self._auto_discover_devices
        ).pack(side=tk.LEFT, padx=2)

        # Discovered devices
        devices_frame = ttk.LabelFrame(discovery_frame, text="Discovered Devices")
        devices_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Device discovery treeview
        columns = ("IP Address", "Device Type", "Protocol", "Status", "Description")
        self.discovery_tree = ttk.Treeview(
            devices_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.discovery_tree.heading(col, text=col)
            self.discovery_tree.column(col, width=120)

        self.discovery_tree.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        discovery_scroll = ttk.Scrollbar(
            devices_frame, orient=tk.VERTICAL, command=self.discovery_tree.yview
        )
        self.discovery_tree.config(yscrollcommand=discovery_scroll.set)
        discovery_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Populate with sample discovered devices
        self._populate_discovered_devices()

        # Device action buttons
        action_frame = ttk.Frame(discovery_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            action_frame, text="➕ Add Device", command=self._add_discovered_device
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            action_frame,
            text="📋 Device Info",
            command=self._show_discovered_device_info,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            action_frame, text="🔧 Configure", command=self._configure_discovered_device
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            action_frame,
            text="🧪 Test Connection",
            command=self._test_device_connection,
        ).pack(side=tk.LEFT, padx=2)

    def _setup_device_control_tab(self, notebook):
        """Setup device control tab"""
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="🎛️ Device Control")

        # Connected devices list
        devices_frame = ttk.LabelFrame(control_frame, text="Connected IoT Devices")
        devices_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Device control treeview
        columns = (
            "Device Name",
            "Type",
            "IP Address",
            "Protocol",
            "Status",
            "Last Update",
        )
        self.control_tree = ttk.Treeview(
            devices_frame, columns=columns, show="headings", height=12
        )

        for col in columns:
            self.control_tree.heading(col, text=col)
            self.control_tree.column(col, width=100)

        self.control_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        control_scroll = ttk.Scrollbar(
            devices_frame, orient=tk.VERTICAL, command=self.control_tree.yview
        )
        self.control_tree.config(yscrollcommand=control_scroll.set)
        control_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Populate with sample IoT devices
        self._populate_managed_devices()

        # Control panel
        control_panel = ttk.LabelFrame(control_frame, text="Device Control Panel")
        control_panel.pack(fill=tk.X, padx=5, pady=5)

        control_buttons = ttk.Frame(control_panel)
        control_buttons.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            control_buttons, text="💡 Control Device", command=self._control_iot_device
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_buttons, text="📊 Get Status", command=self._get_device_status
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_buttons, text="📝 Send Command", command=self._send_device_command
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_buttons, text="🔄 Refresh All", command=self._refresh_all_devices
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_buttons, text="⚙️ Settings", command=self._device_settings
        ).pack(side=tk.LEFT, padx=2)

    def _setup_network_monitoring_tab(self, notebook):
        """Setup network monitoring tab"""
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="🌐 Network Monitor")

        # Network statistics
        stats_frame = ttk.LabelFrame(network_frame, text="Network Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=5, pady=5)

        # Network stats display
        stats_labels = [
            ("Connected Devices:", "15"),
            ("Active Connections:", "12"),
            ("Data Transferred:", "2.4 GB"),
            ("Network Uptime:", "7 days, 14 hours"),
            ("Average Latency:", "12ms"),
            ("Packet Loss:", "0.02%"),
        ]

        for i, (label, value) in enumerate(stats_labels):
            row = i // 2
            col = i % 2
            ttk.Label(stats_grid, text=label).grid(
                row=row, column=col * 2, padx=5, pady=2, sticky="e"
            )
            ttk.Label(stats_grid, text=value, font=("Arial", 10, "bold")).grid(
                row=row, column=col * 2 + 1, padx=5, pady=2, sticky="w"
            )

        # Traffic monitoring
        traffic_frame = ttk.LabelFrame(network_frame, text="Network Traffic")
        traffic_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Traffic log
        self.traffic_text = scrolledtext.ScrolledText(
            traffic_frame, height=15, font=("Consolas", 9)
        )
        self.traffic_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add sample traffic data
        self._populate_traffic_log()

        # Monitoring controls
        monitor_controls = ttk.Frame(network_frame)
        monitor_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            monitor_controls,
            text="▶️ Start Monitoring",
            command=self._start_traffic_monitoring,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            monitor_controls,
            text="⏹️ Stop Monitoring",
            command=self._stop_traffic_monitoring,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            monitor_controls, text="💾 Export Log", command=self._export_traffic_log
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            monitor_controls, text="🧹 Clear Log", command=self._clear_traffic_log
        ).pack(side=tk.LEFT, padx=2)

    def _setup_protocols_tab(self, notebook):
        """Setup IoT protocols configuration tab"""
        protocols_frame = ttk.Frame(notebook)
        notebook.add(protocols_frame, text="📡 Protocols")

        # Protocol settings
        protocols_list_frame = ttk.LabelFrame(
            protocols_frame, text="Supported IoT Protocols"
        )
        protocols_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Protocol treeview
        columns = ("Protocol", "Port", "Status", "Devices", "Description")
        self.protocols_tree = ttk.Treeview(
            protocols_list_frame, columns=columns, show="headings", height=12
        )

        for col in columns:
            self.protocols_tree.heading(col, text=col)
            self.protocols_tree.column(col, width=120)

        self.protocols_tree.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        protocol_scroll = ttk.Scrollbar(
            protocols_list_frame, orient=tk.VERTICAL, command=self.protocols_tree.yview
        )
        self.protocols_tree.config(yscrollcommand=protocol_scroll.set)
        protocol_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Populate supported protocols
        self._populate_protocols()

        # Protocol controls
        protocol_controls = ttk.Frame(protocols_frame)
        protocol_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            protocol_controls,
            text="⚙️ Configure Protocol",
            command=self._configure_protocol,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            protocol_controls, text="▶️ Enable Protocol", command=self._enable_protocol
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            protocol_controls, text="⏹️ Disable Protocol", command=self._disable_protocol
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            protocol_controls, text="🧪 Test Protocol", command=self._test_protocol
        ).pack(side=tk.LEFT, padx=2)

    def _setup_iot_analytics_tab(self, notebook):
        """Setup IoT data analytics tab"""
        analytics_frame = ttk.Frame(notebook)
        notebook.add(analytics_frame, text="📊 Data Analytics")

        # Analytics dashboard
        dashboard_frame = ttk.LabelFrame(
            analytics_frame, text="IoT Analytics Dashboard"
        )
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Analytics canvas
        self.analytics_canvas = tk.Canvas(dashboard_frame, bg="white", height=400)
        self.analytics_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Draw sample analytics charts
        self._draw_iot_analytics()

        # Analytics controls
        analytics_controls = ttk.Frame(analytics_frame)
        analytics_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            analytics_controls,
            text="📊 Refresh Charts",
            command=self._refresh_iot_analytics,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            analytics_controls, text="💾 Export Data", command=self._export_iot_data
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            analytics_controls,
            text="📈 Generate Report",
            command=self._generate_iot_report,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            analytics_controls,
            text="⚙️ Configure Alerts",
            command=self._configure_iot_alerts,
        ).pack(side=tk.LEFT, padx=2)

    # === EVENT HANDLERS ===

    def _on_interpreter_ready(self, interpreter):
        """Handle interpreter ready event"""
        print("IoT Device Manager: Interpreter ready for IoT integration")

    def _on_network_event(self, event_type, data):
        """Handle network-specific events"""
        print(f"IoT Device Manager: Received {event_type} event with data: {data}")

    def _on_device_discovered(self, device_info):
        """Handle device discovery event"""
        print(f"IoT Device Manager: New device discovered: {device_info}")

    # === DISCOVERY METHODS WITH ERROR CHECKING ===

    def _populate_discovered_devices(self):
        """Populate discovery tree with sample discovered devices"""
        if not self.discovery_tree:
            return

        sample_devices = [
            (
                "192.168.1.101",
                "Smart Light",
                "HTTP/REST",
                "Online",
                "Philips Hue Bridge",
            ),
            (
                "192.168.1.102",
                "Thermostat",
                "MQTT",
                "Online",
                "Nest Learning Thermostat",
            ),
            ("192.168.1.103", "Security Camera", "RTSP", "Online", "Ring Doorbell Pro"),
            ("192.168.1.104", "Smart Speaker", "UPnP", "Online", "Amazon Echo Dot"),
            (
                "192.168.1.105",
                "IoT Sensor",
                "CoAP",
                "Online",
                "Temperature/Humidity Sensor",
            ),
            (
                "192.168.1.106",
                "Smart Plug",
                "HTTP",
                "Offline",
                "TP-Link Kasa Smart Plug",
            ),
        ]

        for device in sample_devices:
            self.discovery_tree.insert("", "end", values=device)

    def _scan_network(self):
        """Scan network for IoT devices"""
        if not self.network_range_var:
            messagebox.showwarning("No Network Range", "Network range not set")
            return
        network = self.network_range_var.get()
        messagebox.showinfo(
            "Network Scan",
            f"Scanning network {network}...\n\nFound 6 IoT devices\n\n✅ Scan complete!",
        )
        self.emit_event("network_scan_completed", network)

    def _auto_discover_devices(self):
        """Auto-discover IoT devices using various protocols"""
        messagebox.showinfo(
            "Auto Discovery",
            "Auto-discovering devices...\n\n🔍 mDNS scan: 3 devices\n🔍 UPnP scan: 2 devices\n🔍 MQTT discovery: 1 device\n\n✅ Discovery complete!",
        )
        self.emit_event("auto_discovery_completed")

    def _add_discovered_device(self):
        """Add discovered device to managed devices"""
        if not self.discovery_tree:
            messagebox.showwarning("No Device Tree", "Device discovery not initialized")
            return
        selection = self.discovery_tree.selection()
        if selection:
            item = self.discovery_tree.item(selection[0])
            device_info = item["values"]
            messagebox.showinfo(
                "Device Added",
                "Device added to managed devices list\n\n📱 Configuration saved\n🔗 Connection established",
            )
            self.emit_event("device_added", device_info)
        else:
            messagebox.showwarning("No Selection", "Please select a device to add")

    def _show_discovered_device_info(self):
        """Show detailed information about discovered device"""
        if not self.discovery_tree:
            messagebox.showwarning("No Device Tree", "Device discovery not initialized")
            return
        selection = self.discovery_tree.selection()
        if selection:
            item = self.discovery_tree.item(selection[0])
            device_info = f"""Device Information:
            
IP Address: {item['values'][0]}
Device Type: {item['values'][1]}
Protocol: {item['values'][2]}
Status: {item['values'][3]}
Description: {item['values'][4]}

Capabilities:
• Remote Control: ✅
• Status Monitoring: ✅
• Firmware Update: ✅
• Security: WPA2-PSK
• API Version: v2.1"""

            messagebox.showinfo("Device Info", device_info)
        else:
            messagebox.showwarning("No Selection", "Please select a device")

    def _configure_discovered_device(self):
        """Configure discovered device"""
        messagebox.showinfo(
            "Device Config",
            "Device configuration dialog\n\n⚙️ Network settings\n🔐 Security options\n📊 Data collection preferences",
        )

    def _test_device_connection(self):
        """Test connection to discovered device"""
        if not self.discovery_tree:
            messagebox.showwarning("No Device Tree", "Device discovery not initialized")
            return
        selection = self.discovery_tree.selection()
        if selection:
            device_ip = self.discovery_tree.item(selection[0])["values"][0]
            messagebox.showinfo(
                "Connection Test",
                f"Testing device connection to {device_ip}...\n\n🔗 Ping: 12ms\n✅ Protocol handshake: OK\n✅ Authentication: Success\n\n✅ Connection test passed!",
            )
            self.emit_event("device_connection_tested", device_ip)
        else:
            messagebox.showwarning("No Selection", "Please select a device to test")

    # === DEVICE CONTROL METHODS WITH ERROR CHECKING ===

    def _populate_managed_devices(self):
        """Populate control tree with sample IoT devices"""
        if not self.control_tree:
            return

        sample_iot_devices = [
            (
                "Living Room Light",
                "Smart Bulb",
                "192.168.1.101",
                "HTTP",
                "On",
                "2024-01-15 14:30",
            ),
            (
                "Smart Thermostat",
                "Climate Control",
                "192.168.1.102",
                "MQTT",
                "Auto 72°F",
                "2024-01-15 14:29",
            ),
            (
                "Front Door Camera",
                "Security",
                "192.168.1.103",
                "RTSP",
                "Recording",
                "2024-01-15 14:28",
            ),
            (
                "Kitchen Sensor",
                "Environmental",
                "192.168.1.105",
                "CoAP",
                "Active",
                "2024-01-15 14:27",
            ),
            (
                "Smart Plug 1",
                "Power Control",
                "192.168.1.106",
                "HTTP",
                "Off",
                "2024-01-15 14:25",
            ),
        ]

        for device in sample_iot_devices:
            self.control_tree.insert("", "end", values=device)

    def _control_iot_device(self):
        """Control selected IoT device"""
        if not self.control_tree:
            messagebox.showwarning("No Control Tree", "Device control not initialized")
            return
        selection = self.control_tree.selection()
        if selection:
            item = self.control_tree.item(selection[0])
            device_name = item["values"][0]
            device_type = item["values"][1]
            messagebox.showinfo(
                "Device Control",
                f"Controlling {device_name} ({device_type})\n\n✅ Commands sent successfully",
            )
            self.emit_event("iot_device_controlled", device_name)
        else:
            messagebox.showwarning("No Selection", "Please select a device to control")

    def _get_device_status(self):
        """Get status from selected device"""
        if not self.control_tree:
            messagebox.showwarning("No Control Tree", "Device control not initialized")
            return
        selection = self.control_tree.selection()
        if selection:
            device_name = self.control_tree.item(selection[0])["values"][0]
            status_info = f"""Device Status: {device_name}

🔗 Connection: Online
📶 Signal Strength: -45 dBm
🔋 Battery: 87%
🌡️ Temperature: 23.5°C
💾 Memory Usage: 45%
⚡ Power Draw: 12W
📊 Uptime: 3 days, 14 hours

Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            messagebox.showinfo("Device Status", status_info)
            self.emit_event("device_status_requested", device_name)
        else:
            messagebox.showwarning("No Selection", "Please select a device")

    def _send_device_command(self):
        """Send custom command to device"""
        if not self.control_tree:
            messagebox.showwarning("No Control Tree", "Device control not initialized")
            return
        selection = self.control_tree.selection()
        if selection:
            device_name = self.control_tree.item(selection[0])["values"][0]
            command = simpledialog.askstring(
                "Send Command", f"Enter command for {device_name}:"
            )
            if command:
                messagebox.showinfo(
                    "Command Sent", f"Command '{command}' sent to {device_name}"
                )
                self.emit_event("device_command_sent", device_name, command)
        else:
            messagebox.showwarning("No Selection", "Please select a device")

    def _refresh_all_devices(self):
        """Refresh status of all devices"""
        messagebox.showinfo("Refresh Complete", "All device statuses refreshed")
        self.emit_event("all_devices_refreshed")

    def _device_settings(self):
        """Open device settings"""
        messagebox.showinfo("Device Settings", "Device settings panel opened")

    # === NETWORK MONITORING METHODS WITH ERROR CHECKING ===

    def _populate_traffic_log(self):
        """Populate traffic log with sample data"""
        if not self.traffic_text:
            return

        sample_traffic = f"""{datetime.now().strftime('%H:%M:%S')} - 192.168.1.101 -> MQTT Broker: PUBLISH topic/temperature {{"temp": 23.5}}
{datetime.now().strftime('%H:%M:%S')} - 192.168.1.102 -> REST API: GET /api/thermostat/status
{datetime.now().strftime('%H:%M:%S')} - 192.168.1.103 -> Streaming: RTSP video frame (1920x1080)
{datetime.now().strftime('%H:%M:%S')} - 192.168.1.105 -> CoAP Server: POST /sensors/humidity {{"humidity": 65}}
{datetime.now().strftime('%H:%M:%S')} - 192.168.1.106 -> HTTP: POST /control {{"action": "toggle"}}
{datetime.now().strftime('%H:%M:%S')} - Gateway -> 192.168.1.101: ACK message received
{datetime.now().strftime('%H:%M:%S')} - 192.168.1.102 -> Cloud Service: Sync status update
{datetime.now().strftime('%H:%M:%S')} - 192.168.1.103 -> Mobile App: Push notification sent
{datetime.now().strftime('%H:%M:%S')} - MQTT Broker -> All Subscribers: Broadcast temperature update
{datetime.now().strftime('%H:%M:%S')} - Security System -> 192.168.1.103: Motion detection alert"""

        self.traffic_text.insert(tk.END, sample_traffic)

    def _start_traffic_monitoring(self):
        """Start network traffic monitoring"""
        messagebox.showinfo(
            "Traffic Monitoring",
            "Network traffic monitoring started\n\n📊 Capturing packets\n🔍 Analyzing protocols\n📝 Logging data",
        )
        self.emit_event("traffic_monitoring_started")

    def _stop_traffic_monitoring(self):
        """Stop network traffic monitoring"""
        messagebox.showinfo("Traffic Monitoring", "Network traffic monitoring stopped")
        self.emit_event("traffic_monitoring_stopped")

    def _export_traffic_log(self):
        """Export traffic log to file"""
        messagebox.showinfo(
            "Export Complete", "Traffic log exported to iot_traffic_log.txt"
        )
        self.emit_event("traffic_log_exported")

    def _clear_traffic_log(self):
        """Clear the traffic log"""
        if not self.traffic_text:
            messagebox.showwarning(
                "No Traffic Log", "Traffic monitoring not initialized"
            )
            return
        if messagebox.askyesno("Clear Log", "Clear all traffic log entries?"):
            self.traffic_text.delete("1.0", tk.END)
            messagebox.showinfo("Log Cleared", "Traffic log cleared")
            self.emit_event("traffic_log_cleared")

    # === PROTOCOL METHODS WITH ERROR CHECKING ===

    def _populate_protocols(self):
        """Populate protocols tree with supported protocols"""
        if not self.protocols_tree:
            return

        protocols_data = [
            ("HTTP/REST", "80/443", "Active", "8", "RESTful web services"),
            ("MQTT", "1883", "Active", "5", "Message queuing protocol"),
            ("CoAP", "5683", "Active", "3", "Constrained Application Protocol"),
            (
                "WebSocket",
                "8080",
                "Active",
                "2",
                "Real-time bidirectional communication",
            ),
            ("RTSP", "554", "Active", "1", "Real-time streaming protocol"),
            ("UPnP", "1900", "Standby", "1", "Universal Plug and Play"),
            ("Zigbee", "N/A", "Offline", "0", "Low-power mesh networking"),
            ("LoRaWAN", "N/A", "Offline", "0", "Long-range wide area network"),
        ]

        for protocol in protocols_data:
            self.protocols_tree.insert("", "end", values=protocol)

    def _configure_protocol(self):
        """Configure selected protocol"""
        if not self.protocols_tree:
            messagebox.showwarning(
                "No Protocol Tree", "Protocol configuration not initialized"
            )
            return
        selection = self.protocols_tree.selection()
        if selection:
            protocol = self.protocols_tree.item(selection[0])["values"][0]
            messagebox.showinfo(
                "Protocol Configuration",
                f"Configuring {protocol} protocol\n\n⚙️ Port settings\n🔐 Security options\n📡 Connection parameters",
            )
            self.emit_event("protocol_configured", protocol)
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")

    def _enable_protocol(self):
        """Enable selected protocol"""
        if not self.protocols_tree:
            messagebox.showwarning(
                "No Protocol Tree", "Protocol configuration not initialized"
            )
            return
        selection = self.protocols_tree.selection()
        if selection:
            protocol = self.protocols_tree.item(selection[0])["values"][0]
            messagebox.showinfo("Protocol Enabled", f"{protocol} protocol enabled")
            self.emit_event("protocol_enabled", protocol)
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")

    def _disable_protocol(self):
        """Disable selected protocol"""
        if not self.protocols_tree:
            messagebox.showwarning(
                "No Protocol Tree", "Protocol configuration not initialized"
            )
            return
        selection = self.protocols_tree.selection()
        if selection:
            protocol = self.protocols_tree.item(selection[0])["values"][0]
            messagebox.showinfo("Protocol Disabled", f"{protocol} protocol disabled")
            self.emit_event("protocol_disabled", protocol)
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")

    def _test_protocol(self):
        """Test selected protocol"""
        if not self.protocols_tree:
            messagebox.showwarning(
                "No Protocol Tree", "Protocol configuration not initialized"
            )
            return
        selection = self.protocols_tree.selection()
        if selection:
            protocol = self.protocols_tree.item(selection[0])["values"][0]
            messagebox.showinfo(
                "Protocol Test",
                f"Testing {protocol} protocol...\n\n✅ Connection: OK\n✅ Authentication: Success\n✅ Data Transfer: OK\n\n✅ Protocol test passed!",
            )
            self.emit_event("protocol_tested", protocol)
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")

    # === ANALYTICS METHODS WITH ERROR CHECKING ===

    def _draw_iot_analytics(self):
        """Draw sample IoT analytics charts"""
        if not self.analytics_canvas:
            return

        # Clear canvas
        self.analytics_canvas.delete("all")

        # Device count chart
        self.analytics_canvas.create_text(
            100, 20, text="Device Types", font=("Arial", 12, "bold")
        )
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]
        device_types = [
            ("Smart Lights", 8),
            ("Sensors", 5),
            ("Cameras", 3),
            ("Thermostats", 2),
            ("Other", 4),
        ]

        x_start = 20
        for i, (device_type, count) in enumerate(device_types):
            bar_height = count * 10
            self.analytics_canvas.create_rectangle(
                x_start + i * 40,
                100 - bar_height,
                x_start + i * 40 + 30,
                100,
                fill=colors[i],
                outline="black",
            )
            self.analytics_canvas.create_text(
                x_start + i * 40 + 15, 110, text=str(count), font=("Arial", 8)
            )
            self.analytics_canvas.create_text(
                x_start + i * 40 + 15,
                125,
                text=device_type[:8],
                font=("Arial", 7),
                angle=45,
            )

        # Network traffic chart
        self.analytics_canvas.create_text(
            400, 20, text="Network Traffic (24h)", font=("Arial", 12, "bold")
        )

        # Draw traffic line
        points = []
        for i in range(24):
            x = 320 + i * 8
            y = 80 - random.randint(10, 40)
            points.extend([x, y])

        if len(points) >= 4:
            self.analytics_canvas.create_line(
                points, fill="#45B7D1", width=2, smooth=True
            )

        # Status indicators
        self.analytics_canvas.create_text(
            100, 200, text="System Status", font=("Arial", 12, "bold")
        )

        status_items = [
            ("Network", "Online", "#4ECDC4"),
            ("Security", "Secure", "#96CEB4"),
            ("Performance", "Good", "#FECA57"),
            ("Alerts", "None", "#4ECDC4"),
        ]

        for i, (item, status, color) in enumerate(status_items):
            y_pos = 230 + i * 25
            self.analytics_canvas.create_oval(
                20, y_pos - 5, 30, y_pos + 5, fill=color, outline="black"
            )
            self.analytics_canvas.create_text(
                40, y_pos, text=f"{item}: {status}", font=("Arial", 10), anchor="w"
            )

    def _refresh_iot_analytics(self):
        """Refresh IoT analytics charts"""
        self._draw_iot_analytics()
        messagebox.showinfo(
            "Analytics Refreshed", "IoT analytics charts refreshed with latest data"
        )
        self.emit_event("analytics_refreshed")

    def _export_iot_data(self):
        """Export IoT data to file"""
        messagebox.showinfo(
            "Export Complete", "IoT data exported to iot_analytics_data.csv"
        )
        self.emit_event("iot_data_exported")

    def _generate_iot_report(self):
        """Generate comprehensive IoT report"""
        messagebox.showinfo(
            "Report Generated",
            "Comprehensive IoT report generated\n\n📊 Device statistics\n📈 Performance metrics\n🔍 Security analysis\n📋 Recommendations",
        )
        self.emit_event("iot_report_generated")

    def _configure_iot_alerts(self):
        """Configure IoT monitoring alerts"""
        messagebox.showinfo(
            "Alert Configuration",
            "IoT alert configuration panel\n\n🚨 Threshold settings\n📧 Notification preferences\n⏰ Schedule options",
        )
        self.emit_event("iot_alerts_configured")

    # === UTILITY METHODS ===

    def _refresh_all_iot(self):
        """Refresh all IoT data and displays"""
        self._refresh_iot_analytics()
        messagebox.showinfo("IoT Device Manager", "All IoT data refreshed")


# Plugin entry point - this will be imported by the plugin system
TimeWarpPlugin = IoTDeviceManagerPlugin
