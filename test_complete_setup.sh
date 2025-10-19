#!/bin/bash
# Complete Time_Warp IDE Setup and Test Script
# This script demonstrates the full setup workflow

set -e

echo "🚀 Time_Warp IDE Complete Setup Test"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "Time_Warp.py" ] || [ ! -f "requirements.py" ]; then
    echo "❌ Error: Please run this script from the Time_Warp IDE root directory"
    exit 1
fi

echo "📍 Running from: $(pwd)"

# Step 1: Clean up any existing venv for testing
echo "🧹 Cleaning up existing virtual environment..."
if [ -d ".venv" ]; then
    rm -rf .venv
    echo "✅ Removed existing .venv"
fi

# Step 2: Run requirements.py to set up everything
echo "🔧 Running requirements.py setup..."
python requirements.py

# Step 3: Verify the setup worked
echo "🔍 Verifying setup..."
python requirements.py --check

# Step 4: Test that Time_Warp can import properly
echo "🧪 Testing Time_Warp imports..."
# Activate the virtual environment for testing
source .venv/bin/activate
python -c "
try:
    from core.interpreter import Time_WarpInterpreter
    print('✅ Time_WarpInterpreter imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)

try:
    from unified_canvas import UnifiedCanvas
    print('✅ UnifiedCanvas imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)

try:
    import pyutil
    print('✅ pyutil imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

# Step 5: Test basic functionality
echo "🎯 Testing basic functionality..."
python -c "
from requirements import RequirementsManager
manager = RequirementsManager()
if manager.is_setup_complete():
    print('✅ Environment is fully configured and ready!')
    print(f'📦 Virtual environment: {manager.venv_path}')
    print(f'🐍 Python executable: {manager.get_venv_python()}')
else:
    print('❌ Environment setup verification failed')
    exit(1)
"

echo ""
echo "🎉 Complete setup test successful!"
echo ""
echo "Time_Warp IDE is now ready to use. You can:"
echo "  • Run: python Time_Warp.py"
echo "  • Activate venv later: source .venv/bin/activate"
echo "  • Check status: python requirements.py --check"
echo "  • Force re-setup: python requirements.py --force"