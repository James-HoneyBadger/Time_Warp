10 PRINT "BASIC Native Compiler Test"
20 PRINT "=========================="
30 PRINT "What is your name?"
40 INPUT NAME
50 PRINT "Hello, "; NAME; "!"
60 PRINT "Enter a number from 1 to 10:"
70 INPUT NUMBER
80 IF NUMBER = 7 THEN GOTO 120
90 PRINT "You entered: "; NUMBER
100 PRINT "That's not 7!"
110 GOTO 130
120 PRINT "Lucky number 7!"
130 PRINT "Let's count from 1 to 5:"
140 FOR I = 1 TO 5
150 PRINT "Count: "; I
160 NEXT I
170 PRINT "Program completed successfully!"
180 END