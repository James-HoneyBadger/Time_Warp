10 PRINT "🔄 Time_Warp IDE - BASIC Loops Demo"
20 PRINT "==================================="
30 PRINT
40 PRINT "Demonstrating different types of loops:"
50 PRINT
60
70 PRINT "1. FOR Loop - Counting from 1 to 5:"
80 FOR I = 1 TO 5
90   PRINT "   Count: "; I
100 NEXT I
110 PRINT
120
130 PRINT "2. WHILE Loop simulation - Even numbers:"
140 I = 2
150 IF I > 10 THEN GOTO 170
160 PRINT "   Even: "; I
170 I = I + 2
180 GOTO 150
190 PRINT
200
210 PRINT "3. Nested loops - Multiplication table:"
220 FOR X = 1 TO 5
230   FOR Y = 1 TO 5
240     RESULT = X * Y
250     PRINT "   "; X; " × "; Y; " = "; RESULT;
260     IF Y < 5 THEN PRINT ",";
270   NEXT Y
280   PRINT
290 NEXT X
300 PRINT
310
320 PRINT "4. Loop with STEP - Counting by 3:"
330 FOR I = 3 TO 15 STEP 3
340   PRINT "   Step: "; I
350 NEXT I
360 PRINT
370
380 PRINT "5. Conditional loop - Fibonacci sequence:"
390 A = 0
400 B = 1
410 PRINT "   Fibonacci: "; A; ", "; B;
420 FOR I = 1 TO 8
430   C = A + B
440   PRINT ", "; C;
450   A = B
460   B = C
470 NEXT I
480 PRINT
490 PRINT
500
510 PRINT "Loops demo complete!"
520 END