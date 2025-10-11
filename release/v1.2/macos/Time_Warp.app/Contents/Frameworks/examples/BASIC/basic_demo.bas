10 REM Simple BASIC Demo Program
20 PRINT "JAMES BASIC Native Compiler Demo"
30 PRINT "================================"
40 PRINT ""

50 REM Variables and calculations
60 LET A = 5
70 LET B = 3
80 LET C = A * B
90 PRINT "A = "; A
100 PRINT "B = "; B
110 PRINT "A * B = "; C
120 PRINT ""

130 REM FOR loop
140 PRINT "Counting squares:"
150 FOR I = 1 TO 5
160 LET SQUARE = I * I
170 PRINT I; " squared = "; SQUARE
180 NEXT I
190 PRINT ""

200 REM Conditional logic
210 LET X = 10
220 IF X > 5 THEN PRINT "X is greater than 5"
230 IF X < 15 THEN PRINT "X is less than 15"
240 PRINT ""

250 REM Random numbers
260 PRINT "Random number: "; RND
270 PRINT "Another random: "; RND
280 PRINT ""

290 REM Subroutine
300 PRINT "Calling subroutine..."
310 GOSUB 1000
320 PRINT "Back from subroutine"
330 PRINT ""

340 PRINT "BASIC program completed successfully!"
350 END

1000 REM Subroutine
1010 PRINT "  -> Inside subroutine"
1020 PRINT "  -> GOSUB/RETURN works!"
1030 RETURN