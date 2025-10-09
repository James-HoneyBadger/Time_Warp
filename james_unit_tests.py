#!/usr/bin/env python3
"""
JAMES Comprehensive Unit Testing Framework
==========================================

This framework provides systematic testing for all JAMES commands and functionality.
Each test is designed to verify specific behavior and edge cases.
"""

import sys
import os
import tempfile
import shutil
import time
from datetime import datetime

# Add JAMES to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import JAMES

class JAMESTestFramework:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.temp_dir = None
        
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix='james_test_')
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            os.chdir('..')
            shutil.rmtree(self.temp_dir)
            
    def run_test(self, test_name, program_code, expected_vars=None, expected_output=None, should_fail=False):
        """Run a single test and verify results"""
        self.total_tests += 1
        
        try:
            # Create fresh interpreter for each test
            interp = JAMES.JAMESInterpreter()
            
            # Capture output
            original_log_output = interp.log_output
            captured_output = []
            
            def capture_output(text):
                captured_output.append(str(text))
                
            interp.log_output = capture_output
            
            # Run the program
            success = interp.run_program(program_code)
            
            # Restore original log function
            interp.log_output = original_log_output
            
            # Check if test should fail
            if should_fail:
                if success:
                    self.record_test_result(test_name, False, "Test was expected to fail but succeeded")
                    return
                else:
                    self.record_test_result(test_name, True, "Test correctly failed as expected")
                    return
            
            # Check success
            if not success:
                self.record_test_result(test_name, False, "Program execution failed")
                return
            
            # Check expected variables
            if expected_vars:
                for var_name, expected_value in expected_vars.items():
                    actual_value = interp.variables.get(var_name.upper())
                    if str(actual_value) != str(expected_value):
                        self.record_test_result(test_name, False, 
                                              f"Variable {var_name}: expected '{expected_value}', got '{actual_value}'")
                        return
            
            # Check expected output
            if expected_output is not None:
                output_text = ''.join(captured_output)
                if expected_output not in output_text:
                    self.record_test_result(test_name, False, 
                                          f"Expected output '{expected_output}' not found in '{output_text}'")
                    return
            
            self.record_test_result(test_name, True, "Test passed")
            
        except Exception as e:
            self.record_test_result(test_name, False, f"Exception: {str(e)}")
    
    def record_test_result(self, test_name, passed, message):
        """Record the result of a test"""
        result = {
            'name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        print(f"{status} | {test_name:50} | {message}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("JAMES COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n{self.failed_tests} FAILED TESTS:")
            print("-"*80)
            for result in self.test_results:
                if not result['passed']:
                    print(f"❌ {result['name']}: {result['message']}")
        
        print("\nTEST CATEGORIES:")
        categories = {}
        for result in self.test_results:
            category = result['name'].split('_')[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if result['passed']:
                categories[category]['passed'] += 1
        
        for category, stats in categories.items():
            rate = stats['passed'] / stats['total'] * 100
            print(f"{category:15} | {stats['passed']:3}/{stats['total']:3} | {rate:5.1f}%")

def main():
    print("🧪 JAMES Comprehensive Unit Testing Framework")
    print("="*60)
    
    framework = JAMESTestFramework()
    framework.setUp()
    
    try:
        # Run all test suites
        test_pilot_commands(framework)
        test_file_commands(framework)
        test_string_commands(framework)
        test_datetime_commands(framework)
        test_web_commands(framework)
        test_database_commands(framework)
        test_basic_commands(framework)
        test_logo_commands(framework)
        test_variable_system(framework)
        test_expression_evaluation(framework)
        
    finally:
        framework.tearDown()
        framework.generate_report()

def test_pilot_commands(framework):
    """Test all PILOT commands (T:, A:, Y:, N:, J:, etc.)"""
    print(f"\n{'='*20} TESTING PILOT COMMANDS {'='*20}")
    
    # Test T: command (Text output)
    framework.run_test(
        "PILOT_T_basic_text",
        "T:Hello World\nEND",
        expected_output="Hello World"
    )
    
    framework.run_test(
        "PILOT_T_variable_interpolation",
        "U:NAME=Alice\nT:Hello *NAME*!\nEND",
        expected_output="Hello Alice!"
    )
    
    # Test U: command (Set variable)
    framework.run_test(
        "PILOT_U_set_number",
        "U:COUNT=42\nEND",
        expected_vars={"COUNT": "42"}
    )
    
    framework.run_test(
        "PILOT_U_set_string",
        "U:MESSAGE=Hello World\nEND",
        expected_vars={"MESSAGE": "Hello World"}
    )
    
    framework.run_test(
        "PILOT_U_expression",
        "U:RESULT=10+5\nEND",
        expected_vars={"RESULT": "15"}
    )
    
    # Test Y: and N: commands (Conditions)
    framework.run_test(
        "PILOT_Y_true_condition",
        "U:X=5\nY:*X* > 3\nU:RESULT=YES\nEND",
        expected_vars={"RESULT": "YES"}
    )
    
    framework.run_test(
        "PILOT_N_false_condition", 
        "U:X=5\nN:*X* > 10\nU:RESULT=NO\nEND",
        expected_vars={"RESULT": "NO"}
    )
    
    # Test J: command (Jump)
    framework.run_test(
        "PILOT_J_unconditional_jump",
        "J:SKIP\nU:RESULT=SKIPPED\nL:SKIP\nU:RESULT=JUMPED\nEND",
        expected_vars={"RESULT": "JUMPED"}
    )
    
    framework.run_test(
        "PILOT_J_conditional_jump",
        "U:X=5\nJ(*X*>3):TARGET\nU:RESULT=NO_JUMP\nJ:END\nL:TARGET\nU:RESULT=JUMPED\nEND",
        expected_vars={"RESULT": "JUMPED"}
    )
    
    # Test L: command (Label) - tested implicitly above
    
    # Test M: command (Match)
    framework.run_test(
        "PILOT_M_pattern_match",
        "U:INPUT=YES\nM:YES,OK,SURE\nU:RESULT=MATCHED\nEND",
        expected_vars={"RESULT": "MATCHED"}
    )
    
    # Test C: command (Compute)
    framework.run_test(
        "PILOT_C_calculation",
        "U:A=10\nU:B=5\nC:RESULT=*A*+*B*\nEND",
        expected_vars={"RESULT": "15"}
    )

def test_file_commands(framework):
    """Test all File I/O commands (F:READ, F:WRITE, etc.)"""
    print(f"\n{'='*20} TESTING FILE COMMANDS {'='*20}")
    
    # Test F:WRITE
    framework.run_test(
        "FILE_F_WRITE_basic",
        'F:WRITE "test.txt" "Hello File"\nEND',
        expected_vars={"FILE_WRITE_SUCCESS": "1"}
    )
    
    # Test F:READ
    framework.run_test(
        "FILE_F_READ_basic",
        'F:WRITE "test.txt" "Hello File"\nF:READ "test.txt" CONTENT\nEND',
        expected_vars={"CONTENT": "Hello File", "FILE_READ_SUCCESS": "1"}
    )
    
    # Test F:APPEND
    framework.run_test(
        "FILE_F_APPEND_basic",
        'F:WRITE "test.txt" "Hello"\nF:APPEND "test.txt" " World"\nF:READ "test.txt" CONTENT\nEND',
        expected_vars={"CONTENT": "Hello World"}
    )
    
    # Test F:DELETE
    framework.run_test(
        "FILE_F_DELETE_basic",
        'F:WRITE "test.txt" "Hello"\nF:DELETE "test.txt"\nF:EXISTS "test.txt" EXISTS\nEND',
        expected_vars={"EXISTS": "0"}
    )
    
    # Test F:EXISTS
    framework.run_test(
        "FILE_F_EXISTS_true",
        'F:WRITE "test.txt" "Hello"\nF:EXISTS "test.txt" EXISTS\nEND',
        expected_vars={"EXISTS": "1"}
    )
    
    framework.run_test(
        "FILE_F_EXISTS_false",
        'F:EXISTS "nonexistent.txt" EXISTS\nEND',
        expected_vars={"EXISTS": "0"}
    )
    
    # Test F:SIZE
    framework.run_test(
        "FILE_F_SIZE_basic",
        'F:WRITE "test.txt" "Hello"\nF:SIZE "test.txt" SIZE\nEND',
        expected_vars={"SIZE": "5"}
    )
    
    # Test with spaces in filename
    framework.run_test(
        "FILE_F_spaces_in_name",
        'F:WRITE "test file.txt" "Hello"\nF:READ "test file.txt" CONTENT\nEND',
        expected_vars={"CONTENT": "Hello"}
    )

def test_string_commands(framework):
    """Test all String commands (S:LENGTH, S:UPPER, etc.)"""
    print(f"\n{'='*20} TESTING STRING COMMANDS {'='*20}")
    
    # Test S:LENGTH
    framework.run_test(
        "STRING_S_LENGTH_basic",
        'S:LENGTH "Hello" LEN\nEND',
        expected_vars={"LEN": "5"}
    )
    
    framework.run_test(
        "STRING_S_LENGTH_empty",
        'S:LENGTH "" LEN\nEND',
        expected_vars={"LEN": "0"}
    )
    
    # Test S:UPPER
    framework.run_test(
        "STRING_S_UPPER_basic",
        'S:UPPER "hello" UPPER\nEND',
        expected_vars={"UPPER": "HELLO"}
    )
    
    # Test S:LOWER
    framework.run_test(
        "STRING_S_LOWER_basic",
        'S:LOWER "HELLO" LOWER\nEND',
        expected_vars={"LOWER": "hello"}
    )
    
    # Test S:FIND
    framework.run_test(
        "STRING_S_FIND_found",
        'S:FIND "Hello World" "World" POS\nEND',
        expected_vars={"POS": "6"}
    )
    
    framework.run_test(
        "STRING_S_FIND_not_found",
        'S:FIND "Hello World" "xyz" POS\nEND',
        expected_vars={"POS": "-1"}
    )
    
    # Test S:REPLACE
    framework.run_test(
        "STRING_S_REPLACE_basic",
        'S:REPLACE "Hello World" "World" "Universe" RESULT\nEND',
        expected_vars={"RESULT": "Hello Universe"}
    )
    
    framework.run_test(
        "STRING_S_REPLACE_empty_search",
        'S:REPLACE "Hello" "" "X" RESULT\nEND',
        expected_vars={"RESULT": "Hello"}  # Should not replace anything
    )
    
    # Test S:SUBSTRING
    framework.run_test(
        "STRING_S_SUBSTRING_basic",
        'S:SUBSTRING "Hello World" 0 5 RESULT\nEND',
        expected_vars={"RESULT": "Hello"}
    )
    
    # Test S:SPLIT
    framework.run_test(
        "STRING_S_SPLIT_basic",
        'S:SPLIT "A,B,C" "," RESULT\nEND',
        expected_vars={"RESULT": "A"}  # First part
    )

def test_datetime_commands(framework):
    """Test all DateTime commands (DT:NOW, DT:PARSE, etc.)"""
    print(f"\n{'='*20} TESTING DATETIME COMMANDS {'='*20}")
    
    # Test DT:NOW
    framework.run_test(
        "DATETIME_DT_NOW_basic",
        'DT:NOW "YYYY-MM-DD" TODAY\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    # Test DT:TIMESTAMP
    framework.run_test(
        "DATETIME_DT_TIMESTAMP_basic",
        'DT:TIMESTAMP TIMESTAMP\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    # Test DT:PARSE
    framework.run_test(
        "DATETIME_DT_PARSE_basic",
        'DT:PARSE "2023-01-01" "YYYY-MM-DD" PARSED\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    # Test DT:FORMAT
    framework.run_test(
        "DATETIME_DT_FORMAT_basic",
        'DT:TIMESTAMP TS\nDT:FORMAT "*TS*" "YYYY-MM-DD" FORMATTED\nEND',
        expected_vars={}  # Just check it doesn't crash
    )

def test_web_commands(framework):
    """Test all Web commands (W:ENCODE, W:DECODE, etc.)"""
    print(f"\n{'='*20} TESTING WEB COMMANDS {'='*20}")
    
    # Test W:ENCODE
    framework.run_test(
        "WEB_W_ENCODE_basic",
        'W:ENCODE "Hello World" ENCODED\nEND',
        expected_vars={"ENCODED": "Hello%20World"}
    )
    
    # Test W:DECODE
    framework.run_test(
        "WEB_W_DECODE_basic",
        'W:DECODE "Hello%20World" DECODED\nEND',
        expected_vars={"DECODED": "Hello World"}
    )
    
    # Test round-trip encoding/decoding
    framework.run_test(
        "WEB_W_ROUNDTRIP",
        'W:ENCODE "Special: !@#$" ENCODED\nW:DECODE "*ENCODED*" DECODED\nEND',
        expected_vars={"DECODED": "Special: !@#$"}
    )

def test_database_commands(framework):
    """Test all Database commands (D:OPEN, D:QUERY, etc.)"""
    print(f"\n{'='*20} TESTING DATABASE COMMANDS {'='*20}")
    
    # Test D:OPEN
    framework.run_test(
        "DATABASE_D_OPEN_basic",
        'D:OPEN "test.db"\nEND',
        expected_vars={"DB_OPEN_SUCCESS": "1"}
    )
    
    # Test D:QUERY (CREATE TABLE)
    framework.run_test(
        "DATABASE_D_QUERY_create_table",
        'D:OPEN "test.db"\nD:QUERY "CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)"\nEND',
        expected_vars={"DB_QUERY_SUCCESS": "1"}
    )
    
    # Test D:INSERT
    framework.run_test(
        "DATABASE_D_INSERT_basic",
        '''D:OPEN "test.db"
D:QUERY "CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)"
D:INSERT "test" "id,name" "1,'Alice'"
END''',
        expected_vars={"DB_INSERT_SUCCESS": "1"}
    )
    
    # Test D:QUERY (SELECT)
    framework.run_test(
        "DATABASE_D_QUERY_select",
        '''D:OPEN "test.db"
D:QUERY "CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)"
D:INSERT "test" "id,name" "1,'Alice'"
D:QUERY "SELECT COUNT(*) FROM test" RESULT
END''',
        expected_vars={"DB_QUERY_SUCCESS": "1"}
    )

def test_basic_commands(framework):
    """Test all BASIC commands (LET, PRINT, IF, etc.)"""
    print(f"\n{'='*20} TESTING BASIC COMMANDS {'='*20}")
    
    # Test LET
    framework.run_test(
        "BASIC_LET_number",
        'LET X = 42\nEND',
        expected_vars={"X": "42"}
    )
    
    framework.run_test(
        "BASIC_LET_expression",
        'LET X = 10 + 5\nEND',
        expected_vars={"X": "15"}
    )
    
    # Test PRINT
    framework.run_test(
        "BASIC_PRINT_text",
        'PRINT "Hello World"\nEND',
        expected_output="Hello World"
    )
    
    framework.run_test(
        "BASIC_PRINT_variable",
        'LET X = 42\nPRINT "X is "; X\nEND',
        expected_output="X is 42"
    )
    
    framework.run_test(
        "BASIC_PRINT_expression",
        'PRINT "Result: "; 10 + 5\nEND',
        expected_output="Result: 15"
    )
    
    # Test IF THEN
    framework.run_test(
        "BASIC_IF_true",
        'LET X = 5\nIF X > 3 THEN LET Y = 1\nEND',
        expected_vars={"Y": "1"}
    )
    
    framework.run_test(
        "BASIC_IF_false",
        'LET X = 2\nLET Y = 0\nIF X > 3 THEN LET Y = 1\nEND',
        expected_vars={"Y": "0"}
    )

def test_logo_commands(framework):
    """Test all Logo commands (FORWARD, REPEAT, etc.)"""
    print(f"\n{'='*20} TESTING LOGO COMMANDS {'='*20}")
    
    # Test basic turtle commands
    framework.run_test(
        "LOGO_FORWARD_basic",
        'FORWARD 100\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    framework.run_test(
        "LOGO_RIGHT_basic",
        'RIGHT 90\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    framework.run_test(
        "LOGO_LEFT_basic",
        'LEFT 45\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    # Test REPEAT
    framework.run_test(
        "LOGO_REPEAT_basic",
        'LET COUNT = 0\nREPEAT 3 [LET COUNT = COUNT + 1]\nEND',
        expected_vars={"COUNT": "3"}
    )
    
    # Test HOME
    framework.run_test(
        "LOGO_HOME_basic",
        'FORWARD 100\nHOME\nEND',
        expected_vars={}  # Just check it doesn't crash
    )
    
    # Test CLEARSCREEN
    framework.run_test(
        "LOGO_CLEARSCREEN_basic",
        'CLEARSCREEN\nEND',
        expected_vars={}  # Just check it doesn't crash
    )

def test_variable_system(framework):
    """Test variable resolution, interpolation, and scoping"""
    print(f"\n{'='*20} TESTING VARIABLE SYSTEM {'='*20}")
    
    # Test basic variable setting and getting
    framework.run_test(
        "VARIABLE_basic_set_get",
        'U:TEST=Hello\nT:*TEST*\nEND',
        expected_vars={"TEST": "Hello"},
        expected_output="Hello"
    )
    
    # Test variable interpolation in text
    framework.run_test(
        "VARIABLE_interpolation",
        'U:NAME=World\nU:GREETING=Hello *NAME*\nT:*GREETING*\nEND',
        expected_vars={"GREETING": "Hello World"},
        expected_output="Hello World"
    )
    
    # Test undefined variables
    framework.run_test(
        "VARIABLE_undefined",
        'T:*UNDEFINED*\nEND',
        expected_output="*UNDEFINED*"
    )
    
    # Test empty variables
    framework.run_test(
        "VARIABLE_empty",
        'U:EMPTY=\nT:Value: *EMPTY*\nEND',
        expected_vars={"EMPTY": ""},
        expected_output="Value: "
    )
    
    # Test numeric variables
    framework.run_test(
        "VARIABLE_numeric",
        'U:NUM=42\nU:CALC=*NUM*+8\nEND',
        expected_vars={"NUM": "42", "CALC": "50"}
    )

def test_expression_evaluation(framework):
    """Test mathematical expressions and function calls"""
    print(f"\n{'='*20} TESTING EXPRESSION EVALUATION {'='*20}")
    
    # Test basic arithmetic
    framework.run_test(
        "EXPRESSION_addition",
        'U:RESULT=10+5\nEND',
        expected_vars={"RESULT": "15"}
    )
    
    framework.run_test(
        "EXPRESSION_subtraction",
        'U:RESULT=10-3\nEND',
        expected_vars={"RESULT": "7"}
    )
    
    framework.run_test(
        "EXPRESSION_multiplication",
        'U:RESULT=6*7\nEND',
        expected_vars={"RESULT": "42"}
    )
    
    framework.run_test(
        "EXPRESSION_division",
        'U:RESULT=20/4\nEND',
        expected_vars={"RESULT": "5"}
    )
    
    # Test complex expressions
    framework.run_test(
        "EXPRESSION_complex",
        'U:RESULT=(10+5)*2-3\nEND',
        expected_vars={"RESULT": "27"}
    )
    
    # Test with variables
    framework.run_test(
        "EXPRESSION_with_variables",
        'U:A=10\nU:B=5\nU:RESULT=*A*+*B**2\nEND',
        expected_vars={"RESULT": "35"}
    )
    
    # Test division by zero (should handle gracefully)
    framework.run_test(
        "EXPRESSION_division_by_zero",
        'U:RESULT=10/0\nEND',
        expected_vars={"RESULT": "ERROR: Division by zero"}
    )
    
    # Test string concatenation
    framework.run_test(
        "EXPRESSION_string_concat",
        'PRINT "Hello" + " " + "World"\nEND',
        expected_output="Hello World"
    )

if __name__ == "__main__":
    main()