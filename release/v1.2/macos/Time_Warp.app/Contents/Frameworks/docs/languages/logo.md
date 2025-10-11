# Logo Language Reference

## Overview

Logo is an educational programming language famous for its turtle graphics. Programs control a virtual turtle that draws on the screen using simple movement commands. Time_Warp IDE implements a comprehensive Logo dialect with modern enhancements.

## Basic Concepts

### The Turtle
- An invisible cursor that moves around the screen
- Can draw lines as it moves
- Has a position (X, Y coordinates)
- Has a heading (direction in degrees)
- Can have its pen up or down

### Coordinate System
- Origin (0, 0) is the center of the screen
- Positive X is right, positive Y is up
- Angles measured counterclockwise from positive X axis
- Screen bounds: -200 to 200 in both X and Y

## Commands

### Movement

#### FORWARD / FD
Move turtle forward by specified distance:
```
FORWARD 100
FD 50
```

#### BACK / BK
Move turtle backward by specified distance:
```
BACK 50
BK 25
```

#### LEFT / LT
Turn turtle left by specified angle in degrees:
```
LEFT 90
LT 45
```

#### RIGHT / RT
Turn turtle right by specified angle in degrees:
```
RIGHT 90
RT 45
```

### Pen Control

#### PENDOWN / PD
Put the pen down to draw lines:
```
PENDOWN
PD
```

#### PENUP / PU
Lift the pen up to move without drawing:
```
PENUP
PU
```

#### SETPENCOLOR / SETPC
Set the pen color (0-15):
```
SETPENCOLOR 1
SETPC 15
```

### Position and Heading

#### SETXY
Move turtle to absolute coordinates:
```
SETXY 100 50
SETXY -50 -25
```

#### SETX
Set X coordinate, keep Y the same:
```
SETX 100
```

#### SETY
Set Y coordinate, keep X the same:
```
SETY 50
```

#### SETHEADING / SETH
Set turtle heading in degrees:
```
SETHEADING 0    ; Point right
SETH 90         ; Point up
SETH 180        ; Point left
SETH 270        ; Point down
```

### Information

#### XCOR
Get current X coordinate:
```
PRINT XCOR
```

#### YCOR
Get current Y coordinate:
```
PRINT YCOR
```

#### HEADING
Get current heading in degrees:
```
PRINT HEADING
```

#### PENCOLOR
Get current pen color:
```
PRINT PENCOLOR
```

## Procedures

### Defining Procedures

#### TO ... END
Define a reusable procedure:
```
TO SQUARE :SIZE
  REPEAT 4 [FORWARD :SIZE RIGHT 90]
END
```

#### Calling Procedures
Execute a defined procedure:
```
SQUARE 100
SQUARE 50
```

### Parameters
Procedures can accept parameters (prefixed with colon):
```
TO TRIANGLE :SIZE :ANGLE
  REPEAT 3 [FORWARD :SIZE RIGHT :ANGLE]
END

TRIANGLE 100 120
```

## Control Structures

### REPEAT
Execute commands multiple times:
```
REPEAT 4 [FORWARD 50 RIGHT 90]  ; Square
REPEAT 3 [FORWARD 60 RIGHT 120] ; Triangle
```

### IF
Conditional execution:
```
IF :SIZE > 10 [FORWARD :SIZE]
IF color = "red [SETPENCOLOR 1]
```

### WHILE
Loop while condition is true:
```
WHILE :count < 10 [
  FORWARD 10
  MAKE "count :count + 1
]
```

### FOR
Counted loop:
```
FOR [i 1 10] [PRINT :i]
FOR [x 0 100 10] [FORWARD :x RIGHT 90]
```

## Variables

### MAKE
Create or change a variable:
```
MAKE "size 100
MAKE "color "red
MAKE "count 0
```

### Variable Access
Access variables with colon prefix:
```
MAKE "length 50
FORWARD :length
```

### Local Variables
Variables in procedures are local by default:
```
TO DRAWBOX :size
  MAKE "half :size / 2
  FORWARD :half
  RIGHT 90
  ; half is only available in this procedure
END
```

## Mathematical Operations

### Basic Arithmetic
```
MAKE "a 10
MAKE "b 20
MAKE "sum :a + :b
MAKE "diff :a - :b
MAKE "prod :a * :b
MAKE "quot :a / :b
```

### Advanced Math
```
MAKE "result SIN 45    ; Sine (degrees)
MAKE "root SQRT 16     ; Square root
MAKE "power 2 ^ 3      ; Exponentiation
MAKE "abs ABS -5       ; Absolute value
MAKE "round ROUND 3.7  ; Round to nearest integer
```

## Lists

### Creating Lists
```
MAKE "numbers [1 2 3 4 5]
MAKE "colors [red green blue]
```

### List Operations
```
MAKE "first FIRST :numbers    ; Get first item
MAKE "rest BUTFIRST :numbers  ; Remove first item
MAKE "count COUNT :numbers    ; Get length
MAKE "item ITEM 3 :numbers    ; Get nth item
```

## Examples

### Basic Shapes

#### Square
```
TO SQUARE :size
  REPEAT 4 [FORWARD :size RIGHT 90]
END

SQUARE 100
```

#### Circle
```
TO CIRCLE :radius
  REPEAT 36 [FORWARD (2 * 3.14159 * :radius / 36) RIGHT 10]
END

CIRCLE 50
```

#### Triangle
```
TO TRIANGLE :size
  REPEAT 3 [FORWARD :size RIGHT 120]
END

TRIANGLE 80
```

### Complex Drawings

#### Flower
```
TO PETAL :size
  REPEAT 2 [
    FORWARD :size
    RIGHT 60
    FORWARD :size
    RIGHT 120
  ]
END

TO FLOWER
  REPEAT 6 [
    PETAL 50
    RIGHT 60
  ]
END

FLOWER
```

#### Spiral
```
TO SPIRAL :size :angle :steps
  REPEAT :steps [
    FORWARD :size
    RIGHT :angle
    MAKE "size :size + 2
  ]
END

SPIRAL 5 20 50
```

#### Star
```
TO STAR :size
  REPEAT 5 [
    FORWARD :size
    RIGHT 144
  ]
END

STAR 100
```

### Fractals

#### Tree
```
TO TREE :size
  IF :size < 5 [STOP]
  FORWARD :size
  RIGHT 25
  TREE :size * 0.7
  LEFT 50
  TREE :size * 0.7
  RIGHT 25
  BACK :size
END

TREE 100
```

#### Snowflake
```
TO SIDE :size :level
  IF :level = 0 [FORWARD :size] [
    SIDE :size/3 :level-1
    LEFT 60
    SIDE :size/3 :level-1
    RIGHT 120
    SIDE :size/3 :level-1
    LEFT 60
    SIDE :size/3 :level-1
  ]
END

TO SNOWFLAKE :size
  REPEAT 3 [
    SIDE :size 3
    RIGHT 120
  ]
END

SNOWFLAKE 150
```

### Interactive Programs

#### Drawing Program
```
TO DRAW
  PENDOWN
  WHILE [TRUE] [
    IF MOUSEPRESSED [
      SETXY MOUSEX MOUSEY
    ]
  ]
END

DRAW
```

#### Color Changer
```
TO COLORCYCLE
  MAKE "color 0
  WHILE [TRUE] [
    SETPENCOLOR :color
    MAKE "color MODULO (:color + 1) 16
    WAIT 10
  ]
END

COLORCYCLE
```

## Color Reference

| Number | Color    | Number | Color     |
|--------|----------|--------|-----------|
| 0      | Black    | 8      | Gray      |
| 1      | Blue     | 9      | Light Blue|
| 2      | Green    | 10     | Light Green|
| 3      | Cyan     | 11     | Light Cyan|
| 4      | Red      | 12     | Light Red |
| 5      | Magenta  | 13     | Light Magenta|
| 6      | Yellow   | 14     | Light Yellow|
| 7      | White    | 15     | Bright White|

## Best Practices

1. **Use procedures** to organize code
2. **Choose meaningful names** for procedures and variables
3. **Use parameters** to make procedures flexible
4. **Start simple** and build complexity gradually
5. **Test procedures** individually before combining
6. **Use comments** to explain complex logic

## Error Handling

Logo programs handle errors gracefully:
- Invalid coordinates are clamped to screen bounds
- Division by zero returns infinity
- Missing procedures show error messages
- Type mismatches are converted automatically

## Advanced Features

### Recursion
Procedures can call themselves:
```
TO COUNTDOWN :n
  IF :n > 0 [
    PRINT :n
    COUNTDOWN :n - 1
  ]
END

COUNTDOWN 10
```

### Higher-Order Functions
```
TO APPLY :func :list
  IF NOT EMPTY? :list [
    RUN (SENTENCE :func FIRST :list)
    APPLY :func BUTFIRST :list
  ]
END

APPLY [PRINT] [1 2 3 4 5]
```

### Dynamic Procedure Creation
```
MAKE "procname "MYPROC
DEFINE :procname [[x] [PRINT :x * 2]]
MYPROC 21  ; Prints 42
```

## Compatibility

Time_Warp Logo extends classic Logo with:
- Enhanced graphics capabilities
- Better error handling
- Modern programming constructs
- Improved performance
- Additional mathematical functions

## See Also

- [Logo Sample Programs](../../samples/logo/)
- [Time_Warp IDE User Guide](../user_guide.md)
- [Compiler Documentation](../compiler.md)