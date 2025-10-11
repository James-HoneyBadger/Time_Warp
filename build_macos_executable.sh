#!/bin/bash
#
# Time_Warp IDE macOS Build Script
# Creates a distributable macOS .app bundle for Time_Warp IDE v1.2
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Time_Warp"
VERSION="1.2.0"
BUILD_DIR="build_macos"
DIST_DIR="dist_macos"
DMG_NAME="Time_Warp_IDE_v${VERSION}_macOS"

echo -e "${BLUE}🚀 Time_Warp IDE macOS Build Script v${VERSION}${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to print status messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script must be run on macOS"
    exit 1
fi

print_status "Checking build environment..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Using Python ${PYTHON_VERSION}"

# Check for required directories and files
if [ ! -f "Time_Warp.py" ]; then
    print_error "Time_Warp.py not found in current directory"
    exit 1
fi

if [ ! -f "Time_Warp_macOS.spec" ]; then
    print_error "Time_Warp_macOS.spec not found"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".Time_Warp" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .Time_Warp
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .Time_Warp/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install/upgrade build dependencies
print_status "Installing build dependencies..."
pip install --upgrade pyinstaller pillow pygame

# Install project dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing project dependencies..."
    pip install -r requirements.txt
fi

# Clean previous builds
if [ -d "${BUILD_DIR}" ]; then
    print_status "Cleaning previous build directory..."
    rm -rf "${BUILD_DIR}"
fi

if [ -d "${DIST_DIR}" ]; then
    print_status "Cleaning previous dist directory..."
    rm -rf "${DIST_DIR}"
fi

# Create assets directory and icon if needed
if [ ! -d "assets" ]; then
    print_status "Creating assets directory..."
    mkdir -p assets
fi

# Generate icon if it doesn't exist
if [ ! -f "assets/icon.icns" ]; then
    print_warning "No icon.icns found, creating default icon..."
    if command -v python3 &> /dev/null && python3 -c "from PIL import Image" 2>/dev/null; then
        python3 - << 'EOF'
from PIL import Image, ImageDraw
import os

# Create a simple icon
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a colorful gradient background
for i in range(size):
    color = (int(255 * i / size), int(128 + 127 * i / size), 255 - int(128 * i / size), 255)
    draw.line([(i, 0), (i, size)], fill=color)

# Draw "TW" text
from PIL import ImageFont
try:
    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 180)
except:
    font = ImageFont.load_default()

# Add text with shadow
draw.text((size//2-80, size//2-60), "TW", font=font, fill=(0, 0, 0, 180), anchor="mm")
draw.text((size//2-85, size//2-65), "TW", font=font, fill=(255, 255, 255, 255), anchor="mm")

# Save as PNG first, then convert to ICNS
if not os.path.exists('assets'):
    os.makedirs('assets')
    
img.save('assets/icon.png')
print("Generated default icon.png")

# Convert to ICNS using macOS sips command
import subprocess
try:
    subprocess.run(['sips', '-s', 'format', 'icns', 'assets/icon.png', '--out', 'assets/icon.icns'], 
                  check=True, capture_output=True)
    os.remove('assets/icon.png')
    print("Converted to icon.icns")
except subprocess.CalledProcessError:
    print("Could not convert to ICNS, keeping PNG")
EOF
    else
        print_warning "PIL not available, skipping icon generation"
    fi
fi

# Run PyInstaller
print_status "Building macOS application bundle..."
pyinstaller --distpath="${DIST_DIR}" --workpath="${BUILD_DIR}" --clean --noconfirm Time_Warp_macOS.spec

# Verify the app was created
APP_PATH="${DIST_DIR}/${APP_NAME}.app"
if [ ! -d "${APP_PATH}" ]; then
    print_error "Application bundle was not created successfully"
    exit 1
fi

print_status "Application bundle created: ${APP_PATH}"

# Test the app (basic launch test)
print_status "Testing application launch..."
timeout 10s open "${APP_PATH}" --args --test || print_warning "App launch test timed out (this may be normal)"

# Create DMG if create-dmg is available
if command -v create-dmg &> /dev/null; then
    print_status "Creating DMG installer..."
    
    # Clean old DMG
    [ -f "${DMG_NAME}.dmg" ] && rm "${DMG_NAME}.dmg"
    
    create-dmg \
        --volname "Time_Warp IDE v${VERSION}" \
        --volicon "assets/icon.icns" \
        --window-pos 200 120 \
        --window-size 800 600 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 200 190 \
        --hide-extension "${APP_NAME}.app" \
        --app-drop-link 600 185 \
        --hdiutil-quiet \
        "${DMG_NAME}.dmg" \
        "${DIST_DIR}/"
        
    if [ -f "${DMG_NAME}.dmg" ]; then
        print_status "DMG created: ${DMG_NAME}.dmg"
        
        # Get DMG size
        DMG_SIZE=$(ls -lh "${DMG_NAME}.dmg" | awk '{print $5}')
        print_status "DMG size: ${DMG_SIZE}"
    fi
else
    print_warning "create-dmg not found. Install with: brew install create-dmg"
    print_status "You can manually create a DMG or distribute the .app bundle directly"
fi

# Code signing (if developer certificate is available)
if command -v codesign &> /dev/null; then
    print_status "Checking for code signing certificate..."
    
    # Look for valid signing certificates
    CERT_NAME=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -n1 | sed 's/.*") \(.*\)/\1/' || true)
    
    if [ ! -z "$CERT_NAME" ]; then
        print_status "Found signing certificate: ${CERT_NAME}"
        print_status "Code signing application..."
        
        # Sign the app bundle
        codesign --force --deep --sign "$CERT_NAME" "${APP_PATH}"
        
        # Verify signature
        if codesign --verify --verbose "${APP_PATH}" 2>/dev/null; then
            print_status "Application successfully code signed"
        else
            print_warning "Code signing verification failed"
        fi
        
        # Sign DMG if it exists
        if [ -f "${DMG_NAME}.dmg" ]; then
            print_status "Code signing DMG..."
            codesign --force --sign "$CERT_NAME" "${DMG_NAME}.dmg"
        fi
    else
        print_warning "No Developer ID certificate found"
        print_warning "The app will show security warnings on other machines"
        print_warning "To enable code signing, install a Developer ID certificate from Apple"
    fi
fi

# Display build summary
echo -e "\n${GREEN}🎉 Build completed successfully!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Application: ${APP_PATH}"
if [ -f "${DMG_NAME}.dmg" ]; then
    echo -e "Installer:   ${DMG_NAME}.dmg"
fi
echo -e "Version:     ${VERSION}"
echo -e "Python:      ${PYTHON_VERSION}"
echo -e "Architecture: $(uname -m)"

# Get app bundle size
if [ -d "${APP_PATH}" ]; then
    APP_SIZE=$(du -sh "${APP_PATH}" | cut -f1)
    echo -e "App Size:    ${APP_SIZE}"
fi

echo -e "\n${BLUE}Distribution Notes:${NC}"
echo -e "• The .app bundle can be distributed directly"
echo -e "• Users may need to right-click → Open for first launch (Gatekeeper)"
if [ -f "${DMG_NAME}.dmg" ]; then
    echo -e "• The DMG provides a user-friendly installer experience"
fi
if [ -z "$CERT_NAME" ]; then
    echo -e "• Consider code signing for wider distribution"
fi

echo -e "\n${GREEN}Build process completed! 🚀${NC}"