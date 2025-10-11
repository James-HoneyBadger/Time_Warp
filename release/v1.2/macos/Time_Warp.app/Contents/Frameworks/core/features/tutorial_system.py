"""
Interactive Tutorial System for Time_Warp IDE
Provides guided learning experiences with built-in challenges and progress tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


class TutorialStep:
    """Represents a single step in a tutorial"""

    def __init__(
        self,
        step_id: str,
        title: str,
        description: str,
        code_template: str = "",
        expected_output: str = "",
        hints: List[str] = None,
        validation_code: str = "",
    ):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.code_template = code_template
        self.expected_output = expected_output
        self.hints = hints or []
        self.validation_code = validation_code
        self.completed = False
        self.attempts = 0
        self.start_time = None
        self.completion_time = None


class Tutorial:
    """Represents a complete tutorial for a programming language"""

    def __init__(
        self,
        tutorial_id: str,
        title: str,
        language: str,
        difficulty: str,
        description: str,
    ):
        self.tutorial_id = tutorial_id
        self.title = title
        self.language = language
        self.difficulty = difficulty  # "beginner", "intermediate", "advanced"
        self.description = description
        self.steps: List[TutorialStep] = []
        self.prerequisites: List[str] = []
        self.estimated_time = 0  # minutes
        self.completed_steps = 0
        self.started = False
        self.completed = False

    def add_step(self, step: TutorialStep):
        """Add a step to the tutorial"""
        self.steps.append(step)

    def get_progress(self) -> float:
        """Get completion progress as percentage"""
        if not self.steps:
            return 0.0
        return (self.completed_steps / len(self.steps)) * 100


class TutorialSystem:
    """Main tutorial system for Time_Warp IDE"""

    def __init__(self):
        self.tutorials: Dict[str, Tutorial] = {}
        self.user_progress: Dict[str, Dict] = {}
        self.current_tutorial: Optional[Tutorial] = None
        self.current_step: Optional[TutorialStep] = None
        self.progress_file = Path.home() / ".time_warp" / "tutorial_progress.json"
        self.load_progress()
        self.initialize_tutorials()

        # Callbacks for IDE integration
        self.code_editor_callback: Optional[Callable[[str], None]] = None
        self.output_callback: Optional[Callable[[str], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None

    def set_callbacks(
        self, code_editor_cb: Callable, output_cb: Callable, status_cb: Callable
    ):
        """Set callback functions for IDE integration"""
        self.code_editor_callback = code_editor_cb
        self.output_callback = output_cb
        self.status_callback = status_cb

    def initialize_tutorials(self):
        """Initialize built-in tutorials for all languages"""
        self.create_pilot_tutorials()
        self.create_basic_tutorials()
        self.create_logo_tutorials()
        self.create_python_tutorials()

    def create_pilot_tutorials(self):
        """Create PILOT language tutorials"""

        # Beginner PILOT Tutorial
        pilot_basics = Tutorial(
            "pilot_basics",
            "PILOT Basics: Your First Steps",
            "pilot",
            "beginner",
            "Learn the fundamentals of PILOT programming language",
        )
        pilot_basics.estimated_time = 30

        # Step 1: Hello World
        step1 = TutorialStep(
            "pilot_hello",
            "Your First PILOT Program",
            """Welcome to PILOT programming! PILOT is designed to be simple and educational.
            
Let's start with the classic "Hello World" program. In PILOT, we use the T: command to display text.

Your task: Write a program that displays 'Hello, Time_Warp!' to the screen.""",
            code_template="T:Hello, Time_Warp!\nEND",
            expected_output="Hello, Time_Warp!",
            hints=[
                "Use T: followed by the text you want to display",
                "Always end your PILOT program with END",
                "Don't forget the colon after T",
            ],
        )
        pilot_basics.add_step(step1)

        # Step 2: Variables
        step2 = TutorialStep(
            "pilot_variables",
            "Working with Variables",
            """Great! Now let's learn about variables in PILOT.
            
Variables store information that you can use later. In PILOT:
- U: sets a variable (U:NAME=Value)
- *NAME* displays the variable's value

Your task: Create a variable called 'NAME' with your name, then display a greeting.""",
            code_template="U:NAME=Student\nT:Hello, *NAME*!\nEND",
            expected_output="Hello, Student!",
            hints=[
                "Use U: to set a variable: U:NAME=YourName",
                "Use *NAME* to display the variable",
                "Variables can contain text or numbers",
            ],
        )
        pilot_basics.add_step(step2)

        # Step 3: Math Operations
        step3 = TutorialStep(
            "pilot_math",
            "Mathematical Calculations",
            """PILOT can perform calculations using the C: command.
            
C: calculates mathematical expressions and stores the result in a variable.

Your task: Calculate the area of a rectangle with width 5 and height 8.""",
            code_template="U:WIDTH=5\nU:HEIGHT=8\nC:AREA=*WIDTH* * *HEIGHT*\nT:Area = *AREA*\nEND",
            expected_output="Area = 40",
            hints=[
                "Use C: to calculate: C:RESULT=expression",
                "You can use +, -, *, / for math operations",
                "Variables in calculations need * around them",
            ],
        )
        pilot_basics.add_step(step3)

        self.tutorials["pilot_basics"] = pilot_basics

    def create_basic_tutorials(self):
        """Create BASIC language tutorials"""

        basic_fundamentals = Tutorial(
            "basic_fundamentals",
            "BASIC Programming Fundamentals",
            "basic",
            "beginner",
            "Learn classic BASIC programming with line numbers",
        )
        basic_fundamentals.estimated_time = 45

        # Step 1: Line Numbers and PRINT
        step1 = TutorialStep(
            "basic_hello",
            "BASIC Hello World",
            """Welcome to BASIC programming! BASIC uses line numbers to organize code.
            
Every line starts with a number (like 10, 20, 30) and BASIC executes them in order.
Use PRINT to display text or numbers.

Your task: Write a BASIC program that prints 'Welcome to BASIC!'""",
            code_template='10 PRINT "Welcome to BASIC!"\n20 END',
            expected_output="Welcome to BASIC!",
            hints=[
                "Start each line with a number (10, 20, etc.)",
                'Use PRINT "text" to display text',
                "Always end with END",
            ],
        )
        basic_fundamentals.add_step(step1)

        # Step 2: Variables with LET
        step2 = TutorialStep(
            "basic_variables",
            "Variables and LET Statement",
            """In BASIC, we use LET to assign values to variables.
            
Variables can hold numbers or text (strings). You can then use these variables in calculations or printing.

Your task: Create a variable for your age and display it.""",
            code_template='10 LET AGE = 16\n20 PRINT "I am "; AGE; " years old"\n30 END',
            expected_output="I am 16 years old",
            hints=[
                "Use LET VARIABLE = VALUE to set variables",
                "Use semicolons (;) to combine text and variables in PRINT",
                "Variables don't need quotes, but text does",
            ],
        )
        basic_fundamentals.add_step(step2)

        self.tutorials["basic_fundamentals"] = basic_fundamentals

    def create_logo_tutorials(self):
        """Create Logo turtle graphics tutorials"""

        logo_drawing = Tutorial(
            "logo_drawing",
            "Logo Turtle Graphics",
            "logo",
            "beginner",
            "Learn to draw with the Logo turtle",
        )
        logo_drawing.estimated_time = 40

        # Step 1: Basic Movement
        step1 = TutorialStep(
            "logo_movement",
            "Moving the Turtle",
            """Welcome to Logo! Logo uses a 'turtle' that draws as it moves.
            
Basic commands:
- FORWARD n (or FD n): Move forward n pixels
- BACK n (or BK n): Move backward n pixels  
- RIGHT n (or RT n): Turn right n degrees
- LEFT n (or LT n): Turn left n degrees

Your task: Draw a simple line by moving forward 100 pixels.""",
            code_template="FORWARD 100",
            expected_output="[Turtle draws a line]",
            hints=[
                "Use FORWARD followed by the number of pixels",
                "You can also use FD as a shortcut",
                "Watch the turtle graphics canvas to see the result",
            ],
        )
        logo_drawing.add_step(step1)

        # Step 2: Drawing a Square
        step2 = TutorialStep(
            "logo_square",
            "Drawing Your First Shape",
            """Now let's combine movement and turning to draw a square!
            
To draw a square, you need to:
1. Go forward
2. Turn 90 degrees
3. Repeat 4 times

Your task: Draw a square with sides of 80 pixels.""",
            code_template="FORWARD 80\nRIGHT 90\nFORWARD 80\nRIGHT 90\nFORWARD 80\nRIGHT 90\nFORWARD 80\nRIGHT 90",
            expected_output="[Turtle draws a square]",
            hints=[
                "A square has 4 equal sides and 4 right angles (90 degrees)",
                "Move forward, turn right, repeat",
                "Make sure to turn the same amount each time",
            ],
        )
        logo_drawing.add_step(step2)

        self.tutorials["logo_drawing"] = logo_drawing

    def create_python_tutorials(self):
        """Create Python language tutorials"""

        python_basics = Tutorial(
            "python_basics",
            "Python Programming Basics",
            "python",
            "beginner",
            "Introduction to Python programming language",
        )
        python_basics.estimated_time = 50

        # Step 1: Print and Variables
        step1 = TutorialStep(
            "python_hello",
            "Python Hello World",
            """Welcome to Python! Python is a powerful and popular programming language.
            
Python uses print() to display output, and variables don't need special keywords to be created.

Your task: Print a welcome message and use a variable for your name.""",
            code_template='name = "Python Learner"\nprint(f"Hello, {name}! Welcome to Python!")',
            expected_output="Hello, Python Learner! Welcome to Python!",
            hints=[
                "Use print() to display text",
                "Variables are created by just assigning: name = value",
                "Use f-strings with {variable} for easy formatting",
            ],
        )
        python_basics.add_step(step1)

        self.tutorials["python_basics"] = python_basics

    def get_available_tutorials(self) -> List[Tutorial]:
        """Get list of available tutorials"""
        return list(self.tutorials.values())

    def get_tutorials_by_language(self, language: str) -> List[Tutorial]:
        """Get tutorials for a specific language"""
        return [
            t for t in self.tutorials.values() if t.language.lower() == language.lower()
        ]

    def start_tutorial(self, tutorial_id: str) -> bool:
        """Start a specific tutorial"""
        if tutorial_id not in self.tutorials:
            return False

        self.current_tutorial = self.tutorials[tutorial_id]
        self.current_tutorial.started = True

        if self.current_tutorial.steps:
            self.current_step = self.current_tutorial.steps[0]
            self.current_step.start_time = datetime.now()

        self.save_progress()
        return True

    def get_current_step(self) -> Optional[TutorialStep]:
        """Get the current tutorial step"""
        return self.current_step

    def validate_step(self, user_code: str, output: str) -> Dict[str, Any]:
        """Validate if the current step is completed correctly"""
        if not self.current_step:
            return {"valid": False, "message": "No active tutorial step"}

        # Basic validation - check if expected output is in the actual output
        expected = self.current_step.expected_output.strip()
        actual = output.strip()

        self.current_step.attempts += 1

        if (
            expected.lower() in actual.lower()
            or expected == "[Turtle draws a line]"
            or expected == "[Turtle draws a square]"
        ):
            self.current_step.completed = True
            self.current_step.completion_time = datetime.now()
            self.current_tutorial.completed_steps += 1

            # Move to next step
            current_index = self.current_tutorial.steps.index(self.current_step)
            if current_index + 1 < len(self.current_tutorial.steps):
                self.current_step = self.current_tutorial.steps[current_index + 1]
                self.current_step.start_time = datetime.now()
            else:
                # Tutorial completed!
                self.current_tutorial.completed = True
                self.current_step = None

            self.save_progress()
            return {
                "valid": True,
                "message": "Step completed! Great job!",
                "completed": self.current_step is None,
            }
        else:
            return {
                "valid": False,
                "message": f"Not quite right. Expected output should contain: '{expected}'",
                "hint": (
                    self.current_step.hints[
                        min(
                            self.current_step.attempts - 1,
                            len(self.current_step.hints) - 1,
                        )
                    ]
                    if self.current_step.hints
                    else None
                ),
            }

    def load_progress(self):
        """Load user progress from file"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, "r") as f:
                    self.user_progress = json.load(f)
        except Exception as e:
            print(f"Error loading tutorial progress: {e}")
            self.user_progress = {}

    def save_progress(self):
        """Save user progress to file"""
        try:
            self.progress_file.parent.mkdir(exist_ok=True)

            # Convert tutorial progress to serializable format
            progress_data = {
                "tutorials": {},
                "current_tutorial": (
                    self.current_tutorial.tutorial_id if self.current_tutorial else None
                ),
                "current_step": (
                    self.current_step.step_id if self.current_step else None
                ),
            }

            for tutorial_id, tutorial in self.tutorials.items():
                progress_data["tutorials"][tutorial_id] = {
                    "started": tutorial.started,
                    "completed": tutorial.completed,
                    "completed_steps": tutorial.completed_steps,
                    "steps": {
                        step.step_id: {
                            "completed": step.completed,
                            "attempts": step.attempts,
                        }
                        for step in tutorial.steps
                    },
                }

            with open(self.progress_file, "w") as f:
                json.dump(progress_data, f, indent=2)

        except Exception as e:
            print(f"Error saving tutorial progress: {e}")

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary"""
        total_tutorials = len(self.tutorials)
        completed_tutorials = sum(1 for t in self.tutorials.values() if t.completed)

        total_steps = sum(len(t.steps) for t in self.tutorials.values())
        completed_steps = sum(t.completed_steps for t in self.tutorials.values())

        return {
            "total_tutorials": total_tutorials,
            "completed_tutorials": completed_tutorials,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "overall_progress": (
                (completed_steps / total_steps * 100) if total_steps > 0 else 0
            ),
        }
