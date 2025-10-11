10 PRINT "📊 Time_Warp IDE - BASIC Arrays Demo"
20 PRINT "===================================="
30 PRINT
40 PRINT "Working with arrays and data structures..."
50 PRINT
60
70 ' Define arrays
80 DIM SCORES(5)    ' Array for 5 scores
90 DIM NAMES$(5)    ' Array for 5 names
100
110 ' Input student data
120 PRINT "Enter information for 5 students:"
130 FOR I = 1 TO 5
140   PRINT "Student "; I; ":"
150   INPUT "  Name: "; NAMES$(I)
160   INPUT "  Score: "; SCORES(I)
170 NEXT I
180 PRINT
190
200 ' Display the data
210 PRINT "Student Report:"
220 PRINT "---------------"
230 TOTAL = 0
240 MAX_SCORE = 0
250 MIN_SCORE = 100
260 FOR I = 1 TO 5
270   PRINT NAMES$(I); ": "; SCORES(I)
280   TOTAL = TOTAL + SCORES(I)
290   IF SCORES(I) > MAX_SCORE THEN MAX_SCORE = SCORES(I)
300   IF SCORES(I) < MIN_SCORE THEN MIN_SCORE = SCORES(I)
310 NEXT I
320 PRINT
330
340 ' Calculate and display statistics
350 AVERAGE = TOTAL / 5
360 PRINT "Statistics:"
370 PRINT "  Total Score: "; TOTAL
380 PRINT "  Average Score: "; AVERAGE
390 PRINT "  Highest Score: "; MAX_SCORE
400 PRINT "  Lowest Score: "; MIN_SCORE
410 PRINT
420
430 ' Grade analysis
440 PRINT "Grade Analysis:"
450 A_COUNT = 0
460 B_COUNT = 0
470 C_COUNT = 0
480 F_COUNT = 0
490 FOR I = 1 TO 5
500   IF SCORES(I) >= 90 THEN A_COUNT = A_COUNT + 1
510   IF SCORES(I) >= 80 AND SCORES(I) < 90 THEN B_COUNT = B_COUNT + 1
520   IF SCORES(I) >= 70 AND SCORES(I) < 80 THEN C_COUNT = C_COUNT + 1
530   IF SCORES(I) < 70 THEN F_COUNT = F_COUNT + 1
540 NEXT I
550 PRINT "  A's (90-100): "; A_COUNT
560 PRINT "  B's (80-89): "; B_COUNT
570 PRINT "  C's (70-79): "; C_COUNT
580 PRINT "  F's (<70): "; F_COUNT
590 PRINT
600
610 PRINT "Arrays demo complete!"
620 END