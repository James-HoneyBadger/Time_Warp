"""
Performance Monitoring and Memory Analysis for Time_Warp IDE
Real-time performance tracking, memory usage analysis, and profiling tools
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import sys
import gc
import cProfile
import pstats
import io
import tracemalloc
from typing import Dict, List, Any, Optional, Callable
from collections import deque, defaultdict
from datetime import datetime, timedelta

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PerformanceMonitor:
    """Real-time performance monitoring with live charts and metrics"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()

        # Performance tracking
        self.is_monitoring = False
        self.monitor_thread = None
        self.performance_data = {
            "cpu_usage": deque(maxlen=100),
            "memory_usage": deque(maxlen=100),
            "timestamps": deque(maxlen=100),
            "function_calls": defaultdict(int),
            "execution_times": defaultdict(list),
        }

        # Process reference
        self.process = psutil.Process()

    def setup_ui(self):
        """Create the performance monitoring interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Performance Monitor")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control buttons
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_btn = ttk.Button(
            control_frame, text="Start Monitoring", command=self.start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.stop_btn = ttk.Button(
            control_frame,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(control_frame, text="Clear Data", command=self.clear_data).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            control_frame, text="Export Report", command=self.export_report
        ).pack(side=tk.LEFT, padx=2)

        # Notebook for different views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Live charts tab
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Live Charts")
        self.setup_charts()

        # Metrics tab
        self.metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.metrics_frame, text="Metrics")
        self.setup_metrics()

        # Function profiling tab
        self.profiling_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profiling_frame, text="Function Profiling")
        self.setup_profiling()

    def setup_charts(self):
        """Setup live performance charts"""
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create subplots
        self.cpu_ax = self.figure.add_subplot(2, 1, 1)
        self.memory_ax = self.figure.add_subplot(2, 1, 2)

        # Configure axes
        self.cpu_ax.set_title("CPU Usage (%)")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.grid(True, alpha=0.3)

        self.memory_ax.set_title("Memory Usage (MB)")
        self.memory_ax.grid(True, alpha=0.3)
        self.memory_ax.set_xlabel("Time")

        # Initialize empty plots
        (self.cpu_line,) = self.cpu_ax.plot([], [], "b-", linewidth=2)
        (self.memory_line,) = self.memory_ax.plot([], [], "r-", linewidth=2)

        self.figure.tight_layout()

    def setup_metrics(self):
        """Setup metrics display"""
        # Current metrics frame
        current_frame = ttk.LabelFrame(self.metrics_frame, text="Current Metrics")
        current_frame.pack(fill=tk.X, padx=5, pady=5)

        # Metrics labels
        self.cpu_label = ttk.Label(current_frame, text="CPU Usage: N/A")
        self.cpu_label.pack(anchor=tk.W, padx=5, pady=2)

        self.memory_label = ttk.Label(current_frame, text="Memory Usage: N/A")
        self.memory_label.pack(anchor=tk.W, padx=5, pady=2)

        self.threads_label = ttk.Label(current_frame, text="Thread Count: N/A")
        self.threads_label.pack(anchor=tk.W, padx=5, pady=2)

        self.handles_label = ttk.Label(current_frame, text="Open Handles: N/A")
        self.handles_label.pack(anchor=tk.W, padx=5, pady=2)

        # Statistics frame
        stats_frame = ttk.LabelFrame(self.metrics_frame, text="Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.stats_text = tk.Text(stats_frame, wrap=tk.WORD, height=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        stats_scroll = ttk.Scrollbar(
            stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview
        )
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)

    def setup_profiling(self):
        """Setup function profiling display"""
        # Control frame
        profile_control = ttk.Frame(self.profiling_frame)
        profile_control.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            profile_control, text="Start Profiling", command=self.start_profiling
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            profile_control, text="Stop Profiling", command=self.stop_profiling
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            profile_control, text="Clear Profile", command=self.clear_profile
        ).pack(side=tk.LEFT, padx=2)

        # Profiling results
        self.profile_tree = ttk.Treeview(
            self.profiling_frame,
            columns=("calls", "total_time", "per_call", "cumulative"),
            show="tree headings",
        )
        self.profile_tree.heading("#0", text="Function")
        self.profile_tree.heading("calls", text="Calls")
        self.profile_tree.heading("total_time", text="Total Time")
        self.profile_tree.heading("per_call", text="Per Call")
        self.profile_tree.heading("cumulative", text="Cumulative")

        self.profile_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar for profile tree
        profile_scroll = ttk.Scrollbar(
            self.profiling_frame, orient=tk.VERTICAL, command=self.profile_tree.yview
        )
        profile_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_tree.configure(yscrollcommand=profile_scroll.set)

        # Profiler state
        self.profiler = None
        self.is_profiling = False

    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)

            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect performance data
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                timestamp = datetime.now()

                # Store data
                self.performance_data["cpu_usage"].append(cpu_percent)
                self.performance_data["memory_usage"].append(memory_mb)
                self.performance_data["timestamps"].append(timestamp)

                # Update UI (thread-safe)
                self.parent.after(0, self._update_ui, cpu_percent, memory_mb)

                time.sleep(1)  # Update every second

            except Exception as e:
                print(f"Monitor error: {e}")
                break

    def _update_ui(self, cpu_percent: float, memory_mb: float):
        """Update UI with new performance data"""
        # Update current metrics
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
        self.memory_label.config(text=f"Memory Usage: {memory_mb:.1f} MB")

        try:
            thread_count = self.process.num_threads()
            self.threads_label.config(text=f"Thread Count: {thread_count}")

            if hasattr(self.process, "num_handles"):
                handles = self.process.num_handles()
                self.handles_label.config(text=f"Open Handles: {handles}")
        except Exception:
            pass  # Some metrics may not be available on all platforms

        # Update charts
        self._update_charts()

        # Update statistics
        self._update_statistics()

    def _update_charts(self):
        """Update performance charts"""
        if len(self.performance_data["timestamps"]) < 2:
            return

        # Convert timestamps to relative seconds for plotting
        base_time = self.performance_data["timestamps"][0]
        time_data = [
            (t - base_time).total_seconds() for t in self.performance_data["timestamps"]
        ]

        # Update CPU chart
        self.cpu_line.set_data(time_data, list(self.performance_data["cpu_usage"]))
        self.cpu_ax.set_xlim(min(time_data), max(time_data))
        self.cpu_ax.set_ylim(0, max(100, max(self.performance_data["cpu_usage"]) * 1.1))

        # Update memory chart
        self.memory_line.set_data(
            time_data, list(self.performance_data["memory_usage"])
        )
        self.memory_ax.set_xlim(min(time_data), max(time_data))
        memory_max = max(self.performance_data["memory_usage"])
        self.memory_ax.set_ylim(0, memory_max * 1.1)

        # Refresh canvas
        self.canvas.draw()

    def _update_statistics(self):
        """Update performance statistics"""
        if len(self.performance_data["cpu_usage"]) == 0:
            return

        cpu_data = list(self.performance_data["cpu_usage"])
        memory_data = list(self.performance_data["memory_usage"])

        stats_text = "Performance Statistics:\n\n"
        stats_text += "CPU Usage:\n"
        stats_text += f"  Current: {cpu_data[-1]:.1f}%\n"
        stats_text += f"  Average: {np.mean(cpu_data):.1f}%\n"
        stats_text += f"  Maximum: {np.max(cpu_data):.1f}%\n"
        stats_text += f"  Minimum: {np.min(cpu_data):.1f}%\n\n"

        stats_text += "Memory Usage:\n"
        stats_text += f"  Current: {memory_data[-1]:.1f} MB\n"
        stats_text += f"  Average: {np.mean(memory_data):.1f} MB\n"
        stats_text += f"  Maximum: {np.max(memory_data):.1f} MB\n"
        stats_text += f"  Minimum: {np.min(memory_data):.1f} MB\n\n"

        # Update text widget
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)

    def start_profiling(self):
        """Start function profiling"""
        if not self.is_profiling:
            self.profiler = cProfile.Profile()
            self.profiler.enable()
            self.is_profiling = True

    def stop_profiling(self):
        """Stop function profiling and display results"""
        if self.is_profiling and self.profiler:
            self.profiler.disable()
            self.is_profiling = False
            self._display_profile_results()

    def _display_profile_results(self):
        """Display profiling results in the tree"""
        # Clear existing results
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)

        # Get profiling statistics
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.sort_stats("cumulative")

        # Extract top functions
        stats = ps.get_stats_profile()

        for func_info, (cc, nc, tt, ct, callers) in list(stats.func_profiles.items())[
            :50
        ]:  # Top 50
            filename, line_num, func_name = func_info

            # Format function name
            display_name = f"{func_name} ({filename.split('/')[-1]}:{line_num})"

            # Insert into tree
            self.profile_tree.insert(
                "",
                "end",
                text=display_name,
                values=(
                    nc,
                    f"{tt:.4f}s",
                    f"{tt/nc:.4f}s" if nc > 0 else "0",
                    f"{ct:.4f}s",
                ),
            )

    def clear_profile(self):
        """Clear profiling results"""
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        self.profiler = None

    def clear_data(self):
        """Clear all monitoring data"""
        self.performance_data["cpu_usage"].clear()
        self.performance_data["memory_usage"].clear()
        self.performance_data["timestamps"].clear()
        self.performance_data["function_calls"].clear()
        self.performance_data["execution_times"].clear()

        # Clear UI
        self._update_charts()
        self.stats_text.delete(1.0, tk.END)

    def export_report(self):
        """Export performance report"""
        if len(self.performance_data["timestamps"]) == 0:
            return

        # Generate report
        report = self._generate_report()

        # Save to file
        filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, "w") as f:
                f.write(report)
            print(f"Performance report saved to {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")

    def _generate_report(self) -> str:
        """Generate performance report"""
        report = "Time_Warp IDE Performance Report\n"
        report += "=" * 50 + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Monitoring Duration: {len(self.performance_data['timestamps'])} seconds\n\n"

        if self.performance_data["cpu_usage"]:
            cpu_data = list(self.performance_data["cpu_usage"])
            memory_data = list(self.performance_data["memory_usage"])

            report += "CPU Usage Statistics:\n"
            report += f"  Average: {np.mean(cpu_data):.2f}%\n"
            report += f"  Maximum: {np.max(cpu_data):.2f}%\n"
            report += f"  Minimum: {np.min(cpu_data):.2f}%\n"
            report += f"  Standard Deviation: {np.std(cpu_data):.2f}%\n\n"

            report += "Memory Usage Statistics:\n"
            report += f"  Average: {np.mean(memory_data):.2f} MB\n"
            report += f"  Maximum: {np.max(memory_data):.2f} MB\n"
            report += f"  Minimum: {np.min(memory_data):.2f} MB\n"
            report += f"  Standard Deviation: {np.std(memory_data):.2f} MB\n\n"

        return report


class MemoryAnalyzer:
    """Memory usage analysis and leak detection"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()

        # Memory tracking
        self.is_tracking = False
        self.snapshots = []
        self.current_snapshot = None

    def setup_ui(self):
        """Create memory analyzer interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Memory Analyzer")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control buttons
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            control_frame, text="Start Tracking", command=self.start_tracking
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="Take Snapshot", command=self.take_snapshot
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="Stop Tracking", command=self.stop_tracking
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="Analyze Leaks", command=self.analyze_leaks
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="Clear Snapshots", command=self.clear_snapshots
        ).pack(side=tk.LEFT, padx=2)

        # Notebook for different views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Memory overview tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")
        self.setup_overview()

        # Object tracking tab
        self.objects_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.objects_frame, text="Object Tracking")
        self.setup_object_tracking()

        # Leak detection tab
        self.leaks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.leaks_frame, text="Leak Detection")
        self.setup_leak_detection()

    def setup_overview(self):
        """Setup memory overview"""
        self.overview_text = scrolledtext.ScrolledText(
            self.overview_frame, wrap=tk.WORD, width=80, height=20
        )
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_object_tracking(self):
        """Setup object tracking display"""
        self.objects_tree = ttk.Treeview(
            self.objects_frame,
            columns=("count", "size", "avg_size"),
            show="tree headings",
        )
        self.objects_tree.heading("#0", text="Object Type")
        self.objects_tree.heading("count", text="Count")
        self.objects_tree.heading("size", text="Total Size")
        self.objects_tree.heading("avg_size", text="Avg Size")

        self.objects_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        objects_scroll = ttk.Scrollbar(
            self.objects_frame, orient=tk.VERTICAL, command=self.objects_tree.yview
        )
        objects_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.objects_tree.configure(yscrollcommand=objects_scroll.set)

    def setup_leak_detection(self):
        """Setup leak detection display"""
        self.leaks_text = scrolledtext.ScrolledText(
            self.leaks_frame, wrap=tk.WORD, width=80, height=20
        )
        self.leaks_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def start_tracking(self):
        """Start memory tracking"""
        if not self.is_tracking:
            tracemalloc.start()
            self.is_tracking = True
            self.take_snapshot()  # Initial snapshot

    def stop_tracking(self):
        """Stop memory tracking"""
        if self.is_tracking:
            tracemalloc.stop()
            self.is_tracking = False

    def take_snapshot(self):
        """Take a memory snapshot"""
        if self.is_tracking:
            snapshot = tracemalloc.take_snapshot()
            self.snapshots.append(
                {
                    "snapshot": snapshot,
                    "timestamp": datetime.now(),
                    "description": f"Snapshot {len(self.snapshots) + 1}",
                }
            )
            self.current_snapshot = snapshot
            self._update_displays()

    def _update_displays(self):
        """Update all memory displays"""
        if not self.current_snapshot:
            return

        # Update overview
        self._update_overview()

        # Update object tracking
        self._update_object_tracking()

    def _update_overview(self):
        """Update memory overview display"""
        if not self.current_snapshot:
            return

        # Get top statistics
        top_stats = self.current_snapshot.statistics("lineno")

        overview = "Memory Usage Overview\n"
        overview += "=" * 50 + "\n\n"
        overview += f"Snapshot taken: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        overview += f"Total snapshots: {len(self.snapshots)}\n\n"

        # Total memory usage
        total_size = sum(stat.size for stat in top_stats)
        total_count = sum(stat.count for stat in top_stats)

        overview += f"Total allocated memory: {total_size / 1024 / 1024:.2f} MB\n"
        overview += f"Total allocations: {total_count:,}\n\n"

        overview += "Top Memory Consumers (by file):\n"
        overview += "-" * 30 + "\n"

        for index, stat in enumerate(top_stats[:20]):
            overview += f"{index+1:2}. {stat.traceback.format()[-1]}\n"
            overview += f"    Size: {stat.size / 1024:.1f} KB, Count: {stat.count}\n\n"

        # Update text widget
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(1.0, overview)

    def _update_object_tracking(self):
        """Update object tracking display"""
        # Clear existing items
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)

        if not self.current_snapshot:
            return

        # Get statistics by object type
        stats = self.current_snapshot.statistics("traceback")
        type_stats = defaultdict(lambda: {"count": 0, "size": 0})

        for stat in stats:
            # Try to determine object type from traceback
            obj_type = "Unknown"
            for frame in stat.traceback:
                if "object" in frame.filename or "class" in frame.filename:
                    obj_type = frame.filename.split("/")[-1]
                    break

            type_stats[obj_type]["count"] += stat.count
            type_stats[obj_type]["size"] += stat.size

        # Add to tree
        for obj_type, data in sorted(
            type_stats.items(), key=lambda x: x[1]["size"], reverse=True
        )[:50]:
            avg_size = data["size"] / data["count"] if data["count"] > 0 else 0
            self.objects_tree.insert(
                "",
                "end",
                text=obj_type,
                values=(
                    data["count"],
                    f"{data['size'] / 1024:.1f} KB",
                    f"{avg_size:.1f} B",
                ),
            )

    def analyze_leaks(self):
        """Analyze potential memory leaks"""
        if len(self.snapshots) < 2:
            self.leaks_text.delete(1.0, tk.END)
            self.leaks_text.insert(1.0, "Need at least 2 snapshots to analyze leaks.")
            return

        # Compare last two snapshots
        current = self.snapshots[-1]["snapshot"]
        previous = self.snapshots[-2]["snapshot"]

        top_stats = current.compare_to(previous, "lineno")

        analysis = "Memory Leak Analysis\n"
        analysis += "=" * 50 + "\n\n"
        analysis += f"Comparing snapshots:\n"
        analysis += (
            f"  Previous: {self.snapshots[-2]['timestamp'].strftime('%H:%M:%S')}\n"
        )
        analysis += (
            f"  Current:  {self.snapshots[-1]['timestamp'].strftime('%H:%M:%S')}\n\n"
        )

        if top_stats:
            analysis += "Top Memory Growth (potential leaks):\n"
            analysis += "-" * 40 + "\n"

            for index, stat in enumerate(top_stats[:15]):
                if stat.size_diff > 0:  # Only show increases
                    analysis += f"{index+1:2}. {stat.traceback.format()[-1]}\n"
                    analysis += f"    Size increase: +{stat.size_diff / 1024:.1f} KB "
                    analysis += f"(+{stat.count_diff} allocations)\n\n"
        else:
            analysis += "No significant memory growth detected.\n"

        # Update text widget
        self.leaks_text.delete(1.0, tk.END)
        self.leaks_text.insert(1.0, analysis)

    def clear_snapshots(self):
        """Clear all snapshots"""
        self.snapshots.clear()
        self.current_snapshot = None

        # Clear displays
        self.overview_text.delete(1.0, tk.END)
        self.leaks_text.delete(1.0, tk.END)

        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)


class ProfilerInterface:
    """Interface for various Python profilers"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.profilers = {
            "cProfile": cProfile.Profile(),
            "line_profiler": None,  # Would need line_profiler package
            "memory_profiler": None,  # Would need memory_profiler package
        }

    def setup_ui(self):
        """Create profiler interface"""
        self.frame = ttk.LabelFrame(self.parent, text="Profiler Interface")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Profiler selection
        selection_frame = ttk.Frame(self.frame)
        selection_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(selection_frame, text="Profiler:").pack(side=tk.LEFT)

        self.profiler_var = tk.StringVar(value="cProfile")
        profiler_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.profiler_var,
            values=["cProfile", "line_profiler", "memory_profiler"],
            state="readonly",
        )
        profiler_combo.pack(side=tk.LEFT, padx=5)

        # Control buttons
        ttk.Button(selection_frame, text="Start", command=self.start_profiler).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(selection_frame, text="Stop", command=self.stop_profiler).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(selection_frame, text="Save Report", command=self.save_report).pack(
            side=tk.LEFT, padx=2
        )

        # Results display
        self.results_text = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, width=100, height=25
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def start_profiler(self):
        """Start selected profiler"""
        profiler_name = self.profiler_var.get()

        if profiler_name == "cProfile":
            self.profilers["cProfile"] = cProfile.Profile()
            self.profilers["cProfile"].enable()
            self._log("cProfile started")
        else:
            self._log(f"{profiler_name} not implemented yet")

    def stop_profiler(self):
        """Stop selected profiler and show results"""
        profiler_name = self.profiler_var.get()

        if profiler_name == "cProfile" and self.profilers["cProfile"]:
            self.profilers["cProfile"].disable()
            self._show_cprofile_results()
            self._log("cProfile stopped")
        else:
            self._log(f"{profiler_name} not active")

    def _show_cprofile_results(self):
        """Show cProfile results"""
        if not self.profilers["cProfile"]:
            return

        # Capture profile output
        s = io.StringIO()
        ps = pstats.Stats(self.profilers["cProfile"], stream=s)
        ps.sort_stats("cumulative")
        ps.print_stats(50)  # Top 50 functions

        results = s.getvalue()
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results)

    def save_report(self):
        """Save profiling report to file"""
        content = self.results_text.get(1.0, tk.END)
        if content.strip():
            filename = f"profile_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(filename, "w") as f:
                    f.write(content)
                self._log(f"Report saved to {filename}")
            except Exception as e:
                self._log(f"Error saving report: {e}")
        else:
            self._log("No results to save")

    def _log(self, message: str):
        """Log message to results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        self.results_text.insert(tk.END, log_line)
        self.results_text.see(tk.END)
