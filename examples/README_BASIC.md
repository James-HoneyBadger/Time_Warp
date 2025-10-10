# Time_Warp IDE - Comprehensive BASIC Examples

This directory contains comprehensive BASIC programming examples that demonstrate
various commands, features, and programming concepts in the BASIC language.

## BASIC Language Overview

BASIC (Beginner's All-purpose Symbolic Instruction Code) is a family of general-purpose,
high-level programming languages designed for ease of use. Time_Warp IDE implements
a classic BASIC with line numbers and simple syntax.

Key features:

- Line numbers for program structure
- Simple variable naming (A-Z, A0-Z9)
- Built-in functions and commands
- GOTO for control flow
- PRINT for output
- INPUT for user interaction

## Basic Programs


### hello_world.bas
The classic first program in any language.

```basic
10 PRINT "Hello, World!"
20 PRINT "Welcome to BASIC programming!"
30 END
```


### variables.bas
Working with variables and data types.

```basic
10 REM Variable demonstration
20 LET A = 42
30 LET B$ = "Hello"
40 LET C = 3.14159
50 PRINT "Number: "; A
60 PRINT "String: "; B$
70 PRINT "Float: "; C
80 END
```

## Mathematical Operations


### calculator.bas
Basic calculator with multiple operations.

```basic
10 PRINT "BASIC Calculator"
20 PRINT "Operations:"
30 PRINT "1. Addition"
40 PRINT "2. Subtraction"
50 PRINT "3. Multiplication"
60 PRINT "4. Division"
70 INPUT "Choose operation (1-4): "; OP
80 INPUT "Enter first number: "; A
90 INPUT "Enter second number: "; B
100 IF OP = 1 THEN RESULT = A + B: PRINT A; " + "; B; " = "; RESULT
110 IF OP = 2 THEN RESULT = A - B: PRINT A; " - "; B; " = "; RESULT
120 IF OP = 3 THEN RESULT = A * B: PRINT A; " * "; B; " = "; RESULT
130 IF OP = 4 THEN RESULT = A / B: PRINT A; " / "; B; " = "; RESULT
140 END
```


### fibonacci.bas
Generating Fibonacci sequence.

```basic
10 PRINT "Fibonacci Sequence Generator"
20 INPUT "How many numbers to generate: "; N
30 A = 0
40 B = 1
50 PRINT A
60 PRINT B
70 FOR I = 3 TO N
80 C = A + B
90 PRINT C
100 A = B
110 B = C
120 NEXT I
130 END
```

## Control Structures


### loops.bas
Demonstrating different types of loops.

```basic
10 PRINT "BASIC Loop Demonstrations"
20 PRINT
30 PRINT "FOR Loop (1 to 5):"
40 FOR I = 1 TO 5
50 PRINT "Count: "; I
60 NEXT I
70 PRINT
80 PRINT "WHILE Loop simulation:"
90 I = 1
100 IF I > 5 THEN GOTO 130
110 PRINT "While count: "; I
120 I = I + 1: GOTO 100
130 PRINT
140 PRINT "Nested loops:"
150 FOR X = 1 TO 3
160 FOR Y = 1 TO 3
170 PRINT "X="; X; ", Y="; Y
180 NEXT Y
190 NEXT X
200 END
```


### conditions.bas
Conditional statements and decision making.

```basic
10 PRINT "BASIC Conditions Demo"
20 INPUT "Enter your age: "; AGE
30 IF AGE < 13 THEN PRINT "You are a child"
40 IF AGE >= 13 AND AGE < 20 THEN PRINT "You are a teenager"
50 IF AGE >= 20 AND AGE < 65 THEN PRINT "You are an adult"
60 IF AGE >= 65 THEN PRINT "You are a senior"
70 PRINT
80 INPUT "Enter a grade (A-F): "; GRADE$
90 IF GRADE$ = "A" THEN PRINT "Excellent!": SCORE = 4
100 IF GRADE$ = "B" THEN PRINT "Good job!": SCORE = 3
110 IF GRADE$ = "C" THEN PRINT "Satisfactory": SCORE = 2
120 IF GRADE$ = "D" THEN PRINT "Needs improvement": SCORE = 1
130 IF GRADE$ = "F" THEN PRINT "Failed": SCORE = 0
140 PRINT "Score: "; SCORE
150 END
```

## Games and Interactive Programs


### number_guessing.bas
Classic number guessing game.

```basic
10 PRINT "Number Guessing Game"
20 PRINT "I'm thinking of a number between 1 and 100"
30 SECRET = INT(RND(1) * 100) + 1
40 GUESSES = 0
50 PRINT
60 INPUT "Your guess: "; GUESS
70 GUESSES = GUESSES + 1
80 IF GUESS = SECRET THEN GOTO 120
90 IF GUESS < SECRET THEN PRINT "Too low! Try higher."
100 IF GUESS > SECRET THEN PRINT "Too high! Try lower."
110 GOTO 50
120 PRINT
130 PRINT "Congratulations! You got it!"
140 PRINT "The number was: "; SECRET
150 PRINT "Number of guesses: "; GUESSES
160 IF GUESSES <= 5 THEN PRINT "Excellent guessing!"
170 IF GUESSES > 5 AND GUESSES <= 10 THEN PRINT "Good job!"
180 IF GUESSES > 10 THEN PRINT "Better luck next time!"
190 END
```


### rock_paper_scissors.bas
Rock, Paper, Scissors game.

```basic
10 PRINT "Rock, Paper, Scissors Game"
20 PRINT "Choose: 1=Rock, 2=Paper, 3=Scissors"
30 INPUT "Your choice: "; PLAYER
40 COMPUTER = INT(RND(1) * 3) + 1
50 PRINT "Computer chose: ";
60 IF COMPUTER = 1 THEN PRINT "Rock"
70 IF COMPUTER = 2 THEN PRINT "Paper"
80 IF COMPUTER = 3 THEN PRINT "Scissors"
90 PRINT
100 IF PLAYER = COMPUTER THEN PRINT "It's a tie!": GOTO 10
110 IF PLAYER = 1 AND COMPUTER = 3 THEN PRINT "You win! Rock beats Scissors": GOTO 150
120 IF PLAYER = 2 AND COMPUTER = 1 THEN PRINT "You win! Paper beats Rock": GOTO 150
130 IF PLAYER = 3 AND COMPUTER = 2 THEN PRINT "You win! Scissors beats Paper": GOTO 150
140 PRINT "Computer wins!": GOTO 150
150 PRINT
160 INPUT "Play again? (Y/N): "; AGAIN$
170 IF AGAIN$ = "Y" OR AGAIN$ = "y" THEN GOTO 10
180 PRINT "Thanks for playing!"
190 END
```

## Graphics and Visual Programs


### simple_graphics.bas
Basic graphics using SCREEN and drawing commands.

```basic
10 SCREEN 12  ' Set graphics mode
20 CLS       ' Clear screen
30 PRINT "BASIC Graphics Demo"
40 CIRCLE (320, 240), 50, 15  ' Draw circle
50 PAINT (320, 240), 15       ' Fill circle
60 LINE (200, 200)-(400, 200), 14  ' Draw line
70 FOR I = 1 TO 10
80 CIRCLE (320 + I * 20, 240), 30, I + 1
90 NEXT I
100 SLEEP 3000  ' Wait 3 seconds
110 END
```


### pattern_drawing.bas
Creating patterns with loops and graphics.

```basic
10 SCREEN 12
20 CLS
30 PRINT "Pattern Drawing Demo"
40 FOR X = 50 TO 590 STEP 50
50 LINE (X, 50)-(X, 430), 15
60 NEXT X
70 FOR Y = 50 TO 430 STEP 50
80 LINE (50, Y)-(590, Y), 15
90 NEXT Y
100 FOR I = 1 TO 20
110 X = INT(RND(1) * 540) + 50
120 Y = INT(RND(1) * 380) + 50
130 RADIUS = INT(RND(1) * 20) + 5
140 COLOR = INT(RND(1) * 15) + 1
150 CIRCLE (X, Y), RADIUS, COLOR
160 NEXT I
170 SLEEP 5000
180 END
```

## Advanced Features


### arrays.bas
Working with arrays and data structures.

```basic
10 PRINT "BASIC Arrays Demo"
20 DIM SCORES(5)
30 DIM NAMES$(5)
40 PRINT "Enter 5 student scores:"
50 FOR I = 1 TO 5
60 PRINT "Student "; I; " name: ";
70 INPUT NAMES$(I)
80 PRINT "Score: ";
90 INPUT SCORES(I)
100 NEXT I
110 PRINT
120 PRINT "Results:"
130 TOTAL = 0
140 FOR I = 1 TO 5
150 PRINT NAMES$(I); ": "; SCORES(I)
160 TOTAL = TOTAL + SCORES(I)
170 NEXT I
180 AVERAGE = TOTAL / 5
190 PRINT
200 PRINT "Class average: "; AVERAGE
210 END
```


### file_operations.bas
Reading and writing to files (conceptual - implementation varies).

```basic
10 PRINT "File Operations Demo"
20 PRINT "This demonstrates file I/O concepts"
30 PRINT
40 PRINT "Writing to file..."
50 OPEN "data.txt" FOR OUTPUT AS #1
60 PRINT #1, "BASIC File Demo"
70 PRINT #1, "Line 2 of data"
80 PRINT #1, "Line 3 of data"
90 CLOSE #1
100 PRINT "Data written to file"
110 PRINT
120 PRINT "Reading from file..."
130 OPEN "data.txt" FOR INPUT AS #1
140 WHILE NOT EOF(1)
150 LINE INPUT #1, DATA$
160 PRINT DATA$
170 WEND
180 CLOSE #1
190 PRINT "File read complete"
200 END
```


### sorting.bas
Implementing sorting algorithms.

```basic
10 PRINT "BASIC Sorting Demo"
20 DIM NUMBERS(10)
30 PRINT "Generating random numbers..."
40 FOR I = 1 TO 10
50 NUMBERS(I) = INT(RND(1) * 100) + 1
60 NEXT I
70 PRINT "Original numbers:"
80 FOR I = 1 TO 10
90 PRINT NUMBERS(I); " ";
100 NEXT I
110 PRINT
120 PRINT "Sorting..."
130 FOR I = 1 TO 9
140 FOR J = I + 1 TO 10
150 IF NUMBERS(I) > NUMBERS(J) THEN SWAP NUMBERS(I), NUMBERS(J)
160 NEXT J
170 NEXT I
180 PRINT "Sorted numbers:"
190 FOR I = 1 TO 10
200 PRINT NUMBERS(I); " ";
210 NEXT I
220 PRINT
230 END
```

## Subroutines and Functions


### subroutines.bas
Using GOSUB for subroutines.

```basic
10 PRINT "BASIC Subroutines Demo"
20 GOSUB 1000  ' Call greeting subroutine
30 GOSUB 2000  ' Call calculation subroutine
40 GOSUB 3000  ' Call farewell subroutine
50 END

1000 REM Greeting subroutine
1010 PRINT "Hello! Welcome to the subroutine demo."
1020 PRINT "This is a reusable piece of code."
1030 RETURN

2000 REM Calculation subroutine
2010 PRINT
2020 INPUT "Enter a number: "; NUM
2030 RESULT = NUM * 2
2040 PRINT NUM; " doubled is "; RESULT
2050 RETURN

3000 REM Farewell subroutine
3010 PRINT
3020 PRINT "Thank you for using the subroutine demo!"
3030 PRINT "Subroutines help organize code."
3040 RETURN
```

## Running the Examples

To run these examples in Time_Warp IDE:

1. Launch Time_Warp IDE
2. Select "BASIC" from the language menu
3. Copy and paste any example code
4. Click Run → Execute
5. Follow any INPUT prompts in the output panel

## Learning Path

Start with simple examples and progress to complex ones:

1. **Beginner**: `hello_world.bas`, `variables.bas`
2. **Intermediate**: `calculator.bas`, `conditions.bas`
3. **Games**: `number_guessing.bas`, `rock_paper_scissors.bas`
4. **Graphics**: `simple_graphics.bas`, `pattern_drawing.bas`
5. **Advanced**: `arrays.bas`, `sorting.bas`, `subroutines.bas`

Each example includes comments explaining the BASIC commands and concepts used.
