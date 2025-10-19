10 PRINT "🎯 Time_Warp IDE - Number Guessing Game"
20 PRINT "======================================"
30 PRINT
40 PRINT "I'm thinking of a number between 1 and 100..."
50 PRINT
60 SECRET = INT(RND(1) * 100) + 1
70 GUESSES = 0
80 MAX_GUESSES = 10
90 PRINT "You have "; MAX_GUESSES; " guesses to find my number!"
100 PRINT
110 INPUT "Your guess: "; GUESS
120 GUESSES = GUESSES + 1
130 IF GUESS = SECRET THEN GOTO 200
140 IF GUESS < SECRET THEN PRINT "📈 Too low! Try higher."
150 IF GUESS > SECRET THEN PRINT "📉 Too high! Try lower."
160 PRINT "Guesses used: "; GUESSES; " of "; MAX_GUESSES
170 PRINT
180 IF GUESSES < MAX_GUESSES THEN GOTO 110
190 PRINT "❌ Sorry! You've used all your guesses.": PRINT "The number was: "; SECRET: GOTO 230
200 PRINT
210 PRINT "🎉 Congratulations! You got it!"
220 PRINT "The number was: "; SECRET
230 PRINT "Number of guesses: "; GUESSES
240 IF GUESSES <= 3 THEN PRINT "🏆 Excellent! You're a mind reader!"
250 IF GUESSES > 3 AND GUESSES <= 7 THEN PRINT "👍 Good job!"
260 IF GUESSES > 7 THEN PRINT "😊 Better luck next time!"
270 PRINT
280 INPUT "Play again? (Y/N): "; PLAY$
290 IF PLAY$ = "Y" OR PLAY$ = "y" THEN GOTO 10
300 PRINT
310 PRINT "Thanks for playing! 👋"
320 END