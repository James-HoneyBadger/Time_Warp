#!/bin/bash
echo "🚀 Installing Time_Warp IDE v1.1..."

# Check Python version
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo "✅ Time_Warp IDE v1.1 installed successfully!"
echo "🎯 Run with: python3 Time_Warp.py"
