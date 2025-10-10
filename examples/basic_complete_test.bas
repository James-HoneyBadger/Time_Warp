' Comprehensive BASIC Language Test
' Tests all major BASIC commands and features

REM === Variable Assignment and Operations ===
LET X = 10
LET Y = 20
LET Z = X + Y
PRINT "X ="; X; "Y ="; Y; "Z ="; Z

REM === String Operations ===
LET NAME$ = "BASIC"
LET GREETING$ = "Hello " + NAME$
PRINT GREETING$

REM === Input and Output ===
PRINT "Testing INPUT command:"
INPUT "Enter your name: "; USERNAME$
PRINT "Hello "; USERNAME$; "!"

REM === Conditional Statements ===
IF X > Y THEN PRINT "X is greater than Y"
IF X < Y THEN PRINT "X is less than Y"
IF X = Y THEN 
    PRINT "X equals Y"
ELSE
    PRINT "X does not equal Y"
END IF

REM === For Loops ===
PRINT "Counting from 1 to 5:"
FOR I = 1 TO 5
    PRINT "Count: "; I
NEXT I

PRINT "Counting by 2s from 2 to 10:"
FOR J = 2 TO 10 STEP 2
    PRINT "Even: "; J
NEXT J

REM === While Loops ===
LET K = 1
PRINT "While loop test:"
WHILE K <= 3
    PRINT "While K ="; K
    LET K = K + 1
WEND

REM === Arrays (DIM) ===
DIM NUMBERS(5)
FOR I = 1 TO 5
    LET NUMBERS(I) = I * I
NEXT I

PRINT "Array contents:"
FOR I = 1 TO 5
    PRINT "NUMBERS("; I; ") ="; NUMBERS(I)
NEXT I

REM === Subroutines ===
GOSUB 1000
PRINT "Back from subroutine"
GOTO 2000

1000 REM Subroutine
PRINT "Inside subroutine"
RETURN

2000 REM Continue after subroutine
PRINT "Program continues..."

REM === Functions ===
LET R = RND(1)
PRINT "Random number: "; R
LET S = INT(3.7)
PRINT "INT(3.7) = "; S

REM === Final Test ===
PRINT "All BASIC commands tested successfully!"
END