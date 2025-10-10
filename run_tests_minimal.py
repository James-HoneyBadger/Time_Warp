#!/usr/bin/env python3
"""
TimeWarp IDE Minimal CI Test
Ultra-minimal test for GitHub Actions
"""

import sys
import os

# Set all environment variables for headless operation
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

def test_minimal_import():
    """Test minimal core functionality"""
    try:
        # Just test that we can import the core interpreter
        from core.interpreter import TimeWarpInterpreter
        print("✅ TimeWarpInterpreter import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_instantiation():
    """Test basic object creation"""
    try:
        from core.interpreter import TimeWarpInterpreter
        # Try to create interpreter with minimal initialization
        interpreter = TimeWarpInterpreter(output_widget=None)
        print("✅ TimeWarpInterpreter instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False

def main():
    """Minimal test main function"""
    print("🔬 TimeWarp IDE Minimal CI Test")
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

if __name__ == '__main__':
    sys.exit(main())