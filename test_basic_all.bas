10 REM Comprehensive BASIC Commands Test
20 PRINT "=== BASIC COMMANDS TEST ==="
30 PRINT

40 REM Variable assignment
50 LET A = 42
60 B = 24
70 PRINT "Variables: A ="; A; ", B ="; B

80 REM Mathematical operations
90 LET SUM = A + B
100 LET DIFF = A - B
110 LET PROD = A * B
120 LET QUOT = A / B
130 PRINT "Math: SUM ="; SUM; ", DIFF ="; DIFF; ", PROD ="; PROD; ", QUOT ="; QUOT

140 REM Mathematical functions
150 PRINT "SIN(45°) ="; SIN(45)
160 PRINT "COS(0°) ="; COS(0)
170 PRINT "TAN(45°) ="; TAN(45)
180 PRINT "SQRT(16) ="; SQRT(16)
190 PRINT "ABS(-5) ="; ABS(-5)
200 PRINT "INT(3.7) ="; INT(3.7)
210 PRINT "RND() ="; RND()

220 REM String operations
230 LET NAME$ = "HELLO"
240 PRINT "String: "; NAME$
250 PRINT "LEN("; NAME$; ") ="; LEN(NAME$)
260 PRINT "LEFT("; NAME$; ", 3) ="; LEFT(NAME$, 3)
270 PRINT "RIGHT("; NAME$; ", 2) ="; RIGHT(NAME$, 2)
280 PRINT "MID("; NAME$; ", 2, 3) ="; MID(NAME$, 2, 3)
290 PRINT "INSTR("; NAME$; ", LL) ="; INSTR(NAME$, "LL")
300 PRINT "STR$(123) ="; STR$(123)
310 PRINT "VAL('456') ="; VAL("456")

320 REM Arrays
330 DIM NUMBERS(5)
340 FOR I = 0 TO 4
350 LET NUMBERS(I) = I * 10
360 NEXT I
370 PRINT "Array elements:"
380 FOR I = 0 TO 4
390 PRINT "NUMBERS("; I; ") ="; NUMBERS(I)
400 NEXT I

410 REM Array operations
420 SORT NUMBERS
430 PRINT "Sorted array:"
440 FOR I = 0 TO 4
450 PRINT "NUMBERS("; I; ") ="; NUMBERS(I)
460 NEXT I

470 PRINT "SUM of array ="; SUM(NUMBERS)
480 PRINT "AVG of array ="; AVG(NUMBERS)
490 PRINT "MIN of array ="; MIN(NUMBERS)
500 PRINT "MAX of array ="; MAX(NUMBERS)
510 PRINT "FIND 20 in array ="; FIND(NUMBERS, 20)

520 REM Conditional statements
530 IF A > B THEN PRINT "A > B is true"
540 IF A < B THEN PRINT "A < B is true" ELSE PRINT "A >= B is true"

550 REM Nested FOR loops
560 PRINT "Nested FOR loops:"
570 FOR X = 1 TO 3
580 FOR Y = 1 TO 2
590 PRINT "X="; X; ", Y="; Y
600 NEXT Y
610 NEXT X

620 REM GOTO and labels
630 PRINT "Testing GOTO:"
640 GOTO 660
650 PRINT "This should not print"
660 PRINT "GOTO worked!"

670 REM GOSUB and RETURN
680 PRINT "Testing GOSUB:"
690 GOSUB 710
700 PRINT "Back from subroutine"
710 PRINT "Inside subroutine"
720 RETURN

730 REM INPUT statement
740 PRINT "Testing INPUT:"
750 INPUT "Enter a number: "; VALUE
760 PRINT "You entered:"; VALUE

770 REM Graphics commands (text-based simulation)
780 PRINT "Testing graphics commands:"
790 LINE (10,10)-(50,50), "black"
800 BOX (100,100), 30, 20, 0
810 TRIANGLE (200,200)-(220,180)-(240,200), 1
820 ELLIPSE (300,300), 25, 15, 0
830 FILL (150,150), "blue"

840 REM Sound commands (simulated)
850 PRINT "Testing sound commands:"
860 BEEP 440, 0.5
870 PLAY "C4", 0.5
880 SOUND 880, 1.0, 0.8
890 NOTE "D", 4, 0.3

900 PRINT
910 PRINT "=== ALL BASIC TESTS COMPLETED ==="
920 END