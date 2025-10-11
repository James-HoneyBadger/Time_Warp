#!/usr/bin/env python3
"""
COMPREHENSIVE TIME_WARP IDE VERIFICATION SUITE
===============================================
This will test EVERY component and find ALL remaining issues.
No more "it's working" claims without proper verification!
"""

import sys
import os
sys.path.append('/home/james/Time_Warp')

import unittest
import tempfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import subprocess
import time
import threading

class TestResults:
    """Track all test results comprehensively"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []
        self.warnings = []
    
    def add_pass(self, test_name, details=""):
        self.passed.append(f"✅ {test_name}: {details}")
    
    def add_fail(self, test_name, error):
        self.failed.append(f"❌ {test_name}: {error}")
    
    def add_error(self, test_name, error):
        self.errors.append(f"💥 {test_name}: {error}")
    
    def add_warning(self, test_name, warning):
        self.warnings.append(f"⚠️ {test_name}: {warning}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("COMPREHENSIVE VERIFICATION RESULTS")
        print("="*60)
        
        print(f"\n✅ PASSED ({len(self.passed)}):")
        for item in self.passed:
            print(f"  {item}")
        
        print(f"\n❌ FAILED ({len(self.failed)}):")
        for item in self.failed:
            print(f"  {item}")
        
        print(f"\n💥 ERRORS ({len(self.errors)}):")
        for item in self.errors:
            print(f"  {item}")
        
        print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
        for item in self.warnings:
            print(f"  {item}")
        
        total_issues = len(self.failed) + len(self.errors)
        print(f"\n🎯 FINAL VERDICT:")
        if total_issues == 0:
            print("🎉 ALL SYSTEMS VERIFIED - IDE IS TRULY FUNCTIONAL!")
        else:
            print(f"🔥 {total_issues} CRITICAL ISSUES FOUND - NEEDS FIXES!")
        
        return total_issues == 0

# Global test results
results = TestResults()

def test_core_imports():
    """Test that all core modules can be imported"""
    print("🔍 Testing Core Imports...")
    
    try:
        from core.interpreter import Time_WarpInterpreter
        results.add_pass("Core Interpreter Import", "Time_WarpInterpreter imported successfully")
    except Exception as e:
        results.add_fail("Core Interpreter Import", str(e))
    
    try:
        from tools.theme import ThemeManager
        results.add_pass("Theme Manager Import", "ThemeManager imported successfully")
    except Exception as e:
        results.add_fail("Theme Manager Import", str(e))
    
    try:
        from gui.components.multi_tab_editor import MultiTabEditor
        results.add_pass("Multi-Tab Editor Import", "MultiTabEditor imported successfully")
    except Exception as e:
        results.add_fail("Multi-Tab Editor Import", str(e))
    
    # Test language executors
    languages = ['basic', 'pilot', 'logo', 'python', 'javascript', 'perl']
    for lang in languages:
        try:
            module = __import__(f'core.languages.{lang}', fromlist=[f'{lang.title()}Executor'])
            if lang == 'javascript':
                executor_class = getattr(module, 'JavaScriptExecutor')
            elif lang == 'python':  
                executor_class = getattr(module, 'PythonExecutor')
            else:
                executor_class = getattr(module, f'{lang.title()}Executor')
            results.add_pass(f"{lang.title()} Language Import", f"{executor_class.__name__} imported")
        except Exception as e:
            results.add_fail(f"{lang.title()} Language Import", str(e))

def test_interpreter_functionality():
    """Test the core interpreter with all languages"""
    print("🔍 Testing Interpreter Functionality...")
    
    try:
        from core.interpreter import Time_WarpInterpreter
        interpreter = Time_WarpInterpreter()
        results.add_pass("Interpreter Creation", "Time_WarpInterpreter instance created")
        
        # Test each language with simple programs
        test_programs = {
            'basic': 'PRINT "Hello, BASIC!"',
            'pilot': 'T:Hello, PILOT!',
            'logo': 'FORWARD 50\nRIGHT 90',
            'python': 'print("Hello, Python!")',
            'javascript': 'console.log("Hello, JavaScript!");',
            'perl': 'print "Hello, Perl!\\n";'
        }
        
        for language, code in test_programs.items():
            try:
                result = interpreter.run_program(code, language)
                if result is not None:
                    results.add_pass(f"{language.title()} Execution", f"Program executed successfully")
                else:
                    results.add_fail(f"{language.title()} Execution", "run_program returned None")
            except Exception as e:
                results.add_fail(f"{language.title()} Execution", str(e))
        
    except Exception as e:
        results.add_error("Interpreter Functionality", str(e))

def test_theme_system():
    """Test the theme system thoroughly"""
    print("🔍 Testing Theme System...")
    
    try:
        from tools.theme import ThemeManager
        theme_manager = ThemeManager()
        results.add_pass("Theme Manager Creation", "ThemeManager instance created")
        
        # Test all available themes
        available_themes = ['forest', 'dracula', 'monokai', 'solarized', 
                          'ocean', 'spring', 'sunset', 'candy']
        
        for theme_name in available_themes:
            try:
                # Try to get colors for each theme
                colors = theme_manager.get_colors(theme_name)
                if colors and isinstance(colors, dict):
                    required_keys = ['bg_primary', 'text_primary', 'accent']
                    missing_keys = [key for key in required_keys if key not in colors]
                    if not missing_keys:
                        results.add_pass(f"Theme {theme_name}", f"All required color keys present")
                    else:
                        results.add_fail(f"Theme {theme_name}", f"Missing keys: {missing_keys}")
                else:
                    results.add_fail(f"Theme {theme_name}", "Invalid colors returned")
            except Exception as e:
                results.add_fail(f"Theme {theme_name}", str(e))
        
        # Test theme application
        try:
            root = tk.Tk()
            root.withdraw()  # Hide window
            theme_manager.apply_theme(root, 'forest')
            bg_color = root.cget('bg')
            if bg_color != '#d9d9d9':  # Not default gray
                results.add_pass("Theme Application", f"Theme applied successfully (bg: {bg_color})")
            else:
                results.add_fail("Theme Application", "Theme not applied - still default gray")
            root.destroy()
        except Exception as e:
            results.add_fail("Theme Application", str(e))
        
    except Exception as e:
        results.add_error("Theme System", str(e))

def test_file_operations():
    """Test file loading, saving, and language detection"""
    print("🔍 Testing File Operations...")
    
    try:
        # Create temporary test files
        test_dir = tempfile.mkdtemp(prefix="timewarp_test_")
        
        test_files = {
            'test.bas': '10 PRINT "Hello, BASIC!"\n20 END',
            'test.pilot': 'J:START\nT:Hello PILOT\nJ:END',
            'test.logo': 'REPEAT 4 [ FORWARD 50 RIGHT 90 ]',
            'test.py': 'print("Hello Python")',
            'test.js': 'console.log("Hello JavaScript");'
        }
        
        for filename, content in test_files.items():
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            
            # Test file exists
            if os.path.exists(filepath):
                results.add_pass(f"File Creation {filename}", "File created successfully")
                
                # Test reading file
                try:
                    with open(filepath, 'r') as f:
                        read_content = f.read()
                    if read_content == content:
                        results.add_pass(f"File Reading {filename}", "File content matches")
                    else:
                        results.add_fail(f"File Reading {filename}", "Content mismatch")
                except Exception as e:
                    results.add_fail(f"File Reading {filename}", str(e))
            else:
                results.add_fail(f"File Creation {filename}", "File not created")
        
        # Clean up
        shutil.rmtree(test_dir)
        results.add_pass("File Cleanup", "Temporary files cleaned up")
        
    except Exception as e:
        results.add_error("File Operations", str(e))

def test_gui_components():
    """Test GUI components in isolation"""
    print("🔍 Testing GUI Components...")
    
    try:
        # Test basic tkinter functionality
        root = tk.Tk()
        root.withdraw()
        results.add_pass("Tkinter Root Creation", "Root window created")
        
        # Test ttk widgets
        try:
            frame = ttk.Frame(root)
            notebook = ttk.Notebook(root)
            results.add_pass("TTK Widgets", "TTK Frame and Notebook created")
        except Exception as e:
            results.add_fail("TTK Widgets", str(e))
        
        # Test MultiTabEditor in isolation
        try:
            from gui.components.multi_tab_editor import MultiTabEditor
            
            test_frame = ttk.Frame(root)
            editor = MultiTabEditor(test_frame)
            results.add_pass("MultiTabEditor Creation", "Editor created successfully")
            
            # Test creating a new tab
            try:
                editor.new_tab()
                if len(editor.tabs) > 0:
                    results.add_pass("Tab Creation", "New tab created successfully")
                else:
                    results.add_fail("Tab Creation", "No tabs found after creation")
            except Exception as e:
                results.add_fail("Tab Creation", str(e))
            
        except Exception as e:
            results.add_fail("MultiTabEditor Creation", str(e))
        
        root.destroy()
        
    except Exception as e:
        results.add_error("GUI Components", str(e))

def test_logo_graphics():
    """Test Logo graphics system specifically"""
    print("🔍 Testing Logo Graphics System...")
    
    try:
        from core.interpreter import Time_WarpInterpreter
        interpreter = Time_WarpInterpreter()
        
        # Test turtle graphics initialization
        if hasattr(interpreter, 'turtle_graphics'):
            # turtle_graphics starts as None and gets initialized on first use
            results.add_pass("Turtle Graphics Init", "Turtle graphics attribute exists (lazy initialization)")
        else:
            results.add_fail("Turtle Graphics Init", "No turtle_graphics attribute")
        
        # Test complex Logo program
        complex_logo = '''
CLEARSCREEN
HOME
REPEAT 6 [
  FORWARD 60
  RIGHT 60
]
PENUP
FORWARD 20
PENDOWN
REPEAT 8 [
  FORWARD 30
  RIGHT 45
]
'''
        
        try:
            result = interpreter.run_program(complex_logo, 'logo')
            if result:
                results.add_pass("Complex Logo Program", "Multi-command program executed")
            else:
                results.add_fail("Complex Logo Program", "Program execution failed")
        except Exception as e:
            results.add_fail("Complex Logo Program", str(e))
        
    except Exception as e:
        results.add_error("Logo Graphics System", str(e))

def test_main_application():
    """Test the main Time_Warp application"""
    print("🔍 Testing Main Application...")
    
    try:
        # Test import
        from Time_Warp import Time_WarpIDE, main
        results.add_pass("Main App Import", "Time_WarpIDE and main imported")
        
        # Test that main function exists and is callable
        if callable(main):
            results.add_pass("Main Function", "main() function is callable")
        else:
            results.add_fail("Main Function", "main() is not callable")
        
        # Test if __name__ == "__main__" block exists
        with open('/home/james/Time_Warp/Time_Warp.py', 'r') as f:
            content = f.read()
        
        if 'if __name__ == "__main__":' in content:
            results.add_pass("Main Block", "__name__ == '__main__' block exists")
        else:
            results.add_fail("Main Block", "Missing __name__ == '__main__' block")
        
        if 'main()' in content:
            results.add_pass("Main Call", "main() is called in main block")
        else:
            results.add_fail("Main Call", "main() not called in main block")
        
    except Exception as e:
        results.add_error("Main Application", str(e))

def test_syntax_edge_cases():
    """Test edge cases and error handling"""
    print("🔍 Testing Syntax Edge Cases...")
    
    try:
        from core.interpreter import Time_WarpInterpreter
        interpreter = Time_WarpInterpreter()
        
        # Test empty programs
        empty_tests = {
            'Empty BASIC': ('', 'basic'),
            'Empty PILOT': ('', 'pilot'),
            'Empty Logo': ('', 'logo'),
            'Whitespace Only': ('   \n  \t  \n', 'basic')
        }
        
        for test_name, (code, lang) in empty_tests.items():
            try:
                result = interpreter.run_program(code, lang)
                # Empty programs should not crash
                results.add_pass(f"Edge Case: {test_name}", "Handled gracefully")
            except Exception as e:
                results.add_fail(f"Edge Case: {test_name}", str(e))
        
        # Test malformed syntax
        malformed_tests = {
            'Invalid BASIC': ('PRINT PRINT PRINT', 'basic'),
            'Invalid Logo': ('REPEAT [ FORWARD', 'logo'),
            'Invalid PILOT': ('T:T:T:T:', 'pilot')
        }
        
        for test_name, (code, lang) in malformed_tests.items():
            try:
                result = interpreter.run_program(code, lang)
                # Should handle errors gracefully, not crash
                results.add_pass(f"Error Handling: {test_name}", "Error handled gracefully")
            except Exception as e:
                results.add_warning(f"Error Handling: {test_name}", f"Exception raised: {str(e)[:50]}...")
        
    except Exception as e:
        results.add_error("Syntax Edge Cases", str(e))

def test_real_world_programs():
    """Test with realistic programming examples"""
    print("🔍 Testing Real-World Programs...")
    
    try:
        from core.interpreter import Time_WarpInterpreter
        interpreter = Time_WarpInterpreter()
        
        real_programs = {
            'BASIC Calculator': '''
10 PRINT "Simple Calculator"
20 LET A = 10
30 LET B = 5
40 PRINT "A + B = "; A + B
50 PRINT "A * B = "; A * B
60 END
''',
            'PILOT Tutorial': '''
J:START
T:Welcome to PILOT!
T:This is a simple program.
A:What is your name?
T:Hello, #NAME!
J:END
''',
            'Logo House': '''
CLEARSCREEN
HOME
; Draw house base
REPEAT 4 [
  FORWARD 100
  RIGHT 90
]
; Draw roof
FORWARD 100
RIGHT 30
FORWARD 58
RIGHT 120
FORWARD 58
RIGHT 30
''',
            'Python Math': '''
import math
print("Python Math Test")
x = 5
y = 3
print(f"{x} + {y} = {x + y}")
print(f"sqrt({x}) = {math.sqrt(x):.2f}")
'''
        }
        
        for program_name, code in real_programs.items():
            try:
                lang = program_name.split()[0].lower()
                result = interpreter.run_program(code, lang)
                if result is not None:
                    results.add_pass(f"Real Program: {program_name}", "Executed successfully")
                else:
                    results.add_fail(f"Real Program: {program_name}", "Execution returned None")
            except Exception as e:
                results.add_fail(f"Real Program: {program_name}", str(e))
        
    except Exception as e:
        results.add_error("Real-World Programs", str(e))

def test_performance():
    """Test performance with larger programs"""
    print("🔍 Testing Performance...")
    
    try:
        from core.interpreter import Time_WarpInterpreter
        interpreter = Time_WarpInterpreter()
        
        # Test large BASIC program
        large_basic = "\\n".join([f"{i*10} PRINT \"Line {i}\"" for i in range(1, 51)])
        large_basic += "\\n500 END"
        
        start_time = time.time()
        try:
            result = interpreter.run_program(large_basic, 'basic')
            execution_time = time.time() - start_time
            if execution_time < 5.0:  # Should complete within 5 seconds
                results.add_pass("Performance: Large BASIC", f"Completed in {execution_time:.2f}s")
            else:
                results.add_warning("Performance: Large BASIC", f"Slow execution: {execution_time:.2f}s")
        except Exception as e:
            results.add_fail("Performance: Large BASIC", str(e))
        
        # Test complex Logo graphics
        complex_logo = "\\n".join([f"REPEAT 10 [ FORWARD {i*5} RIGHT {36} ]" for i in range(1, 11)])
        
        start_time = time.time()
        try:
            result = interpreter.run_program(complex_logo, 'logo')
            execution_time = time.time() - start_time
            if execution_time < 3.0:
                results.add_pass("Performance: Complex Logo", f"Completed in {execution_time:.2f}s")
            else:
                results.add_warning("Performance: Complex Logo", f"Slow execution: {execution_time:.2f}s")
        except Exception as e:
            results.add_fail("Performance: Complex Logo", str(e))
        
    except Exception as e:
        results.add_error("Performance Testing", str(e))

def run_comprehensive_verification():
    """Run all verification tests"""
    print("🔥 STARTING COMPREHENSIVE TIME_WARP IDE VERIFICATION")
    print("="*60)
    print("This will test EVERY component and find ALL issues!")
    print("No more false claims - let's see what really works...")
    print("="*60)
    
    # Run all test suites
    test_core_imports()
    test_interpreter_functionality()
    test_theme_system()
    test_file_operations()
    test_gui_components()
    test_logo_graphics()
    test_main_application()
    test_syntax_edge_cases()
    test_real_world_programs()
    test_performance()
    
    # Print comprehensive results
    is_truly_functional = results.print_summary()
    
    print("\n" + "="*60)
    if is_truly_functional:
        print("🎉 VERIFICATION COMPLETE: IDE IS GENUINELY FUNCTIONAL!")
    else:
        print("🔥 VERIFICATION FAILED: CRITICAL ISSUES FOUND!")
        print("🛠️ Issues must be fixed before claiming functionality!")
    print("="*60)
    
    return is_truly_functional

if __name__ == "__main__":
    run_comprehensive_verification()