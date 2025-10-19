#!/usr/bin/env python3
"""
Time_Warp IDE 1.1 - Master Test Runner
Runs all tests for the Time_Warp IDE project
"""

import sys
import subprocess
from pathlib import Path


# Get project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_comprehensive_tests():
    """Run the comprehensive test suite"""
    print("🧪 Running Comprehensive Test Suite...")
    test_file = project_root / "tests" / "test_comprehensive.py"
    result = subprocess.run([sys.executable, str(test_file)],
                           capture_output=False, check=True)
    return result.returncode == 0


def run_minimal_tests():
    """Run minimal smoke tests"""
    print("🔥 Running Minimal Smoke Tests...")
    test_file = project_root / "scripts" / "run_tests_minimal.py"
    if test_file.exists():
        result = subprocess.run([sys.executable, str(test_file)],
                               capture_output=False, check=True)
        return result.returncode == 0
    return True


def run_ci_tests():
    """Run CI/CD pipeline tests"""
    print("🚀 Running CI/CD Tests...")
    test_file = project_root / "scripts" / "run_tests_ci.py"
    if test_file.exists():
        result = subprocess.run([sys.executable, str(test_file)],
                               capture_output=False, check=True)
        return result.returncode == 0
    return True


def main():
    """Main test runner"""
    print("=" * 60)
    print("🎯 Time_Warp IDE 1.1 - Master Test Runner")
    print("=" * 60)
    
    all_passed = True
    
    # Run comprehensive tests
    if not run_comprehensive_tests():
        all_passed = False
        print("❌ Comprehensive tests failed!")
    else:
        print("✅ Comprehensive tests passed!")
    
    print("\n" + "-" * 40 + "\n")
    
    # Run minimal tests
    if not run_minimal_tests():
        all_passed = False
        print("❌ Minimal tests failed!")
    else:
        print("✅ Minimal tests passed!")
    
    print("\n" + "-" * 40 + "\n")
    
    # Run CI tests
    if not run_ci_tests():
        all_passed = False
        print("❌ CI tests failed!")
    else:
        print("✅ CI tests passed!")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Time_Warp IDE 1.1 is ready for release!")
        return 0
    else:
        print("💥 Some tests failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
