#!/usr/bin/env python3
"""
Time_Warp IDE Minimal CI Test
Ultra-minimal test for GitHub Actions
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


def test_minimal_import():
    """Test minimal core functionality"""
    try:
        # Test basic Python imports first
        print("✅ Basic Python imports successful")
        
        # Test pygame import
        import pygame
        print(f"✅ Pygame {pygame.version.ver} import successful")
        
        # Just test that we can import the core interpreter
        from core.interpreter import Time_WarpInterpreter
        print("✅ Time_WarpInterpreter import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_instantiation():
    """Test basic object creation"""
    try:
        from core.interpreter import Time_WarpInterpreter

        # Try to create interpreter with minimal initialization
        interpreter = Time_WarpInterpreter(output_widget=None)
        print("✅ Time_WarpInterpreter instantiation successful")
        
        # Test a simple execution
        interpreter.run_program("# Simple comment test", language="python")
        print("✅ Basic execution test successful")
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Minimal test main function"""
    print("🔬 Time_Warp IDE Minimal CI Test")
    print("-" * 40)
    
    # Print environment info for debugging
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries
    print("Environment variables:")
    for key in ["SDL_VIDEODRIVER", "SDL_AUDIODRIVER",
                "PYGAME_HIDE_SUPPORT_PROMPT"]:
        print(f"  {key}: {os.environ.get(key, 'Not set')}")
    print("-" * 40)

    success_count = 0

    # Test 1: Import
    if test_minimal_import():
        success_count += 1

    # Test 2: Instantiation
    if test_basic_instantiation():
        success_count += 1

    print("-" * 40)

    if success_count == 2:
        print("✅ All minimal tests passed!")
        return 0
    else:
        print(f"❌ {success_count}/2 tests passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
