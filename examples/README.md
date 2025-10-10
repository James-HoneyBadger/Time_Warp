# TimeWarp IDE Examples

This directory contains sample programs demonstrating TimeWarp IDE's capabilities across different programming languages.

## 📁 Directory Structure

### `BASIC/` - BASIC Language Examples
- `basic_demo.bas` - Simple "Hello World" and basic operations
- `basic_complete_test.bas` - Comprehensive BASIC feature test
- `calculator.bas` - Simple calculator implementation
- `graphics_demo.bas` - BASIC graphics demonstrations
- `number_guessing.bas` - Number guessing game
- `loops_demo.bas` - FOR/WHILE loop examples
- `arrays_demo.bas` - Array manipulation examples
- `test_*.bas` - Various test programs

### `PILOT/` - PILOT Language Examples
- `pilot_demo.pilot` - Introduction to PILOT commands
- `pilot_complete_test.pilot` - Full PILOT language test
- `pilot_feature_test.pilot` - Advanced PILOT features
- `calculator.pilot` - Calculator in PILOT
- `test_*.pilot` - Test programs for specific features

### `Logo/` - Logo Language Examples
- `logo_demo.logo` - Basic turtle graphics
- `logo_complete_test.logo` - Comprehensive Logo test
- `flower.logo` - Draw a flower pattern
- `spiral.logo` - Spiral drawing
- `square.logo` - Square and geometric shapes
- `shapes.logo` - Various shape demonstrations
- `simple_shapes.logo` - Basic shape drawing
- `test_*.logo` - Logo test programs

### `TimeWarp/` - Multi-Language Programs (.timewarp)
- `hello.timewarp` - Hello World in multiple languages
- `multimode_demo.timewarp` - Demonstrates language switching
- `galaga_*.timewarp` - Galaga game implementations
- `graphics_test.timewarp` - Graphics testing across languages
- `turtle_test.timewarp` - Turtle graphics demo
- `pilot_demo.timewarp` - PILOT demonstration
- `python_demo.timewarp` - Python integration demo

### `Python/` - Python Integration Examples
- `demo_galaga.py` - Galaga game in Python
- `demo_learning_assistant.py` - AI learning assistant
- `demo_refactored.py` - Refactored code examples
- `pygame_graphics_test.py` - PyGame graphics testing
- `simple_graphics_test.py` - Simple graphics demonstrations

### `JavaScript/` - JavaScript Examples
- JavaScript integration examples (coming soon)

### `Perl/` - Perl Examples  
- Perl integration examples (coming soon)

## 🚀 Getting Started

### Running Examples

```bash
# Install TimeWarp IDE
pip install timewarp-ide

# Compile and run a BASIC program
timewarp-compiler BASIC/basic_demo.bas -o hello
./hello

# Compile and run a PILOT program
timewarp-compiler PILOT/pilot_demo.pilot -o pilot_demo
./pilot_demo

# Compile and run a Logo program
timewarp-compiler Logo/square.logo -o square
./square

# Run a multi-language TimeWarp program
timewarp-compiler TimeWarp/hello.timewarp -o hello_multi
./hello_multi
```

### Example Progression

**Beginners Start Here:**
1. `BASIC/basic_demo.bas` - Simple Hello World
2. `PILOT/pilot_demo.pilot` - Basic PILOT commands  
3. `Logo/square.logo` - First turtle graphics
4. `TimeWarp/hello.timewarp` - Multi-language intro

**Intermediate Examples:**
1. `BASIC/calculator.bas` - Input/output and math
2. `PILOT/calculator.pilot` - Conditional logic
3. `Logo/flower.logo` - Complex graphics
4. `TimeWarp/multimode_demo.timewarp` - Language mixing

**Advanced Examples:**
1. `BASIC/arrays_demo.bas` - Data structures
2. `PILOT/pilot_feature_test.pilot` - Advanced features
3. `Logo/logo_complete_test.logo` - Full Logo capabilities
4. `TimeWarp/galaga_game.timewarp` - Complete game

## 📚 Language-Specific Documentation

- `README_BASIC.md` - Detailed BASIC language guide
- `README_PILOT.md` - Comprehensive PILOT reference
- `README_Logo.md` - Logo programming tutorial

## 🎮 Featured Programs

### Galaga Game Series
Three versions of the classic Galaga game:
- `galaga_simple.timewarp` - Basic version
- `galaga_basic.timewarp` - Enhanced gameplay
- `galaga_game.timewarp` - Full-featured implementation

### Educational Calculators
Calculator implementations across languages:
- `BASIC/calculator.bas` - BASIC version
- `PILOT/calculator.pilot` - PILOT version

### Graphics Demonstrations
Turtle graphics across languages:
- `Logo/flower.logo` - Beautiful flower pattern
- `Logo/spiral.logo` - Mathematical spiral
- `TimeWarp/graphics_test.timewarp` - Cross-language graphics

## 🛠️ Development

### Adding New Examples

1. **Choose appropriate subdirectory** based on primary language
2. **Follow naming convention**: `descriptive_name.extension`
3. **Include comments** explaining the program
4. **Test compilation** with TimeWarp IDE
5. **Update this README** with new example description

### File Extensions
- `.bas` - BASIC programs
- `.pilot` - PILOT programs  
- `.logo` - Logo programs
- `.timewarp` - Multi-language programs
- `.py` - Python integration examples

## 📖 Learning Path

### 1. Start with Hello World
```basic
10 PRINT "Hello, TimeWarp!"
20 END
```

### 2. Learn Basic Input/Output
```pilot
T:What's your name?
A:name
T:Hello, #name#!
```

### 3. Try Turtle Graphics
```logo
FORWARD 100
RIGHT 90
FORWARD 100
```

### 4. Combine Languages
```timewarp
LANGUAGE BASIC
10 PRINT "Starting..."

LANGUAGE LOGO  
FORWARD 50
RIGHT 90

LANGUAGE PILOT
T:Program complete!
```

## 🎯 Tips for Success

- **Start simple** - Begin with basic examples
- **Read the code** - All examples are well-commented
- **Experiment** - Modify examples to learn
- **Mix languages** - Try .timewarp files for advanced features
- **Check documentation** - Refer to language-specific README files

Happy coding with TimeWarp IDE! 🚀