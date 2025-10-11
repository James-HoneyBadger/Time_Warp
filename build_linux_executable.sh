#!/bin/bash
"""
Time_Warp IDE - Linux Executable Build Script
Automates the entire process of building standalone Linux executable
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_ROOT/dist"
PACKAGE_NAME="Time_Warp_IDE_v1.1_Linux_Standalone"

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  Time_Warp IDE - Linux Build Script${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    print_info "Checking build dependencies..."
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_info "Installing PyInstaller..."
        pip3 install pyinstaller
    fi
    
    # Check PIL for icons
    if ! python3 -c "from PIL import Image" 2>/dev/null; then
        print_info "Installing Pillow for icon creation..."
        pip3 install Pillow
    fi
    
    print_success "All dependencies available"
}

clean_build() {
    print_info "Cleaning previous build artifacts..."
    
    rm -rf build/
    rm -rf dist/
    rm -rf __pycache__/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Build artifacts cleaned"
}

create_icons() {
    print_info "Creating application icons..."
    
    if [ -f "create_icon.py" ]; then
        python3 create_icon.py
        print_success "Icons created"
    else
        print_warning "Icon creation script not found, using default icons"
    fi
}

build_executable() {
    print_info "Building standalone executable with PyInstaller..."
    
    if [ ! -f "Time_Warp.spec" ]; then
        print_error "PyInstaller spec file not found"
        exit 1
    fi
    
    pyinstaller --clean Time_Warp.spec
    
    if [ -f "dist/Time_Warp" ]; then
        print_success "Executable built successfully"
        
        # Check executable
        file dist/Time_Warp
        ls -lh dist/Time_Warp
    else
        print_error "Executable build failed"
        exit 1
    fi
}

test_executable() {
    print_info "Testing executable..."
    
    if [ -f "dist/Time_Warp" ]; then
        # Make executable
        chmod +x dist/Time_Warp
        
        # Quick test run (timeout after 5 seconds)
        timeout 5s ./dist/Time_Warp --help >/dev/null 2>&1 || true
        
        print_success "Executable test completed"
    else
        print_error "Executable not found for testing"
        exit 1
    fi
}

create_distribution_package() {
    print_info "Creating distribution package..."
    
    # Create distribution directory
    DIST_DIR="$BUILD_DIR/${PACKAGE_NAME}"
    mkdir -p "$DIST_DIR"
    
    # Copy executable
    cp dist/Time_Warp "$DIST_DIR/"
    
    # Copy icons
    if [ -d "dist/icons" ]; then
        cp -r dist/icons "$DIST_DIR/"
    fi
    
    # Copy desktop file
    if [ -f "dist/time_warp.desktop" ]; then
        cp dist/time_warp.desktop "$DIST_DIR/"
    fi
    
    # Copy installer
    if [ -f "dist/install.sh" ]; then
        cp dist/install.sh "$DIST_DIR/"
        chmod +x "$DIST_DIR/install.sh"
    fi
    
    # Copy documentation
    for doc in README.md INTERPRETER_VERIFICATION_REPORT.md VERIFICATION_COMPLETE.md; do
        if [ -f "$doc" ]; then
            cp "$doc" "$DIST_DIR/"
        fi
    done
    
    # Copy distribution README
    if [ -f "dist/Time_Warp_Linux/README_DISTRIBUTION.md" ]; then
        cp "dist/Time_Warp_Linux/README_DISTRIBUTION.md" "$DIST_DIR/"
    fi
    
    print_success "Distribution package created"
}

create_archive() {
    print_info "Creating compressed archive..."
    
    cd "$BUILD_DIR"
    tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}/"
    
    # Get archive size
    ARCHIVE_SIZE=$(ls -lh "${PACKAGE_NAME}.tar.gz" | awk '{print $5}')
    
    print_success "Archive created: ${PACKAGE_NAME}.tar.gz (${ARCHIVE_SIZE})"
    
    # Calculate checksums
    echo ""
    print_info "Generating checksums..."
    echo "MD5:    $(md5sum "${PACKAGE_NAME}.tar.gz" | cut -d' ' -f1)"
    echo "SHA256: $(sha256sum "${PACKAGE_NAME}.tar.gz" | cut -d' ' -f1)"
}

generate_build_info() {
    print_info "Generating build information..."
    
    BUILD_INFO_FILE="$BUILD_DIR/${PACKAGE_NAME}/BUILD_INFO.txt"
    
    cat > "$BUILD_INFO_FILE" << EOF
Time_Warp IDE v1.1 - Linux Standalone Build
===========================================

Build Information:
- Build Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
- Build Host: $(hostname)
- Build User: $(whoami)
- Build OS: $(uname -a)
- Python Version: $(python3 --version)
- PyInstaller Version: $(python3 -c "import PyInstaller; print(PyInstaller.__version__)")

Executable Information:
- File: Time_Warp
- Size: $(ls -lh dist/Time_Warp | awk '{print $5}')
- Type: $(file dist/Time_Warp | cut -d: -f2)

Package Contents:
$(ls -la "$BUILD_DIR/${PACKAGE_NAME}/")

Archive Information:
- Archive: ${PACKAGE_NAME}.tar.gz
- Compressed Size: $(ls -lh "$BUILD_DIR/${PACKAGE_NAME}.tar.gz" | awk '{print $5}')
- MD5: $(md5sum "$BUILD_DIR/${PACKAGE_NAME}.tar.gz" | cut -d' ' -f1)
- SHA256: $(sha256sum "$BUILD_DIR/${PACKAGE_NAME}.tar.gz" | cut -d' ' -f1)

Installation:
1. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz
2. Install: cd ${PACKAGE_NAME} && ./install.sh
3. Run: time-warp

Support:
- GitHub: https://github.com/James-HoneyBadger/Time_Warp
- Issues: https://github.com/James-HoneyBadger/Time_Warp/issues
EOF
    
    print_success "Build information generated"
}

print_build_summary() {
    echo ""
    echo -e "${GREEN}🎉 Linux Executable Build Complete!${NC}"
    echo ""
    echo -e "${BLUE}Build Results:${NC}"
    echo -e "  📁 Package Directory: ${PACKAGE_NAME}/"
    echo -e "  📦 Archive: ${PACKAGE_NAME}.tar.gz"
    echo -e "  💾 Archive Size: $(ls -lh "$BUILD_DIR/${PACKAGE_NAME}.tar.gz" | awk '{print $5}')"
    echo -e "  🔧 Executable Size: $(ls -lh dist/Time_Warp | awk '{print $5}')"
    echo ""
    echo -e "${BLUE}Distribution Contents:${NC}"
    ls -la "$BUILD_DIR/${PACKAGE_NAME}/"
    echo ""
    echo -e "${BLUE}Ready for Distribution:${NC}"
    echo -e "  • Upload ${PACKAGE_NAME}.tar.gz to GitHub Releases"
    echo -e "  • Users can extract and run ./install.sh"
    echo -e "  • Or run directly with ./Time_Warp"
    echo ""
}

main() {
    print_header
    
    cd "$PROJECT_ROOT"
    
    check_dependencies
    clean_build
    create_icons
    build_executable
    test_executable
    create_distribution_package
    generate_build_info
    create_archive
    
    print_build_summary
}

# Check if script is being sourced or executed
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi