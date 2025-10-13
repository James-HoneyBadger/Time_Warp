#!/usr/bin/env python3
"""
Time_Warp IDE Ultra-Minimal CI Test
Fallback test with minimal dependencies for GitHub Actions
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set all environment variables for headless operation
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


def test_core_imports():
    """Test that we can import core modules"""
    try:
        print("Testing core imports...")

        # Test basic Python modules
        import json
        import threading
        import subprocess

        print("✅ Basic Python modules imported")

        # Test pygame
        import pygame

        print(f"✅ Pygame {pygame.version.ver} imported")

        # Test our core modules
        from core.interpreter import Time_WarpInterpreter

        print("✅ Time_WarpInterpreter imported")

        from src.timewarp.utils.theme import ThemeManager

        print("✅ ThemeManager imported")

        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality without full GUI"""
    try:
        print("Testing basic functionality...")

        # Test ThemeManager
        from src.timewarp.utils.theme import ThemeManager, get_theme_colors

        theme_manager = ThemeManager()
        colors = theme_manager.get_colors()
        print(f"✅ ThemeManager working - got colors: {type(colors)}")

        # Test theme colors function
        test_colors = get_theme_colors("forest")
        print(f"✅ Theme colors function working - got {len(test_colors)} colors")

        # Test very basic interpreter creation
        from core.interpreter import Time_WarpInterpreter

        interpreter = Time_WarpInterpreter(output_widget=None)
        print("✅ Basic interpreter creation successful")

        return True
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Ultra-minimal test main function"""
    print("🔬 Time_Warp IDE Ultra-Minimal CI Test")
    print("=" * 50)

    # Print environment info
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Directory: {os.getcwd()}")
    print("-" * 50)

    tests_passed = 0
    total_tests = 2

    # Test 1: Core imports
    if test_core_imports():
        tests_passed += 1
    print("-" * 50)

    # Test 2: Basic functionality
    if test_basic_functionality():
        tests_passed += 1
    print("-" * 50)

    print(f"Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All ultra-minimal tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
