#!/bin/bash
# Build Script for Time_Warp IDE v1.2.0 Binaries
# Creates standalone executables for distribution

set -e

echo "🔨 Building Time_Warp IDE v1.2.0 Binaries"
echo "=========================================="

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.spec

# Ensure we have the build environment
if [ ! -d "build_env" ]; then
    echo "📦 Creating build environment..."
    python3 -m venv build_env
    source build_env/bin/activate
    pip install pyinstaller
else
    echo "📦 Using existing build environment..."
    source build_env/bin/activate
fi

# Create the main binary
echo "🔨 Building standalone binary..."
pyinstaller --onefile \
    --windowed \
    --name="Time_Warp_IDE_v1.2.0" \
    --add-data "src:src" \
    --hidden-import="tkinter" \
    --hidden-import="tkinter.ttk" \
    --hidden-import="tkinter.filedialog" \
    --hidden-import="tkinter.messagebox" \
    timewarp.py

# Create console version (for debugging)
echo "🔨 Building console version..."
pyinstaller --onefile \
    --console \
    --name="Time_Warp_IDE_v1.2.0_console" \
    --add-data "src:src" \
    --hidden-import="tkinter" \
    --hidden-import="tkinter.ttk" \
    --hidden-import="tkinter.filedialog" \
    --hidden-import="tkinter.messagebox" \
    timewarp.py

# Create release directory structure
echo "📁 Creating release structure..."
mkdir -p releases/v1.2.0/binaries/linux-arm64
mkdir -p releases/v1.2.0/source
mkdir -p releases/v1.2.0/demos

# Copy binaries
echo "📦 Organizing release files..."
cp dist/Time_Warp_IDE_v1.2.0 releases/v1.2.0/binaries/linux-arm64/
cp dist/Time_Warp_IDE_v1.2.0_console releases/v1.2.0/binaries/linux-arm64/

# Copy source files
cp timewarp.py releases/v1.2.0/source/
cp README.md releases/v1.2.0/
cp CHANGELOG.md releases/v1.2.0/
cp RELEASE_NOTES_v1.2.0.md releases/v1.2.0/
cp requirements.txt releases/v1.2.0/source/

# Copy demo files
cp demo_*.* releases/v1.2.0/demos/ 2>/dev/null || echo "No demo files found"

# Create checksums
echo "🔐 Creating checksums..."
cd releases/v1.2.0/binaries/linux-arm64/
sha256sum * > SHA256SUMS
cd ../../../../

# Show results
echo ""
echo "✅ Build Complete!"
echo ""
echo "📦 Release files created in releases/v1.2.0/:"
ls -lah releases/v1.2.0/
echo ""
echo "🔨 Binaries (linux-arm64):"
ls -lah releases/v1.2.0/binaries/linux-arm64/
echo ""
echo "🎯 Ready for GitHub release upload!"
echo ""
echo "Binary sizes:"
echo "- GUI Version: $(du -h releases/v1.2.0/binaries/linux-arm64/Time_Warp_IDE_v1.2.0 | cut -f1)"
echo "- Console Version: $(du -h releases/v1.2.0/binaries/linux-arm64/Time_Warp_IDE_v1.2.0_console | cut -f1)"
echo ""
echo "Upload these files to GitHub release:"
echo "1. releases/v1.2.0/binaries/linux-arm64/Time_Warp_IDE_v1.2.0 (Linux ARM64 GUI)"
echo "2. releases/v1.2.0/binaries/linux-arm64/Time_Warp_IDE_v1.2.0_console (Linux ARM64 Console)"
echo "3. releases/v1.2.0/binaries/linux-arm64/SHA256SUMS (Checksums)"
echo "4. Plus all the source files in releases/v1.2.0/"