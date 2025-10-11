#!/bin/bash
# Time_Warp IDE v1.2.0 Installation Script

echo "🚀 Installing Time_Warp IDE v1.2.0..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Make launcher executable
chmod +x timewarp.py

echo "✅ Installation complete!"
echo "🚀 Run with: python3 timewarp.py"
