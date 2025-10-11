#!/bin/bash
# Create GitHub Release Assets for Time_Warp IDE v1.2.0
# This creates the standard release files that should be attached to GitHub releases

set -e

echo "📦 Creating GitHub Release Assets for Time_Warp IDE v1.2.0"
echo "========================================================"

VERSION="1.2.0"
RELEASE_DIR="github_release_assets_v${VERSION}"

# Clean and create release directory
echo "🧹 Cleaning previous release assets..."
rm -rf "${RELEASE_DIR}" *.zip *.tar.gz *.sha256

echo "📁 Creating release asset directory..."
mkdir -p "${RELEASE_DIR}"

# Create source code archive (ZIP)
echo "📦 Creating source code ZIP archive..."
git archive --format=zip --prefix="Time_Warp-${VERSION}/" HEAD > "${RELEASE_DIR}/Time_Warp_IDE_v${VERSION}_Source.zip"

# Create source code archive (TAR.GZ)
echo "📦 Creating source code TAR.GZ archive..."
git archive --format=tar.gz --prefix="Time_Warp-${VERSION}/" HEAD > "${RELEASE_DIR}/Time_Warp_IDE_v${VERSION}_Source.tar.gz"

# Create release package with essential files
echo "📦 Creating release package..."
PACKAGE_DIR="Time_Warp_IDE_v${VERSION}"
mkdir -p "${RELEASE_DIR}/${PACKAGE_DIR}"

# Copy essential files to package
cp timewarp.py "${RELEASE_DIR}/${PACKAGE_DIR}/"
cp README.md "${RELEASE_DIR}/${PACKAGE_DIR}/"
cp CHANGELOG.md "${RELEASE_DIR}/${PACKAGE_DIR}/"
cp RELEASE_NOTES_v${VERSION}.md "${RELEASE_DIR}/${PACKAGE_DIR}/"
cp requirements.txt "${RELEASE_DIR}/${PACKAGE_DIR}/"

# Copy source directory
cp -r src/ "${RELEASE_DIR}/${PACKAGE_DIR}/"

# Copy demo files
mkdir -p "${RELEASE_DIR}/${PACKAGE_DIR}/demos"
cp demo_*.* "${RELEASE_DIR}/${PACKAGE_DIR}/demos/" 2>/dev/null || echo "No demo files to copy"

# Create package archives
echo "📦 Creating release package ZIP..."
cd "${RELEASE_DIR}"
zip -r "Time_Warp_IDE_v${VERSION}_Package.zip" "${PACKAGE_DIR}/"

echo "📦 Creating release package TAR.GZ..."
tar -czf "Time_Warp_IDE_v${VERSION}_Package.tar.gz" "${PACKAGE_DIR}/"

cd ..

# Generate checksums
echo "🔐 Generating SHA256 checksums..."
cd "${RELEASE_DIR}"
sha256sum *.zip *.tar.gz > SHA256SUMS.txt
cd ..

# Create install script
echo "📝 Creating installation script..."
cat > "${RELEASE_DIR}/install.sh" << 'EOF'
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
EOF

chmod +x "${RELEASE_DIR}/install.sh"

# Show results
echo ""
echo "✅ GitHub Release Assets Created!"
echo ""
echo "📁 Release assets in ${RELEASE_DIR}/:"
ls -lah "${RELEASE_DIR}/"
echo ""
echo "📊 File sizes:"
du -h "${RELEASE_DIR}"/* | sort -h
echo ""
echo "🔐 Checksums:"
cat "${RELEASE_DIR}/SHA256SUMS.txt"
echo ""
echo "🎯 Upload these files to GitHub Release v${VERSION}:"
echo "1. Time_Warp_IDE_v${VERSION}_Source.zip"
echo "2. Time_Warp_IDE_v${VERSION}_Source.tar.gz" 
echo "3. Time_Warp_IDE_v${VERSION}_Package.zip"
echo "4. Time_Warp_IDE_v${VERSION}_Package.tar.gz"
echo "5. SHA256SUMS.txt"
echo "6. install.sh"
echo ""
echo "✅ Ready for GitHub release!"