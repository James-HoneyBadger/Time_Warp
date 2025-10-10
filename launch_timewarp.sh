#!/bin/bash
# TimeWarp IDE v1.0.1 Launch Script
# This script launches the TimeWarp IDE with proper Python environment

echo "🚀 Launching TimeWarp IDE v1.0.1..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the TimeWarp directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Found Python 3"
    python3 TimeWarp_v101.py
elif command -v python >/dev/null 2>&1; then
    echo "✅ Found Python"
    python TimeWarp_v101.py
else
    echo "❌ Python not found!"
    echo "Please install Python 3 to run TimeWarp IDE"
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "👋 TimeWarp IDE session ended."