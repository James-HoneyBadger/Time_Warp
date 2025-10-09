#!/usr/bin/env python3
"""
JAMES IDE Comprehensive Test Suite
==================================

This test suite provides comprehensive testing for all JAMES components,
languages, and functionality. It fixes issues found in the existing test
framework and provides detailed error reporting.
"""

import sys
import os
import tempfile
import shutil
import time
import unittest
from datetime import datetime

# Add JAMES to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class JAMESTestSuite(unittest.TestCase):
    """Comprehensive test suite for JAMES IDE"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix='james_test_')
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def run_james_program(self, program_code, expected_vars=None, expected_output=None):
        """Helper method to run JAMES program and check results"""
        import JAMES
        
        # Create fresh interpreter for each test
        interp = JAMES.JAMESInterpreter()
        
        # Capture output
        captured_output = []
        original_log_output = interp.log_output
        
        def capture_output(text):
            captured_output.append(str(text))
            
        interp.log_output = capture_output
        
        # Run the program
        try:
            success = interp.run_program(program_code)
            self.assertTrue(success, "Program execution should succeed")
            
            # Check expected variables
            if expected_vars:
                for var_name, expected_value in expected_vars.items():
                    actual_value = interp.variables.get(var_name.upper())
                    self.assertEqual(str(actual_value), str(expected_value), 
                                   f"Variable {var_name}: expected '{expected_value}', got '{actual_value}'")
            
            # Check expected output
            if expected_output is not None:
                output_text = ''.join(captured_output)
                self.assertIn(expected_output, output_text, 
                            f"Expected output '{expected_output}' not found in '{output_text}'")
                            
        finally:
            interp.log_output = original_log_output
            
        return interp, captured_output

    # ===== PILOT COMMAND TESTS =====
    
    def test_pilot_text_output(self):
        """Test PILOT T: text output command"""
        interp, output = self.run_james_program("T:Hello World\nEND", 
                                               expected_output="Hello World")
    
    def test_pilot_variable_interpolation(self):
        """Test PILOT variable interpolation in text"""
        interp, output = self.run_james_program("U:NAME=Alice\nT:Hello *NAME*!\nEND",
                                               expected_vars={"NAME": "Alice"},
                                               expected_output="Hello Alice!")
    
    def test_pilot_variable_assignment(self):
        """Test PILOT U: variable assignment"""
        interp, output = self.run_james_program("U:COUNT=42\nEND",
                                               expected_vars={"COUNT": "42"})
        
        interp, output = self.run_james_program("U:MESSAGE=Hello World\nEND",
                                               expected_vars={"MESSAGE": "Hello World"})
    
    def test_pilot_variable_interpolation_complex(self):
        """Test complex PILOT variable interpolation"""
        # This was failing before - should now work
        interp, output = self.run_james_program("U:NAME=World\nU:GREETING=Hello *NAME*\nT:*GREETING*\nEND",
                                               expected_vars={"GREETING": "Hello World"},
                                               expected_output="Hello World")
    
    def test_pilot_expressions(self):
        """Test PILOT mathematical expressions"""
        interp, output = self.run_james_program("U:RESULT=10+5\nEND",
                                               expected_vars={"RESULT": "15"})
        
        interp, output = self.run_james_program("U:A=10\nU:B=5\nC:RESULT=*A*+*B*\nEND",
                                               expected_vars={"RESULT": "15"})
    
    def test_pilot_conditions(self):
        """Test PILOT Y: and N: conditions"""
        interp, output = self.run_james_program("U:X=5\nY:*X* > 3\nU:RESULT=YES\nEND",
                                               expected_vars={"RESULT": "YES"})
        
        interp, output = self.run_james_program("U:X=5\nN:*X* > 10\nU:RESULT=NO\nEND",
                                               expected_vars={"RESULT": "NO"})
    
    def test_pilot_jumps(self):
        """Test PILOT J: jump commands"""
        interp, output = self.run_james_program("J:SKIP\nU:RESULT=SKIPPED\nL:SKIP\nU:RESULT=JUMPED\nEND",
                                               expected_vars={"RESULT": "JUMPED"})

    # ===== FILE COMMAND TESTS =====
    
    def test_file_operations(self):
        """Test PILOT F: file operations"""
        # Test F:WRITE
        interp, output = self.run_james_program('F:WRITE "test.txt" "Hello File"\nEND',
                                               expected_vars={"FILE_WRITE_SUCCESS": "1"})
        
        # Verify file was created
        self.assertTrue(os.path.exists("test.txt"))
        
        # Test F:READ
        interp, output = self.run_james_program('F:READ "test.txt" CONTENT\nEND',
                                               expected_vars={"CONTENT": "Hello File", "FILE_READ_SUCCESS": "1"})
        
        # Test F:APPEND
        interp, output = self.run_james_program('F:APPEND "test.txt" " World"\nF:READ "test.txt" CONTENT\nEND',
                                               expected_vars={"CONTENT": "Hello File World"})
        
        # Test F:EXISTS
        interp, output = self.run_james_program('F:EXISTS "test.txt" EXISTS\nEND',
                                               expected_vars={"EXISTS": "1"})
        
        interp, output = self.run_james_program('F:EXISTS "nonexistent.txt" EXISTS\nEND',
                                               expected_vars={"EXISTS": "0"})
        
        # Test F:SIZE
        interp, output = self.run_james_program('F:SIZE "test.txt" SIZE\nEND',
                                               expected_vars={"SIZE": str(len("Hello File World"))})
        
        # Test F:DELETE
        interp, output = self.run_james_program('F:DELETE "test.txt"\nF:EXISTS "test.txt" EXISTS\nEND',
                                               expected_vars={"EXISTS": "0"})

    # ===== STRING COMMAND TESTS =====
    
    def test_string_operations(self):
        """Test PILOT S: string operations"""
        # Test S:LENGTH
        interp, output = self.run_james_program('S:LENGTH "Hello" LEN\nEND',
                                               expected_vars={"LEN": "5"})
        
        interp, output = self.run_james_program('S:LENGTH "" LEN\nEND',
                                               expected_vars={"LEN": "0"})
        
        # Test S:UPPER
        interp, output = self.run_james_program('S:UPPER "hello" UPPER\nEND',
                                               expected_vars={"UPPER": "HELLO"})
        
        # Test S:LOWER
        interp, output = self.run_james_program('S:LOWER "HELLO" LOWER\nEND',
                                               expected_vars={"LOWER": "hello"})
        
        # Test S:FIND
        interp, output = self.run_james_program('S:FIND "Hello World" "World" POS\nEND',
                                               expected_vars={"POS": "6"})
        
        interp, output = self.run_james_program('S:FIND "Hello World" "xyz" POS\nEND',
                                               expected_vars={"POS": "-1"})
        
        # Test S:REPLACE
        interp, output = self.run_james_program('S:REPLACE "Hello World" "World" "Universe" RESULT\nEND',
                                               expected_vars={"RESULT": "Hello Universe"})
        
        # Test S:SUBSTRING
        interp, output = self.run_james_program('S:SUBSTRING "Hello World" 0 5 RESULT\nEND',
                                               expected_vars={"RESULT": "Hello"})

    # ===== WEB COMMAND TESTS =====
    
    def test_web_operations(self):
        """Test PILOT W: web operations"""
        # Test W:ENCODE
        interp, output = self.run_james_program('W:ENCODE "Hello World" ENCODED\nEND',
                                               expected_vars={"ENCODED": "Hello%20World"})
        
        # Test W:DECODE
        interp, output = self.run_james_program('W:DECODE "Hello%20World" DECODED\nEND',
                                               expected_vars={"DECODED": "Hello World"})
        
        # Test round-trip
        interp, output = self.run_james_program('W:ENCODE "Special: !@#$" ENCODED\nW:DECODE "*ENCODED*" DECODED\nEND',
                                               expected_vars={"DECODED": "Special: !@#$"})

    # ===== DATABASE COMMAND TESTS =====
    
    def test_database_operations(self):
        """Test PILOT D: database operations"""
        # Test D:OPEN
        interp, output = self.run_james_program('D:OPEN "test.db"\nEND',
                                               expected_vars={"DB_OPEN_SUCCESS": "1"})
        
        # Test D:QUERY (CREATE TABLE)
        interp, output = self.run_james_program('''D:OPEN "test.db"
D:QUERY "CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)"
END''', expected_vars={"DB_QUERY_SUCCESS": "1"})
        
        # Test D:INSERT
        interp, output = self.run_james_program('''D:OPEN "test.db"
D:QUERY "CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)"
D:INSERT "test" "id,name" "1,'Alice'"
END''', expected_vars={"DB_INSERT_SUCCESS": "1"})

    # ===== BASIC COMMAND TESTS =====
    
    def test_basic_commands(self):
        """Test BASIC language commands"""
        # Test LET
        interp, output = self.run_james_program('LET X = 42\nEND',
                                               expected_vars={"X": "42"})
        
        interp, output = self.run_james_program('LET X = 10 + 5\nEND',
                                               expected_vars={"X": "15"})
        
        # Test PRINT - fixed formatting issue
        interp, output = self.run_james_program('PRINT "Hello World"\nEND',
                                               expected_output="Hello World")
        
        interp, output = self.run_james_program('LET X = 42\nPRINT "X is "; X\nEND',
                                               expected_output="X is 42")
        
        # Test IF THEN
        interp, output = self.run_james_program('LET X = 5\nIF X > 3 THEN LET Y = 1\nEND',
                                               expected_vars={"Y": "1"})

    # ===== LOGO COMMAND TESTS =====
    
    def test_logo_commands(self):
        """Test Logo language commands"""
        # Basic turtle commands - these should not crash
        interp, output = self.run_james_program('FORWARD 100\nEND')
        interp, output = self.run_james_program('RIGHT 90\nEND')  
        interp, output = self.run_james_program('LEFT 45\nEND')
        interp, output = self.run_james_program('HOME\nEND')
        interp, output = self.run_james_program('CLEARSCREEN\nEND')

    # ===== EXPRESSION EVALUATION TESTS =====
    
    def test_expressions(self):
        """Test mathematical expression evaluation"""
        # Basic arithmetic
        interp, output = self.run_james_program('U:RESULT=10+5\nEND',
                                               expected_vars={"RESULT": "15"})
        
        interp, output = self.run_james_program('U:RESULT=10-3\nEND',
                                               expected_vars={"RESULT": "7"})
        
        interp, output = self.run_james_program('U:RESULT=6*7\nEND',
                                               expected_vars={"RESULT": "42"})
        
        # Division - handle both integer and float results
        interp, output = self.run_james_program('U:RESULT=20/4\nEND')
        result = interp.variables.get("RESULT")
        self.assertIn(str(result), ["5", "5.0"], f"Division result should be 5 or 5.0, got {result}")
        
        # Complex expressions
        interp, output = self.run_james_program('U:RESULT=(10+5)*2-3\nEND',
                                               expected_vars={"RESULT": "27"})
        
        # With variables - fix the operator precedence issue
        interp, output = self.run_james_program('U:A=10\nU:B=5\nU:RESULT=*A*+*B**2\nEND')
        # This should be 10 + (5*2) = 20, not (10+5)*2 = 30
        result = interp.variables.get("RESULT")
        self.assertEqual(str(result), "20", f"Expected 20, got {result}")
        
        # Division by zero
        interp, output = self.run_james_program('U:RESULT=10/0\nEND')
        result = interp.variables.get("RESULT")
        self.assertTrue("ERROR" in str(result) or "Division by zero" in str(result),
                       f"Division by zero should return error, got {result}")

    # ===== THEME SYSTEM TESTS =====
    
    def test_theme_system(self):
        """Test theme management system"""
        from tools.theme import ThemeManager, load_config, save_config, get_theme_colors
        
        # Test loading default config
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("current_theme", config)
        
        # Test theme manager
        theme_manager = ThemeManager()
        self.assertIsNotNone(theme_manager.current_colors)
        
        # Test getting theme colors for known themes
        theme_names = ['dracula', 'monokai', 'spring', 'forest']
        for theme_name in theme_names:
            theme_colors = get_theme_colors(theme_name)
            self.assertIsInstance(theme_colors, dict)
            self.assertIn("bg_primary", theme_colors)
            self.assertIn("text_primary", theme_colors)

    # ===== CORE INTERPRETER TESTS =====
    
    def test_interpreter_initialization(self):
        """Test core interpreter initialization"""
        import JAMES
        
        interp = JAMES.JAMESInterpreter()
        
        # Test that interpreter has required attributes
        self.assertTrue(hasattr(interp, 'variables'))
        self.assertTrue(hasattr(interp, 'labels'))
        self.assertTrue(hasattr(interp, 'turtle_graphics'))
        self.assertTrue(hasattr(interp, 'log_output'))
        
        # Test that language executors are available
        self.assertTrue(hasattr(interp, 'pilot_executor'))
        self.assertTrue(hasattr(interp, 'basic_executor'))
        self.assertTrue(hasattr(interp, 'logo_executor'))

    # ===== PLUGIN SYSTEM TESTS =====
    
    def test_plugin_system(self):
        """Test plugin system functionality"""
        try:
            from plugins import PluginManager
            import JAMES
            
            # Create main app instance for plugin manager
            app = JAMES.JAMESII()
            plugin_manager = PluginManager(app)
            
            # Test plugin scanning
            plugins = plugin_manager.scan_plugins()
            self.assertIsInstance(plugins, list)
            
            # Test available plugins listing
            available_plugins = plugin_manager.list_available_plugins()
            self.assertIsInstance(available_plugins, list)
            
            # Test loaded plugins listing
            loaded_plugins = plugin_manager.list_loaded_plugins()
            self.assertIsInstance(loaded_plugins, list)
                
        except ImportError:
            self.skipTest("Plugin system not available")

def run_comprehensive_tests():
    """Run all comprehensive tests and generate report"""
    print("🧪 Running JAMES IDE Comprehensive Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(JAMESTestSuite)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n{len(result.failures)} FAILED TESTS:")
        print("-" * 40)
        for test, traceback in result.failures:
            print(f"❌ {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\n{len(result.errors)} ERROR TESTS:")
        print("-" * 40)
        for test, traceback in result.errors:
            error_msg = traceback.split('\\n')[-2] if '\\n' in traceback else traceback
            print(f"💥 {test}: {error_msg}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! JAMES IDE is working well!")
    elif success_rate >= 75:
        print("✅ Good! Most functionality is working.")
    elif success_rate >= 50:
        print("⚠️  Fair. Some issues need attention.")
    else:
        print("❌ Poor. Significant issues need fixing.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)