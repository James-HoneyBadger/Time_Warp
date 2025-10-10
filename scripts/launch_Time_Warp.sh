#!/bin/bash
# Time_Warp IDE Launch Script
# This script launches the Time_Warp IDE with proper Python environment

echo "🚀 Launching Time_Warp IDE 1.1..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the Time_Warp directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Found Python 3"
    python3 Time_Warp.py
elif command -v python >/dev/null 2>&1; then
    echo "✅ Found Python"
    python Time_Warp.py
else
    echo "❌ Python not found!"
    echo "Please install Python 3 to run Time_Warp IDE"
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "👋 Time_Warp IDE session ended."