# BASIC Language Reference

## Overview

BASIC (Beginners All-purpose Symbolic Instruction Code) is a classic programming language designed for simplicity and ease of learning. Time_Warp IDE implements a comprehensive BASIC dialect with modern enhancements.

## Program Structure

BASIC programs use line numbers and are executed sequentially:

```
10 PRINT "Hello, World!"
20 END
```

## Data Types

### Numbers
- **Integers**: `42`, `-15`
- **Floating Point**: `3.14`, `-2.5`
- **Scientific Notation**: `1.23E-4`

### Strings
- Enclosed in quotes: `"Hello"`, `"Name: "`
- Concatenation: `"Hello" + " World"`

### Arrays
- Declared with `DIM`: `DIM SCORES(10)`
- Accessed with parentheses: `SCORES(5) = 100`

## Variables

### Naming Rules
- Start with a letter
- Can contain letters, numbers, and underscores
- Case-insensitive
- Maximum 40 characters

### Examples
```basic
10 LET NAME$ = "Alice"
20 LET AGE = 25
30 LET PI = 3.14159
40 DIM SCORES(5)
```

## Operators

### Arithmetic
- `+` : Addition
- `-` : Subtraction
- `*` : Multiplication
- `/` : Division
- `^` : Exponentiation
- `MOD` : Modulo

### Comparison
- `=` : Equal to
- `<>` : Not equal to
- `<` : Less than
- `<=` : Less than or equal
- `>` : Greater than
- `>=` : Greater than or equal

### Logical
- `AND` : Logical AND
- `OR` : Logical OR
- `NOT` : Logical NOT

## Statements

### PRINT
Display text and variables:
```basic
10 PRINT "Hello, World!"
20 PRINT "The answer is: "; 42
30 PRINT NAME$; " is "; AGE; " years old"
```

### INPUT
Get user input:
```basic
10 INPUT "Enter your name: ", NAME$
20 INPUT "Enter a number: ", NUM
```

### LET
Assign values to variables:
```basic
10 LET X = 10
20 LET NAME$ = "Bob"
30 LET RESULT = X * 2 + 5
```

### IF-THEN-ELSE
Conditional execution:
```basic
10 IF AGE >= 18 THEN PRINT "Adult" ELSE PRINT "Minor"
20 IF SCORE > 90 THEN
30     PRINT "Excellent!"
40     GRADE$ = "A"
50 ELSEIF SCORE > 80 THEN
60     PRINT "Good job!"
70     GRADE$ = "B"
80 ELSE
90     PRINT "Keep trying!"
100     GRADE$ = "C"
110 END IF
```

### FOR-NEXT
Loop with counter:
```basic
10 FOR I = 1 TO 10
20     PRINT "Count: "; I
30 NEXT I

40 FOR X = 0 TO 100 STEP 10
50     PRINT X
60 NEXT X
```

### WHILE-WEND
Conditional loops:
```basic
10 WHILE COUNT < 10
20     PRINT COUNT
30     COUNT = COUNT + 1
40 WEND
```

### GOTO
Unconditional jump:
```basic
10 PRINT "Start"
20 GOTO 50
30 PRINT "This won't print"
40 END
50 PRINT "End"
```

### GOSUB-RETURN
Subroutines:
```basic
10 PRINT "Main program"
20 GOSUB 100
30 PRINT "Back in main"
40 END

100 PRINT "In subroutine"
110 RETURN
```

### DIM
Declare arrays:
```basic
10 DIM NUMBERS(10)
20 DIM NAMES$(5)
30 DIM MATRIX(3, 3)
```

## Functions

### Mathematical Functions
- `SIN(X)` : Sine of X (degrees)
- `COS(X)` : Cosine of X (degrees)
- `TAN(X)` : Tangent of X (degrees)
- `ATN(X)` : Arctangent of X
- `SQR(X)` : Square root of X
- `ABS(X)` : Absolute value of X
- `INT(X)` : Integer part of X
- `EXP(X)` : e raised to X
- `LOG(X)` : Natural logarithm of X

### String Functions
- `LEN(S$)` : Length of string S$
- `LEFT$(S$, N)` : Left N characters of S$
- `RIGHT$(S$, N)` : Right N characters of S$
- `MID$(S$, P, N)` : N characters from position P in S$
- `STR$(X)` : String representation of number X
- `VAL(S$)` : Numeric value of string S$

### Other Functions
- `RND` : Random number between 0 and 1
- `RND(N)` : Random integer from 1 to N
- `TAB(N)` : Tab to column N

## Examples

### Simple Calculator
```basic
10 PRINT "BASIC Calculator"
20 PRINT "Operations: +, -, *, /"
30 INPUT "Enter first number: ", A
40 INPUT "Enter operation: ", OP$
50 INPUT "Enter second number: ", B
60 IF OP$ = "+" THEN RESULT = A + B
70 IF OP$ = "-" THEN RESULT = A - B
80 IF OP$ = "*" THEN RESULT = A * B
90 IF OP$ = "/" THEN RESULT = A / B
100 PRINT "Result: "; RESULT
110 END
```

### Number Guessing Game
```basic
10 PRINT "Number Guessing Game"
20 SECRET = INT(RND * 100) + 1
30 GUESSES = 0
40 PRINT "I'm thinking of a number between 1 and 100"
50 INPUT "Your guess: ", GUESS
60 GUESSES = GUESSES + 1
70 IF GUESS = SECRET THEN GOTO 100
80 IF GUESS < SECRET THEN PRINT "Too low!"
90 IF GUESS > SECRET THEN PRINT "Too high!"
95 GOTO 50
100 PRINT "Correct! You took"; GUESSES; "guesses"
110 END
```

### Array Operations
```basic
10 DIM SCORES(5)
20 PRINT "Enter 5 test scores:"
30 FOR I = 1 TO 5
40     PRINT "Score"; I; ": ";
50     INPUT SCORES(I)
60 NEXT I
70 TOTAL = 0
80 FOR I = 1 TO 5
90     TOTAL = TOTAL + SCORES(I)
100 NEXT I
110 AVERAGE = TOTAL / 5
120 PRINT "Average score: "; AVERAGE
130 END
```

### String Processing
```basic
10 INPUT "Enter your full name: ", FULLNAME$
20 SPACE_POS = INSTR(FULLNAME$, " ")
30 IF SPACE_POS > 0 THEN
40     FIRST$ = LEFT$(FULLNAME$, SPACE_POS - 1)
50     LAST$ = MID$(FULLNAME$, SPACE_POS + 1, LEN(FULLNAME$) - SPACE_POS)
60     PRINT "First name: "; FIRST$
70     PRINT "Last name: "; LAST$
80 ELSE
90     PRINT "Please enter first and last name"
100 END IF
110 END
```

## Error Handling

BASIC programs will display runtime errors:
- Division by zero
- Array index out of bounds
- Undefined variables
- Type mismatches

## Best Practices

1. **Use meaningful variable names**
2. **Add comments with REM**
3. **Structure programs with subroutines**
4. **Validate user input**
5. **Use arrays for related data**
6. **Test with different inputs**

## Compatibility

Time_Warp BASIC is compatible with classic BASIC while adding modern enhancements:
- Long variable names
- Nested IF statements
- WHILE loops
- Enhanced string functions
- Better error messages

## See Also

- [BASIC Sample Programs](../../samples/basic/)
- [Time_Warp IDE User Guide](../user_guide.md)
- [Compiler Documentation](../compiler.md)