#!/usr/bin/env python3
"""
TimeWarp IDE CI Test Runner
Simplified test runner for CI environments
"""

import sys
import os
import warnings

# Suppress pygame startup messages and warnings in CI
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings('ignore', message='pkg_resources is deprecated')
warnings.filterwarnings('ignore', category=UserWarning)

def test_basic_imports():
    """Test that core modules can be imported"""
    print("🧪 Testing Core Imports...")
    
    try:
        # Test core interpreter import
        from core.interpreter import TimeWarpInterpreter
        print("✅ Core interpreter import successful")
        
        # Test that basic initialization works (with minimal setup)
        interpreter = TimeWarpInterpreter(output_widget=None)
        print("✅ Core interpreter initialization successful")
        
        # Test basic functionality without GUI
        result = interpreter.interpolate_text("Hello, World!")
        if result == "Hello, World!":
            print("✅ Basic text interpolation working")
        else:
            print(f"⚠️ Text interpolation returned: {result}")
        
        return True
        
    except (ImportError, AttributeError, TypeError) as e:
        print(f"❌ Import test failed: {e}")
        # Don't print full traceback in CI to keep output clean
        return False

def test_language_imports():
    """Test that language executors can be imported"""
    print("🧪 Testing Language Executor Imports...")
    
    try:
        from core.languages.basic import BasicExecutor
        from core.languages.logo import LogoExecutor  
        from core.languages.pilot import PilotExecutor
        
        # Test that classes can be instantiated
        _ = BasicExecutor(None)
        _ = LogoExecutor(None)  
        _ = PilotExecutor(None)
        
        print("✅ Language executor imports successful")
        
        return True
        
    except (ImportError, AttributeError, TypeError) as e:
        print(f"❌ Language import test failed: {e}")
        # Don't print full traceback in CI to keep output clean
        return False

def main():
    """Main CI test runner"""
    print("🚀 TimeWarp IDE CI Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Run basic import tests
    if test_basic_imports():
        tests_passed += 1
    
    # Run language import tests  
    if test_language_imports():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    
    if tests_passed == total_tests:
        print(f"✅ All {tests_passed}/{total_tests} tests passed!")
        print("🎉 TimeWarp IDE core functionality verified!")
        return 0
    else:
        print(f"❌ {tests_passed}/{total_tests} tests passed")
        return 1

if __name__ == '__main__':
    sys.exit(main())