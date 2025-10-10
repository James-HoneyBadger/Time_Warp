"""
Learning Assistant Plugin for Time_Warp IDE
Provides educational features including tutorials, code analysis, and progress tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import datetime
from typing import Dict, List, Optional, Any, Tuple
import threading
import time
import re

try:
    from ...tool_manager import ToolPlugin
except ImportError:
    # Fallback for standalone testing
    class ToolPlugin:
        def __init__(self, ide_instance=None, framework=None):
            self.ide_instance = ide_instance
            self.framework = framework

        def initialize(self, parent=None):
            return True

        def activate(self):
            return True

        def deactivate(self):
            return True

        def destroy(self):
            return True

        def create_ui(self):
            pass


class LearningPath:
    """Represents a learning path with lessons and progress"""

    def __init__(self, name: str, description: str, lessons: List[Dict]):
        self.name = name
        self.description = description
        self.lessons = lessons
        self.current_lesson = 0
        self.completed_lessons = set()
        self.started_date = datetime.datetime.now()
        self.last_accessed = datetime.datetime.now()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "lessons": self.lessons,
            "current_lesson": self.current_lesson,
            "completed_lessons": list(self.completed_lessons),
            "started_date": self.started_date.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "LearningPath":
        path = cls(data["name"], data["description"], data["lessons"])
        path.current_lesson = data.get("current_lesson", 0)
        path.completed_lessons = set(data.get("completed_lessons", []))
        if "started_date" in data:
            path.started_date = datetime.datetime.fromisoformat(data["started_date"])
        if "last_accessed" in data:
            path.last_accessed = datetime.datetime.fromisoformat(data["last_accessed"])
        return path


class CodeAnalyzer:
    """Analyzes code quality and provides educational feedback"""

    def __init__(self):
        self.analysis_rules = {
            "pilot": self._pilot_rules(),
            "basic": self._basic_rules(),
            "logo": self._logo_rules(),
            "python": self._python_rules(),
        }

    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code and return educational feedback"""
        if language not in self.analysis_rules:
            return {"score": 0, "suggestions": [], "quality": "unknown"}

        rules = self.analysis_rules[language]
        suggestions = []
        score = 100

        for rule in rules:
            result = rule["check"](code)
            if not result["passed"]:
                suggestions.append(
                    {
                        "type": rule["type"],
                        "message": result["message"],
                        "suggestion": rule["suggestion"],
                        "line": result.get("line", 0),
                    }
                )
                score -= rule["penalty"]

        # Determine quality level
        if score >= 90:
            quality = "excellent"
        elif score >= 75:
            quality = "good"
        elif score >= 60:
            quality = "fair"
        else:
            quality = "needs improvement"

        return {
            "score": max(0, score),
            "quality": quality,
            "suggestions": suggestions,
            "language": language,
        }

    def _pilot_rules(self) -> List[Dict]:
        """PILOT language analysis rules"""
        return [
            {
                "name": "comments",
                "type": "documentation",
                "penalty": 10,
                "check": lambda code: {
                    "passed": "R:" in code,
                    "message": "Add comments to explain your code",
                },
                "suggestion": "Use R: to add comments explaining what your program does",
            },
            {
                "name": "structure",
                "type": "organization",
                "penalty": 15,
                "check": lambda code: {
                    "passed": "*" in code and "E:" in code,
                    "message": "Use labels and proper program ending",
                },
                "suggestion": "Organize your code with labels (*LABEL) and end with E:",
            },
            {
                "name": "user_interaction",
                "type": "functionality",
                "penalty": 5,
                "check": lambda code: {
                    "passed": "A:" in code or "T:" in code,
                    "message": "Include user interaction",
                },
                "suggestion": "Use T: to display messages and A: to get input from users",
            },
        ]

    def _basic_rules(self) -> List[Dict]:
        """BASIC language analysis rules"""
        return [
            {
                "name": "comments",
                "type": "documentation",
                "penalty": 10,
                "check": lambda code: {
                    "passed": "REM" in code.upper() or "'" in code,
                    "message": "Add comments to explain your code",
                },
                "suggestion": "Use REM or ' to add comments explaining your program logic",
            },
            {
                "name": "structured_end",
                "type": "organization",
                "penalty": 15,
                "check": lambda code: {
                    "passed": "END" in code.upper(),
                    "message": "Programs should have a clear ending",
                },
                "suggestion": "End your program with END statement",
            },
            {
                "name": "meaningful_variables",
                "type": "readability",
                "penalty": 10,
                "check": lambda code: self._check_variable_names(code),
                "suggestion": "Use descriptive variable names like NAME$ instead of N$",
            },
        ]

    def _logo_rules(self) -> List[Dict]:
        """Logo language analysis rules"""
        return [
            {
                "name": "procedures",
                "type": "organization",
                "penalty": 15,
                "check": lambda code: {
                    "passed": "TO " in code.upper(),
                    "message": "Break code into procedures",
                },
                "suggestion": "Create procedures with TO/END for reusable code blocks",
            },
            {
                "name": "comments",
                "type": "documentation",
                "penalty": 10,
                "check": lambda code: {
                    "passed": ";" in code,
                    "message": "Add comments to explain your drawings",
                },
                "suggestion": "Use ; to add comments explaining your turtle graphics",
            },
            {
                "name": "turtle_home",
                "type": "best_practice",
                "penalty": 5,
                "check": lambda code: {
                    "passed": "HOME" in code.upper() or "CS" in code.upper(),
                    "message": "Reset turtle position",
                },
                "suggestion": "Use HOME or CLEARSCREEN to start with a clean canvas",
            },
        ]

    def _python_rules(self) -> List[Dict]:
        """Python language analysis rules"""
        return [
            {
                "name": "docstrings",
                "type": "documentation",
                "penalty": 10,
                "check": lambda code: {
                    "passed": '"""' in code or "'''" in code,
                    "message": "Add docstrings to functions",
                },
                "suggestion": "Use triple quotes to document your functions",
            },
            {
                "name": "main_guard",
                "type": "best_practice",
                "penalty": 5,
                "check": lambda code: {
                    "passed": "__main__" in code,
                    "message": "Use main guard for executable scripts",
                },
                "suggestion": 'Add if __name__ == "__main__": for script execution',
            },
            {
                "name": "imports",
                "type": "organization",
                "penalty": 5,
                "check": lambda code: self._check_python_imports(code),
                "suggestion": "Place import statements at the top of the file",
            },
        ]

    def _check_variable_names(self, code: str) -> Dict[str, Any]:
        """Check for meaningful variable names in BASIC"""
        # Simple check for single-letter variables
        single_letters = re.findall(r"\b[A-Z]\$?\b", code.upper())
        meaningful_vars = re.findall(r"\b[A-Z][A-Z0-9_]+\$?\b", code.upper())

        if len(single_letters) > len(meaningful_vars):
            return {"passed": False, "message": "Use more descriptive variable names"}
        return {"passed": True, "message": "Good variable naming"}

    def _check_python_imports(self, code: str) -> Dict[str, Any]:
        """Check if imports are at the top"""
        lines = code.split("\n")
        import_found = False
        code_before_import = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(("import ", "from ")):
                import_found = True
                if code_before_import:
                    return {"passed": False, "message": "Move imports to top of file"}
            elif not line.startswith(('"""', "'''")):
                code_before_import = True

        return {"passed": True, "message": "Imports properly placed"}


class TutorialManager:
    """Manages interactive tutorials"""

    def __init__(self):
        self.tutorials = self._load_default_tutorials()
        self.current_tutorial: Optional[str] = None
        self.current_step = 0

    def _load_default_tutorials(self) -> Dict[str, Dict]:
        """Load default tutorials for each language"""
        return {
            "pilot_basics": {
                "title": "PILOT Programming Basics",
                "language": "pilot",
                "difficulty": "beginner",
                "steps": [
                    {
                        "title": "Your First PILOT Program",
                        "content": "Let's create your first PILOT program! PILOT uses simple commands to interact with users.",
                        "code": "T: Hello, World!\nE:",
                        "explanation": "T: displays text to the user. E: ends the program.",
                        "task": "Try changing the message to say hello to yourself!",
                    },
                    {
                        "title": "Getting User Input",
                        "content": "Now let's get input from the user using the A: command.",
                        "code": "T: What is your name?\nA: #NAME\nT: Hello, #NAME!\nE:",
                        "explanation": "A: gets input and stores it in variable #NAME. We can then use #NAME in our messages.",
                        "task": "Add another question to ask for the user's age.",
                    },
                    {
                        "title": "Using Labels and Jumps",
                        "content": "PILOT uses labels (*) and jumps (J:) to control program flow.",
                        "code": "*START\nT: Welcome to PILOT!\nJ: *END\n*END\nT: Goodbye!\nE:",
                        "explanation": "Labels start with * and J: jumps to a label. This creates program structure.",
                        "task": "Create a simple menu system using labels and jumps.",
                    },
                ],
            },
            "basic_fundamentals": {
                "title": "BASIC Programming Fundamentals",
                "language": "basic",
                "difficulty": "beginner",
                "steps": [
                    {
                        "title": "Hello World in BASIC",
                        "content": "Let's start with the classic Hello World program in BASIC.",
                        "code": '10 PRINT "Hello, World!"\n20 END',
                        "explanation": "Line numbers organize the program. PRINT displays text. END stops execution.",
                        "task": "Add line 15 to print your name too!",
                    },
                    {
                        "title": "Variables and Input",
                        "content": "BASIC uses variables to store data. String variables end with $.",
                        "code": '10 INPUT "Enter your name: "; N$\n20 PRINT "Hello, "; N$\n30 END',
                        "explanation": "INPUT gets user input. Variables store values. ; continues on same line.",
                        "task": "Create variables for name and age, then display both.",
                    },
                ],
            },
            "logo_graphics": {
                "title": "Logo Turtle Graphics",
                "language": "logo",
                "difficulty": "beginner",
                "steps": [
                    {
                        "title": "Moving the Turtle",
                        "content": "Logo controls a turtle that draws as it moves.",
                        "code": "FORWARD 100\nRIGHT 90\nFORWARD 100",
                        "explanation": "FORWARD moves the turtle. RIGHT turns it. The turtle draws a line as it moves.",
                        "task": "Draw a complete square by adding two more sides.",
                    },
                    {
                        "title": "Creating Procedures",
                        "content": "Procedures let you reuse code and create complex patterns.",
                        "code": "TO SQUARE\n  REPEAT 4 [\n    FORWARD 50\n    RIGHT 90\n  ]\nEND\n\nSQUARE",
                        "explanation": "TO defines a procedure. REPEAT loops commands. Procedures make code reusable.",
                        "task": "Create a TRIANGLE procedure and use it to draw multiple triangles.",
                    },
                ],
            },
        }

    def get_tutorial(self, tutorial_id: str) -> Optional[Dict]:
        """Get tutorial by ID"""
        return self.tutorials.get(tutorial_id)

    def get_tutorials_for_language(self, language: str) -> List[Dict]:
        """Get all tutorials for a specific language"""
        return [
            {"id": tid, **tutorial}
            for tid, tutorial in self.tutorials.items()
            if tutorial["language"] == language
        ]


class LearningAssistantPlugin(ToolPlugin):
    """Learning Assistant Plugin for educational features"""

    def __init__(self, ide_instance=None, framework=None):
        super().__init__(ide_instance, framework)
        self.name = "Learning Assistant"
        self.version = "1.0.0"
        self.description = (
            "Educational plugin with tutorials, code analysis, and progress tracking"
        )

        # Core components
        self.code_analyzer = CodeAnalyzer()
        self.tutorial_manager = TutorialManager()
        self.learning_paths: Dict[str, LearningPath] = {}
        self.user_progress = {}

        # UI components
        self.main_window = None
        self.notebook = None

        # Load user data
        self._load_user_data()

    def create_ui(self):
        """Create UI for the plugin"""
        self.create_main_interface()

    def initialize(self, parent=None):
        """Initialize the plugin"""
        self.parent = parent
        self.create_main_interface()
        return True

    def activate(self):
        """Activate the plugin"""
        if self.main_window:
            self.main_window.deiconify()
            self.main_window.lift()
        else:
            self.create_main_interface()
        return True

    def deactivate(self):
        """Deactivate the plugin"""
        if self.main_window:
            self.main_window.withdraw()
        return True

    def destroy(self):
        """Clean up the plugin"""
        self._save_user_data()
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        return True

    def create_main_interface(self):
        """Create the main learning assistant interface"""
        if self.main_window:
            self.main_window.deiconify()
            return

        self.main_window = tk.Toplevel(self.parent)
        self.main_window.title("🎓 Learning Assistant")
        self.main_window.geometry("1000x700")
        self.main_window.transient(self.parent)

        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_tutorial_tab()
        self.create_code_analysis_tab()
        self.create_progress_tab()
        self.create_learning_paths_tab()
        self.create_achievements_tab()

        # Bind close event
        self.main_window.protocol("WM_DELETE_WINDOW", self.deactivate)

    def create_tutorial_tab(self):
        """Create interactive tutorials tab"""
        tutorial_frame = ttk.Frame(self.notebook)
        self.notebook.add(tutorial_frame, text="📚 Tutorials")

        # Left panel - tutorial list
        left_panel = ttk.Frame(tutorial_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        ttk.Label(
            left_panel, text="Available Tutorials", font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        # Language filter
        filter_frame = ttk.Frame(left_panel)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Language:").pack(side=tk.LEFT)
        self.tutorial_language_var = tk.StringVar(value="all")
        language_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.tutorial_language_var,
            values=["all", "pilot", "basic", "logo", "python"],
            state="readonly",
            width=10,
        )
        language_combo.pack(side=tk.LEFT, padx=(5, 0))
        language_combo.bind("<<ComboboxSelected>>", self.filter_tutorials)

        # Tutorial list
        self.tutorial_listbox = tk.Listbox(left_panel, width=30, height=15)
        self.tutorial_listbox.pack(fill=tk.BOTH, expand=True)
        self.tutorial_listbox.bind("<<ListboxSelect>>", self.on_tutorial_select)

        # Right panel - tutorial content
        right_panel = ttk.Frame(tutorial_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tutorial info
        info_frame = ttk.LabelFrame(right_panel, text="Tutorial Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.tutorial_title_label = ttk.Label(
            info_frame, text="Select a tutorial", font=("Arial", 14, "bold")
        )
        self.tutorial_title_label.pack(anchor=tk.W, padx=10, pady=5)

        self.tutorial_info_label = ttk.Label(info_frame, text="", wraplength=400)
        self.tutorial_info_label.pack(anchor=tk.W, padx=10, pady=5)

        # Tutorial content
        content_frame = ttk.LabelFrame(right_panel, text="Tutorial Content")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Step navigation
        nav_frame = ttk.Frame(content_frame)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)

        self.prev_button = ttk.Button(
            nav_frame, text="◀ Previous", command=self.prev_tutorial_step
        )
        self.prev_button.pack(side=tk.LEFT)

        self.step_label = ttk.Label(nav_frame, text="Step 1 of 1")
        self.step_label.pack(side=tk.LEFT, padx=20)

        self.next_button = ttk.Button(
            nav_frame, text="Next ▶", command=self.next_tutorial_step
        )
        self.next_button.pack(side=tk.LEFT)

        # Content area
        self.tutorial_content_text = tk.Text(
            content_frame, height=8, wrap=tk.WORD, state=tk.DISABLED
        )
        self.tutorial_content_text.pack(fill=tk.X, padx=10, pady=5)

        # Code area
        code_frame = ttk.LabelFrame(content_frame, text="Example Code")
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tutorial_code_text = tk.Text(code_frame, height=8, font=("Courier", 10))
        self.tutorial_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Action buttons
        action_frame = ttk.Frame(content_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            action_frame, text="📝 Try This Code", command=self.try_tutorial_code
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame, text="✅ Mark Complete", command=self.complete_tutorial_step
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame, text="💡 Get Hint", command=self.get_tutorial_hint
        ).pack(side=tk.LEFT, padx=5)

        # Populate tutorial list
        self.populate_tutorial_list()

    def create_code_analysis_tab(self):
        """Create code analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🔍 Code Analysis")

        # Input area
        input_frame = ttk.LabelFrame(analysis_frame, text="Code to Analyze")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Language selection
        lang_frame = ttk.Frame(input_frame)
        lang_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        self.analysis_language_var = tk.StringVar(value="pilot")
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.analysis_language_var,
            values=["pilot", "basic", "logo", "python"],
            state="readonly",
            width=15,
        )
        lang_combo.pack(side=tk.LEFT, padx=(5, 20))

        ttk.Button(
            lang_frame, text="🔍 Analyze Code", command=self.analyze_current_code
        ).pack(side=tk.LEFT)
        ttk.Button(
            lang_frame, text="📁 Load from File", command=self.load_code_file
        ).pack(side=tk.LEFT, padx=5)

        # Code input
        self.analysis_code_text = tk.Text(input_frame, height=12, font=("Courier", 10))
        self.analysis_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Results area
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Score display
        score_frame = ttk.Frame(results_frame)
        score_frame.pack(fill=tk.X, padx=5, pady=5)

        self.score_label = ttk.Label(
            score_frame, text="Code Quality Score: --", font=("Arial", 12, "bold")
        )
        self.score_label.pack(side=tk.LEFT)

        self.quality_label = ttk.Label(score_frame, text="", font=("Arial", 12))
        self.quality_label.pack(side=tk.LEFT, padx=20)

        # Suggestions list
        self.analysis_results_text = tk.Text(
            results_frame, height=8, wrap=tk.WORD, state=tk.DISABLED
        )
        self.analysis_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_progress_tab(self):
        """Create progress tracking tab"""
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="📊 Progress")

        # Overall progress
        overall_frame = ttk.LabelFrame(progress_frame, text="Overall Progress")
        overall_frame.pack(fill=tk.X, padx=10, pady=5)

        # Progress bars and stats
        self.create_progress_displays(overall_frame)

        # Detailed progress
        detail_frame = ttk.LabelFrame(progress_frame, text="Detailed Progress")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Progress tree
        self.progress_tree = ttk.Treeview(
            detail_frame,
            columns=("Status", "Score", "Last Activity"),
            show="tree headings",
        )
        self.progress_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure columns
        self.progress_tree.heading("#0", text="Activity")
        self.progress_tree.heading("Status", text="Status")
        self.progress_tree.heading("Score", text="Score")
        self.progress_tree.heading("Last Activity", text="Last Activity")

        self.update_progress_display()

    def create_learning_paths_tab(self):
        """Create learning paths tab"""
        paths_frame = ttk.Frame(self.notebook)
        self.notebook.add(paths_frame, text="🛤️ Learning Paths")

        # Path selection
        selection_frame = ttk.Frame(paths_frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            selection_frame,
            text="Choose your learning path:",
            font=("Arial", 12, "bold"),
        ).pack(anchor=tk.W)

        # Path options
        self.create_default_learning_paths()

        paths_list_frame = ttk.Frame(paths_frame)
        paths_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left - path list
        left_paths_frame = ttk.Frame(paths_list_frame)
        left_paths_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        self.paths_listbox = tk.Listbox(left_paths_frame, width=30)
        self.paths_listbox.pack(fill=tk.BOTH, expand=True)
        self.paths_listbox.bind("<<ListboxSelect>>", self.on_path_select)

        # Right - path details
        right_paths_frame = ttk.Frame(paths_list_frame)
        right_paths_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.path_details_text = tk.Text(
            right_paths_frame, wrap=tk.WORD, state=tk.DISABLED
        )
        self.path_details_text.pack(fill=tk.BOTH, expand=True)

        # Path actions
        path_actions_frame = ttk.Frame(paths_frame)
        path_actions_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            path_actions_frame, text="🚀 Start Path", command=self.start_learning_path
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            path_actions_frame, text="📈 View Progress", command=self.view_path_progress
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            path_actions_frame, text="⏸️ Pause Path", command=self.pause_learning_path
        ).pack(side=tk.LEFT, padx=5)

        self.populate_learning_paths()

    def create_achievements_tab(self):
        """Create achievements and gamification tab"""
        achievements_frame = ttk.Frame(self.notebook)
        self.notebook.add(achievements_frame, text="🏆 Achievements")

        # Achievement categories
        categories_frame = ttk.Frame(achievements_frame)
        categories_frame.pack(fill=tk.X, padx=10, pady=5)

        self.achievement_category_var = tk.StringVar(value="all")
        ttk.Label(categories_frame, text="Category:").pack(side=tk.LEFT)
        category_combo = ttk.Combobox(
            categories_frame,
            textvariable=self.achievement_category_var,
            values=["all", "tutorials", "coding", "quality", "exploration"],
            state="readonly",
        )
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind("<<ComboboxSelected>>", self.filter_achievements)

        # Achievements display
        self.achievements_canvas = tk.Canvas(achievements_frame, bg="white")
        achievements_scroll = ttk.Scrollbar(
            achievements_frame,
            orient=tk.VERTICAL,
            command=self.achievements_canvas.yview,
        )

        self.achievements_canvas.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5
        )
        achievements_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.achievements_canvas.configure(yscrollcommand=achievements_scroll.set)

        # Create achievements content
        self.create_achievements_content()

    # Tutorial methods
    def populate_tutorial_list(self):
        """Populate the tutorial list"""
        self.tutorial_listbox.delete(0, tk.END)

        selected_lang = self.tutorial_language_var.get()

        for tutorial_id, tutorial in self.tutorial_manager.tutorials.items():
            if selected_lang == "all" or tutorial["language"] == selected_lang:
                display_name = f"[{tutorial['language'].upper()}] {tutorial['title']}"
                self.tutorial_listbox.insert(tk.END, display_name)
                # Store the ID as a data attribute
                self.tutorial_listbox.insert(tk.END, tutorial_id)
                self.tutorial_listbox.delete(tk.END)  # Remove the ID line

    def filter_tutorials(self, event=None):
        """Filter tutorials by language"""
        self.populate_tutorial_list()

    def on_tutorial_select(self, event):
        """Handle tutorial selection"""
        selection = self.tutorial_listbox.curselection()
        if not selection:
            return

        # Get tutorial ID from the selected item
        tutorial_ids = list(self.tutorial_manager.tutorials.keys())
        selected_lang = self.tutorial_language_var.get()

        if selected_lang != "all":
            tutorial_ids = [
                tid
                for tid, t in self.tutorial_manager.tutorials.items()
                if t["language"] == selected_lang
            ]

        if selection[0] < len(tutorial_ids):
            tutorial_id = tutorial_ids[selection[0]]
            self.load_tutorial(tutorial_id)

    def load_tutorial(self, tutorial_id: str):
        """Load and display a tutorial"""
        tutorial = self.tutorial_manager.get_tutorial(tutorial_id)
        if not tutorial:
            return

        self.tutorial_manager.current_tutorial = tutorial_id
        self.tutorial_manager.current_step = 0

        # Update UI
        self.tutorial_title_label.config(text=tutorial["title"])
        self.tutorial_info_label.config(
            text=f"Language: {tutorial['language'].upper()} | Difficulty: {tutorial['difficulty']}"
        )

        self.display_tutorial_step()

    def display_tutorial_step(self):
        """Display current tutorial step"""
        if not self.tutorial_manager.current_tutorial:
            return

        current_tutorial_id = self.tutorial_manager.current_tutorial
        if current_tutorial_id not in self.tutorial_manager.tutorials:
            return

        tutorial = self.tutorial_manager.tutorials[current_tutorial_id]
        step_index = self.tutorial_manager.current_step

        if step_index >= len(tutorial["steps"]):
            return

        step = tutorial["steps"][step_index]

        # Update step navigation
        self.step_label.config(
            text=f"Step {step_index + 1} of {len(tutorial['steps'])}"
        )
        self.prev_button.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)
        self.next_button.config(
            state=tk.NORMAL if step_index < len(tutorial["steps"]) - 1 else tk.DISABLED
        )

        # Update content
        self.tutorial_content_text.config(state=tk.NORMAL)
        self.tutorial_content_text.delete(1.0, tk.END)
        self.tutorial_content_text.insert(
            tk.END,
            f"{step['title']}\n\n{step['content']}\n\n{step['explanation']}\n\nYour task: {step['task']}",
        )
        self.tutorial_content_text.config(state=tk.DISABLED)

        # Update code
        self.tutorial_code_text.delete(1.0, tk.END)
        self.tutorial_code_text.insert(tk.END, step["code"])

    def prev_tutorial_step(self):
        """Go to previous tutorial step"""
        if self.tutorial_manager.current_step > 0:
            self.tutorial_manager.current_step -= 1
            self.display_tutorial_step()

    def next_tutorial_step(self):
        """Go to next tutorial step"""
        if not self.tutorial_manager.current_tutorial:
            return

        current_tutorial_id = self.tutorial_manager.current_tutorial
        if current_tutorial_id not in self.tutorial_manager.tutorials:
            return

        tutorial = self.tutorial_manager.tutorials[current_tutorial_id]
        if self.tutorial_manager.current_step < len(tutorial["steps"]) - 1:
            self.tutorial_manager.current_step += 1
            self.display_tutorial_step()

    def try_tutorial_code(self):
        """Send tutorial code to main editor"""
        code = self.tutorial_code_text.get(1.0, tk.END).strip()
        if code:
            # This would integrate with the main Time_Warp editor
            messagebox.showinfo(
                "Code Sent", "Tutorial code has been sent to the main editor!"
            )

    def complete_tutorial_step(self):
        """Mark current tutorial step as complete"""
        if self.tutorial_manager.current_tutorial:
            tutorial_id = self.tutorial_manager.current_tutorial
            step_index = self.tutorial_manager.current_step

            # Record progress
            if tutorial_id not in self.user_progress:
                self.user_progress[tutorial_id] = {"completed_steps": set(), "score": 0}

            self.user_progress[tutorial_id]["completed_steps"].add(step_index)

            messagebox.showinfo(
                "Step Complete", "Great job! Tutorial step marked as complete."
            )
            self.update_progress_display()

    def get_tutorial_hint(self):
        """Provide hint for current tutorial step"""
        hints = [
            "💡 Read the explanation carefully - it contains important clues!",
            "💡 Try running the example code first to see how it works.",
            "💡 Look at the variable names - they often tell you what they store.",
            "💡 Break down the problem into smaller steps.",
            "💡 Don't forget to test your code with different inputs!",
        ]

        import random

        hint = random.choice(hints)
        messagebox.showinfo("Hint", hint)

    # Code Analysis methods
    def analyze_current_code(self):
        """Analyze the code in the text area"""
        code = self.analysis_code_text.get(1.0, tk.END).strip()
        language = self.analysis_language_var.get()

        if not code:
            messagebox.showwarning("No Code", "Please enter some code to analyze.")
            return

        # Perform analysis
        results = self.code_analyzer.analyze_code(code, language)

        # Update UI
        self.score_label.config(text=f"Code Quality Score: {results['score']}/100")
        self.quality_label.config(text=f"Quality: {results['quality'].title()}")

        # Color code the quality
        quality_colors = {
            "excellent": "green",
            "good": "blue",
            "fair": "orange",
            "needs improvement": "red",
        }
        self.quality_label.config(
            foreground=quality_colors.get(results["quality"], "black")
        )

        # Display suggestions
        self.analysis_results_text.config(state=tk.NORMAL)
        self.analysis_results_text.delete(1.0, tk.END)

        if results["suggestions"]:
            self.analysis_results_text.insert(
                tk.END, "📋 Suggestions for Improvement:\n\n"
            )

            for i, suggestion in enumerate(results["suggestions"], 1):
                self.analysis_results_text.insert(
                    tk.END, f"{i}. {suggestion['message']}\n"
                )
                self.analysis_results_text.insert(
                    tk.END, f"   💡 {suggestion['suggestion']}\n\n"
                )
        else:
            self.analysis_results_text.insert(
                tk.END,
                "🎉 Excellent! Your code looks great. No suggestions at this time.",
            )

        self.analysis_results_text.config(state=tk.DISABLED)

    def load_code_file(self):
        """Load code from a file for analysis"""
        filetypes = [
            ("PILOT files", "*.pilot"),
            ("BASIC files", "*.bas"),
            ("Logo files", "*.logo"),
            ("Python files", "*.py"),
            ("All files", "*.*"),
        ]

        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()

                self.analysis_code_text.delete(1.0, tk.END)
                self.analysis_code_text.insert(1.0, content)

                # Auto-detect language from extension
                ext = os.path.splitext(filename)[1].lower()
                lang_map = {
                    ".pilot": "pilot",
                    ".bas": "basic",
                    ".logo": "logo",
                    ".py": "python",
                }
                if ext in lang_map:
                    self.analysis_language_var.set(lang_map[ext])

            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {str(e)}")

    # Progress tracking methods
    def create_progress_displays(self, parent):
        """Create progress display widgets"""
        # Overall stats
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        # Tutorials completed
        ttk.Label(stats_frame, text="Tutorials Completed:").grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        self.tutorials_progress_bar = ttk.Progressbar(
            stats_frame, length=200, mode="determinate"
        )
        self.tutorials_progress_bar.grid(row=0, column=1, padx=5)
        self.tutorials_count_label = ttk.Label(stats_frame, text="0/0")
        self.tutorials_count_label.grid(row=0, column=2, padx=5)

        # Code quality average
        ttk.Label(stats_frame, text="Average Code Quality:").grid(
            row=1, column=0, sticky=tk.W, padx=5
        )
        self.quality_progress_bar = ttk.Progressbar(
            stats_frame, length=200, mode="determinate"
        )
        self.quality_progress_bar.grid(row=1, column=1, padx=5)
        self.quality_score_label = ttk.Label(stats_frame, text="--")
        self.quality_score_label.grid(row=1, column=2, padx=5)

        # Learning streak
        ttk.Label(stats_frame, text="Learning Streak:").grid(
            row=2, column=0, sticky=tk.W, padx=5
        )
        self.streak_label = ttk.Label(
            stats_frame, text="0 days", font=("Arial", 10, "bold")
        )
        self.streak_label.grid(row=2, column=1, sticky=tk.W, padx=5)

    def update_progress_display(self):
        """Update the progress display"""
        # Calculate statistics
        total_tutorials = len(self.tutorial_manager.tutorials)
        completed_tutorials = len(
            [t for t in self.user_progress.values() if t.get("completed_steps")]
        )

        if total_tutorials > 0:
            tutorial_progress = (completed_tutorials / total_tutorials) * 100
            self.tutorials_progress_bar["value"] = tutorial_progress
            self.tutorials_count_label.config(
                text=f"{completed_tutorials}/{total_tutorials}"
            )

        # Average code quality
        quality_scores = [
            p.get("score", 0) for p in self.user_progress.values() if "score" in p
        ]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            self.quality_progress_bar["value"] = avg_quality
            self.quality_score_label.config(text=f"{avg_quality:.1f}/100")

        # Update detailed tree
        self.update_progress_tree()

    def update_progress_tree(self):
        """Update the detailed progress tree"""
        # Clear existing items
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)

        # Add tutorial progress
        tutorials_node = self.progress_tree.insert(
            "", "end", text="Tutorials", values=("In Progress", "--", "--")
        )

        for tutorial_id, tutorial in self.tutorial_manager.tutorials.items():
            progress = self.user_progress.get(tutorial_id, {})
            completed_steps = len(progress.get("completed_steps", set()))
            total_steps = len(tutorial["steps"])

            status = (
                "Completed"
                if completed_steps == total_steps
                else f"{completed_steps}/{total_steps}"
            )

            self.progress_tree.insert(
                tutorials_node,
                "end",
                text=tutorial["title"],
                values=(status, "--", "Recently"),
            )

    # Learning paths methods
    def create_default_learning_paths(self):
        """Create default learning paths"""
        self.learning_paths = {
            "beginner_programmer": LearningPath(
                "Complete Beginner",
                "Start from scratch and learn programming fundamentals",
                [
                    {"type": "tutorial", "id": "pilot_basics", "title": "PILOT Basics"},
                    {
                        "type": "practice",
                        "id": "pilot_exercises",
                        "title": "PILOT Practice",
                    },
                    {
                        "type": "tutorial",
                        "id": "basic_fundamentals",
                        "title": "BASIC Fundamentals",
                    },
                    {
                        "type": "project",
                        "id": "simple_calculator",
                        "title": "Build a Calculator",
                    },
                ],
            ),
            "graphics_explorer": LearningPath(
                "Graphics and Art",
                "Learn to create graphics and visual art with programming",
                [
                    {
                        "type": "tutorial",
                        "id": "logo_graphics",
                        "title": "Logo Turtle Graphics",
                    },
                    {
                        "type": "project",
                        "id": "geometric_art",
                        "title": "Geometric Art Project",
                    },
                    {
                        "type": "tutorial",
                        "id": "advanced_graphics",
                        "title": "Advanced Graphics",
                    },
                    {
                        "type": "project",
                        "id": "animation",
                        "title": "Create Animations",
                    },
                ],
            ),
            "python_pathway": LearningPath(
                "Modern Python",
                "Learn contemporary Python programming",
                [
                    {
                        "type": "tutorial",
                        "id": "python_basics",
                        "title": "Python Fundamentals",
                    },
                    {
                        "type": "practice",
                        "id": "python_exercises",
                        "title": "Python Practice",
                    },
                    {
                        "type": "project",
                        "id": "text_adventure",
                        "title": "Text Adventure Game",
                    },
                    {
                        "type": "project",
                        "id": "data_analysis",
                        "title": "Data Analysis Project",
                    },
                ],
            ),
        }

    def populate_learning_paths(self):
        """Populate the learning paths list"""
        self.paths_listbox.delete(0, tk.END)

        for path_id, path in self.learning_paths.items():
            self.paths_listbox.insert(tk.END, path.name)

    def on_path_select(self, event):
        """Handle learning path selection"""
        selection = self.paths_listbox.curselection()
        if not selection:
            return

        path_ids = list(self.learning_paths.keys())
        if selection[0] < len(path_ids):
            path_id = path_ids[selection[0]]
            path = self.learning_paths[path_id]

            # Display path details
            self.path_details_text.config(state=tk.NORMAL)
            self.path_details_text.delete(1.0, tk.END)

            content = f"{path.name}\n{'=' * len(path.name)}\n\n"
            content += f"Description: {path.description}\n\n"
            content += f"Lessons ({len(path.lessons)}):\n"

            for i, lesson in enumerate(path.lessons, 1):
                status = "✅" if i - 1 in path.completed_lessons else "⭕"
                content += f"{status} {i}. {lesson['title']}\n"

            content += f"\nProgress: {len(path.completed_lessons)}/{len(path.lessons)} lessons completed\n"
            content += f"Started: {path.started_date.strftime('%Y-%m-%d')}\n"
            content += f"Last accessed: {path.last_accessed.strftime('%Y-%m-%d')}\n"

            self.path_details_text.insert(1.0, content)
            self.path_details_text.config(state=tk.DISABLED)

    def start_learning_path(self):
        """Start selected learning path"""
        messagebox.showinfo(
            "Path Started", "Learning path started! Your progress will be tracked."
        )

    def view_path_progress(self):
        """View detailed progress for selected path"""
        messagebox.showinfo("Path Progress", "Detailed progress view would open here.")

    def pause_learning_path(self):
        """Pause selected learning path"""
        messagebox.showinfo("Path Paused", "Learning path paused. Resume anytime!")

    # Achievements methods
    def create_achievements_content(self):
        """Create achievements display content"""
        # This would create a scrollable frame with achievement badges
        achievements_frame = ttk.Frame(self.achievements_canvas)
        self.achievements_canvas.create_window(
            (0, 0), window=achievements_frame, anchor="nw"
        )

        # Sample achievements
        achievements = [
            {
                "name": "First Steps",
                "description": "Complete your first tutorial",
                "icon": "👶",
                "earned": True,
            },
            {
                "name": "Code Analyzer",
                "description": "Analyze 10 code samples",
                "icon": "🔍",
                "earned": False,
            },
            {
                "name": "Quality Coder",
                "description": "Achieve 90+ code quality score",
                "icon": "⭐",
                "earned": False,
            },
            {
                "name": "Explorer",
                "description": "Try all programming languages",
                "icon": "🚀",
                "earned": False,
            },
            {
                "name": "Persistent Learner",
                "description": "7-day learning streak",
                "icon": "🔥",
                "earned": False,
            },
        ]

        for i, achievement in enumerate(achievements):
            self.create_achievement_badge(achievements_frame, achievement, i)

        # Update scroll region
        achievements_frame.update_idletasks()
        self.achievements_canvas.configure(
            scrollregion=self.achievements_canvas.bbox("all")
        )

    def create_achievement_badge(self, parent, achievement, row):
        """Create an individual achievement badge"""
        frame = ttk.Frame(parent, relief="ridge", padding=10)
        frame.grid(row=row // 3, column=row % 3, padx=10, pady=10, sticky="ew")

        # Icon and status
        icon_label = ttk.Label(frame, text=achievement["icon"], font=("Arial", 24))
        icon_label.pack()

        # Name
        name_label = ttk.Label(
            frame, text=achievement["name"], font=("Arial", 12, "bold")
        )
        name_label.pack()

        # Description
        desc_label = ttk.Label(frame, text=achievement["description"], wraplength=150)
        desc_label.pack()

        # Status
        status = "🏆 EARNED" if achievement["earned"] else "🔒 LOCKED"
        status_label = ttk.Label(frame, text=status, font=("Arial", 10))
        status_label.pack(pady=(5, 0))

        # Color coding
        if achievement["earned"]:
            frame.configure(style="Earned.TFrame")

    def filter_achievements(self, event=None):
        """Filter achievements by category"""
        # This would update the achievements display based on category
        pass

    # Data persistence methods
    def _load_user_data(self):
        """Load user progress and settings"""
        try:
            data_file = os.path.join(
                os.path.expanduser("~"), ".james", "learning_assistant.json"
            )
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    data = json.load(f)
                    self.user_progress = data.get("progress", {})

                    # Load learning paths
                    paths_data = data.get("learning_paths", {})
                    for path_id, path_data in paths_data.items():
                        self.learning_paths[path_id] = LearningPath.from_dict(path_data)
        except Exception as e:
            print(f"Could not load user data: {e}")

    def _save_user_data(self):
        """Save user progress and settings"""
        try:
            # Ensure directory exists
            data_dir = os.path.join(os.path.expanduser("~"), ".james")
            os.makedirs(data_dir, exist_ok=True)

            # Prepare data
            data = {
                "progress": self.user_progress,
                "learning_paths": {
                    path_id: path.to_dict()
                    for path_id, path in self.learning_paths.items()
                },
                "last_saved": datetime.datetime.now().isoformat(),
            }

            # Save to file
            data_file = os.path.join(data_dir, "learning_assistant.json")
            with open(data_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Could not save user data: {e}")


# Plugin factory function
def create_plugin():
    """Factory function to create the plugin instance"""
    return LearningAssistantPlugin()
