# Time_Warp Multi-Language Support Specification

## Overview
Time_Warp IDE supports multiple distinct programming languages through separate interpreters: PILOT (text processing), BASIC (structured programming), Logo (turtle graphics), Python, JavaScript, and Perl. Each language operates independently with its own syntax and semantics.

## Supported Languages

### 1. BASIC Language
Traditional BASIC programming with line numbers (.bas files):
```basic
10 LET X = 10
20 FOR I = 1 TO X
30   PRINT "Hello World ", I
40 NEXT I
50 END
```

### 2. PILOT Language
Text processing and educational programming (.pilot files):
```pilot
T:Enter your name
A:#NAME
M:#NAME = ""
J:END
T:Hello, #NAME!
END:
```

### 3. Logo Language
Turtle graphics and geometric programming (.logo files):
```logo
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

### 4. Python Language
Modern Python scripting (.py files):
```python
import math
result = math.sqrt(16)
print(f"Square root is: {result}")
```

### 5. JavaScript Language
JavaScript programming (.js files):
```javascript
const result = Math.sqrt(16);
console.log(`Square root is: ${result}`);
```

### 6. Perl Language
Perl scripting (.pl files):
```perl
use Math::Complex;
my $result = sqrt(16);
print "Square root is: $result\n";
```

## Language Independence

Each language in Time_Warp operates independently:

### Separate Interpreters
- Each language has its own dedicated interpreter
- No shared variables between languages
- Each language maintains its own syntax and semantics
- Programs are written in one language per file

### File Extensions
- `.bas` - BASIC programs
- `.pilot` - PILOT programs  
- `.logo` - Logo programs
- `.py` - Python programs
- `.js` - JavaScript programs
- `.pl` - Perl programs

### Language Selection
- Users select the target language via the IDE's Language menu
- Language auto-detection based on file extension
- Each language runs in its own execution context

## Language-Specific Features

### BASIC Language Features
- Line-numbered programming (10, 20, 30, etc.)
- Commands: LET, PRINT, INPUT, IF/THEN/ELSE, FOR/NEXT, GOTO
- Variables and arrays
- Mathematical expressions and functions

### PILOT Language Features  
- Text processing and pattern matching
- Commands: T: (output), A: (input), M: (match), J: (jump)
- Variable interpolation with #NAME syntax
- Educational programming constructs

### Logo Language Features
- Turtle graphics programming
- Commands: FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN
- Recursive procedures and functions
- Mathematical and geometric operations

### Python Language Features
- Full Python 3 language support
- Standard library access
- Object-oriented programming
- Modern Python syntax and features

### JavaScript Language Features
- ECMAScript standard compliance
- Console output and basic I/O
- Modern JavaScript syntax
- Node.js runtime environment

### Perl Language Features
- Full Perl scripting support
- Regular expressions
- Text processing capabilities
- CPAN module system integration

## Time_Warp IDE Features

### Multi-Language Editor
- Syntax highlighting for each language
- Language-specific auto-completion
- File extension-based language detection
- Integrated development environment

### Execution Environment
- Separate interpreters for each language
- Graphics canvas for turtle graphics (Logo, PILOT)
- Console output for all languages
- Error reporting and debugging support