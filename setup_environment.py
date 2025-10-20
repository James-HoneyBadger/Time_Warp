#!/usr/bin/env python3
"""
Time_Warp IDE Environment Setup Helper
A simple script to help users set up the development environment manually
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main setup function"""
    print("🚀 Time_Warp IDE Environment Setup Helper")
    print("=" * 50)

    project_root = Path(__file__).resolve().parent

    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print("✅ Python version OK")

    # Check if virtual environment exists
    venv_path = project_root / ".venv"
    if venv_path.exists():
        print(f"✅ Virtual environment found at {venv_path}")
    else:
        print("📦 Creating virtual environment...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            sys.exit(1)

    # Get virtual environment Python
    if os.name == 'nt':  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        venv_python = venv_path / "bin" / "python"

    if not venv_python.exists():
        print("❌ Virtual environment Python not found")
        sys.exit(1)

    # Upgrade pip
    print("⬆️ Upgrading pip...")
    try:
        subprocess.check_call([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to upgrade pip: {e}")

    # Install requirements
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("📚 Installing requirements...")
        try:
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)])
            print("✅ Requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            sys.exit(1)
    else:
        print("⚠️ requirements.txt not found")

    # Install from pyproject.toml if it exists
    pyproject_file = project_root / "pyproject.toml"
    if pyproject_file.exists():
        print("📦 Installing from pyproject.toml...")
        try:
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "-e", str(project_root)])
            print("✅ Project installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to install project: {e}")

    # Test basic imports
    print("🧪 Testing basic imports...")
    test_imports = [
        ("PIL", "Pillow"),
        ("pygame", "pygame"),
    ]

    for module, package in test_imports:
        try:
            result = subprocess.run([str(venv_python), "-c", f"import {module}"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} available")
            else:
                print(f"❌ {package} not available")
        except Exception as e:
            print(f"❌ Error testing {package}: {e}")

    print("=" * 50)
    print("🎉 Environment setup complete!")
    print(f"💡 To activate: source {venv_path}/bin/activate")
    print("🚀 You can now run: python Time_Warp.py")

if __name__ == "__main__":
    main()