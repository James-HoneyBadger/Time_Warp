# Time_Warp IDE - Comprehensive Logo Examples

This directory contains comprehensive Logo programming examples that demonstrate
various commands, features, and programming concepts in the Logo language.

## Logo Language Overview

Logo is an educational programming language known for its turtle graphics capabilities.
It uses a turtle that can move around the screen, drawing lines as it goes. Logo
emphasizes procedural programming, recursion, and mathematical concepts.

## Basic Movement Commands

### simple_shapes.logo
Basic geometric shapes using fundamental movement commands.

```logo
; Simple Shapes Demo
; Demonstrates basic turtle movement

; Draw a square
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90

; Move to new position
PENUP
FORWARD 150
PENDOWN

; Draw a triangle
FORWARD 100
RIGHT 120
FORWARD 100
RIGHT 120
FORWARD 100
RIGHT 120
```

### movement_demo.logo
Comprehensive demonstration of all movement commands.

```logo
; Movement Commands Demo
; Shows all basic movement and drawing commands

; Setup
CLEARSCREEN
PENUP
SETXY -200 100
SETHEADING 0
PENDOWN

; Basic movement
FORWARD 50
BACK 25
RIGHT 45
LEFT 90

; Pen control
PENUP
FORWARD 50
PENDOWN

; Heading commands
SETH 90
FORWARD 50
SETH 180
FORWARD 50
SETH 270
FORWARD 50
SETH 0
FORWARD 50
```

## Procedures and Functions

### procedures.logo
Creating and using custom procedures.

```logo
; Procedures Demo
; Shows how to define and use custom procedures

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

; Use the procedures
SQUARE 50
TRIANGLE 60
POLYGON 6 40
```

### recursive_patterns.logo
Advanced recursive procedures for complex patterns.

```logo
; Recursive Patterns
; Demonstrates recursion in Logo

TO TREE :SIZE
  IF :SIZE < 5 [STOP]
  FORWARD :SIZE
  RIGHT 25
  TREE :SIZE * 0.7
  LEFT 50
  TREE :SIZE * 0.7
  RIGHT 25
  BACK :SIZE
END

TO SPIRAL :SIZE :ANGLE :LIMIT
  IF :SIZE > :LIMIT [STOP]
  FORWARD :SIZE
  RIGHT :ANGLE
  SPIRAL :SIZE + 2 :ANGLE :LIMIT
END

; Draw recursive tree
PENUP
SETXY -100 -100
SETHEADING 90
PENDOWN
TREE 80

; Draw spiral
PENUP
SETXY 100 -100
PENDOWN
SPIRAL 1 15 100
```

## Color and Styling

### colors.logo
Using colors and pen styling.

```logo
; Colors and Styling Demo
; Shows color commands and pen properties

; Set up color palette
SETPC 1    ; Red
FORWARD 50
RIGHT 90

SETPC 2    ; Blue
FORWARD 50
RIGHT 90

SETPC 3    ; Green
FORWARD 50
RIGHT 90

SETPC 4    ; Yellow
FORWARD 50
RIGHT 90

; Pen size variations
SETPENSIZE [1 1]
FORWARD 30
SETPENSIZE [3 3]
FORWARD 30
SETPENSIZE [5 5]
FORWARD 30
```

### rainbow_spiral.logo
Creating colorful spiral patterns.

```logo
; Rainbow Spiral
; Colorful recursive spiral pattern

TO RAINBOW_SPIRAL :SIZE :ANGLE :COLOR
  IF :SIZE > 150 [STOP]
  SETPC :COLOR
  FORWARD :SIZE
  RIGHT :ANGLE
  RAINBOW_SPIRAL :SIZE + 1 :ANGLE MODULO (:COLOR + 1) 16
END

; Start the rainbow spiral
PENUP
SETXY 0 0
PENDOWN
RAINBOW_SPIRAL 1 23 1
```

## Mathematical Concepts

### geometry.logo
Exploring geometric patterns and mathematical relationships.

```logo
; Geometry Demo
; Mathematical patterns and relationships

TO CIRCLE_PATTERN :RADIUS :COUNT
  REPEAT :COUNT [
    PENUP
    FORWARD :RADIUS
    PENDOWN
    CIRCLE :RADIUS
    PENUP
    BACK :RADIUS
    RIGHT 360 / :COUNT
  ]
END

TO FRACTAL_SNOWFLAKE :SIZE :LEVEL
  IF :LEVEL = 0 [FORWARD :SIZE STOP]
  FRACTAL_SNOWFLAKE :SIZE/3 :LEVEL-1
  LEFT 60
  FRACTAL_SNOWFLAKE :SIZE/3 :LEVEL-1
  RIGHT 120
  FRACTAL_SNOWFLAKE :SIZE/3 :LEVEL-1
  LEFT 60
  FRACTAL_SNOWFLAKE :SIZE/3 :LEVEL-1
END

; Draw concentric circles
CIRCLE_PATTERN 20 8

; Move to new position
PENUP
SETXY 150 0
PENDOWN

; Draw fractal snowflake
FRACTAL_SNOWFLAKE 100 4
```

### fibonacci.logo
Fibonacci sequence visualization.

```logo
; Fibonacci Spiral
; Visualizing the Fibonacci sequence

TO FIB_SPIRAL :A :B :COUNT
  IF :COUNT = 0 [STOP]
  FORWARD :A
  RIGHT 90
  FIB_SPIRAL :B :A + :B :COUNT - 1
END

TO FIB_RECTANGLES :A :B :COUNT
  IF :COUNT = 0 [STOP]
  REPEAT 2 [
    FORWARD :A
    RIGHT 90
    FORWARD :B
    RIGHT 90
  ]
  FIB_RECTANGLES :B :A + :B :COUNT - 1
END

; Draw Fibonacci rectangles
PENUP
SETXY -150 -100
PENDOWN
FIB_RECTANGLES 5 8 8

; Draw Fibonacci spiral
PENUP
SETXY 50 -100
SETHEADING 90
PENDOWN
FIB_SPIRAL 5 8 8
```

## Interactive Programs

### interactive_drawing.logo
Mouse and keyboard interaction.

```logo
; Interactive Drawing
; Mouse and keyboard controlled drawing

TO SETUP
  CLEARSCREEN
  SETPENSIZE [3 3]
  SETPC 4
  PENUP
  SETXY 0 0
  PENDOWN
END

TO DRAW_LOOP
  IF MOUSEPRESSED [
    SETXY MOUSEX MOUSEY
  ]
  DRAW_LOOP
END

TO CHANGE_COLOR
  SETPC MODULO (PC + 1) 16
END

TO CLEAR_CANVAS
  CLEARSCREEN
  SETUP
END

; Setup and start
SETUP
DRAW_LOOP
```

### keyboard_control.logo
Keyboard input and control.

```logo
; Keyboard Control Demo
; Using keyboard input for control

TO SETUP
  CLEARSCREEN
  SETPENSIZE [5 5]
  SETPC 2
  PENUP
  SETXY 0 0
  PENDOWN
END

TO MOVE_FORWARD
  FORWARD 10
END

TO MOVE_BACK
  BACK 10
END

TO TURN_LEFT
  LEFT 15
END

TO TURN_RIGHT
  RIGHT 15
END

TO CHANGE_COLOR
  SETPC MODULO (PC + 1) 16
END

TO PEN_TOGGLE
  IF PENDOWNP [PENUP] [PENDOWN]
END

; Setup
SETUP

; Main control loop (would be event-driven in full implementation)
; W - forward, S - back, A - left, D - right
; C - color change, P - pen toggle
```

## Advanced Techniques

### lsystems.logo
L-Systems for generating complex patterns.

```logo
; L-Systems Demo
; Using formal grammar systems for patterns

TO DRAW_LINE
  FORWARD 10
END

TO TURN_LEFT_25
  LEFT 25
END

TO TURN_RIGHT_25
  RIGHT 25
END

TO SAVE_POSITION
  ; In full Logo, this would push position to stack
END

TO RESTORE_POSITION
  ; In full Logo, this would pop position from stack
END

; Simple plant-like structure
TO PLANT :GENERATION
  IF :GENERATION = 0 [FORWARD 20 STOP]
  FORWARD 10
  RIGHT 25
  PLANT :GENERATION - 1
  LEFT 50
  PLANT :GENERATION - 1
  RIGHT 25
  BACK 10
END

; Draw plant
PENUP
SETXY 0 -150
SETHEADING 90
PENDOWN
PLANT 4
```

### physics_simulation.logo
Simple physics simulation concepts.

```logo
; Physics Simulation
; Basic concepts of motion and physics

TO GRAVITY_BALL :HEIGHT
  ; Simulate ball dropping with gravity
  LOCAL "VELOCITY
  MAKE "VELOCITY 0

  REPEAT :HEIGHT / 5 [
    FORWARD :VELOCITY
    MAKE "VELOCITY :VELOCITY + 2  ; Gravity acceleration
    RIGHT 1  ; Slight rotation for realism
  ]
END

TO BOUNCE_BALL :HEIGHT :BOUNCES
  IF :BOUNCES = 0 [STOP]
  GRAVITY_BALL :HEIGHT
  RIGHT 180  ; Bounce back up
  BOUNCE_BALL :HEIGHT * 0.7 :BOUNCES - 1  ; Energy loss
END

; Demonstrate bouncing ball
PENUP
SETXY -100 100
SETHEADING 270  ; Point down
PENDOWN
BOUNCE_BALL 50 5
```

## File I/O and Data

### data_persistence.logo
Saving and loading data (conceptual - Logo implementations vary).

```logo
; Data Persistence Demo
; Concepts for saving and loading data

TO SAVE_POSITION
  ; In full Logo implementation:
  ; PRINT [POSITION] POS
  ; Would save current position to file
END

TO LOAD_POSITION
  ; In full Logo implementation:
  ; SETPOS LOAD "position.data"
  ; Would load position from file
END

TO SAVE_DRAWING
  ; Save current drawing commands
  ; This is conceptual - actual implementation varies
END

TO LOAD_DRAWING
  ; Load and replay drawing commands
  ; This is conceptual - actual implementation varies
END
```

## Running the Examples

To run these examples in Time_Warp IDE:

1. Launch Time_Warp IDE
2. Select "Logo" from the language menu
3. Copy and paste any example code
4. Click Run → Execute
5. Watch the turtle graphics in the canvas panel

## Learning Path

Start with simple examples and progress to complex ones:

1. **Beginner**: `simple_shapes.logo`, `movement_demo.logo`
2. **Intermediate**: `procedures.logo`, `colors.logo`
3. **Advanced**: `recursive_patterns.logo`, `geometry.logo`
4. **Expert**: `lsystems.logo`, `physics_simulation.logo`

Each example includes comments explaining the concepts and commands used.