# Time_Warp IDE - Comprehensive PILOT Examples

This directory contains comprehensive PILOT (Programmed Inquiry, Learning Or Teaching)
programming examples that demonstrate various commands, features, and programming
concepts in the PILOT language.

## PILOT Language Overview

PILOT is an educational programming language designed for interactive learning and
teaching. It emphasizes structured programming with commands for:
- Text output (T:)
- User input (A:)
- Computations (C:)
- Jumps and control flow (J:, Y:, N:)
- Comments (R:)

## Basic Commands

### hello_world.pilot
Basic text output and program structure.

```pilot
R: Hello World Program
R: Demonstrates basic PILOT text output

*START
T: Hello, World!
T: Welcome to PILOT programming!
T: This is a simple demonstration program.
E:
```

### variables_and_math.pilot
Working with variables and mathematical operations.

```pilot
R: Variables and Math Demo
R: Shows variable assignment and arithmetic operations

*START
T: PILOT Calculator Demo
T:

C: #NUM1 = 15
C: #NUM2 = 7
C: #SUM = #NUM1 + #NUM2
C: #DIFF = #NUM1 - #NUM2
C: #PROD = #NUM1 * #NUM2
C: #QUOT = #NUM1 / #NUM2

T: First number: #NUM1
T: Second number: #NUM2
T: Sum: #SUM
T: Difference: #DIFF
T: Product: #PROD
T: Quotient: #QUOT
E:
```

## Interactive Programs

### user_input.pilot
Getting input from the user and responding.

```pilot
R: User Input Demo
R: Shows how to get input from the user

*START
T: What's your name?

A: Please enter your name
T: Hello, *ANS!
T: Nice to meet you.
T:
T: How old are you?

A: Enter your age
C: #AGE = *ANS
C: #NEXT_YEAR = #AGE + 1

T: You are #AGE years old.
T: Next year you will be #NEXT_YEAR years old!
E:
```

### simple_quiz.pilot
Creating an interactive quiz with conditional responses.

```pilot
R: Simple Quiz Program
R: Demonstrates conditional logic and user interaction

*START
T: PILOT Quiz Program
T: Let's test your knowledge!
T:

T: Question 1: What is 2 + 2?

A: Your answer
J: (*ANS = 4) *CORRECT1
T: Sorry, that's not correct. The answer is 4.
J: *QUESTION2

*CORRECT1
T: Excellent! 2 + 2 = 4
C: #SCORE = 1

*QUESTION2
T: Question 2: What color is the sky on a clear day?

A: Your answer
J: (*ANS = BLUE) *CORRECT2
J: (*ANS = blue) *CORRECT2
T: Actually, the sky appears blue due to light scattering.
J: *FINAL

*CORRECT2
T: Correct! The sky is blue.
C: #SCORE = #SCORE + 1

*FINAL
T: Quiz complete!
T: Your score: #SCORE out of 2
J: (#SCORE = 2) *PERFECT
T: Good job!
E:

*PERFECT
T: Perfect score! You're a PILOT expert!
E:
```

## Control Flow

### loops_and_conditions.pilot
Demonstrating loops and conditional statements.

```pilot
R: Loops and Conditions Demo
R: Shows conditional jumps and counting loops

*START
T: PILOT Control Flow Demo
T:

C: #COUNT = 1
C: #TOTAL = 0

*LOOP
T: Count: #COUNT
C: #TOTAL = #TOTAL + #COUNT
C: #COUNT = #COUNT + 1
J: (#COUNT <= 5) *LOOP

T: Total sum: #TOTAL
T:
T: Now let's check if the total is even or odd...

C: #REMAINDER = #TOTAL % 2
J: (#REMAINDER = 0) *EVEN
T: The total is odd.
E:

*EVEN
T: The total is even.
E:
```

### number_guessing.pilot
A complete number guessing game with loops.

```pilot
R: Number Guessing Game
R: Interactive game demonstrating loops and conditions

*START
T: PILOT Number Guessing Game
T: I'm thinking of a number between 1 and 10.
T:

C: #SECRET = 7
C: #GUESSES = 0

*GUESS_LOOP
C: #GUESSES = #GUESSES + 1
T: Guess ##GUESSES:

A: Enter your guess (1-10)
C: #GUESS = *ANS

J: (#GUESS = #SECRET) *WIN
J: (#GUESS < #SECRET) *TOO_LOW
J: (#GUESS > #SECRET) *TOO_HIGH

*TOO_LOW
T: Too low! Try higher.
J: *GUESS_LOOP

*TOO_HIGH
T: Too high! Try lower.
J: *GUESS_LOOP

*WIN
T: Congratulations! You guessed it!
T: The number was #SECRET
T: It took you #GUESSES guesses.
J: (#GUESSES = 1) *LUCKY
T: Good job!
E:

*LUCKY
T: Wow! You got it on the first try!
T: Are you psychic?
E:
```

## Turtle Graphics

### basic_graphics.pilot
Introduction to PILOT turtle graphics.

```pilot
R: Basic Turtle Graphics
R: Introduction to PILOT drawing commands

*START
T: PILOT Turtle Graphics Demo
T: Watch the turtle draw!
T:

FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90

T: Square complete!
T:

PENUP
FORWARD 150
PENDOWN

FORWARD 80
RIGHT 120
FORWARD 80
RIGHT 120
FORWARD 80
RIGHT 120

T: Triangle complete!
E:
```

### complex_drawing.pilot
Advanced turtle graphics with patterns.

```pilot
R: Complex Drawing Patterns
R: Advanced turtle graphics with loops and patterns

*START
T: PILOT Complex Drawing Demo
T:

C: #SIZE = 50
C: #SIDES = 3

*SHAPE_LOOP
T: Drawing shape with #SIDES sides, size #SIZE

C: #ANGLE = 360 / #SIDES
C: #I = 1

*DRAW_LOOP
FORWARD #SIZE
RIGHT #ANGLE
C: #I = #I + 1
J: (#I <= #SIDES) *DRAW_LOOP

PENUP
FORWARD #SIZE + 20
PENDOWN

C: #SIDES = #SIDES + 1
J: (#SIDES <= 8) *SHAPE_LOOP

T: All shapes drawn!
E:
```

## Advanced Features

### calculator.pilot
A complete calculator program.

```pilot
R: PILOT Calculator
R: Full-featured calculator with multiple operations

*START
T: PILOT Calculator
T: Choose an operation:
T: 1. Addition
T: 2. Subtraction
T: 3. Multiplication
T: 4. Division

A: Enter choice (1-4)
C: #CHOICE = *ANS

T: Enter first number:
A: First number
C: #NUM1 = *ANS

T: Enter second number:
A: Second number
C: #NUM2 = *ANS

J: (#CHOICE = 1) *ADD
J: (#CHOICE = 2) *SUBTRACT
J: (#CHOICE = 3) *MULTIPLY
J: (#CHOICE = 4) *DIVIDE
T: Invalid choice!
J: *START

*ADD
C: #RESULT = #NUM1 + #NUM2
T: #NUM1 + #NUM2 = #RESULT
J: *CONTINUE

*SUBTRACT
C: #RESULT = #NUM1 - #NUM2
T: #NUM1 - #NUM2 = #RESULT
J: *CONTINUE

*MULTIPLY
C: #RESULT = #NUM1 * #NUM2
T: #NUM1 * #NUM2 = #RESULT
J: *CONTINUE

*DIVIDE
J: (#NUM2 = 0) *DIVIDE_ZERO
C: #RESULT = #NUM1 / #NUM2
T: #NUM1 / #NUM2 = #RESULT
J: *CONTINUE

*DIVIDE_ZERO
T: Error: Cannot divide by zero!
J: *CONTINUE

*CONTINUE
T: Calculate again? (Y/N)
A: Your choice
J: (*ANS = Y) *START
J: (*ANS = y) *START
T: Goodbye!
E:
```

### grade_calculator.pilot
Student grade calculation program.

```pilot
R: Grade Calculator
R: Calculates student grades and GPA

*START
T: PILOT Grade Calculator
T: Enter grades for 5 subjects (A, B, C, D, F)
T:

C: #TOTAL_POINTS = 0
C: #SUBJECT_COUNT = 5

T: Subject 1 grade:
A: Enter grade (A/B/C/D/F)
J: (*ANS = A) *GRADE_A_1
J: (*ANS = B) *GRADE_B_1
J: (*ANS = C) *GRADE_C_1
J: (*ANS = D) *GRADE_D_1
J: (*ANS = F) *GRADE_F_1
T: Invalid grade! Use A, B, C, D, or F
J: *START

*GRADE_A_1
C: #TOTAL_POINTS = #TOTAL_POINTS + 4
J: *SUBJECT_2

*GRADE_B_1
C: #TOTAL_POINTS = #TOTAL_POINTS + 3
J: *SUBJECT_2

*GRADE_C_1
C: #TOTAL_POINTS = #TOTAL_POINTS + 2
J: *SUBJECT_2

*GRADE_D_1
C: #TOTAL_POINTS = #TOTAL_POINTS + 1
J: *SUBJECT_2

*GRADE_F_1
C: #TOTAL_POINTS = #TOTAL_POINTS + 0
J: *SUBJECT_2

*SUBJECT_2
T: Subject 2 grade:
A: Enter grade (A/B/C/D/F)
C: #POINTS = 0
J: (*ANS = A) *ADD_4
J: (*ANS = B) *ADD_3
J: (*ANS = C) *ADD_2
J: (*ANS = D) *ADD_1
J: (*ANS = F) *ADD_0

*ADD_4
C: #POINTS = 4
J: *ADD_POINTS

*ADD_3
C: #POINTS = 3
J: *ADD_POINTS

*ADD_2
C: #POINTS = 2
J: *ADD_POINTS

*ADD_1
C: #POINTS = 1
J: *ADD_POINTS

*ADD_0
C: #POINTS = 0
J: *ADD_POINTS

*ADD_POINTS
C: #TOTAL_POINTS = #TOTAL_POINTS + #POINTS
C: #GPA = #TOTAL_POINTS / #SUBJECT_COUNT

T: Total points: #TOTAL_POINTS
T: GPA: #GPA

J: (#GPA >= 3.5) *EXCELLENT
J: (#GPA >= 3.0) *GOOD
J: (#GPA >= 2.0) *AVERAGE
T: Academic probation recommended.
E:

*EXCELLENT
T: Excellent work! Dean's List material!
E:

*GOOD
T: Good job! Keep up the good work!
E:

*AVERAGE
T: Satisfactory performance.
E:
```

## File I/O and Data

### data_storage.pilot
Basic data storage concepts (conceptual - PILOT implementations vary).

```pilot
R: Data Storage Demo
R: Concepts for storing and retrieving data

*START
T: PILOT Data Storage Demo
T: This demonstrates data persistence concepts
T:

C: #STUDENT_COUNT = 3
C: #TOTAL_SCORE = 0

T: Enter student scores:
T:

T: Student 1 score:
A: Enter score
C: #SCORE1 = *ANS
C: #TOTAL_SCORE = #TOTAL_SCORE + #SCORE1

T: Student 2 score:
A: Enter score
C: #SCORE2 = *ANS
C: #TOTAL_SCORE = #TOTAL_SCORE + #SCORE2

T: Student 3 score:
A: Enter score
C: #SCORE3 = *ANS
C: #TOTAL_SCORE = #TOTAL_SCORE + #SCORE3

C: #AVERAGE = #TOTAL_SCORE / #STUDENT_COUNT

T: Scores entered: #SCORE1, #SCORE2, #SCORE3
T: Total: #TOTAL_SCORE
T: Average: #AVERAGE

T: Data would be saved to file in full PILOT implementation
E:
```

## Running the Examples

To run these examples in Time_Warp IDE:

1. Launch Time_Warp IDE
2. Select "PILOT" from the language menu
3. Copy and paste any example code
4. Click Run → Execute
5. Follow any prompts in the output panel

## Learning Path

Start with simple examples and progress to complex ones:

1. **Beginner**: `hello_world.pilot`, `variables_and_math.pilot`
2. **Intermediate**: `user_input.pilot`, `simple_quiz.pilot`
3. **Advanced**: `calculator.pilot`, `grade_calculator.pilot`
4. **Graphics**: `basic_graphics.pilot`, `complex_drawing.pilot`

Each example includes comments explaining the PILOT commands and concepts used.