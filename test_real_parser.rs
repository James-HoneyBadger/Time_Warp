mod languages {
    include!("src/languages/basic.rs");
}

fn main() {
    let program_code = r#"REM Number Guessing Game : PRINT "I'm thinking of a number between 1 and 100" : LET SECRET = 42 : PRINT "Guess the number:" : INPUT GUESS : IF GUESS = SECRET THEN GOTO 100 : IF GUESS < SECRET THEN PRINT "Too low!" : IF GUESS > SECRET THEN PRINT "Too high!" : GOTO 40 : PRINT "Correct! You win!""#;
    
    println!("Testing program code:");
    println!("{}", program_code);
    println!("\n--- Executing ---");
    
    let mut interpreter = languages::basic::BasicInterpreter::new();
    
    match interpreter.execute(program_code) {
        Ok(result) => {
            match result {
                languages::basic::ExecutionResult::Complete { output, .. } => {
                    println!("Execution successful!");
                    println!("Output: {}", output);
                }
                languages::basic::ExecutionResult::NeedInput { prompt, partial_output, .. } => {
                    println!("Execution needs input:");
                    println!("Partial output: {}", partial_output);
                    println!("Prompt: {}", prompt);
                }
                languages::basic::ExecutionResult::Error(err) => {
                    println!("Execution error: {:?}", err);
                }
            }
        }
        Err(err) => {
            println!("Interpreter error: {:?}", err);
        }
    }
}
