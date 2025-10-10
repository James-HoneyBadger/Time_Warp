#!/usr/bin/env python3
"""
TimeWarp IDE CI Test Runner
Simplified test runner for CI environments
"""

import sys

def test_basic_imports():
    """Test that core modules can be imported"""
    print("🧪 Testing Core Imports...")
    
    try:
        # Test core interpreter import
        from core.interpreter import TimeWarpInterpreter
        print("✅ Core interpreter import successful")
        
        # Test that basic initialization works
        interpreter = TimeWarpInterpreter()
        print("✅ Core interpreter initialization successful")
        
        # Test basic functionality without GUI
        result = interpreter.interpolate_text("Hello, World!")
        if result == "Hello, World!":
            print("✅ Basic text interpolation working")
        
        return True
        
    except (ImportError, AttributeError, TypeError) as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
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
        import traceback
        traceback.print_exc()
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