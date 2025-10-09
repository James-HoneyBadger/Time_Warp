# JAMES III Language Specification

## Overview
JAMES III is a unified programming language that combines the best features of PILOT (text processing), BASIC (structured programming), Logo (turtle graphics), and Python integration into a single, cohesive language.

## Language Modes

### 1. BASIC Mode (Default)
Traditional BASIC-style programming with modern enhancements:
```james
10 LET X = 10
20 FOR I = 1 TO X
30   PRINT "Hello World ", I
40 NEXT I
50 END
```

### 2. PILOT Mode
Text processing and pattern matching:
```james
PILOT:
T: Enter your name
A: #NAME
M: #NAME = ""
J: END
T: Hello, #NAME!
END:
```

### 3. Logo Mode
Turtle graphics and geometric programming:
```james
LOGO:
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
```

### 4. Python Integration
Execute Python code within JAMES programs:
```james
PYTHON:
import math
result = math.sqrt(16)
JAMES.SET("SQRT_RESULT", result)
END_PYTHON

PRINT "Square root is: ", SQRT_RESULT
```

## Unified Syntax Elements

### Variables
- Global scope across all modes
- Automatic type conversion
- Shared between JAMES and Python

### Control Flow
```james
IF condition THEN
  statements
ELIF condition THEN
  statements
ELSE
  statements
ENDIF

WHILE condition
  statements
WEND

FOR variable = start TO end STEP increment
  statements
NEXT variable
```

### Functions
```james
DEF FUNCTION_NAME(param1, param2)
  REM Function body
  RETURN value
END_DEF

REM Call function
RESULT = FUNCTION_NAME(10, 20)
```

### Mode Switching
```james
REM Switch to different modes within the same program
MODE PILOT
  T: Processing text...
MODE LOGO
  FORWARD 50
  RIGHT 90
MODE BASIC
  PRINT "Back to BASIC"
```

## File Format
- Extension: `.james`
- UTF-8 encoding
- Line-based execution
- Support for multiline constructs

## Built-in Commands

### BASIC Commands
- LET, PRINT, INPUT, IF/THEN/ELSE, FOR/NEXT, WHILE/WEND
- GOSUB/RETURN, DATA/READ/RESTORE
- DIM (arrays), DEF (functions)

### PILOT Commands
- T: (type/output), A: (accept input), M: (match)
- J: (jump), C: (compute), U: (use)
- R: (remark), E: (end)

### Logo Commands
- FORWARD/FD, BACK/BK, LEFT/LT, RIGHT/RT
- PENUP/PU, PENDOWN/PD, SETCOLOR
- REPEAT, HOME, CLEARSCREEN/CS

### Python Integration
- PYTHON:/END_PYTHON blocks
- JAMES.GET(var) - get JAMES variable in Python
- JAMES.SET(var, value) - set JAMES variable from Python
- JAMES.CALL(function, args) - call JAMES function from Python

## Standard Library
- Math functions (SIN, COS, TAN, SQRT, etc.)
- String functions (LEFT$, RIGHT$, MID$, LEN, etc.)
- File I/O functions (OPEN, CLOSE, READ, WRITE)
- Graphics functions (PLOT, LINE, CIRCLE, etc.)
- System functions (TIME$, DATE$, SYSTEM)

## Error Handling
```james
TRY
  risky_operation()
CATCH error_type
  PRINT "Error: ", ERROR_MESSAGE$
FINALLY
  cleanup_operations()
END_TRY
```

## Comments
```james
REM This is a comment
' This is also a comment (single quote)
// C-style comments also supported
/* Multi-line comments
   are supported too */
```