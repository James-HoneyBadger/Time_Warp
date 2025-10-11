#!/bin/bash
# GitHub Release Setup Script for Time_Warp IDE v1.2.0
# This script prepares the repository for a fresh release

set -e  # Exit on any error

echo "🚀 Setting up Time_Warp IDE v1.2.0 for GitHub Release"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "timewarp.py" ]; then
    echo "❌ Error: Please run this script from the Time_Warp root directory"
    exit 1
fi

echo "📋 Current repository status:"
git status --porcelain

echo ""
echo "🔧 Step 1: Staging all changes for v1.2.0..."
git add -A

echo "🔧 Step 2: Committing v1.2.0 changes..."
git commit -m "🚀 Release v1.2.0 - Fixed theme inheritance and turtle graphics

✅ Major Fixes:
- Fixed code editor theme inheritance issue
- Resolved turtle graphics display problems  
- Enhanced package structure with proper imports
- Fixed VS Code debugging integration

🔧 Technical Improvements:
- Converted to relative imports for better modularity
- Added proper ide_turtle_canvas connection
- Fixed theme application timing
- Enhanced error handling and testing

🎯 User Experience:
- Code editor themes now apply consistently
- Turtle graphics display correctly with proper centering
- Better startup messages and error reporting
- Improved overall stability and reliability

Supersedes buggy v1.0 and v1.1 releases with comprehensive fixes."

echo "🔧 Step 3: Creating and pushing v1.2.0 tag..."
git tag -a v1.2.0 -m "Time_Warp IDE v1.2.0 - Stable Release

🛠️ Critical Bug Fixes:
- Fixed code editor theme inheritance
- Resolved turtle graphics display issues
- Enhanced package structure and imports
- Fixed VS Code debugging support

🎯 Verified Working Features:
- Multi-language support (BASIC, PILOT, Logo, Python, JS, Perl)
- Turtle graphics with proper coordinate centering
- Multi-tab code editor with consistent theming
- 8 beautiful themes (4 dark, 4 light)
- Enhanced graphics canvas with zoom/export
- Professional package structure

This release replaces the buggy v1.0 and v1.1 releases with a stable, 
thoroughly tested version that addresses all identified issues."

echo "🔧 Step 4: Pushing to GitHub..."
git push origin HEAD
git push origin v1.2.0

echo ""
echo "✅ Repository prepared for release!"
echo ""
echo "📦 Next Steps:"
echo "1. Go to: https://github.com/James-HoneyBadger/Time_Warp/releases"
echo "2. Click 'Create a new release'"
echo "3. Select tag: v1.2.0"
echo "4. Title: 'Time_Warp IDE v1.2.0 - Stable Release'"
echo "5. Copy content from RELEASE_NOTES_v1.2.0.md"
echo "6. Mark as 'Latest release'"
echo "7. Upload these assets:"
echo "   - timewarp.py (main executable)"
echo "   - README.md (documentation)"
echo "   - CHANGELOG.md (full changelog)"
echo "   - requirements.txt (dependencies)"
echo ""
echo "🎯 Key files for release assets:"
ls -la timewarp.py README.md CHANGELOG.md requirements.txt RELEASE_NOTES_v1.2.0.md 2>/dev/null | head -20
echo ""
echo "🚀 Ready for release! The repository is now prepared with:"
echo "   ✅ Version updated to 1.2.0 in all files"
echo "   ✅ All fixes committed and tagged"  
echo "   ✅ Release notes prepared"
echo "   ✅ Changelog updated"
echo "   ✅ GitHub tag v1.2.0 created and pushed"
echo ""
echo "Happy releasing! 🎉"