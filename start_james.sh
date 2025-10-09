#!/bin/bash
# JAMES IDE Startup Script
# This script ensures the virtual environment is activated before running JAMES

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "james_venv" ]; then
    echo "🐍 Virtual environment not found. Please run JAMES once to create it."
    echo "Or manually create it with: python3 -m venv james_venv"
    exit 1
fi

# Activate virtual environment and run JAMES
echo "🐍 Activating JAMES virtual environment..."
source james_venv/bin/activate

echo "🚀 Starting JAMES IDE..."
python JAMES.py