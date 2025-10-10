#!/bin/bash
# Development Setup Script for Time_Warp IDE

set -e

echo "🚀 Setting up Time_Warp IDE development environment..."

# Check if we're in the right directory
if [ ! -f "Time_Warp.py" ]; then
    echo "❌ Error: Time_Warp.py not found. Are you in the right directory?"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".Time_Warp" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .Time_Warp
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .Time_Warp/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Run initial tests
echo "🧪 Running initial tests..."
python run_tests.py

# Check if Time_Warp can be imported
echo "✅ Testing Time_Warp import..."
python -c "from core.interpreter import Time_WarpInterpreter; print('Time_Warp core imported successfully!')"

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment: source .Time_Warp/bin/activate"
echo "  2. Run Time_Warp IDE: python Time_Warp.py"
echo "  3. Run tests: python run_tests.py"
echo "  4. Format code: black ."
echo "  5. Lint code: flake8 ."
echo ""
echo "Happy coding! 🐍✨"