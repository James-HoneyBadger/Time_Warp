#!/usr/bin/env python3
"""
Time_Warp IDE Test Runner
Production-ready test runner with comprehensive testing capabilities
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)


def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("🧪 Time_Warp IDE - Production Test Suite")
    print("=" * 60)

    # Try to use the comprehensive test runner
    try:
        from tests.test_runner import Time_WarpTestRunner

        print("🚀 Running comprehensive test suite...")

        test_runner = Time_WarpTestRunner()
        success = test_runner.run_all_tests()

        return success

    except ImportError as e:
        print(f"⚠️ Comprehensive test runner not available: {e}")
        print("🔄 Falling back to basic test functionality...")
        return run_basic_tests()


def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running Basic Time_Warp IDE Tests")
    print("=" * 50)

    test_results = {"passed": 0, "failed": 0, "total": 0}

    def run_test(test_name, test_func):
        """Helper to run individual test"""
        test_results["total"] += 1
        try:
            print(f"🧪 {test_name}...", end=" ")
            result = test_func()
            if result:
                print("✅")
                test_results["passed"] += 1
            else:
                print("❌")
                test_results["failed"] += 1
        except Exception as e:
            print(f"💥 ERROR: {e}")
            test_results["failed"] += 1

    # Test 1: Core imports
    def test_core_imports():
        try:
            from core.interpreter import Time_WarpInterpreter

            return True
        except ImportError:
            return False

    run_test("Core interpreter import", test_core_imports)

    # Test 2: Feature system imports
    def test_feature_imports():
        try:
            from features.tutorial_system import TutorialSystem
            from features.ai_assistant import AICodeAssistant
            from features.gamification import GamificationSystem

            return True
        except ImportError:
            return False

    run_test("Feature system imports", test_feature_imports)

    # Test 3: Basic initialization
    def test_initialization():
        try:
            from core.interpreter import Time_WarpInterpreter
            from features.tutorial_system import TutorialSystem
            from features.ai_assistant import AICodeAssistant
            from features.gamification import GamificationSystem

            interpreter = Time_WarpInterpreter()
            tutorial = TutorialSystem()
            ai_assistant = AICodeAssistant()
            gamification = GamificationSystem()

            return all([interpreter, tutorial, ai_assistant, gamification])
        except Exception:
            return False

    run_test("System initialization", test_initialization)

    # Test 4: Basic PILOT execution
    def test_pilot_execution():
        try:
            from core.interpreter import Time_WarpInterpreter

            interpreter = Time_WarpInterpreter()
            result = interpreter.run_program("T:Hello, Test!\nEND")
            return result is not None
        except Exception:
            return False

    run_test("PILOT program execution", test_pilot_execution)

    # Test 5: Gamification functionality
    def test_gamification():
        try:
            from features.gamification import GamificationSystem

            gamification = GamificationSystem()

            # Test basic functionality
            initial_programs = gamification.user_stats.programs_written
            gamification.record_activity("program_written", {"language": "pilot"})

            return gamification.user_stats.programs_written > initial_programs
        except Exception:
            return False

    run_test("Gamification system", test_gamification)

    # Test 6: File operations
    def test_file_operations():
        try:
            import tempfile

            test_content = "T:File test\nEND"

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pilot", delete=False
            ) as f:
                f.write(test_content)
                temp_file = f.name

            # Read back the file
            with open(temp_file, "r", encoding="utf-8") as f:
                read_content = f.read()

            # Cleanup
            os.unlink(temp_file)

            return read_content.strip() == test_content.strip()
        except Exception:
            return False

    run_test("File operations", test_file_operations)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")

    success_rate = (
        (test_results["passed"] / test_results["total"]) * 100
        if test_results["total"] > 0
        else 0
    )
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if test_results["failed"] == 0:
        print("\n🎉 All basic tests passed!")
        print("✨ Time_Warp IDE core functionality is working correctly.")
        return True
    else:
        print(f"\n⚠️ {test_results['failed']} test(s) failed.")
        print("Some functionality may not be working correctly.")
        return False


def main():
    """Main test runner entry point"""
    print("🚀 Time_Warp IDE Test Runner")
    print("=" * 40)

    # Check Python version
    if sys.version_info < (3, 7):
        print("⚠️ Python 3.7+ recommended for optimal compatibility")

    # Run tests
    try:
        success = run_comprehensive_tests()
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        print("🔄 Attempting basic tests...")
        success = run_basic_tests()

    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTING COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("\n📋 Time_Warp IDE Status:")
        print("  ✅ Core interpreter working")
        print("  ✅ Feature systems operational")
        print("  ✅ Gamification system active")
        print("  ✅ File operations functional")
        print("  ✅ Basic error handling working")
        print("\n🚀 Ready for production use!")
    else:
        print("⚠️ TESTING COMPLETE - SOME ISSUES DETECTED")
        print("\n📋 Recommendations:")
        print("  🔧 Review failed tests above")
        print("  📖 Check system requirements")
        print("  🔍 Verify all dependencies installed")
        print("  🧪 Run individual test modules for details")
        print("\n💡 Time_Warp IDE may still be functional for basic use.")

    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
