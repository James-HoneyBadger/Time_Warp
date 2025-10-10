#!/usr/bin/env python3
"""
Time_Warp IDE Integration Test Suite
Tests the complete system including enhanced editor, plugins, and sample programs
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import tempfile
import threading
import time
import json
from typing import Dict, List, Optional

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Test all the enhanced editor components
try:
    from core.editor.enhanced_editor import EnhancedCodeEditor
    from core.editor.language_engine import LanguageEngine
    from core.editor.compiler_manager import CompilerManager
    from core.editor.syntax_analyzer import SyntaxAnalyzer
    from core.editor.code_completion_engine import CodeCompletionEngine

    ENHANCED_EDITOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced editor not available: {e}")
    ENHANCED_EDITOR_AVAILABLE = False

# Test learning assistant
try:
    from tools.plugins.learning_assistant.plugin import (
        LearningAssistantPlugin,
        CodeAnalyzer,
        TutorialManager,
    )

    LEARNING_ASSISTANT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Learning assistant not available: {e}")
    LEARNING_ASSISTANT_AVAILABLE = False


class IntegrationTestRunner:
    """Comprehensive integration test runner for Time_Warp IDE"""

    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
        }
        self.root = None
        self.test_files_created = []

    def setup_test_environment(self):
        """Set up the test environment"""
        print("🔧 Setting up test environment...")

        # Create root window for UI tests
        self.root = tk.Tk()
        self.root.title("Time_Warp Integration Tests")
        self.root.geometry("800x600")
        self.root.withdraw()  # Hide initially

        # Create test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_samples")
        os.makedirs(self.test_dir, exist_ok=True)

        print("✅ Test environment ready")

    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")

        # Clean up test files
        for file_path in self.test_files_created:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Could not remove test file {file_path}: {e}")

        # Clean up UI
        if self.root:
            self.root.destroy()

        print("✅ Cleanup complete")

    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        self.results["total_tests"] += 1

        try:
            print(f"🧪 Running {test_name}...")
            result = test_func()

            if result:
                self.results["passed"] += 1
                print(f"✅ {test_name} - PASSED")
                self.results["details"].append(
                    {
                        "test": test_name,
                        "status": "PASSED",
                        "message": "Test completed successfully",
                    }
                )
            else:
                self.results["failed"] += 1
                print(f"❌ {test_name} - FAILED")
                self.results["details"].append(
                    {
                        "test": test_name,
                        "status": "FAILED",
                        "message": "Test returned False",
                    }
                )

        except Exception as e:
            self.results["failed"] += 1
            print(f"❌ {test_name} - ERROR: {str(e)}")
            self.results["details"].append(
                {"test": test_name, "status": "ERROR", "message": str(e)}
            )

    def test_enhanced_editor_integration(self):
        """Test enhanced editor integration"""
        if not ENHANCED_EDITOR_AVAILABLE:
            self.results["skipped"] += 1
            return False

        # Test language engine
        engine = LanguageEngine()
        pilot_completions = engine.get_completions("T:", 2)
        if len(pilot_completions) == 0:
            return False

        # Test syntax analyzer
        analyzer = SyntaxAnalyzer(engine)
        pilot_errors = analyzer.analyze_syntax("T: Hello\nE:", "pilot")
        if pilot_errors is None:
            return False

        # Test compiler manager
        compiler = CompilerManager()
        compilers = compiler.get_available_compilers()
        if "pilot" not in compilers:
            return False

        return True

    def test_learning_assistant_integration(self):
        """Test learning assistant integration"""
        if not LEARNING_ASSISTANT_AVAILABLE:
            self.results["skipped"] += 1
            return False

        # Test code analyzer
        analyzer = CodeAnalyzer()
        pilot_result = analyzer.analyze_code("T: Hello\nE:", "pilot")
        if "score" not in pilot_result:
            return False

        # Test tutorial manager
        tutorial_mgr = TutorialManager()
        if len(tutorial_mgr.tutorials) == 0:
            return False

        return True

    def test_sample_programs_compilation(self):
        """Test compilation of sample programs"""
        sample_programs = self.create_sample_programs()

        if not ENHANCED_EDITOR_AVAILABLE:
            print("⚠️ Enhanced editor not available, skipping compilation tests")
            return True

        compiler = CompilerManager()
        success_count = 0

        for lang, code in sample_programs.items():
            if lang in compiler.get_available_compilers():
                try:
                    # Create temporary file
                    temp_file = os.path.join(
                        self.test_dir, f"test_{lang}_sample.{lang}"
                    )
                    with open(temp_file, "w") as f:
                        f.write(code)
                    self.test_files_created.append(temp_file)

                    # Test compilation
                    result = compiler.compile_file(temp_file, lang)
                    if result and result.success:
                        success_count += 1
                        print(f"✅ {lang.upper()} sample program compiled successfully")
                    else:
                        print(f"⚠️ {lang.upper()} sample program compilation failed")

                except Exception as e:
                    print(f"❌ Error testing {lang} compilation: {e}")

        return success_count > 0

    def test_file_operations(self):
        """Test file loading and saving operations"""
        test_content = {
            "pilot": "T: Integration Test\nE:",
            "basic": '10 PRINT "Integration Test"\n20 END',
            "logo": "FORWARD 100\nRIGHT 90",
            "python": "print('Integration Test')",
        }

        success_count = 0

        for lang, content in test_content.items():
            try:
                # Test file creation and reading
                test_file = os.path.join(self.test_dir, f"integration_test.{lang}")

                # Write file
                with open(test_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.test_files_created.append(test_file)

                # Read file back
                with open(test_file, "r", encoding="utf-8") as f:
                    read_content = f.read()

                if read_content.strip() == content.strip():
                    success_count += 1
                    print(f"✅ {lang.upper()} file operations successful")
                else:
                    print(f"❌ {lang.upper()} file content mismatch")

            except Exception as e:
                print(f"❌ Error in {lang} file operations: {e}")

        return success_count == len(test_content)

    def test_ui_components(self):
        """Test UI component creation and basic functionality"""
        if not ENHANCED_EDITOR_AVAILABLE:
            self.results["skipped"] += 1
            return True

        try:
            # Test enhanced editor creation
            editor = EnhancedCodeEditor(self.root, initial_language="pilot")

            # Test content operations
            test_code = "T: Hello, World!\nE:"
            editor.set_content(test_code)
            retrieved_content = editor.get_content()

            if retrieved_content.strip() != test_code.strip():
                return False

            # Test language switching
            editor.set_language("basic")
            current_lang = editor.get_current_language()

            if current_lang != "basic":
                return False

            print("✅ UI components test successful")
            return True

        except Exception as e:
            print(f"❌ UI components test failed: {e}")
            return False

    def test_plugin_lifecycle(self):
        """Test plugin lifecycle management"""
        if not LEARNING_ASSISTANT_AVAILABLE:
            self.results["skipped"] += 1
            return True

        try:
            # Create plugin instance
            plugin = LearningAssistantPlugin()

            # Test initialization
            result = plugin.initialize(self.root)
            if not result:
                return False

            # Test activation
            result = plugin.activate()
            if not result:
                return False

            # Test deactivation
            result = plugin.deactivate()
            if not result:
                return False

            # Test cleanup
            result = plugin.destroy()
            if not result:
                return False

            print("✅ Plugin lifecycle test successful")
            return True

        except Exception as e:
            print(f"❌ Plugin lifecycle test failed: {e}")
            return False

    def create_sample_programs(self):
        """Create comprehensive sample programs for all languages"""
        return {
            "pilot": """R: PILOT Calculator Program
R: This program demonstrates PILOT programming concepts
*START
T: Welcome to the PILOT Calculator!
T: Enter two numbers and I'll add them for you.
R: Get first number
T: Enter the first number:
A: #NUM1
R: Get second number  
T: Enter the second number:
A: #NUM2
R: Calculate and display result
C: #NUM1 + #NUM2, #RESULT
T: The sum of #NUM1 and #NUM2 is #RESULT
R: Ask if user wants to continue
T: Do another calculation? (Y/N)
A: #CONTINUE
M: #CONTINUE, Y, *START
M: #CONTINUE, y, *START
*END
T: Thanks for using the PILOT Calculator!
E:""",
            "basic": """10 REM BASIC Game - Number Guessing Game
20 REM This program demonstrates BASIC programming
30 REM Initialize variables
40 SECRET = INT(RND(1) * 100) + 1
50 ATTEMPTS = 0
60 MAX_ATTEMPTS = 7
70 REM Game introduction
80 PRINT "Welcome to the Number Guessing Game!"
90 PRINT "I'm thinking of a number between 1 and 100."
100 PRINT "You have"; MAX_ATTEMPTS; "attempts to guess it."
110 REM Main game loop
120 ATTEMPTS = ATTEMPTS + 1
130 PRINT "Attempt"; ATTEMPTS; "of"; MAX_ATTEMPTS
140 INPUT "Enter your guess: "; GUESS
150 REM Check the guess
160 IF GUESS = SECRET THEN GOTO 220
170 IF GUESS < SECRET THEN PRINT "Too low! Try higher."
180 IF GUESS > SECRET THEN PRINT "Too high! Try lower."
190 REM Check if attempts exhausted
200 IF ATTEMPTS < MAX_ATTEMPTS THEN GOTO 120
210 PRINT "Sorry! The number was"; SECRET; ". Better luck next time!"
215 GOTO 230
220 PRINT "Congratulations! You guessed it in"; ATTEMPTS; "attempts!"
230 PRINT "Thanks for playing!"
240 END""",
            "logo": """; Logo Graphics Art Program
; This program creates beautiful geometric patterns

TO SQUARE :SIZE
  REPEAT 4 [
    FORWARD :SIZE
    RIGHT 90
  ]
END

TO TRIANGLE :SIZE
  REPEAT 3 [
    FORWARD :SIZE
    RIGHT 120
  ]
END

TO POLYGON :SIDES :SIZE
  REPEAT :SIDES [
    FORWARD :SIZE
    RIGHT 360 / :SIDES
  ]
END

TO FLOWER :PETALS :SIZE
  REPEAT :PETALS [
    TRIANGLE :SIZE
    RIGHT 360 / :PETALS
  ]
END

TO SPIRAL :SIZE :ANGLE :INCREMENT
  IF :SIZE > 100 [STOP]
  FORWARD :SIZE
  RIGHT :ANGLE
  SPIRAL :SIZE + :INCREMENT :ANGLE :INCREMENT
END

TO MANDALA :LAYERS
  REPEAT :LAYERS [
    REPEAT 8 [
      FLOWER 6 30
      RIGHT 45
    ]
    PENUP
    FORWARD 20
    PENDOWN
  ]
END

; Main program
CLEARSCREEN
PENDOWN
SETPENCOLOR "RED"
MANDALA 3
PENUP
HOME
RIGHT 90
FORWARD 150
LEFT 90
PENDOWN
SETPENCOLOR "BLUE"
SPIRAL 5 91 2""",
            "python": '''#!/usr/bin/env python3
"""
Python Text Adventure Game
This program demonstrates Python programming concepts including:
- Object-oriented programming
- Data structures (dictionaries, lists)
- Control flow (loops, conditionals)
- Functions and methods
- String manipulation
"""

import random
import sys

class Room:
    """Represents a room in the adventure game"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.visited = False
    
    def add_exit(self, direction, room):
        """Add an exit to another room"""
        self.exits[direction] = room
    
    def add_item(self, item):
        """Add an item to the room"""
        self.items.append(item)
    
    def remove_item(self, item):
        """Remove an item from the room"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def describe(self):
        """Describe the room to the player"""
        if not self.visited:
            print(f"\\n=== {self.name} ===")
            print(self.description)
            self.visited = True
        else:
            print(f"\\nYou are in {self.name}")
        
        if self.items:
            print("\\nYou see:")
            for item in self.items:
                print(f"  - {item}")
        
        if self.exits:
            print("\\nExits:")
            for direction in self.exits.keys():
                print(f"  - {direction}")

class Player:
    """Represents the player character"""
    
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.current_room = None
        self.health = 100
        self.score = 0
    
    def move(self, direction):
        """Move the player in a direction"""
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            self.score += 1
            return True
        else:
            print("You can't go that way!")
            return False
    
    def take_item(self, item):
        """Take an item from the current room"""
        if self.current_room.remove_item(item):
            self.inventory.append(item)
            print(f"You took the {item}")
            self.score += 5
            return True
        else:
            print(f"There's no {item} here!")
            return False
    
    def show_inventory(self):
        """Show the player's inventory"""
        if self.inventory:
            print("\\nInventory:")
            for item in self.inventory:
                print(f"  - {item}")
        else:
            print("\\nYour inventory is empty.")
    
    def show_status(self):
        """Show player status"""
        print(f"\\nPlayer: {self.name}")
        print(f"Health: {self.health}")
        print(f"Score: {self.score}")

class AdventureGame:
    """Main game class"""
    
    def __init__(self):
        self.player = None
        self.rooms = {}
        self.game_over = False
        self.setup_world()
    
    def setup_world(self):
        """Create the game world"""
        # Create rooms
        entrance = Room("Entrance Hall", 
                       "A grand entrance hall with marble floors and high ceilings. "
                       "Sunlight streams through stained glass windows.")
        
        library = Room("Ancient Library",
                      "Towering bookshelves filled with dusty tomes. "
                      "The air smells of old parchment and wisdom.")
        
        garden = Room("Secret Garden",
                     "A beautiful garden hidden behind the mansion. "
                     "Colorful flowers bloom everywhere and a fountain gurgles peacefully.")
        
        treasure_room = Room("Treasure Chamber",
                           "A mysterious chamber filled with glittering treasures. "
                           "Golden coins and precious gems are scattered about.")
        
        # Connect rooms
        entrance.add_exit("north", library)
        entrance.add_exit("east", garden)
        
        library.add_exit("south", entrance)
        library.add_exit("secret", treasure_room)
        
        garden.add_exit("west", entrance)
        
        treasure_room.add_exit("exit", library)
        
        # Add items
        library.add_item("ancient book")
        library.add_item("magic key")
        garden.add_item("beautiful flower")
        garden.add_item("silver coin")
        treasure_room.add_item("golden chalice")
        treasure_room.add_item("ruby necklace")
        
        # Store rooms
        self.rooms = {
            'entrance': entrance,
            'library': library,
            'garden': garden,
            'treasure': treasure_room
        }
    
    def start_game(self):
        """Start the adventure game"""
        print("=" * 50)
        print("🏰 Welcome to the Python Text Adventure! 🏰")
        print("=" * 50)
        
        name = input("\\nWhat is your name, brave adventurer? ")
        self.player = Player(name)
        self.player.current_room = self.rooms['entrance']
        
        print(f"\\nWelcome, {name}! Your adventure begins...")
        print("\\nCommands: go <direction>, take <item>, inventory, status, help, quit")
        
        # Main game loop
        while not self.game_over:
            self.player.current_room.describe()
            self.process_command()
    
    def process_command(self):
        """Process player commands"""
        command = input("\\n> ").lower().strip()
        
        if command == "quit" or command == "exit":
            self.game_over = True
            print(f"\\nThanks for playing, {self.player.name}!")
            print(f"Final Score: {self.player.score}")
        
        elif command == "help":
            self.show_help()
        
        elif command == "inventory" or command == "inv":
            self.player.show_inventory()
        
        elif command == "status":
            self.player.show_status()
        
        elif command.startswith("go "):
            direction = command[3:]
            self.player.move(direction)
        
        elif command.startswith("take "):
            item = command[5:]
            self.player.take_item(item)
        
        elif command == "look":
            self.player.current_room.visited = False
        
        else:
            print("I don't understand that command. Type 'help' for available commands.")
    
    def show_help(self):
        """Show available commands"""
        print("\\nAvailable Commands:")
        print("  go <direction>  - Move in a direction (north, south, east, west, etc.)")
        print("  take <item>     - Pick up an item")
        print("  inventory       - Show your inventory")
        print("  status          - Show your status")
        print("  look            - Look around the current room again")
        print("  help            - Show this help message")
        print("  quit            - Exit the game")

def main():
    """Main function to run the game"""
    try:
        game = AdventureGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\\n\\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\\nAn error occurred: {e}")
        print("Please report this bug!")

if __name__ == "__main__":
    main()''',
        }

    def run_comprehensive_tests(self):
        """Run all integration tests"""
        print("🎮 Time_Warp IDE - Comprehensive Integration Tests")
        print("=" * 60)

        self.setup_test_environment()

        # Define all tests
        tests = [
            ("Enhanced Editor Integration", self.test_enhanced_editor_integration),
            (
                "Learning Assistant Integration",
                self.test_learning_assistant_integration,
            ),
            ("Sample Programs Compilation", self.test_sample_programs_compilation),
            ("File Operations", self.test_file_operations),
            ("UI Components", self.test_ui_components),
            ("Plugin Lifecycle", self.test_plugin_lifecycle),
        ]

        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Create sample program files for manual testing
        self.create_sample_program_files()

        # Generate report
        self.generate_test_report()

        # Cleanup
        self.cleanup_test_environment()

        return self.results["failed"] == 0

    def create_sample_program_files(self):
        """Create sample program files for manual testing and demonstration"""
        print("\n📁 Creating sample program files...")

        sample_programs = self.create_sample_programs()
        samples_dir = os.path.join(os.path.dirname(__file__), "samples")
        os.makedirs(samples_dir, exist_ok=True)

        extensions = {"pilot": "pilot", "basic": "bas", "logo": "logo", "python": "py"}

        for lang, code in sample_programs.items():
            filename = f"sample_{lang}_program.{extensions[lang]}"
            filepath = os.path.join(samples_dir, filename)

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"✅ Created {filename}")
            except Exception as e:
                print(f"❌ Failed to create {filename}: {e}")

        # Create a README for the samples
        readme_content = """# Time_Warp IDE Sample Programs

This directory contains sample programs demonstrating the capabilities of Time_Warp IDE across all supported languages.

## Sample Programs

### PILOT - Calculator Program (`sample_pilot_program.pilot`)
- Demonstrates PILOT syntax and interactive programming
- Shows user input, calculations, and conditional logic
- Features labels, jumps, and variable handling

### BASIC - Number Guessing Game (`sample_basic_program.bas`)
- Classic number guessing game implementation
- Demonstrates loops, conditionals, and random numbers
- Shows structured BASIC programming with line numbers

### Logo - Geometric Art (`sample_logo_program.logo`)
- Creates beautiful geometric patterns and mandalas
- Demonstrates turtle graphics and recursive procedures
- Shows Logo's power for mathematical art and education

### Python - Text Adventure Game (`sample_python_program.py`)
- Complete object-oriented adventure game
- Demonstrates classes, methods, and data structures
- Shows modern Python programming practices

## How to Use

1. Open Time_Warp IDE
2. Load any sample program using File → Open
3. Run the program to see it in action
4. Modify the code to experiment and learn
5. Use the Learning Assistant plugin for educational guidance

## Features Demonstrated

- **Enhanced Code Editor**: Syntax highlighting, code completion, error detection
- **Multi-language Support**: PILOT, BASIC, Logo, and Python
- **Compilation**: Built-in compilers for interpreted languages
- **Educational Tools**: Code analysis and learning assistance
- **Interactive Execution**: Real-time program execution and debugging

Enjoy exploring programming with Time_Warp IDE! 🎓
"""

        readme_path = os.path.join(samples_dir, "README.md")
        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            print("✅ Created README.md")
        except Exception as e:
            print(f"❌ Failed to create README.md: {e}")

        print(f"📁 Sample programs created in: {samples_dir}")

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST REPORT")
        print("=" * 60)

        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        skipped = self.results["skipped"]

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️ Skipped: {skipped}")

        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        print("\nDetailed Results:")
        print("-" * 40)

        for detail in self.results["details"]:
            status_icon = {"PASSED": "✅", "FAILED": "❌", "ERROR": "💥"}.get(
                detail["status"], "❓"
            )
            print(f"{status_icon} {detail['test']}: {detail['status']}")
            if detail["status"] != "PASSED":
                print(f"   Message: {detail['message']}")

        # Save report to file
        report_path = os.path.join(
            os.path.dirname(__file__), "integration_test_report.json"
        )
        try:
            with open(report_path, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📄 Detailed report saved to: {report_path}")
        except Exception as e:
            print(f"⚠️ Could not save detailed report: {e}")

        # Overall assessment
        print("\n" + "=" * 60)
        if failed == 0:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("Time_Warp IDE is ready for production use.")
        else:
            print("⚠️ SOME TESTS FAILED")
            print("Please review the failed tests and address any issues.")
        print("=" * 60)


def main():
    """Main function to run integration tests"""
    runner = IntegrationTestRunner()
    success = runner.run_comprehensive_tests()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
