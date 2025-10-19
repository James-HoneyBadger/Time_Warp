#!/usr/bin/env python3
"""
Sensor Visualizer Plugin for Time_Warp IDE
Comprehensive sensor data visualization with real-time charts, data logging, and analysis capabilities
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import random
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Import the base framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.framework import ToolPlugin


class SensorVisualizerPlugin(ToolPlugin):
    """Sensor data visualization tool plugin"""

    def __init__(self, ide_instance, framework):
        super().__init__(ide_instance, framework)

        # Plugin metadata
        self.name = "Sensor Visualizer"
        self.version = "1.0.0"
        self.author = "Time_Warp IDE Team"
        self.description = "Comprehensive sensor data visualization with real-time charts, data logging, and analysis capabilities"
        self.category = "sensors"

        # Sensor state
        self.sensor_state = {
            "active_sensors": {},
            "data_log": [],
            "thresholds": {},
            "real_time_enabled": False,
            "logging_enabled": False,
        }

        # UI references
        self._tool_window = None
        self.charts_canvas = None
        self.history_canvas = None
        self.log_tree = None
        self.thresholds_tree = None
        self.alerts_text = None
        self.reports_listbox = None

        # Configuration variables
        self.log_interval_var = None
        self.log_file_var = None
        self.sensor_vars = {}
        self.export_format_var = None
        self.include_charts_var = None
        self.from_date_var = None
        self.to_date_var = None

    def initialize(self) -> bool:
        """Initialize the sensor visualizer plugin"""
        try:
            # Subscribe to relevant events
            self.subscribe_event("sensor_data_received", self._on_sensor_data_received)
            self.subscribe_event("sensor_connected", self._on_sensor_connected)
            self.subscribe_event("sensor_disconnected", self._on_sensor_disconnected)

            # Initialize default sensor configuration
            self._initialize_default_sensors()

            return True
        except Exception as e:
            print(f"Error initializing Sensor Visualizer: {e}")
            return False

    def activate(self) -> bool:
        """Activate the sensor visualizer"""
        try:
            # Add menu item
            self.add_menu_item(
                "Tools", "📊 Sensor Visualizer", self.show_tool_dialog, "Ctrl+Shift+S"
            )

            # Add toolbar item
            self.add_toolbar_item(
                "📊 Sensors", self.show_tool_dialog, tooltip="Open Sensor Visualizer"
            )

            return True
        except Exception as e:
            print(f"Error activating Sensor Visualizer: {e}")
            return False

    def deactivate(self) -> bool:
        """Deactivate the sensor visualizer"""
        try:
            # Stop any running monitoring
            self.sensor_state["real_time_enabled"] = False
            self.sensor_state["logging_enabled"] = False

            # Close visualizer window if open
            if self._tool_window:
                self._tool_window.destroy()
                self._tool_window = None

            return True
        except Exception as e:
            print(f"Error deactivating Sensor Visualizer: {e}")
            return False

    def show_tool_dialog(self):
        """Show sensor visualizer tool dialog"""
        if self._tool_window and self._tool_window.winfo_exists():
            self._tool_window.lift()
            return

        # Create tool window
        self._tool_window = tk.Toplevel(self.ide)
        self._tool_window.title("📊 Sensor Data Visualizer")
        self._tool_window.geometry("1000x700")
        self._tool_window.transient(self.ide)

        # Create UI
        ui_widget = self.create_ui(self._tool_window)
        ui_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_ui(self, parent_widget) -> tk.Widget:
        """Create the sensor visualizer UI"""
        try:
            # Main container
            main_frame = ttk.Frame(parent_widget)

            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                header_frame,
                text="📊 Sensor Data Visualizer",
                font=("Arial", 16, "bold"),
            ).pack(side=tk.LEFT)

            ttk.Button(
                header_frame, text="🔄 Refresh All", command=self._refresh_all_sensors
            ).pack(side=tk.RIGHT, padx=5)

            # Create notebook for different sensor aspects
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Setup tabs
            self._setup_live_data_tab(notebook)
            self._setup_charts_tab(notebook)
            self._setup_data_log_tab(notebook)
            self._setup_sensor_config_tab(notebook)
            self._setup_alerts_tab(notebook)

            return main_frame

        except Exception as e:
            print(f"Error creating sensor visualizer UI: {e}")
            return ttk.Label(
                parent_widget, text=f"Error creating sensor visualizer UI: {e}"
            )

    def _setup_live_data_tab(self, notebook):
        """Setup live sensor data tab"""
        live_frame = ttk.Frame(notebook)
        notebook.add(live_frame, text="📊 Live Data")

        # Real-time charts
        charts_frame = ttk.LabelFrame(live_frame, text="Real-time Sensor Charts")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create scrollable canvas for multiple charts
        self.charts_canvas = tk.Canvas(charts_frame, bg="white", height=500)
        self.charts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        charts_scroll = ttk.Scrollbar(
            charts_frame, orient=tk.VERTICAL, command=self.charts_canvas.yview
        )
        self.charts_canvas.config(yscrollcommand=charts_scroll.set)
        charts_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Draw initial sensor charts
        self._draw_sensor_charts()

        # Chart controls
        chart_controls = ttk.Frame(live_frame)
        chart_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            chart_controls,
            text="▶️ Start Real-time",
            command=self._start_realtime_monitoring,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            chart_controls, text="⏸️ Pause", command=self._pause_realtime_monitoring
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            chart_controls, text="🔄 Refresh", command=self._refresh_sensor_charts
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            chart_controls,
            text="⚙️ Configure Charts",
            command=self._configure_sensor_charts,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            chart_controls, text="📸 Save Chart", command=self._save_sensor_chart
        ).pack(side=tk.LEFT, padx=2)

    def _setup_charts_tab(self, notebook):
        """Setup customizable charts tab"""
        charts_frame = ttk.Frame(notebook)
        notebook.add(charts_frame, text="📈 Charts")

        # Historical charts
        history_frame = ttk.LabelFrame(charts_frame, text="Historical Analysis")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.history_canvas = tk.Canvas(history_frame, bg="white", height=400)
        self.history_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Draw historical charts
        self._draw_historical_charts()

        # Date range selection
        range_frame = ttk.LabelFrame(charts_frame, text="Data Range Selection")
        range_frame.pack(fill=tk.X, padx=5, pady=5)

        range_grid = ttk.Frame(range_frame)
        range_grid.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(range_grid, text="From:").grid(row=0, column=0, padx=5, pady=2)
        self.from_date_var = tk.StringVar(value="2024-01-01")
        ttk.Entry(range_grid, textvariable=self.from_date_var).grid(
            row=0, column=1, padx=5, pady=2
        )

        ttk.Label(range_grid, text="To:").grid(row=0, column=2, padx=5, pady=2)
        self.to_date_var = tk.StringVar(value="2024-01-15")
        ttk.Entry(range_grid, textvariable=self.to_date_var).grid(
            row=0, column=3, padx=5, pady=2
        )

        ttk.Button(
            range_grid, text="📊 Load Data", command=self._load_historical_data
        ).grid(row=0, column=4, padx=5, pady=2)

        # Analysis controls
        analysis_controls = ttk.Frame(charts_frame)
        analysis_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            analysis_controls, text="📈 Trend Analysis", command=self._analyze_trends
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            analysis_controls, text="📊 Statistics", command=self._show_statistics
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            analysis_controls, text="🔍 Find Patterns", command=self._find_patterns
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            analysis_controls,
            text="⚠️ Anomaly Detection",
            command=self._detect_anomalies,
        ).pack(side=tk.LEFT, padx=2)

    def _setup_data_log_tab(self, notebook):
        """Setup data logging tab"""
        logger_frame = ttk.Frame(notebook)
        notebook.add(logger_frame, text="📝 Data Log")

        # Logger configuration
        config_frame = ttk.LabelFrame(logger_frame, text="Data Logger Configuration")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(config_grid, text="Log Interval:").grid(
            row=0, column=0, padx=5, pady=2, sticky="e"
        )
        self.log_interval_var = tk.StringVar(value="5 seconds")
        ttk.Combobox(
            config_grid,
            textvariable=self.log_interval_var,
            values=["1 second", "5 seconds", "10 seconds", "30 seconds", "1 minute"],
        ).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(config_grid, text="Log File:").grid(
            row=0, column=2, padx=5, pady=2, sticky="e"
        )
        self.log_file_var = tk.StringVar(value="sensor_data.csv")
        ttk.Entry(config_grid, textvariable=self.log_file_var, width=20).grid(
            row=0, column=3, padx=5, pady=2
        )
        ttk.Button(config_grid, text="📁 Browse", command=self._browse_log_file).grid(
            row=0, column=4, padx=5, pady=2
        )

        # Data log display
        log_frame = ttk.LabelFrame(logger_frame, text="Recent Log Entries")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log treeview
        columns = ("Timestamp", "Sensor", "Value", "Unit", "Status")
        self.log_tree = ttk.Treeview(
            log_frame, columns=columns, show="headings", height=12
        )

        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=120)

        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_scroll = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_tree.yview
        )
        self.log_tree.config(yscrollcommand=log_scroll.set)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Populate with sample log entries
        self._populate_sample_log_entries()

        # Logger controls
        logger_controls = ttk.Frame(logger_frame)
        logger_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            logger_controls, text="▶️ Start Logging", command=self._start_data_logging
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            logger_controls, text="⏹️ Stop Logging", command=self._stop_data_logging
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            logger_controls, text="🧹 Clear Log", command=self._clear_data_log
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            logger_controls, text="💾 Export Log", command=self._export_data_log
        ).pack(side=tk.LEFT, padx=2)

    def _setup_sensor_config_tab(self, notebook):
        """Setup sensor configuration tab"""
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="⚙️ Sensors")

        # Active sensors selection
        sensors_frame = ttk.LabelFrame(config_frame, text="Active Sensors")
        sensors_frame.pack(fill=tk.X, padx=5, pady=5)

        sensor_names = [
            "Temperature",
            "Humidity",
            "Pressure",
            "Light Level",
            "Motion",
            "Distance",
            "Air Quality",
            "Sound Level",
        ]

        sensors_grid = ttk.Frame(sensors_frame)
        sensors_grid.pack(fill=tk.X, padx=5, pady=5)

        for i, sensor in enumerate(sensor_names):
            var = tk.BooleanVar(value=True)
            self.sensor_vars[sensor] = var
            row = i // 4
            col = i % 4
            ttk.Checkbutton(sensors_grid, text=sensor, variable=var).grid(
                row=row, column=col, padx=10, pady=2, sticky="w"
            )

        # Export configuration
        export_config_frame = ttk.LabelFrame(config_frame, text="Export Configuration")
        export_config_frame.pack(fill=tk.X, padx=5, pady=5)

        export_grid = ttk.Frame(export_config_frame)
        export_grid.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(export_grid, text="Format:").grid(
            row=0, column=0, padx=5, pady=2, sticky="e"
        )
        self.export_format_var = tk.StringVar(value="CSV")
        ttk.Combobox(
            export_grid,
            textvariable=self.export_format_var,
            values=["CSV", "JSON", "XML", "Excel", "PDF"],
        ).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(export_grid, text="Include:").grid(
            row=0, column=2, padx=5, pady=2, sticky="e"
        )
        self.include_charts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            export_grid, text="Charts", variable=self.include_charts_var
        ).grid(row=0, column=3, padx=5, pady=2)

        # Available reports
        reports_frame = ttk.LabelFrame(config_frame, text="Available Reports")
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        reports_list = [
            "📊 Daily Sensor Summary",
            "📈 Weekly Trend Analysis",
            "📉 Monthly Performance Report",
            "🚨 Alert History Report",
            "📋 Sensor Calibration Report",
            "🔍 Data Quality Assessment",
            "📊 Comparative Analysis",
            "📱 Mobile Dashboard Export",
        ]

        self.reports_listbox = tk.Listbox(reports_frame, font=("Arial", 10))
        self.reports_listbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        for report in reports_list:
            self.reports_listbox.insert(tk.END, report)

        reports_scroll = ttk.Scrollbar(
            reports_frame, orient=tk.VERTICAL, command=self.reports_listbox.yview
        )
        self.reports_listbox.config(yscrollcommand=reports_scroll.set)
        reports_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Export controls
        export_controls = ttk.Frame(config_frame)
        export_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            export_controls,
            text="📄 Generate Report",
            command=self._generate_sensor_report,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            export_controls, text="💾 Export Data", command=self._export_sensor_data
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            export_controls, text="📧 Email Report", command=self._email_sensor_report
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            export_controls, text="🌐 Web Dashboard", command=self._open_web_dashboard
        ).pack(side=tk.LEFT, padx=2)

    def _setup_alerts_tab(self, notebook):
        """Setup sensor alerts and thresholds tab"""
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="🚨 Alerts")

        # Threshold configuration
        thresholds_frame = ttk.LabelFrame(alerts_frame, text="Sensor Thresholds")
        thresholds_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Thresholds treeview
        columns = ("Sensor", "Min Value", "Max Value", "Current", "Status", "Actions")
        self.thresholds_tree = ttk.Treeview(
            thresholds_frame, columns=columns, show="headings", height=10
        )

        for col in columns:
            self.thresholds_tree.heading(col, text=col)
            self.thresholds_tree.column(col, width=100)

        self.thresholds_tree.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        thresholds_scroll = ttk.Scrollbar(
            thresholds_frame, orient=tk.VERTICAL, command=self.thresholds_tree.yview
        )
        self.thresholds_tree.config(yscrollcommand=thresholds_scroll.set)
        thresholds_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Populate threshold settings
        self._populate_threshold_settings()

        # Alert history
        alerts_history_frame = ttk.LabelFrame(alerts_frame, text="Recent Alerts")
        alerts_history_frame.pack(fill=tk.X, padx=5, pady=5)

        self.alerts_text = scrolledtext.ScrolledText(
            alerts_history_frame, height=8, font=("Consolas", 9)
        )
        self.alerts_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add sample alerts
        self._populate_sample_alerts()

        # Alert controls
        alert_controls = ttk.Frame(alerts_frame)
        alert_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            alert_controls,
            text="⚙️ Configure Thresholds",
            command=self._configure_thresholds,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(alert_controls, text="🧪 Test Alert", command=self._test_alert).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            alert_controls, text="🧹 Clear Alerts", command=self._clear_alerts
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            alert_controls, text="📧 Email Alerts", command=self._setup_email_alerts
        ).pack(side=tk.LEFT, padx=2)

    # === EVENT HANDLERS ===

    def _on_sensor_data_received(self, sensor_name, value, unit):
        """Handle sensor data received event"""
        print(f"Sensor Visualizer: Received data from {sensor_name}: {value} {unit}")
        # Update real-time charts if enabled
        if self.sensor_state["real_time_enabled"]:
            self._update_realtime_data(sensor_name, value, unit)

    def _on_sensor_connected(self, sensor_name):
        """Handle sensor connected event"""
        print(f"Sensor Visualizer: {sensor_name} connected")
        self.emit_event("sensor_configured", sensor_name)

    def _on_sensor_disconnected(self, sensor_name):
        """Handle sensor disconnected event"""
        print(f"Sensor Visualizer: {sensor_name} disconnected")

    # === INITIALIZATION METHODS ===

    def _initialize_default_sensors(self):
        """Initialize default sensor configuration"""
        default_sensors = {
            "Temperature": {"min": 18, "max": 28, "unit": "°C", "current": 23.5},
            "Humidity": {"min": 40, "max": 70, "unit": "%", "current": 65.2},
            "Pressure": {"min": 990, "max": 1030, "unit": "hPa", "current": 1013.2},
            "Light Level": {"min": 100, "max": 1000, "unit": "lux", "current": 450},
            "Air Quality": {"min": 0, "max": 50, "unit": "ppm", "current": 15},
            "Sound Level": {"min": 30, "max": 80, "unit": "dB", "current": 45},
        }

        self.sensor_state["active_sensors"] = default_sensors

        for sensor, config in default_sensors.items():
            self.sensor_state["thresholds"][sensor] = {
                "min": config["min"],
                "max": config["max"],
                "unit": config["unit"],
            }

    # === CHART DRAWING METHODS ===

    def _draw_sensor_charts(self):
        """Draw real-time sensor charts"""
        if not self.charts_canvas:
            return

        canvas = self.charts_canvas
        canvas.delete("all")

        # Chart 1: Temperature over time
        self._draw_line_chart(
            canvas,
            50,
            50,
            300,
            150,
            "Temperature (°C)",
            [(0, 22), (10, 23), (20, 24), (30, 23.5), (40, 25), (50, 24.2)],
            "#FF6B6B",
        )

        # Chart 2: Humidity over time
        self._draw_line_chart(
            canvas,
            400,
            50,
            300,
            150,
            "Humidity (%)",
            [(0, 60), (10, 62), (20, 65), (30, 63), (40, 67), (50, 65.2)],
            "#4ECDC4",
        )

        # Chart 3: Light level
        self._draw_bar_chart(
            canvas,
            50,
            250,
            300,
            150,
            "Light Level (lux)",
            ["Morning", "Noon", "Afternoon", "Evening", "Night"],
            [200, 800, 600, 300, 50],
            "#95E1D3",
        )

        # Chart 4: Sensor status indicators
        self._draw_status_indicators(canvas, 400, 250, 300, 150)

    def _draw_line_chart(self, canvas, x, y, width, height, title, data, color):
        """Draw a line chart on canvas"""
        # Chart border and title
        canvas.create_rectangle(
            x, y, x + width, y + height, outline="black", fill="white"
        )
        canvas.create_text(
            x + width // 2, y - 10, text=title, font=("Arial", 10, "bold")
        )

        # Scale data to fit chart
        if not data or len(data) < 2:
            canvas.create_text(
                x + width // 2, y + height // 2, text="No Data", font=("Arial", 12)
            )
            return

        max_val = max(point[1] for point in data)
        min_val = min(point[1] for point in data)
        val_range = max_val - min_val if max_val != min_val else 1
        max_x = max(point[0] for point in data)

        # Draw data points and lines
        for i in range(len(data) - 1):
            x1_data, y1_data = data[i]
            x2_data, y2_data = data[i + 1]

            x1_pos = x + (x1_data / max_x) * (width - 20) + 10
            y1_pos = y + height - ((y1_data - min_val) / val_range) * (height - 20) - 10

            x2_pos = x + (x2_data / max_x) * (width - 20) + 10
            y2_pos = y + height - ((y2_data - min_val) / val_range) * (height - 20) - 10

            canvas.create_line(x1_pos, y1_pos, x2_pos, y2_pos, fill=color, width=2)
            canvas.create_oval(
                x1_pos - 3, y1_pos - 3, x1_pos + 3, y1_pos + 3, fill=color
            )

    def _draw_bar_chart(
        self, canvas, x, y, width, height, title, labels, values, color
    ):
        """Draw a bar chart on canvas"""
        canvas.create_rectangle(
            x, y, x + width, y + height, outline="black", fill="white"
        )
        canvas.create_text(
            x + width // 2, y - 10, text=title, font=("Arial", 10, "bold")
        )

        if not values:
            canvas.create_text(
                x + width // 2, y + height // 2, text="No Data", font=("Arial", 12)
            )
            return

        max_val = max(values)
        bar_width = (width - 40) // len(values)

        for i, (label, value) in enumerate(zip(labels, values)):
            bar_x = x + 20 + i * bar_width
            bar_height = (value / max_val) * (height - 40)
            bar_y = y + height - 20 - bar_height

            canvas.create_rectangle(
                bar_x,
                bar_y,
                bar_x + bar_width - 5,
                y + height - 20,
                fill=color,
                outline="black",
            )
            canvas.create_text(
                bar_x + bar_width // 2,
                y + height - 5,
                text=label[:8],
                font=("Arial", 8),
                angle=45,
            )

    def _draw_status_indicators(self, canvas, x, y, width, height):
        """Draw sensor status indicators"""
        canvas.create_rectangle(
            x, y, x + width, y + height, outline="black", fill="white"
        )
        canvas.create_text(
            x + width // 2, y - 10, text="Sensor Status", font=("Arial", 10, "bold")
        )

        sensors = [
            ("Temperature", "Online", "#4CAF50"),
            ("Humidity", "Online", "#4CAF50"),
            ("Motion", "Alert", "#FF9800"),
            ("Light", "Online", "#4CAF50"),
            ("Air Quality", "Offline", "#F44336"),
        ]

        for i, (sensor, status, color) in enumerate(sensors):
            indicator_y = y + 30 + i * 20
            canvas.create_oval(
                x + 20, indicator_y, x + 30, indicator_y + 10, fill=color
            )
            canvas.create_text(
                x + 50,
                indicator_y + 5,
                text=f"{sensor}: {status}",
                font=("Arial", 9),
                anchor="w",
            )

    def _draw_historical_charts(self):
        """Draw historical data analysis charts"""
        if not self.history_canvas:
            return

        canvas = self.history_canvas
        canvas.delete("all")

        # Historical trend chart
        canvas.create_text(
            500, 20, text="Historical Sensor Data Analysis", font=("Arial", 14, "bold")
        )

        # Multi-sensor trend lines
        self._draw_line_chart(
            canvas,
            50,
            50,
            400,
            200,
            "Temperature Trend (7 Days)",
            [(0, 20), (1, 22), (2, 25), (3, 23), (4, 24), (5, 26), (6, 23.5)],
            "#FF6B6B",
        )

        self._draw_line_chart(
            canvas,
            500,
            50,
            400,
            200,
            "Humidity Trend (7 Days)",
            [(0, 55), (1, 60), (2, 65), (3, 62), (4, 68), (5, 63), (6, 65.2)],
            "#4ECDC4",
        )

        # Statistics summary
        stats_text = """Data Summary (Last 7 Days):
        
Temperature: Avg 23.2°C, Min 20.0°C, Max 26.0°C
Humidity: Avg 62.7%, Min 55.0%, Max 68.0%
Pressure: Avg 1013.5 hPa, Min 995.2 hPa, Max 1025.8 hPa
Light: Avg 425 lux, Min 50 lux, Max 850 lux

Alerts Generated: 5
Data Points Collected: 10,080
Uptime: 99.8%"""

        canvas.create_text(50, 300, text=stats_text, font=("Consolas", 9), anchor="nw")

    # === DATA POPULATION METHODS ===

    def _populate_sample_log_entries(self):
        """Populate log tree with sample entries"""
        if not self.log_tree:
            return

        sample_logs = [
            ("2024-01-15 14:30:25", "Temperature", "23.5", "°C", "Normal"),
            ("2024-01-15 14:30:20", "Humidity", "65.2", "%", "Normal"),
            ("2024-01-15 14:30:15", "Pressure", "1013.2", "hPa", "Normal"),
            ("2024-01-15 14:30:10", "Light Level", "450", "lux", "Normal"),
            ("2024-01-15 14:30:05", "Motion", "1", "detected", "Alert"),
            ("2024-01-15 14:30:00", "Distance", "15.2", "cm", "Normal"),
        ]

        for log_entry in sample_logs:
            self.log_tree.insert("", "end", values=log_entry)

    def _populate_threshold_settings(self):
        """Populate thresholds tree with settings"""
        if not self.thresholds_tree:
            return

        threshold_data = [
            ("Temperature", "18°C", "28°C", "23.5°C", "Normal", "None"),
            ("Humidity", "40%", "70%", "65.2%", "Normal", "None"),
            ("Pressure", "990 hPa", "1030 hPa", "1013.2 hPa", "Normal", "None"),
            ("Light Level", "100 lux", "1000 lux", "450 lux", "Normal", "None"),
            ("Air Quality", "0 ppm", "50 ppm", "15 ppm", "Normal", "None"),
            ("Sound Level", "30 dB", "80 dB", "45 dB", "Normal", "None"),
        ]

        for threshold in threshold_data:
            self.thresholds_tree.insert("", "end", values=threshold)

    def _populate_sample_alerts(self):
        """Populate alerts text with sample alerts"""
        if not self.alerts_text:
            return

        sample_alerts = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚨 HIGH ALERT: Motion sensor triggered in Zone A
[{(datetime.now() - timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ WARNING: Temperature exceeded 28°C (29.2°C) in Server Room
[{(datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')}] ℹ️ INFO: Humidity sensor calibrated successfully
[{(datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')}] 🚨 HIGH ALERT: Air quality exceeded threshold (65 ppm)
[{(datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')}] ✅ RESOLVED: Temperature back to normal range (24.1°C)
[{(datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ WARNING: Low light level detected (85 lux)"""

        self.alerts_text.insert(tk.END, sample_alerts)

    # === ACTION METHODS ===

    def _start_realtime_monitoring(self):
        """Start real-time sensor monitoring"""
        self.sensor_state["real_time_enabled"] = True
        messagebox.showinfo(
            "Real-time Monitor",
            "Real-time sensor monitoring started\n\n📊 Updating charts every 5 seconds\n📡 Receiving live data streams",
        )
        self.emit_event("visualization_updated", "real_time_started")

    def _pause_realtime_monitoring(self):
        """Pause real-time sensor monitoring"""
        self.sensor_state["real_time_enabled"] = False
        messagebox.showinfo("Real-time Monitor", "Real-time sensor monitoring paused")
        self.emit_event("visualization_updated", "real_time_paused")

    def _refresh_sensor_charts(self):
        """Refresh sensor charts"""
        self._draw_sensor_charts()
        messagebox.showinfo(
            "Charts Refreshed", "Sensor charts refreshed with latest data"
        )
        self.emit_event("visualization_updated", "charts_refreshed")

    def _configure_sensor_charts(self):
        """Configure sensor chart settings"""
        messagebox.showinfo(
            "Chart Configuration",
            "Chart configuration dialog\n\n⚙️ Chart types and colors\n📊 Display preferences\n🎨 Styling options",
        )

    def _save_sensor_chart(self):
        """Save current sensor chart"""
        messagebox.showinfo("Chart Saved", "Current sensor chart saved as image")
        self.emit_event("data_exported", "chart_saved")

    def _load_historical_data(self):
        """Load historical data for analysis"""
        if not self.from_date_var or not self.to_date_var:
            messagebox.showwarning("Date Range", "Date range not set")
            return

        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        messagebox.showinfo(
            "Historical Data",
            f"Loading historical data from {from_date} to {to_date}\n\n📊 Processing data...\n✅ Data loaded successfully",
        )
        self._draw_historical_charts()

    def _analyze_trends(self):
        """Analyze sensor data trends"""
        messagebox.showinfo(
            "Trend Analysis",
            "Trend analysis complete\n\n📈 Temperature: Upward trend\n📊 Humidity: Stable\n📉 Pressure: Slight decline\n💡 Light: Seasonal variation",
        )

    def _show_statistics(self):
        """Show sensor statistics"""
        messagebox.showinfo(
            "Statistics",
            "Sensor Statistics Summary\n\n📊 Data points: 10,080\n📈 Average readings within normal range\n⚠️ 5% of readings triggered alerts\n✅ 99.8% sensor uptime",
        )

    def _find_patterns(self):
        """Find patterns in sensor data"""
        messagebox.showinfo(
            "Pattern Analysis",
            "Pattern analysis complete\n\n🔍 Daily temperature cycle detected\n📅 Weekly humidity patterns found\n🌡️ Seasonal pressure variations identified",
        )

    def _detect_anomalies(self):
        """Detect anomalies in sensor data"""
        messagebox.showinfo(
            "Anomaly Detection",
            "Anomaly detection complete\n\n⚠️ 3 temperature spikes detected\n🔍 2 humidity anomalies found\n✅ No critical anomalies",
        )

    def _start_data_logging(self):
        """Start data logging"""
        self.sensor_state["logging_enabled"] = True
        messagebox.showinfo(
            "Data Logging",
            "Data logging started\n\n📝 Logging sensor data\n💾 Saving to file",
        )
        self.emit_event("data_logging_started")

    def _stop_data_logging(self):
        """Stop data logging"""
        self.sensor_state["logging_enabled"] = False
        messagebox.showinfo("Data Logging", "Data logging stopped")
        self.emit_event("data_logging_stopped")

    def _clear_data_log(self):
        """Clear data log"""
        if not self.log_tree:
            return
        if messagebox.askyesno("Clear Log", "Clear all log entries?"):
            self.log_tree.delete(*self.log_tree.get_children())
            messagebox.showinfo("Log Cleared", "Data log cleared")

    def _export_data_log(self):
        """Export data log"""
        messagebox.showinfo("Export Complete", "Data log exported to sensor_data.csv")
        self.emit_event("data_exported", "log_exported")

    def _browse_log_file(self):
        """Browse for log file location"""
        if not self.log_file_var:
            return
        filename = filedialog.asksaveasfilename(
            title="Select Log File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            self.log_file_var.set(filename)

    def _generate_sensor_report(self):
        """Generate sensor report"""
        messagebox.showinfo(
            "Report Generated",
            "Sensor report generated\n\n📊 Daily summary report\n📈 Trend analysis included\n💾 Saved as PDF",
        )
        self.emit_event("data_exported", "report_generated")

    def _export_sensor_data(self):
        """Export sensor data"""
        if not self.export_format_var:
            return
        format_type = self.export_format_var.get()
        messagebox.showinfo("Export Complete", f"Sensor data exported as {format_type}")
        self.emit_event("data_exported", format_type.lower())

    def _email_sensor_report(self):
        """Email sensor report"""
        messagebox.showinfo(
            "Email Report",
            "Sensor report emailed\n\n📧 Report sent to configured recipients\n✅ Delivery confirmed",
        )

    def _open_web_dashboard(self):
        """Open web dashboard"""
        messagebox.showinfo(
            "Web Dashboard",
            "Opening web dashboard\n\n🌐 Dashboard available at http://localhost:8080\n📱 Mobile-friendly interface",
        )

    def _configure_thresholds(self):
        """Configure sensor thresholds"""
        messagebox.showinfo(
            "Threshold Configuration",
            "Threshold configuration panel\n\n⚙️ Min/Max values\n🚨 Alert settings\n📧 Notification preferences",
        )

    def _test_alert(self):
        """Test alert system"""
        messagebox.showinfo(
            "Alert Test",
            "Alert system test\n\n🧪 Test alert sent\n✅ Alert system functioning",
        )
        self.emit_event("alert_triggered", "test_alert")

    def _clear_alerts(self):
        """Clear alert history"""
        if not self.alerts_text:
            return
        if messagebox.askyesno("Clear Alerts", "Clear all alert history?"):
            self.alerts_text.delete("1.0", tk.END)
            messagebox.showinfo("Alerts Cleared", "Alert history cleared")

    def _setup_email_alerts(self):
        """Setup email alerts"""
        messagebox.showinfo(
            "Email Alerts",
            "Email alert configuration\n\n📧 Email settings\n⏰ Alert schedules\n👥 Recipient lists",
        )

    def _update_realtime_data(self, sensor_name, value, unit):
        """Update real-time data display"""
        # Add new data point to log if logging enabled
        if self.sensor_state["logging_enabled"] and self.log_tree:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "Normal"  # Could be determined by threshold checking
            self.log_tree.insert(
                "", 0, values=(timestamp, sensor_name, value, unit, status)
            )

        # Update charts if canvas exists
        if self.charts_canvas:
            self._draw_sensor_charts()

    def _refresh_all_sensors(self):
        """Refresh all sensor data and displays"""
        self._draw_sensor_charts()
        self._draw_historical_charts()
        messagebox.showinfo("Sensor Visualizer", "All sensor data refreshed")


# Plugin entry point - this will be imported by the plugin system
TimeWarpPlugin = SensorVisualizerPlugin
