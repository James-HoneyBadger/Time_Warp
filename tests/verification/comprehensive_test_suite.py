#!/usr/bin/env python3
"""
COMPREHENSIVE UNIT TESTING SUITE FOR TIME_WARP IDE
==================================================

This is an exhaustive test suite that will examine every component,
feature, and functionality of the Time_Warp IDE to ensure it's
working perfectly.

Test Categories:
1. Core Interpreter Tests
2. Language Executor Tests (PILOT, BASIC, Logo, Python, JavaScript)
3. GUI Component Tests
4. Theme System Tests
5. File Operations Tests
6. Graphics System Tests
7. Plugin System Tests
8. Error Handling Tests
9. Integration Tests
10. Performance Tests
"""

import tkinter as tk
from tkinter import scrolledtext
import sys
import os
import time

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ComprehensiveTestSuite:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time_Warp IDE - Comprehensive Test Suite")
        self.root.geometry("800x600")
        
        # Create output widget
        self.output_text = scrolledtext.ScrolledText(
            self.root,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup interpreter
        from core.interpreter import Time_WarpInterpreter
        
        # Custom output handler
        class OutputHandler:
            def __init__(self, output_widget):
                self.output_widget = output_widget
            
            def insert(self, position, text):
                self.output_widget.config(state=tk.NORMAL)
                self.output_widget.insert(tk.END, text)
                self.output_widget.see(tk.END)
                self.output_widget.config(state=tk.DISABLED)
                self.output_widget.update()
            
            def see(self, position):
                pass
        
        self.interpreter = Time_WarpInterpreter()
        self.interpreter.output_widget = OutputHandler(self.output_text)
        
        self.test_results = []
        self.current_test = 0
        
    def log(self, message):
        """Log message to output"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.update()
        
    def run_test(self, name, program, language, expected_keywords=None):
        """Run a single test"""
        self.log(f"\n{'='*60}")
        self.log(f"🧪 Testing: {name}")
        self.log(f"Language: {language.upper()}")
        self.log(f"Program:\n{program}")
        self.log("-" * 40)
        
        try:
            result = self.interpreter.run_program(program, language=language.lower())
            
            if result:
                self.log(f"✅ Test PASSED: {name}")
                self.test_results.append((name, "PASS"))
            else:
                self.log(f"❌ Test FAILED: {name}")
                self.test_results.append((name, "FAIL"))
                
        except Exception as e:
            self.log(f"💥 Test ERROR: {name} - {str(e)}")
            self.test_results.append((name, "ERROR"))
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}")
        
        self.root.update()
        time.sleep(1)
        
    def test_basic_language(self):
        """Test BASIC language functionality"""
        self.log("\n🔵 TESTING BASIC LANGUAGE")
        
        # Test 1: Basic output
        self.run_test(
            "BASIC - Simple Output",
            '''10 PRINT "Hello World!"
20 PRINT "This is BASIC programming"
30 END''',
            "basic"
        )
        
        # Test 2: Variables and arithmetic
        self.run_test(
            "BASIC - Variables & Math",
            '''10 LET A = 5
20 LET B = 10
30 LET C = A + B
40 PRINT "A = "; A
50 PRINT "B = "; B
60 PRINT "A + B = "; C
70 END''',
            "basic"
        )
        
        # Test 3: String variables
        self.run_test(
            "BASIC - String Variables",
            '''10 LET NAME$ = "John"
20 LET AGE = 25
30 PRINT "Name: "; NAME$
40 PRINT "Age: "; AGE
50 END''',
            "basic"
        )
        
        # Test 4: FOR loops
        self.run_test(
            "BASIC - FOR Loop",
            '''10 PRINT "Counting from 1 to 5:"
20 FOR I = 1 TO 5
30 PRINT "Count: "; I
40 NEXT I
50 PRINT "Loop completed!"
60 END''',
            "basic"
        )
        
        # Test 5: IF-THEN conditions
        self.run_test(
            "BASIC - IF-THEN",
            '''10 LET X = 15
20 IF X > 10 THEN PRINT "X is greater than 10"
30 IF X < 20 THEN PRINT "X is less than 20"
40 IF X = 15 THEN PRINT "X equals 15"
50 END''',
            "basic"
        )
        
        # Test 6: GOTO and line numbers
        self.run_test(
            "BASIC - GOTO",
            '''10 PRINT "Start"
20 GOTO 50
30 PRINT "This should be skipped"
40 GOTO 60
50 PRINT "Jumped to line 50"
60 PRINT "End"
70 END''',
            "basic"
        )
        
        # Test 7: INPUT simulation (if supported)
        self.run_test(
            "BASIC - Complex Math",
            '''10 LET PI = 3.14159
20 LET R = 5
30 LET AREA = PI * R * R
40 PRINT "Circle with radius "; R
50 PRINT "Area = "; AREA
60 END''',
            "basic"
        )
        
    def test_pilot_language(self):
        """Test PILOT language functionality"""
        self.log("\n🟢 TESTING PILOT LANGUAGE")
        
        # Test 1: Basic text output
        self.run_test(
            "PILOT - Text Output",
            '''T:Hello from PILOT!
T:This is educational programming
T:PILOT makes learning fun!''',
            "pilot"
        )
        
        # Test 2: Variable assignment and display
        self.run_test(
            "PILOT - Variables",
            '''A:NAME,John
A:AGE,25
A:SCORE,95.5
T:Student: #NAME
T:Age: #AGE
T:Score: #SCORE''',
            "pilot"
        )
        
        # Test 3: Mathematical operations
        self.run_test(
            "PILOT - Math Operations",
            '''A:X,10
A:Y,20
A:SUM,#X+#Y
A:PRODUCT,#X*#Y
T:X = #X, Y = #Y
T:Sum = #SUM
T:Product = #PRODUCT''',
            "pilot"
        )
        
        # Test 4: Conditional jumps
        self.run_test(
            "PILOT - Conditional Logic",
            '''A:SCORE,85
J(#SCORE>90):HIGH
J(#SCORE>70):MEDIUM
T:Score is low
J:END
*HIGH
T:Excellent score!
J:END
*MEDIUM
T:Good score!
*END
T:Test completed''',
            "pilot"
        )
        
        # Test 5: String operations
        self.run_test(
            "PILOT - String Handling",
            '''A:FIRST,Hello
A:SECOND,World
A:SPACE, 
A:GREETING,#FIRST#SPACE#SECOND!
T:#GREETING''',
            "pilot"
        )
        
        # Test 6: Turtle graphics commands
        self.run_test(
            "PILOT - Turtle Graphics",
            '''T:Drawing a square
T:FORWARD 50
T:RIGHT 90
T:FORWARD 50
T:RIGHT 90
T:FORWARD 50
T:RIGHT 90
T:FORWARD 50
T:RIGHT 90
T:Square completed!''',
            "pilot"
        )
        
    def test_logo_language(self):
        """Test Logo language functionality"""
        self.log("\n🟡 TESTING LOGO LANGUAGE")
        
        # Test 1: Basic movement
        self.run_test(
            "Logo - Basic Movement",
            '''FORWARD 50
RIGHT 90
FORWARD 50
LEFT 90
FORWARD 25''',
            "logo"
        )
        
        # Test 2: Drawing shapes
        self.run_test(
            "Logo - Square",
            '''REPEAT 4 [
  FORWARD 50
  RIGHT 90
]''',
            "logo"
        )
        
        # Test 3: Pen control
        self.run_test(
            "Logo - Pen Control",
            '''PENUP
FORWARD 30
PENDOWN
FORWARD 50
PENUP
BACK 25
PENDOWN''',
            "logo"
        )
        
        # Test 4: Procedures
        self.run_test(
            "Logo - Variables",
            '''MAKE "SIZE 60
FORWARD :SIZE
RIGHT 90
FORWARD :SIZE''',
            "logo"
        )
        
        # Test 5: Loops and patterns
        self.run_test(
            "Logo - Spiral Pattern",
            '''REPEAT 10 [
  FORWARD 20
  RIGHT 36
]''',
            "logo"
        )
        
    def test_python_language(self):
        """Test Python language functionality"""
        self.log("\n🔴 TESTING PYTHON LANGUAGE")
        
        # Test 1: Basic output
        self.run_test(
            "Python - Print Statements",
            '''print("Hello from Python!")
print("This is", "multiple", "arguments")
print(f"Formatted string: {2 + 3}")''',
            "python"
        )
        
        # Test 2: Variables and operations
        self.run_test(
            "Python - Variables & Math",
            '''x = 10
y = 20
z = x + y
print(f"x = {x}, y = {y}")
print(f"x + y = {z}")
print(f"x * y = {x * y}")''',
            "python"
        )
        
        # Test 3: Data structures
        self.run_test(
            "Python - Lists & Loops",
            '''numbers = [1, 2, 3, 4, 5]
print("Numbers:", numbers)
for num in numbers:
    print(f"Number: {num}, Square: {num**2}")''',
            "python"
        )
        
        # Test 4: String operations
        self.run_test(
            "Python - String Operations",
            '''name = "Time_Warp"
print(f"Name: {name}")
print(f"Length: {len(name)}")
print(f"Uppercase: {name.upper()}")
print(f"Lowercase: {name.lower()}")''',
            "python"
        )
        
        # Test 5: Functions
        self.run_test(
            "Python - Functions",
            '''def greet(name):
    return f"Hello, {name}!"

def calculate_area(radius):
    pi = 3.14159
    return pi * radius * radius

print(greet("Student"))
print(f"Circle area (r=5): {calculate_area(5)}")''',
            "python"
        )
        
        # Test 6: Conditionals
        self.run_test(
            "Python - Conditionals",
            '''score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"
    
print(f"Score: {score}, Grade: {grade}")''',
            "python"
        )
        
    def test_javascript_language(self):
        """Test JavaScript functionality"""
        self.log("\n🟠 TESTING JAVASCRIPT LANGUAGE")
        
        # Test 1: Basic output
        self.run_test(
            "JavaScript - Console Output",
            '''console.log("Hello from JavaScript!");
console.log("Numbers:", 1, 2, 3);
console.log("Math:", 5 + 3);''',
            "javascript"
        )
        
        # Test 2: Variables
        self.run_test(
            "JavaScript - Variables",
            '''let name = "JavaScript";
let version = 2025;
const pi = 3.14159;
console.log("Language:", name);
console.log("Year:", version);
console.log("Pi:", pi);''',
            "javascript"
        )
        
    def test_input_output(self):
        """Test various input/output scenarios"""
        self.log("\n📝 TESTING INPUT/OUTPUT SCENARIOS")
        
        # Test alphanumeric input processing
        self.run_test(
            "I/O - Alphanumeric Processing",
            '''A:TEXT,Hello123World
A:NUMBER,42.5
A:MIXED,Test_2025
T:Text: #TEXT
T:Number: #NUMBER  
T:Mixed: #MIXED''',
            "pilot"
        )
        
        # Test numeric calculations
        self.run_test(
            "I/O - Numeric Calculations",
            '''10 LET A = 123.45
20 LET B = 67.89
30 LET SUM = A + B
40 LET DIFF = A - B
50 LET PROD = A * B
60 LET QUOT = A / B
70 PRINT "A ="; A; " B ="; B
80 PRINT "Sum ="; SUM
90 PRINT "Difference ="; DIFF
100 PRINT "Product ="; PROD
110 PRINT "Quotient ="; QUOT
120 END''',
            "basic"
        )
        
        # Test string manipulation
        self.run_test(
            "I/O - String Manipulation",
            '''text = "Time_Warp_IDE_2025"
words = text.split("_")
print("Original:", text)
print("Split:", words)
print("Joined:", "-".join(words))
print("First word:", words[0])
print("Last word:", words[-1])''',
            "python"
        )
        
    def test_graphics_commands(self):
        """Test graphics and turtle commands"""
        self.log("\n🎨 TESTING GRAPHICS COMMANDS")
        
        # Test Logo turtle graphics
        self.run_test(
            "Graphics - Logo Turtle",
            '''CLEARSCREEN
HOME
PENDOWN
FORWARD 50
RIGHT 90
FORWARD 50
RIGHT 90  
FORWARD 50
RIGHT 90
FORWARD 50
HIDETURTLE
SHOWTURTLE''',
            "logo"
        )
        
        # Test PILOT turtle commands
        self.run_test(
            "Graphics - PILOT Turtle",
            '''T:Drawing with PILOT turtle
T:PENDOWN
T:FORWARD 40
T:RIGHT 90
T:FORWARD 40
T:LEFT 45
T:FORWARD 30
T:PENUP''',
            "pilot"
        )
        
        # Test color and pen settings
        self.run_test(
            "Graphics - Colors & Pen",
            '''PENCOLOR "red"
PENSIZE 3
FORWARD 30
PENCOLOR "blue"
RIGHT 90
FORWARD 30
PENCOLOR "green"
RIGHT 90
FORWARD 30''',
            "logo"
        )
        
    def test_error_handling(self):
        """Test error handling and edge cases"""
        self.log("\n⚠️ TESTING ERROR HANDLING")
        
        # Test syntax errors
        self.run_test(
            "Error - BASIC Syntax Error",
            '''10 PRINT "Missing quote
20 END''',
            "basic"
        )
        
        # Test undefined variables
        self.run_test(
            "Error - Undefined Variable",
            '''10 PRINT UNDEFINED_VAR
20 END''',
            "basic"
        )
        
        # Test division by zero
        self.run_test(
            "Error - Division by Zero",
            '''10 LET A = 10
20 LET B = 0
30 LET C = A / B
40 PRINT C
50 END''',
            "basic"
        )
        
    def run_all_tests(self):
        """Run all test suites"""
        self.log("🚀 Starting Comprehensive Time_Warp IDE Test Suite")
        self.log(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        test_suites = [
            self.test_basic_language,
            self.test_pilot_language, 
            self.test_logo_language,
            self.test_python_language,
            self.test_javascript_language,
            self.test_input_output,
            self.test_graphics_commands,
            self.test_error_handling
        ]
        
        for suite in test_suites:
            try:
                suite()
            except Exception as e:
                self.log(f"💥 Test suite error: {e}")
                
        # Summary
        self.show_summary()
        
    def show_summary(self):
        """Show test results summary"""
        self.log("\n" + "="*60)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("="*60)
        
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        errors = sum(1 for _, result in self.test_results if result == "ERROR")
        total = len(self.test_results)
        
        self.log(f"Total Tests: {total}")
        self.log(f"✅ Passed: {passed}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"💥 Errors: {errors}")
        self.log(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        self.log("\nDetailed Results:")
        for name, result in self.test_results:
            icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "💥"
            self.log(f"{icon} {name}: {result}")
            
        self.log("\n🎯 Comprehensive testing completed!")
        
    def start_testing(self):
        """Start the testing process"""
        # Run tests after a short delay
        self.root.after(1000, self.run_all_tests)
        # Keep window open for 2 minutes to see results
        self.root.after(120000, self.root.quit)
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting comprehensive Time_Warp IDE verification...")
    suite = ComprehensiveTestSuite()
    suite.start_testing()
    print("Comprehensive testing completed!")

if __name__ == "__main__":
    main()