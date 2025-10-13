10 PRINT "Welcome to the TW BASIC Calculator!"
20 PRINT "Enter two numbers:"
30 INPUT A
40 INPUT B
50 PRINT "Choose an operation:"
60 PRINT "1. Addition"
70 PRINT "2. Subtraction"
80 PRINT "3. Multiplication"
90 PRINT "4. Division"
100 INPUT OP
110 IF OP = 1 THEN LET RESULT = A + B
120 IF OP = 2 THEN LET RESULT = A - B
130 IF OP = 3 THEN LET RESULT = A * B
140 IF OP = 4 THEN IF B <> 0 THEN LET RESULT = A / B ELSE PRINT "Error: Division by zero" : GOTO 200
150 PRINT "The result is: "; RESULT
200 PRINT "Do you want to calculate again? (Y/N)"
210 INPUT ANSWER$
220 IF ANSWER$ = "Y" THEN GOTO 20
230 PRINT "Goodbye!"
240 END