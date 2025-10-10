#!/bin/bash

# Time_Warp IDE v1.1 Release Preparation Script
# This script prepares the project for GitHub release

echo "🚀 Preparing Time_Warp IDE v1.1 Release..."

# Set version info
VERSION="1.1"
RELEASE_DATE=$(date "+%B %Y")

echo "📋 Version: $VERSION"
echo "📅 Release Date: $RELEASE_DATE"

# Create release directory
echo "📁 Creating release directory..."
mkdir -p release/v$VERSION

# Run comprehensive tests
echo "🧪 Running comprehensive test suite..."
cd /home/james/Time_Warp
python3 scripts/run_all_tests.py

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed! Please fix issues before release."
    exit 1
fi

# Check file organization
echo "🗂️ Verifying project structure..."
if [ ! -d "tests" ]; then
    echo "❌ Missing tests directory"
    exit 1
fi

if [ ! -d "scripts" ]; then
    echo "❌ Missing scripts directory" 
    exit 1
fi

if [ ! -d "docs" ]; then
    echo "❌ Missing docs directory"
    exit 1
fi

echo "✅ Project structure verified!"

# Verify core files exist
echo "📝 Checking core files..."
REQUIRED_FILES=(
    "Time_Warp.py"
    "README.md"
    "CHANGELOG.md"
    "requirements.txt"
    "core/interpreter.py"
    "tools/theme.py"
    "tests/test_comprehensive.py"
    "docs/PROJECT_STRUCTURE.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required files present!"

# Create release archive
echo "📦 Creating release archive..."
tar -czf "release/v$VERSION/Time_Warp-IDE-v$VERSION.tar.gz" \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.vscode' \
    --exclude='release' \
    --exclude='archive' \
    --exclude='*.log' \
    .

# Create distribution files
echo "📋 Creating distribution files..."

# Create install script
cat > "release/v$VERSION/install.sh" << 'EOF'
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
EOF

chmod +x "release/v$VERSION/install.sh"

# Create version info file
cat > "release/v$VERSION/VERSION_INFO.txt" << EOF
Time_Warp IDE Version $VERSION
Release Date: $RELEASE_DATE

🎉 Major Features:
- Multi-Tab Editor System with syntax highlighting
- 8 Professional Themes (4 dark, 4 light)
- Comprehensive Features Menu with AI Assistant
- VS Code Integration with F5/Ctrl+F5 support
- Enhanced Testing Suite (23 unit tests)

🔧 Technical Improvements:
- Clean project structure with organized directories
- Professional APIs with proper error handling
- Optimized performance and memory management
- Comprehensive documentation updates

📚 Educational Enhancements:
- Multi-language learning environment
- Interactive tutorials and progress tracking
- Visual programming with turtle graphics
- Achievement system for motivation

For full changelog, see CHANGELOG.md
EOF

# Generate checksums
echo "🔐 Generating checksums..."
cd "release/v$VERSION"
sha256sum * > SHA256SUMS.txt
cd ../..

echo "✅ Release preparation complete!"
echo ""
echo "📋 Release Summary:"
echo "   Version: $VERSION"
echo "   Date: $RELEASE_DATE"
echo "   Archive: release/v$VERSION/Time_Warp-IDE-v$VERSION.tar.gz"
echo "   Install Script: release/v$VERSION/install.sh"
echo "   Checksums: release/v$VERSION/SHA256SUMS.txt"
echo ""
echo "🚀 Ready for GitHub release!"
echo "   1. Create release branch: git checkout -b release/v$VERSION"
echo "   2. Commit changes: git add . && git commit -m 'Release v$VERSION'"
echo "   3. Create tag: git tag -a v$VERSION -m 'Time_Warp IDE v$VERSION'"
echo "   4. Push to GitHub: git push origin release/v$VERSION --tags"
echo "   5. Create GitHub release with archive and install script"