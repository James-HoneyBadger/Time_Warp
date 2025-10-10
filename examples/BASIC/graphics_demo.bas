10 PRINT "🎨 Time_Warp IDE - BASIC Graphics Demo"
20 PRINT "====================================="
30 PRINT
40 SCREEN 12  ' Set graphics mode (640x480)
50 CLS       ' Clear screen
60 PRINT "Drawing geometric shapes..."
70 PRINT
80 ' Draw a filled circle in the center
90 CIRCLE (320, 240), 80, 15  ' Circle at center with radius 80, color 15
100 PAINT (320, 240), 15      ' Fill the circle
110 SLEEP 1000                ' Wait 1 second
120
130 ' Draw a rectangle
140 LINE (200, 150)-(440, 330), 14, B  ' Rectangle with border
150 SLEEP 1000
160
170 ' Draw some colorful circles in a pattern
180 FOR I = 1 TO 8
190   X = 320 + COS(I * 45 * 3.14159 / 180) * 120
200   Y = 240 + SIN(I * 45 * 3.14159 / 180) * 120
210   CIRCLE (X, Y), 25, I + 1
220   PAINT (X, Y), I + 1
230 NEXT I
240 SLEEP 2000
250
260 ' Draw a star pattern
270 FOR I = 1 TO 12
280   X1 = 320 + COS(I * 30 * 3.14159 / 180) * 60
290   Y1 = 240 + SIN(I * 30 * 3.14159 / 180) * 60
300   X2 = 320 + COS(I * 30 * 3.14159 / 180) * 150
310   Y2 = 240 + SIN(I * 30 * 3.14159 / 180) * 150
320   LINE (X1, Y1)-(X2, Y2), 12
330 NEXT I
340 SLEEP 3000
350
360 PRINT "Graphics demo complete!"
370 PRINT "Press any key to exit..."
380 INPUT ""; DUMMY$
390 END