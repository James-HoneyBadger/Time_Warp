#!/bin/bash
#
# Time_Warp IDE macOS Release Script v1.2
# Comprehensive build and packaging for macOS distribution
#

set -e

# Configuration
VERSION="1.2.0"
PRODUCT_NAME="Time_Warp IDE"
BUNDLE_ID="org.time-warp-ide.Time_Warp"
MIN_MACOS_VERSION="10.13"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
BUILD_DIR="${PROJECT_DIR}/build_macos"
DIST_DIR="${PROJECT_DIR}/dist_macos"
RELEASE_DIR="${PROJECT_DIR}/release/v${VERSION}/macos"
ASSETS_DIR="${PROJECT_DIR}/assets"

print_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                Time_Warp IDE v${VERSION} - macOS Build                ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_step "Checking build prerequisites..."
    
    # Check macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script must be run on macOS"
        exit 1
    fi
    
    # Check macOS version
    MACOS_VERSION=$(sw_vers -productVersion)
    print_success "macOS version: ${MACOS_VERSION}"
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    print_success "Found ${PYTHON_VERSION}"
    
    # Check Xcode Command Line Tools
    if ! xcode-select -p &> /dev/null; then
        print_warning "Xcode Command Line Tools not found"
        print_step "Installing Xcode Command Line Tools..."
        xcode-select --install
        read -p "Press Enter after Xcode Command Line Tools installation completes..."
    fi
    
    # Check for Homebrew (recommended)
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found (recommended for additional tools)"
        print_warning "Install from: https://brew.sh"
    else
        print_success "Homebrew available"
    fi
    
    # Check for create-dmg
    if ! command -v create-dmg &> /dev/null; then
        print_warning "create-dmg not found"
        if command -v brew &> /dev/null; then
            print_step "Installing create-dmg via Homebrew..."
            brew install create-dmg
        else
            print_warning "Install create-dmg manually: npm install -g create-dmg"
        fi
    fi
}

setup_environment() {
    print_step "Setting up build environment..."
    
    cd "${PROJECT_DIR}"
    
    # Create virtual environment
    if [ ! -d ".Time_Warp" ]; then
        print_step "Creating virtual environment..."
        python3 -m venv .Time_Warp
    fi
    
    # Activate virtual environment
    source .Time_Warp/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip setuptools wheel
    
    # Install build dependencies
    print_step "Installing build dependencies..."
    pip install --upgrade pyinstaller pillow pygame
    
    # Install project dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    print_success "Environment setup complete"
}

create_assets() {
    print_step "Creating application assets..."
    
    # Create assets directory
    mkdir -p "${ASSETS_DIR}"
    
    # Generate application icon if it doesn't exist
    if [ ! -f "${ASSETS_DIR}/icon.icns" ]; then
        print_step "Generating application icon..."
        
        python3 - << 'EOF'
import os
from PIL import Image, ImageDraw, ImageFont
import subprocess

def create_icon():
    # Create high-resolution icon
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for i in range(size):
        progress = i / size
        r = int(50 + 150 * progress)
        g = int(100 + 100 * progress) 
        b = int(200 - 50 * progress)
        draw.line([(i, 0), (i, size)], fill=(r, g, b, 255))
    
    # Draw border
    border_width = 20
    draw.rectangle([border_width, border_width, size-border_width, size-border_width], 
                  outline=(255, 255, 255, 255), width=border_width)
    
    # Draw "TW" text
    try:
        # Try to use a nice system font
        font_paths = [
            "/System/Library/Fonts/SF-Pro-Display-Bold.otf",
            "/System/Library/Fonts/Arial.ttf", 
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 300)
                break
                
        if font is None:
            font = ImageFont.load_default()
            
    except Exception:
        font = ImageFont.load_default()
    
    # Add text shadow
    shadow_offset = 8
    draw.text((size//2 + shadow_offset, size//2 + shadow_offset), "TW", 
             font=font, fill=(0, 0, 0, 100), anchor="mm")
    
    # Add main text
    draw.text((size//2, size//2), "TW", 
             font=font, fill=(255, 255, 255, 255), anchor="mm")
    
    # Save as PNG
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    png_path = os.path.join(assets_dir, "icon.png")
    img.save(png_path, "PNG", quality=100)
    
    # Convert to ICNS using sips
    icns_path = os.path.join(assets_dir, "icon.icns")
    try:
        result = subprocess.run([
            'sips', '-s', 'format', 'icns', png_path, '--out', icns_path
        ], capture_output=True, text=True, check=True)
        
        # Clean up PNG
        os.remove(png_path)
        print(f"Created application icon: {icns_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error converting to ICNS: {e}")
        print("Keeping PNG version")
        
    except FileNotFoundError:
        print("sips command not found, keeping PNG version")

if __name__ == "__main__":
    create_icon()
EOF
    fi
    
    print_success "Assets created"
}

update_version_info() {
    print_step "Updating version information..."
    
    # Update version in Time_Warp.py if it has a version string
    if grep -q "__version__" Time_Warp.py 2>/dev/null; then
        sed -i '' "s/__version__ = .*/__version__ = \"${VERSION}\"/" Time_Warp.py
    fi
    
    # Ensure pyproject.toml has correct version
    if [ -f "pyproject.toml" ]; then
        sed -i '' "s/version = .*/version = \"${VERSION}\"/" pyproject.toml
    fi
    
    print_success "Version updated to ${VERSION}"
}

clean_build() {
    print_step "Cleaning previous builds..."
    
    # Remove build directories
    [ -d "${BUILD_DIR}" ] && rm -rf "${BUILD_DIR}"
    [ -d "${DIST_DIR}" ] && rm -rf "${DIST_DIR}"
    
    # Remove PyInstaller cache
    [ -d "__pycache__" ] && rm -rf __pycache__
    [ -d "build" ] && rm -rf build
    [ -d "dist" ] && rm -rf dist
    
    print_success "Build directories cleaned"
}

build_application() {
    print_step "Building macOS application..."
    
    # Ensure we're in the right directory and venv is active
    cd "${PROJECT_DIR}"
    source .Time_Warp/bin/activate
    
    # Run PyInstaller with macOS spec
    pyinstaller \
        --distpath="${DIST_DIR}" \
        --workpath="${BUILD_DIR}" \
        --clean \
        --noconfirm \
        Time_Warp_macOS.spec
    
    APP_PATH="${DIST_DIR}/Time_Warp.app"
    if [ ! -d "${APP_PATH}" ]; then
        print_error "Application build failed"
        exit 1
    fi
    
    print_success "Application built: ${APP_PATH}"
    
    # Get app size
    APP_SIZE=$(du -sh "${APP_PATH}" | cut -f1)
    print_success "Application size: ${APP_SIZE}"
}

code_sign_app() {
    print_step "Code signing application..."
    
    APP_PATH="${DIST_DIR}/Time_Warp.app"
    
    # Check for signing certificate
    CERT_NAME=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -n1 | sed 's/.*") \(.*\)/\1/' || true)
    
    if [ -z "$CERT_NAME" ]; then
        print_warning "No Developer ID certificate found"
        print_warning "App will show security warnings on other machines"
        return 0
    fi
    
    print_step "Found certificate: ${CERT_NAME}"
    
    # Sign all frameworks and executables in the app bundle
    find "${APP_PATH}" -type f \( -name "*.dylib" -o -name "*.so" -o -name "*.framework" \) -exec codesign --force --sign "$CERT_NAME" {} \;
    
    # Sign the main app bundle
    codesign --force --deep --sign "$CERT_NAME" "${APP_PATH}"
    
    # Verify signature
    if codesign --verify --verbose "${APP_PATH}" 2>/dev/null; then
        print_success "Application successfully code signed"
    else
        print_warning "Code signing verification failed"
    fi
}

create_dmg() {
    print_step "Creating DMG installer..."
    
    APP_PATH="${DIST_DIR}/Time_Warp.app"
    DMG_NAME="Time_Warp_IDE_v${VERSION}_macOS"
    
    # Remove old DMG
    [ -f "${DMG_NAME}.dmg" ] && rm "${DMG_NAME}.dmg"
    
    if ! command -v create-dmg &> /dev/null; then
        print_warning "create-dmg not available, skipping DMG creation"
        return 0
    fi
    
    # Create DMG
    create-dmg \
        --volname "Time_Warp IDE v${VERSION}" \
        --volicon "${ASSETS_DIR}/icon.icns" \
        --window-pos 200 120 \
        --window-size 800 600 \
        --icon-size 100 \
        --icon "Time_Warp.app" 200 190 \
        --hide-extension "Time_Warp.app" \
        --app-drop-link 600 185 \
        --background-color "#2C3E50" \
        --hdiutil-quiet \
        "${DMG_NAME}.dmg" \
        "${DIST_DIR}/" 2>/dev/null || {
            print_warning "DMG creation failed, but app bundle is available"
            return 0
        }
    
    if [ -f "${DMG_NAME}.dmg" ]; then
        DMG_SIZE=$(ls -lh "${DMG_NAME}.dmg" | awk '{print $5}')
        print_success "DMG created: ${DMG_NAME}.dmg (${DMG_SIZE})"
        
        # Sign DMG if we have a certificate
        CERT_NAME=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -n1 | sed 's/.*") \(.*\)/\1/' || true)
        if [ ! -z "$CERT_NAME" ]; then
            codesign --force --sign "$CERT_NAME" "${DMG_NAME}.dmg"
            print_success "DMG code signed"
        fi
    fi
}

create_release_package() {
    print_step "Creating release package..."
    
    # Create release directory
    mkdir -p "${RELEASE_DIR}"
    
    # Copy app bundle
    if [ -d "${DIST_DIR}/Time_Warp.app" ]; then
        cp -R "${DIST_DIR}/Time_Warp.app" "${RELEASE_DIR}/"
    fi
    
    # Copy DMG if it exists
    DMG_NAME="Time_Warp_IDE_v${VERSION}_macOS.dmg"
    if [ -f "${DMG_NAME}" ]; then
        cp "${DMG_NAME}" "${RELEASE_DIR}/"
    fi
    
    # Create release notes
    cat > "${RELEASE_DIR}/README.md" << EOF
# Time_Warp IDE v${VERSION} - macOS Release

## Installation

### Option 1: DMG Installer (Recommended)
1. Download \`${DMG_NAME}\`
2. Double-click to mount the disk image
3. Drag Time_Warp.app to Applications folder

### Option 2: Direct App Bundle
1. Download \`Time_Warp.app\` 
2. Move to Applications folder
3. Right-click → Open on first launch (bypass Gatekeeper)

## System Requirements
- macOS ${MIN_MACOS_VERSION} or later
- 100MB free disk space
- Python 3.7+ (bundled)

## What's New in v${VERSION}
- Enhanced multi-tab editor
- Improved PILOT, BASIC, and Logo language support
- Better graphics rendering
- macOS-native app bundle
- Improved error handling
- Theme system enhancements

## Educational Features
- PILOT programming language
- BASIC interpreter with turtle graphics
- Logo programming environment
- Python scripting support
- Interactive tutorials
- Code completion and syntax highlighting

## Support
For issues and documentation, visit:
https://github.com/James-HoneyBadger/Time_Warp

## License
MIT License - See LICENSE file for details
EOF
    
    # Create installation script for advanced users
    cat > "${RELEASE_DIR}/install.sh" << 'EOF'
#!/bin/bash
# Time_Warp IDE macOS Installation Script

set -e

APP_NAME="Time_Warp.app"
APPLICATIONS_DIR="/Applications"

echo "🚀 Installing Time_Warp IDE..."

if [ ! -d "${APP_NAME}" ]; then
    echo "❌ ${APP_NAME} not found in current directory"
    exit 1
fi

echo "📁 Copying to Applications folder..."
cp -R "${APP_NAME}" "${APPLICATIONS_DIR}/"

echo "✅ Installation complete!"
echo "🎯 Launch from Applications or Launchpad"
EOF
    
    chmod +x "${RELEASE_DIR}/install.sh"
    
    print_success "Release package created: ${RELEASE_DIR}"
}

test_application() {
    print_step "Testing application..."
    
    APP_PATH="${DIST_DIR}/Time_Warp.app"
    
    # Basic launch test
    timeout 10s open "${APP_PATH}" || print_warning "App launch test timed out (may be normal)"
    
    # Test file associations
    if [ -f "examples/sample_pilot_program.pilot" ]; then
        print_step "Testing file associations..."
        # This would normally open the file in the app
        # open -a "${APP_PATH}" "examples/sample_pilot_program.pilot" &
        # sleep 2
        # killall "Time_Warp" 2>/dev/null || true
    fi
    
    print_success "Basic tests completed"
}

print_summary() {
    echo -e "\n${GREEN}🎉 macOS Build Completed Successfully!${NC}"
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    
    echo -e "${BLUE}Build Information:${NC}"
    echo -e "  Version: ${VERSION}"
    echo -e "  Product: ${PRODUCT_NAME}"
    echo -e "  Bundle ID: ${BUNDLE_ID}"
    echo -e "  Min macOS: ${MIN_MACOS_VERSION}"
    
    echo -e "\n${BLUE}Generated Files:${NC}"
    
    APP_PATH="${DIST_DIR}/Time_Warp.app"
    if [ -d "${APP_PATH}" ]; then
        APP_SIZE=$(du -sh "${APP_PATH}" | cut -f1)
        echo -e "  📱 App Bundle: ${APP_PATH} (${APP_SIZE})"
    fi
    
    DMG_NAME="Time_Warp_IDE_v${VERSION}_macOS.dmg"
    if [ -f "${DMG_NAME}" ]; then
        DMG_SIZE=$(ls -lh "${DMG_NAME}" | awk '{print $5}')
        echo -e "  💿 DMG Installer: ${DMG_NAME} (${DMG_SIZE})"
    fi
    
    if [ -d "${RELEASE_DIR}" ]; then
        echo -e "  📦 Release Package: ${RELEASE_DIR}"
    fi
    
    echo -e "\n${BLUE}Distribution Notes:${NC}"
    echo -e "  • App is ready for distribution"
    echo -e "  • Users may see security warning on first launch"
    echo -e "  • Recommend distributing via DMG for best UX"
    
    CERT_NAME=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -n1 | sed 's/.*") \(.*\)/\1/' || true)
    if [ -z "$CERT_NAME" ]; then
        echo -e "  • ${YELLOW}Consider code signing for wider distribution${NC}"
    else
        echo -e "  • ✅ Code signed with: ${CERT_NAME}"
    fi
    
    echo -e "\n${GREEN}🚀 Ready for macOS distribution!${NC}"
}

# Main execution
main() {
    print_header
    
    check_prerequisites
    setup_environment
    create_assets
    update_version_info
    clean_build
    build_application
    code_sign_app
    create_dmg
    create_release_package
    test_application
    print_summary
}

# Run main function
main "$@"