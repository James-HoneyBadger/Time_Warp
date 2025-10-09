#!/usr/bin/env python3
"""
TimeWarp IDE Dependency Installer
Installs all required and optional dependencies for TimeWarp IDE
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Install all TimeWarp IDE dependencies"""
    print("🔧 Installing TimeWarp IDE Dependencies")
    print("=" * 40)
    
    # Required dependencies
    required_packages = [
        "Pillow",  # Image processing (PIL)
    ]
    
    # Optional dependencies for enhanced features
    optional_packages = [
        "pygame",         # Game development and audio

        "matplotlib",     # Plotting and visualization
        "requests",       # HTTP requests
        "beautifulsoup4", # Web scraping
        "lxml",          # XML/HTML parsing
    ]
    
    print("Installing required packages...")
    required_success = 0
    for package in required_packages:
        if install_package(package):
            required_success += 1
    
    print(f"\nRequired packages: {required_success}/{len(required_packages)} installed")
    
    print("\nInstalling optional packages...")
    optional_success = 0
    for package in optional_packages:
        if install_package(package):
            optional_success += 1
    
    print(f"\nOptional packages: {optional_success}/{len(optional_packages)} installed")
    
    print("\n" + "=" * 40)
    if required_success == len(required_packages):
        print("✅ All required dependencies installed successfully!")
        print("🚀 TimeWarp IDE is ready to use!")
    else:
        print("⚠️  Some required dependencies failed to install")
        print("Please check the error messages above")
    
    print(f"📊 Total: {required_success + optional_success}/{len(required_packages) + len(optional_packages)} packages installed")

if __name__ == "__main__":
    main()