use std::fs;

fn main() {
    // Read the BASIC interpreter source
    let basic_source = fs::read_to_string("src/languages/basic.rs").expect("Failed to read basic.rs");
    
    // Test a simple BASIC statement that should work
    let test_code = "LET X = 5";
    println!("Testing: {}", test_code);
    
    // Check if LET is recognized
    if basic_source.contains("Token::Let") {
        println!("✓ LET token is defined");
    } else {
        println!("✗ LET token not found");
    }
    
    // Check if parse_let_statement exists
    if basic_source.contains("fn parse_let_statement") {
        println!("✓ parse_let_statement method exists");
    } else {
        println!("✗ parse_let_statement method not found");
    }
    
    // Test the processed game code
    let game_code = "REM Number Guessing Game : PRINT \"I'm thinking of a number between 1 and 100\" : LET SECRET = 42 : PRINT \"Guess the number:\" : INPUT GUESS : IF GUESS = SECRET THEN GOTO 100 : IF GUESS < SECRET THEN PRINT \"Too low!\" : IF GUESS > SECRET THEN PRINT \"Too high!\" : GOTO 40 : PRINT \"Correct! You win!\"";
    println!("\nProcessed game code length: {} characters", game_code.len());
    
    // Check for problematic tokens
    let problematic_patterns = vec![
        ("<", "Less than operator"),
        (">", "Greater than operator"), 
        ("=", "Equals operator"),
        ("GOTO", "GOTO keyword"),
        ("IF", "IF keyword"),
        ("THEN", "THEN keyword"),
        ("INPUT", "INPUT keyword"),
        ("REM", "REM keyword"),
    ];
    
    println!("\nChecking for problematic patterns:");
    for (pattern, description) in problematic_patterns {
        if game_code.contains(pattern) {
            println!("✓ {} ({}) found", pattern, description);
        } else {
            println!("✗ {} ({}) not found", pattern, description);
        }
    }
    
    println!("\n=== Conclusion ===");
    println!("The BasicInterpreter appears to have all necessary components.");
    println!("If parsing fails, the issue is likely in:");
    println!("1. Multi-statement line handling with colons");
    println!("2. Complex IF statement parsing");
    println!("3. GOTO with line numbers vs expressions");
}
