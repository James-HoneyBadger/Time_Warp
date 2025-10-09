#!/bin/bash
# 🚀 JAMES IDE GitHub Setup Script

echo "🎯 Setting up JAMES IDE for GitHub with VS Code Integration"
echo "=========================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Please follow these steps:${NC}"
echo ""

echo -e "${YELLOW}1. Create GitHub Repository:${NC}"
echo "   • Go to https://github.com/new"
echo "   • Repository name: JAMES-IDE"
echo "   • Description: 🚀 JAMES IDE - Multi-language educational programming IDE"
echo "   • Make it Public or Private (your choice)"
echo "   • DO NOT initialize with README, .gitignore, or license"
echo "   • Click 'Create repository'"
echo ""

echo -e "${YELLOW}2. Get your GitHub username and run these commands:${NC}"
echo "   Replace YOUR_USERNAME with your actual GitHub username:"
echo ""
echo -e "${GREEN}   git remote add origin https://github.com/YOUR_USERNAME/JAMES-IDE.git${NC}"
echo -e "${GREEN}   git branch -M main${NC}"
echo -e "${GREEN}   git push -u origin main${NC}"
echo ""

echo -e "${YELLOW}3. VS Code Setup:${NC}"
echo "   • Open VS Code in this folder: code ."
echo "   • Install recommended extensions (VS Code will prompt)"
echo "   • Sign in to GitHub: Ctrl+Shift+P → 'GitHub: Sign In'"
echo "   • Open JAMES.code-workspace for full integration"
echo ""

echo -e "${YELLOW}4. Auto-Sync Configuration:${NC}"
echo "   • VS Code → Settings → search 'git autofetch'"
echo "   • Enable 'Git: Auto Fetch'"
echo "   • Enable 'Git: Enable Smart Commit'"
echo "   • Disable 'Git: Confirm Sync' for automatic sync"
echo ""

echo -e "${GREEN}✅ Your JAMES IDE will then have:${NC}"
echo "   • Automatic GitHub sync"
echo "   • CI/CD pipeline with GitHub Actions"
echo "   • Custom file associations for .james, .pilot, .bas, .logo files"
echo "   • Integrated debugging and testing"
echo "   • Professional development workflow"
echo ""

echo -e "${BLUE}🎨 After setup, try changing themes in JAMES IDE - they'll persist!${NC}"
echo -e "${BLUE}🔧 Use F5 in VS Code to launch JAMES with debugging enabled${NC}"
echo ""

echo "Happy coding with JAMES IDE! 🚀"