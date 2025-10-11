#!/bin/bash
#
# macOS Launch Script for Time_Warp IDE
# Handles macOS-specific environment setup and launches the IDE
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up environment variables for macOS
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
export PATH="${SCRIPT_DIR}/.Time_Warp/bin:${PATH}"

# macOS-specific settings
export TKINTER_BACKEND="cocoa"  # Use Cocoa backend for better macOS integration
export PYTHON_CONFIGURE_OPTS="--enable-framework"

# Check if we're running inside an app bundle
if [[ "$0" == *".app/Contents/MacOS/"* ]]; then
    # Running from app bundle
    APP_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
    RESOURCES_DIR="${APP_DIR}/Contents/Resources"
    
    # Set up paths for app bundle
    export PYTHONPATH="${RESOURCES_DIR}:${PYTHONPATH}"
    cd "${RESOURCES_DIR}"
else
    # Running from source
    cd "${SCRIPT_DIR}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".Time_Warp" ]; then
    echo "🔧 Setting up Time_Warp environment for macOS..."
    python3 -m venv .Time_Warp
    
    # Activate and install dependencies
    source .Time_Warp/bin/activate
    pip install --upgrade pip
    
    # Install required packages
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # Install minimal requirements
        pip install pillow pygame
    fi
fi

# Activate virtual environment if not in app bundle
if [[ "$0" != *".app/Contents/MacOS/"* ]]; then
    source .Time_Warp/bin/activate
fi

# Launch Time_Warp with macOS optimizations
if [ -f "Time_Warp.py" ]; then
    # Use python3 explicitly for better compatibility
    exec python3 Time_Warp.py "$@"
else
    echo "❌ Time_Warp.py not found"
    exit 1
fi