fn main() {
    let code = r#"10 REM Number Guessing Game
20 PRINT "I'm thinking of a number between 1 and 100"
30 LET SECRET = 42
40 PRINT "Guess the number:"
50 INPUT GUESS
60 IF GUESS = SECRET THEN GOTO 100
70 IF GUESS < SECRET THEN PRINT "Too low!"
80 IF GUESS > SECRET THEN PRINT "Too high!"
90 GOTO 40
100 PRINT "Correct! You win!""#;

    println!("Original code:");
    println!("{}", code);
    println!("\n--- Processing ---");

    // Convert line-numbered BASIC to statements without line numbers
    let mut statements = Vec::new();
    for line in code.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }

        // Try to parse line number and extract the statement
        if let Some((line_num_str, command)) = line.split_once(' ') {
            if line_num_str.parse::<u32>().is_ok() {
                println!("Line with number: '{}' -> '{}'", line, command.trim());
                statements.push(command.trim().to_string());
            } else {
                println!("Line without number: '{}'", line);
                statements.push(line.to_string());
            }
        } else {
            println!("Line without space: '{}'", line);
            statements.push(line.to_string());
        }
    }

    // Join statements with colons for the interpreter (BASIC statement separator)
    let program_code = statements.join(" : ");
    println!("\nFinal program code:");
    println!("{}", program_code);
}
