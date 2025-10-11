#!/usr/bin/env python3
"""
Performance Optimizer Module for Time_Warp IDE
Provides optimizations for memory usage, output handling, and system performance.
"""

import sys
import gc
import re
import time
import threading
from collections import deque
from typing import Dict, List, Any
import weakref


class OutputBuffer:
    """Optimized output buffer with size limits and efficient handling."""

    def __init__(self, max_lines: int = 1000, max_chars_per_line: int = 200):
        self.max_lines = max_lines
        self.max_chars_per_line = max_chars_per_line
        self._buffer = deque(maxlen=max_lines)
        self._total_chars = 0
        self._lock = threading.Lock()

    def add_line(self, line: str) -> str:
        """Add a line to buffer with optimization for repeated content."""
        with self._lock:
            # Truncate overly long lines
            if len(line) > self.max_chars_per_line:
                line = line[: self.max_chars_per_line - 3] + "..."

            # Detect and summarize repetitive content
            if len(self._buffer) > 0:
                last_line = self._buffer[-1]
                if self._is_repetitive(line, last_line):
                    return self._handle_repetitive_content(line)

            self._buffer.append(line)
            self._total_chars += len(line)
            return line

    def _is_repetitive(self, new_line: str, last_line: str) -> bool:
        """Check if content is repetitive (pattern detection)."""
        # Check for simple repetition patterns
        if new_line == last_line:
            return True

        # Check for PILOT comment lines: "R: This is comment line N"
        pilot_pattern = r"^R:\s*This is comment line \d+$"
        if re.match(pilot_pattern, new_line.strip()) and re.match(
            pilot_pattern, last_line.strip()
        ):
            return True

        # Check for numbered sequences (like "line N")
        if len(new_line) == len(last_line):
            diff_count = sum(c1 != c2 for c1, c2 in zip(new_line, last_line))
            if diff_count <= 3:  # Allow small differences (numbers)
                return True

        return False

    def _handle_repetitive_content(self, line: str) -> str:
        """Handle repetitive content by summarizing."""
        # Count how many similar lines we have
        similar_count = 1
        for idx in range(len(self._buffer) - 1, -1, -1):
            if self._is_repetitive(line, self._buffer[idx]):
                similar_count += 1
            else:
                break

        if similar_count > 3:
            # Replace with summary
            summary = f"... ({similar_count} similar lines omitted for performance) ..."
            # Remove the repetitive lines and add summary
            for _ in range(min(similar_count - 1, len(self._buffer))):
                if self._buffer:
                    removed = self._buffer.pop()
                    self._total_chars -= len(removed)

            self._buffer.append(summary)
            self._total_chars += len(summary)
            return f"📊 Performance: Summarized {similar_count} repetitive lines"

        return line

    def get_content(self) -> List[str]:
        """Get buffer content efficiently."""
        with self._lock:
            return list(self._buffer)

    def clear(self):
        """Clear buffer and free memory."""
        with self._lock:
            self._buffer.clear()
            self._total_chars = 0
            gc.collect()  # Force garbage collection


class MemoryManager:
    """Memory management utilities for Time_Warp IDE."""

    def __init__(self):
        self._weak_refs = weakref.WeakSet()
        self._memory_threshold = 100 * 1024 * 1024  # 100MB

    def register_object(self, obj):
        """Register object for memory monitoring."""
        self._weak_refs.add(obj)

    def cleanup_memory(self):
        """Perform memory cleanup."""
        # Clear weak references
        self._weak_refs.clear()

        # Force garbage collection
        collected = gc.collect()

        return {"objects_collected": collected, "memory_freed": True}

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available / 1024 / 1024,  # MB
            }
        except (ImportError, Exception):
            # Fallback without psutil or on error
            return {
                "rss": 0,
                "vms": 0,
                "percent": 0,
                "available": 1000,
            }  # Assume 1GB available


class PerformanceProfiler:
    """Performance profiling and optimization suggestions."""

    def __init__(self):
        self._timings = {}
        self._counters = {}
        self._start_times = {}

    def start_timing(self, operation: str):
        """Start timing an operation."""
        self._start_times[operation] = time.perf_counter()

    def end_timing(self, operation: str):
        """End timing an operation and record results."""
        if operation in self._start_times:
            duration = time.perf_counter() - self._start_times[operation]
            if operation not in self._timings:
                self._timings[operation] = []
            self._timings[operation].append(duration)
            del self._start_times[operation]
            return duration
        return 0

    def increment_counter(self, counter: str, value: int = 1):
        """Increment a performance counter."""
        self._counters[counter] = self._counters.get(counter, 0) + value

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report with optimization suggestions."""
        report = {"timings": {}, "counters": self._counters.copy(), "suggestions": []}

        # Process timing data
        for operation, times in self._timings.items():
            if times:
                report["timings"][operation] = {
                    "count": len(times),
                    "total": sum(times),
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                }

                # Generate suggestions based on performance
                avg_time = report["timings"][operation]["average"]
                if avg_time > 0.1:  # 100ms
                    report["suggestions"].append(
                        f"⚠️ {operation} averaging {avg_time:.3f}s - consider optimization"
                    )

        # Analyze counters for suggestions
        if self._counters.get("output_lines", 0) > 1000:
            report["suggestions"].append(
                "📊 High output volume detected - consider using output buffering"
            )

        if self._counters.get("unicode_operations", 0) > 100:
            report["suggestions"].append(
                "🌍 Many Unicode operations - ensure proper encoding handling"
            )

        return report

    def reset(self):
        """Reset all performance data."""
        self._timings.clear()
        self._counters.clear()
        self._start_times.clear()


class OptimizedInterpreterMixin:
    """Mixin to add performance optimizations to interpreters."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._output_buffer = OutputBuffer()
        self._memory_manager = MemoryManager()
        self._profiler = PerformanceProfiler()

    def optimized_output(self, text: str):
        """Output text with performance optimizations."""
        self._profiler.start_timing("output_processing")

        lines = text.split("\n")
        processed_lines = []

        for line in lines:
            processed_line = self._output_buffer.add_line(line)
            processed_lines.append(processed_line)
            self._profiler.increment_counter("output_lines")

            # Check for Unicode characters
            if any(ord(char) > 127 for char in line):
                self._profiler.increment_counter("unicode_operations")

        self._profiler.end_timing("output_processing")
        return "\n".join(processed_lines)

    def cleanup_resources(self):
        """Cleanup resources for better performance."""
        self._output_buffer.clear()
        cleanup_result = self._memory_manager.cleanup_memory()
        return cleanup_result

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            "profiler": self._profiler.get_performance_report(),
            "memory": self._memory_manager.get_memory_usage(),
            "buffer_stats": {
                "lines": len(self._output_buffer.get_content()),
                "chars": self._output_buffer._total_chars,
            },
        }


# Global performance optimizer instance
performance_optimizer = PerformanceProfiler()
memory_manager = MemoryManager()


def optimize_for_production():
    """Apply production-level optimizations."""
    # Enable garbage collection optimizations
    gc.set_threshold(700, 10, 10)  # More aggressive collection

    # Set recursion limit for better stack management
    sys.setrecursionlimit(1500)  # Reasonable limit

    return {
        "gc_threshold_set": True,
        "recursion_limit": sys.getrecursionlimit(),
        "optimization_level": "production",
    }


def get_system_performance() -> Dict[str, Any]:
    """Get overall system performance metrics."""
    return {
        "memory": memory_manager.get_memory_usage(),
        "profiler": performance_optimizer.get_performance_report(),
        "python_version": sys.version,
        "gc_stats": gc.get_stats() if hasattr(gc, "get_stats") else {},
    }


if __name__ == "__main__":
    # Performance optimization demo
    print("🚀 Time_Warp Performance Optimizer")
    print("=" * 50)

    # Apply optimizations
    result = optimize_for_production()
    print(f"✅ Production optimizations applied: {result}")

    # Test output buffer
    buffer = OutputBuffer(max_lines=10)
    for i in range(20):
        buffer.add_line(f"Test line {i}")

    print(f"📊 Buffer test - Lines stored: {len(buffer.get_content())}")

    # Performance report
    stats = get_system_performance()
    print(f"💾 Memory usage: {stats['memory']}")
    print("🎯 Performance optimization ready!")
