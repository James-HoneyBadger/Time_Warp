10 REM BASIC Game - Number Guessing Game
20 REM This program demonstrates BASIC programming
30 REM Initialize variables
40 SECRET = INT(RND(1) * 100) + 1
50 ATTEMPTS = 0
60 MAX_ATTEMPTS = 7
70 REM Game introduction
80 PRINT "Welcome to the Number Guessing Game!"
90 PRINT "I'm thinking of a number between 1 and 100."
100 PRINT "You have"; MAX_ATTEMPTS; "attempts to guess it."
110 REM Main game loop
120 ATTEMPTS = ATTEMPTS + 1
130 PRINT "Attempt"; ATTEMPTS; "of"; MAX_ATTEMPTS
140 INPUT "Enter your guess: "; GUESS
150 REM Check the guess
160 IF GUESS = SECRET THEN GOTO 220
170 IF GUESS < SECRET THEN PRINT "Too low! Try higher."
180 IF GUESS > SECRET THEN PRINT "Too high! Try lower."
190 REM Check if attempts exhausted
200 IF ATTEMPTS < MAX_ATTEMPTS THEN GOTO 120
210 PRINT "Sorry! The number was"; SECRET; ". Better luck next time!"
215 GOTO 230
220 PRINT "Congratulations! You guessed it in"; ATTEMPTS; "attempts!"
230 PRINT "Thanks for playing!"
240 END