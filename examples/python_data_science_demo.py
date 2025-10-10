#!/usr/bin/env python3
"""
Python Data Science Demonstration
Educational program showing data analysis and visualization concepts
Perfect for learning scientific computing with Python
"""

import random
import math
import json
from datetime import datetime, timedelta


# Simple data structures for educational purposes
class DataPoint:
    """Represents a single data point with timestamp and value"""

    def __init__(self, timestamp, value, category="default"):
        self.timestamp = timestamp
        self.value = value
        self.category = category

    def __str__(self):
        return f"{self.timestamp}: {self.value} ({self.category})"


class SimpleDataAnalyzer:
    """Educational data analysis class demonstrating key concepts"""

    def __init__(self):
        self.data = []
        self.results = {}

    def add_data_point(self, value, category="default"):
        """Add a data point with current timestamp"""
        timestamp = datetime.now()
        point = DataPoint(timestamp, value, category)
        self.data.append(point)

    def load_sample_data(self):
        """Generate sample data for demonstration"""
        print("📊 Generating sample data...")

        # Generate temperature data for a week
        base_temp = 20  # Base temperature in Celsius
        for day in range(7):
            for hour in range(24):
                # Simulate daily temperature variation
                time_factor = math.sin(2 * math.pi * hour / 24)
                daily_variation = 10 * time_factor
                random_noise = random.uniform(-2, 2)

                temperature = base_temp + daily_variation + random_noise
                timestamp = datetime.now() - timedelta(days=6 - day, hours=23 - hour)

                point = DataPoint(timestamp, temperature, "temperature")
                self.data.append(point)

        # Generate some sales data
        for day in range(30):
            base_sales = 100
            trend = day * 2  # Upward trend
            seasonal = 20 * math.sin(2 * math.pi * day / 7)  # Weekly pattern
            noise = random.uniform(-15, 15)

            sales = max(0, base_sales + trend + seasonal + noise)
            timestamp = datetime.now() - timedelta(days=29 - day)

            point = DataPoint(timestamp, sales, "sales")
            self.data.append(point)

        print(f"✅ Generated {len(self.data)} data points")

    def calculate_statistics(self, category=None):
        """Calculate basic statistics for the data"""
        print(f"📈 Calculating statistics for {category or 'all'} data...")

        # Filter data by category if specified
        if category:
            filtered_data = [p.value for p in self.data if p.category == category]
        else:
            filtered_data = [p.value for p in self.data]

        if not filtered_data:
            print("❌ No data found for analysis")
            return None

        # Calculate statistics
        stats = {
            "count": len(filtered_data),
            "mean": sum(filtered_data) / len(filtered_data),
            "min": min(filtered_data),
            "max": max(filtered_data),
            "range": max(filtered_data) - min(filtered_data),
        }

        # Calculate median
        sorted_data = sorted(filtered_data)
        n = len(sorted_data)
        if n % 2 == 0:
            stats["median"] = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
        else:
            stats["median"] = sorted_data[n // 2]

        # Calculate standard deviation
        mean = stats["mean"]
        variance = sum((x - mean) ** 2 for x in filtered_data) / len(filtered_data)
        stats["std_dev"] = math.sqrt(variance)

        # Store results
        key = category or "all"
        self.results[key] = stats

        return stats

    def print_statistics(self, stats, category=None):
        """Print statistics in a formatted way"""
        category_name = category or "All Data"
        print(f"\n📊 Statistics for {category_name}")
        print("=" * 40)
        print(f"Count:               {stats['count']:>10}")
        print(f"Mean:                {stats['mean']:>10.2f}")
        print(f"Median:              {stats['median']:>10.2f}")
        print(f"Minimum:             {stats['min']:>10.2f}")
        print(f"Maximum:             {stats['max']:>10.2f}")
        print(f"Range:               {stats['range']:>10.2f}")
        print(f"Standard Deviation:  {stats['std_dev']:>10.2f}")

    def find_patterns(self, category):
        """Demonstrate pattern finding in time series data"""
        print(f"\n🔍 Analyzing patterns in {category} data...")

        # Filter data by category
        category_data = [p for p in self.data if p.category == category]
        if len(category_data) < 10:
            print("❌ Insufficient data for pattern analysis")
            return

        # Sort by timestamp
        category_data.sort(key=lambda x: x.timestamp)

        # Calculate trends
        values = [p.value for p in category_data]
        n = len(values)

        # Simple trend calculation (slope of best fit line)
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator != 0:
            slope = numerator / denominator
            if slope > 0.1:
                trend = "📈 Increasing"
            elif slope < -0.1:
                trend = "📉 Decreasing"
            else:
                trend = "➡️ Stable"
        else:
            trend = "➡️ Stable"

        print(f"Trend: {trend} (slope: {slope:.4f})")

        # Find peaks and valleys
        peaks = []
        valleys = []

        for i in range(1, len(values) - 1):
            if values[i] > values[i - 1] and values[i] > values[i + 1]:
                peaks.append((i, values[i]))
            elif values[i] < values[i - 1] and values[i] < values[i + 1]:
                valleys.append((i, values[i]))

        print(f"Peaks found: {len(peaks)}")
        print(f"Valleys found: {len(valleys)}")

        if peaks:
            avg_peak = sum(p[1] for p in peaks) / len(peaks)
            print(f"Average peak value: {avg_peak:.2f}")

        if valleys:
            avg_valley = sum(v[1] for v in valleys) / len(valleys)
            print(f"Average valley value: {avg_valley:.2f}")

    def create_simple_histogram(self, category, bins=10):
        """Create a simple text-based histogram"""
        print(f"\n📊 Histogram for {category} data:")

        # Filter data
        values = [p.value for p in self.data if p.category == category]
        if not values:
            print("❌ No data found")
            return

        # Calculate bin ranges
        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins

        # Count values in each bin
        bin_counts = [0] * bins
        for value in values:
            bin_index = min(int((value - min_val) / bin_width), bins - 1)
            bin_counts[bin_index] += 1

        # Find maximum count for scaling
        max_count = max(bin_counts)
        scale = 50 / max_count if max_count > 0 else 1

        # Print histogram
        print(f"Range: {min_val:.1f} to {max_val:.1f}")
        print("-" * 60)

        for i in range(bins):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            count = bin_counts[i]
            bar_length = int(count * scale)
            bar = "█" * bar_length

            print(f"{bin_start:6.1f}-{bin_end:6.1f}: {count:3d} {bar}")

    def correlation_analysis(self):
        """Demonstrate correlation between different data categories"""
        print("\n🔗 Correlation Analysis")
        print("=" * 40)

        # Get all categories
        categories = list(set(p.category for p in self.data))

        if len(categories) < 2:
            print("❌ Need at least 2 categories for correlation analysis")
            return

        # Simple correlation between first two categories
        cat1, cat2 = categories[0], categories[1]

        # Get data points for both categories (assuming same timestamps)
        cat1_data = {}
        cat2_data = {}

        for point in self.data:
            timestamp_key = point.timestamp.strftime("%Y-%m-%d %H")
            if point.category == cat1:
                cat1_data[timestamp_key] = point.value
            elif point.category == cat2:
                cat2_data[timestamp_key] = point.value

        # Find common timestamps
        common_times = set(cat1_data.keys()) & set(cat2_data.keys())

        if len(common_times) < 5:
            print(f"❌ Insufficient overlapping data between {cat1} and {cat2}")
            return

        # Calculate correlation coefficient
        pairs = [(cat1_data[t], cat2_data[t]) for t in common_times]
        n = len(pairs)

        sum_x = sum(p[0] for p in pairs)
        sum_y = sum(p[1] for p in pairs)
        sum_xy = sum(p[0] * p[1] for p in pairs)
        sum_x2 = sum(p[0] ** 2 for p in pairs)
        sum_y2 = sum(p[1] ** 2 for p in pairs)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))

        if denominator != 0:
            correlation = numerator / denominator
            print(f"Correlation between {cat1} and {cat2}: {correlation:.4f}")

            if abs(correlation) > 0.7:
                strength = "Strong"
            elif abs(correlation) > 0.3:
                strength = "Moderate"
            else:
                strength = "Weak"

            direction = "positive" if correlation > 0 else "negative"
            print(f"Interpretation: {strength} {direction} correlation")
        else:
            print("❌ Cannot calculate correlation (zero variance)")

    def export_results(self, filename="analysis_results.json"):
        """Export analysis results to JSON file"""
        print(f"\n💾 Exporting results to {filename}...")

        export_data = {
            "analysis_date": datetime.now().isoformat(),
            "total_data_points": len(self.data),
            "categories": list(set(p.category for p in self.data)),
            "statistics": self.results,
            "summary": {
                "data_range": {
                    "start": min(p.timestamp for p in self.data).isoformat(),
                    "end": max(p.timestamp for p in self.data).isoformat(),
                }
            },
        }

        try:
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
            print(f"✅ Results exported successfully")
        except Exception as e:
            print(f"❌ Export failed: {e}")


def main():
    """Main demonstration function"""
    print("🐍 Python Data Science Educational Demo")
    print("=" * 50)
    print("This program demonstrates key data science concepts:")
    print("- Data collection and organization")
    print("- Statistical analysis")
    print("- Pattern recognition")
    print("- Data visualization (text-based)")
    print("- Correlation analysis")
    print("- Data export")
    print()

    # Create analyzer and load data
    analyzer = SimpleDataAnalyzer()
    analyzer.load_sample_data()

    print("\n" + "=" * 50)
    print("📈 STATISTICAL ANALYSIS")
    print("=" * 50)

    # Analyze each category
    categories = list(set(p.category for p in analyzer.data))

    for category in categories:
        stats = analyzer.calculate_statistics(category)
        if stats:
            analyzer.print_statistics(stats, category)

    # Overall statistics
    overall_stats = analyzer.calculate_statistics()
    analyzer.print_statistics(overall_stats, "Overall")

    print("\n" + "=" * 50)
    print("🔍 PATTERN ANALYSIS")
    print("=" * 50)

    # Pattern analysis for each category
    for category in categories:
        analyzer.find_patterns(category)

    print("\n" + "=" * 50)
    print("📊 DATA VISUALIZATION")
    print("=" * 50)

    # Create histograms
    for category in categories:
        analyzer.create_simple_histogram(category)

    # Correlation analysis
    analyzer.correlation_analysis()

    print("\n" + "=" * 50)
    print("💾 DATA EXPORT")
    print("=" * 50)

    # Export results
    analyzer.export_results()

    print("\n" + "=" * 50)
    print("🎓 EDUCATIONAL SUMMARY")
    print("=" * 50)
    print("This demonstration covered:")
    print("✅ Object-oriented programming with classes")
    print("✅ Data structures (lists, dictionaries)")
    print("✅ Statistical calculations (mean, median, std dev)")
    print("✅ Time series data handling")
    print("✅ Pattern recognition algorithms")
    print("✅ Simple data visualization")
    print("✅ File I/O operations")
    print("✅ Error handling")
    print("✅ Mathematical operations")
    print("✅ Date/time manipulation")
    print()
    print("🎯 Key Learning Outcomes:")
    print("- Understanding of basic statistics")
    print("- Data analysis workflow")
    print("- Python programming concepts")
    print("- Scientific computing principles")
    print()
    print("🚀 Next Steps:")
    print("- Try modifying the sample data generation")
    print("- Add new statistical measures")
    print("- Implement more visualization types")
    print("- Explore machine learning concepts")
    print()
    print("Happy learning! 📚")


if __name__ == "__main__":
    main()
