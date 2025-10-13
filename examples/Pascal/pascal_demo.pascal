PROGRAM HelloPascal;
{ Educational Pascal demo for Time_Warp IDE }
{ Demonstrates structured programming concepts }

VAR
    counter, sum, number: INTEGER;
    average: REAL;
    name: STRING;
    is_valid: BOOLEAN;

CONST
    MAX_COUNT = 5;
    PI = 3.14159;

PROCEDURE DisplayWelcome;
BEGIN
    WRITELN('Welcome to TW Pascal in Time_Warp IDE!');
    WRITELN('This demonstrates structured programming concepts.');
    WRITELN('');
END;

FUNCTION CalculateAverage(a, b, c: INTEGER): REAL;
VAR
    total: INTEGER;
BEGIN
    total := a + b + c;
    CalculateAverage := total / 3.0;
END;

PROCEDURE ProcessNumbers;
VAR
    i: INTEGER;
BEGIN
    WRITELN('Number processing demonstration:');
    sum := 0;

    FOR i := 1 TO MAX_COUNT DO
    BEGIN
        number := i * 10;
        sum := sum + number;
        WRITELN('Number ', i, ': ', number);
    END;

    average := sum / MAX_COUNT;
    WRITELN('Sum: ', sum);
    WRITELN('Average: ', average:0:2);
    WRITELN('');
END;

PROCEDURE DemonstrateControlStructures;
VAR
    choice: INTEGER;
BEGIN
    WRITELN('Control Structures Demo:');
    WRITELN('Enter a number (1-3):');
    READLN(choice);

    CASE choice OF
        1: WRITELN('You chose option 1');
        2: WRITELN('You chose option 2');
        3: WRITELN('You chose option 3');
    ELSE
        WRITELN('Invalid choice');
    END;

    { WHILE loop demo }
    counter := 1;
    WHILE counter <= 3 DO
    BEGIN
        WRITELN('While loop iteration: ', counter);
        counter := counter + 1;
    END;

    { REPEAT loop demo }
    counter := 1;
    REPEAT
        WRITELN('Repeat loop iteration: ', counter);
        counter := counter + 1;
    UNTIL counter > 3;

    WRITELN('');
END;

BEGIN
    { Main program }
    DisplayWelcome;

    ProcessNumbers;

    DemonstrateControlStructures;

    { Function call demo }
    WRITELN('Function Demo:');
    WRITELN('Average of 10, 20, 30 = ', CalculateAverage(10, 20, 30):0:2);

    WRITELN('');
    WRITELN('Pascal demo completed successfully!');
END.