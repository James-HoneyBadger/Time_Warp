10 PRINT "Time_Warp IDE - BASIC Calculator Demo"
20 PRINT "=================================="
30 PRINT
40 PRINT "Operations available:"
50 PRINT "1. Addition (+)"
60 PRINT "2. Subtraction (-)"
70 PRINT "3. Multiplication (*)"
80 PRINT "4. Division (/)"
90 PRINT "5. Exponentiation (^)"
100 PRINT
110 INPUT "Choose operation (1-5): "; OP
120 IF OP < 1 OR OP > 5 THEN PRINT "Invalid choice!": GOTO 110
130 INPUT "Enter first number: "; A
140 INPUT "Enter second number: "; B
150 PRINT
160 PRINT "Calculating..."
170 PRINT
180 IF OP = 1 THEN RESULT = A + B: PRINT A; " + "; B; " = "; RESULT
190 IF OP = 2 THEN RESULT = A - B: PRINT A; " - "; B; " = "; RESULT
200 IF OP = 3 THEN RESULT = A * B: PRINT A; " * "; B; " = "; RESULT
210 IF OP = 4 THEN RESULT = A / B: PRINT A; " / "; B; " = "; RESULT
220 IF OP = 5 THEN RESULT = A ^ B: PRINT A; " ^ "; B; " = "; RESULT
230 PRINT
240 INPUT "Calculate again? (Y/N): "; AGAIN$
250 IF AGAIN$ = "Y" OR AGAIN$ = "y" THEN GOTO 10
260 PRINT
270 PRINT "Thanks for using the BASIC Calculator!"
280 END