# Time_Warp IDE: Educational Programming Environment with Multi-Language Support

**Show HN:** Built an educational IDE that brings classic programming languages (PILOT, BASIC, Logo) into a modern development environment! 🚀

## What is Time_Warp IDE?

Time_Warp IDE is a comprehensive educational programming environment designed for learning fundamental programming concepts. It supports 6 programming languages including three foundational educational languages from the 1960s alongside modern ones, all in a unified tkinter-based IDE.

## Supported Languages

### **Classic Educational Languages:**
- **PILOT (1962)** - Educational language with turtle graphics and branching logic
- **BASIC (1964)** - Line-numbered programming with arrays and control structures  
- **Logo (1967)** - Turtle graphics programming with procedures and recursion

### **Modern Languages:**
- **Python** - Full Python 3 support with built-in execution
- **JavaScript** - Client-side scripting capabilities
- **Perl** - Text processing and scripting

## Key Features

✅ **Unified IDE** - Single environment for multiple languages  
✅ **Turtle Graphics** - Built-in canvas for Logo and PILOT graphics  
✅ **Educational Focus** - Perfect for computer science teaching  
✅ **Theme System** - 8 built-in themes (4 dark, 4 light)  
✅ **Plugin Architecture** - Extensible with custom functionality  
✅ **Open Source** - MIT licensed, contributions welcome  
✅ **Cross-Platform** - Runs on Linux, Windows, macOS  

## Why This Matters

Most programming education today jumps straight to modern languages without understanding the foundational concepts. Time_Warp IDE lets students and educators explore the evolution of programming languages while working in a modern, feature-rich environment.

## Quick Demo

```bash
# Clone and run
git clone https://github.com/James-HoneyBadger/Time_Warp.git
cd Time_Warp
python Time_Warp.py

# Or with auto-environment setup
./start_timewarp.sh
```

## Sample Programs Showcase

**BASIC with Arrays:**
```basic
10 DIM SCORES(10)
20 FOR I = 1 TO 10
30   SCORES(I) = I * 15 + RND(20)
40 NEXT I
50 PRINT "Game Scores:"
60 FOR I = 1 TO 10
70   PRINT "Player "; I; ": "; SCORES(I)
80 NEXT I
90 END
```

**Logo Recursive Graphics:**
```logo
TO FRACTAL_TREE :SIZE :DEPTH
  IF :DEPTH = 0 [STOP]
  FORWARD :SIZE
  LEFT 30
  FRACTAL_TREE :SIZE * 0.7 :DEPTH - 1
  RIGHT 60
  FRACTAL_TREE :SIZE * 0.7 :DEPTH - 1
  LEFT 30
  BACK :SIZE
END

FRACTAL_TREE 100 5
```

**PILOT Interactive Quiz:**
```pilot
R: Programming Quiz System

*START
T: What year was BASIC created?
A: Your answer
C: #CORRECT = 1964
J: (#ANS = #CORRECT) *RIGHT
T: Try again! BASIC was created in the 1960s.
J: *START

*RIGHT
T: Correct! BASIC was created in 1964 at Dartmouth.
T: Quiz complete!
E:
```

## Technical Architecture

### **Multi-Language Interpreter System:**
- **Central Time_WarpInterpreter** - Unified execution engine
- **Language-Specific Executors** - Dedicated handlers for each language
- **Shared Canvas System** - Common turtle graphics for Logo/PILOT
- **Plugin Manager** - Extensible architecture for custom tools

### **Modern Development Features:**
- **Syntax Highlighting** - Language-aware code coloring
- **Error Handling** - Detailed error messages and debugging
- **File Management** - Support for all standard file operations
- **Theme Engine** - Persistent user customization
- **Testing Framework** - Comprehensive test coverage

## Use Cases

🎓 **Education** - Teach programming fundamentals and language evolution  
🏫 **Classrooms** - All-in-one solution for programming courses  
🔍 **Research** - Study language design and compiler implementation  
🎮 **Gaming** - Built-in game engine for 2D game development  
👥 **Learning Groups** - Collaborative programming environment  

## Advanced Features

### **Game Development Engine**
```
games/engine/
├── game_objects.py    # Sprite and object management
├── physics.py         # 2D physics simulation  
├── game_renderer.py   # Graphics rendering
└── examples/          # Sample games
```

### **Plugin System**
```
plugins/
├── sample_plugin/          # Plugin template
├── advanced_debugger/      # Visual debugging tools
├── learning_assistant/     # AI-powered help system
└── hardware_controller/    # IoT/hardware integration
```

### **Educational Tools**
- **Tutorial System** - Interactive programming lessons
- **Gamification** - Achievement system and progress tracking
- **AI Assistant** - Context-aware programming help
- **Performance Monitor** - Real-time execution analysis

## Installation & Requirements

```bash
# Requirements: Python 3.8+, tkinter
pip install -r requirements.txt

# Run with auto-environment setup
python Time_Warp.py

# Or use the shell script
./start_timewarp.sh
```

**Dependencies:**
- `tkinter` - GUI framework (usually pre-installed)
- `pygame` - Graphics and game development (optional)
- `numpy` - Mathematical operations (optional)
- `PIL` - Image processing (optional)

## Project Status & CI/CD

✅ **Continuous Integration** - GitHub Actions with Python 3.9-3.12 testing  
✅ **Code Quality** - Black formatting and comprehensive testing  
✅ **Documentation** - Complete API docs and user guides  
✅ **Release Management** - Semantic versioning and automated releases  

## Community & Contributions

Time_Warp IDE is actively developed and welcomes contributions! Whether you want to:
- Add support for new programming languages
- Develop plugins for specialized functionality  
- Improve the educational content and tutorials
- Enhance the graphics and game engine
- Port to additional platforms

Your contributions help make programming education more accessible!

## Links

- **GitHub Repository:** https://github.com/James-HoneyBadger/Time_Warp
- **CI/CD Pipeline:** https://github.com/James-HoneyBadger/Time_Warp/actions
- **Documentation:** https://github.com/James-HoneyBadger/Time_Warp/tree/main/docs
- **Issues & Feature Requests:** https://github.com/James-HoneyBadger/Time_Warp/issues

## Roadmap

### **Short Term:**
- Web-based IDE version
- Additional language support (Pascal, FORTRAN)
- Enhanced debugging tools
- Mobile companion app

### **Long Term:**
- Cloud-based collaborative editing
- VR/AR programming environment
- Hardware integration expansion
- AI-powered code generation

---

**Time_Warp IDE** - Bridging the gap between programming history and modern development! Experience the evolution of programming languages in one powerful educational environment. 🌟

#programming #education #ide #python #opensource #computerscience #retrocomputing