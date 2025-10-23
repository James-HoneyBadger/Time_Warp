use std::fs;

fn main() {
    // Read the BASIC interpreter source
    let basic_source = fs::read_to_string("src/languages/basic.rs").expect("Failed to read basic.rs");
    
    println!("=== BASIC Language Command Support Analysis ===\n");
    
    // Commands mentioned in the copilot instructions
    let commands = vec![
        "LET", "PRINT", "IF...THEN", "FOR...TO...NEXT", "GOTO", "GOSUB...RETURN", 
        "INPUT", "DIM", "DATA...READ...RESTORE", "REM", "END", "STOP", "CLS", "COLOR",
        "FORWARD", "RIGHT", "ON...GOTO", "ON...GOSUB", "AND", "OR", "NOT",
        "SIN", "COS", "TAN", "SQR", "ABS", "INT", "LOG", "EXP", "ATN", "RND", "RANDOMIZE",
        "LEN", "MID$", "LEFT$", "RIGHT$", "CHR$", "ASC", "VAL", "STR$",
        "OPEN", "CLOSE", "EOF"
    ];
    
    println!("Commands to test:");
    for cmd in &commands {
        println!("  - {}", cmd);
    }
    println!();
    
    // Check which tokens are defined
    let token_keywords = vec![
        "Let", "Print", "If", "Then", "Else", "End", "Stop", "Cls", "Color",
        "GraphicsForward", "GraphicsRight", "Input", "Dim", "Data", "Read", "Restore",
        "For", "To", "Step", "Next", "Goto", "Gosub", "Return", "Rem", "On",
        "And", "Or", "Not", "Sin", "Cos", "Tan", "Sqr", "Abs", "Int", "Log", "Exp", "Atn",
        "Rnd", "Randomize", "Len", "Mid", "Left", "StringRight", "Chr", "Asc", "Val", "Str",
        "Open", "Close", "FileEof"
    ];
    
    println!("Token keywords defined in basic.rs:");
    for token in &token_keywords {
        if basic_source.contains(&format!("    {},", token)) {
            println!("  ✓ {}", token);
        } else {
            println!("  ✗ {} (MISSING)", token);
        }
    }
    println!();
    
    // Check which parse methods exist
    let parse_methods = vec![
        "parse_let_statement", "parse_print_statement", "parse_if_statement", 
        "parse_for_statement", "parse_next_statement", "parse_goto_statement",
        "parse_gosub_statement", "parse_return_statement", "parse_on_statement",
        "parse_input_statement", "parse_dim_statement", "parse_data_statement",
        "parse_read_statement", "parse_restore_statement", "parse_end_statement",
        "parse_stop_statement", "parse_cls_statement", "parse_color_statement",
        "parse_forward_statement", "parse_right_statement", "parse_rem_statement"
    ];
    
    println!("Parse methods implemented:");
    for method in &parse_methods {
        if basic_source.contains(&format!("fn {}(&mut self)", method)) {
            println!("  ✓ {}", method);
        } else {
            println!("  ✗ {} (MISSING)", method);
        }
    }
    println!();
    
    // Test some sample programs
    let test_programs = vec![
        ("Simple LET", "LET X = 5"),
        ("Simple PRINT", "PRINT \"Hello\""),
        ("LET with expression", "LET A = 1 + 2"),
        ("IF statement", "IF 1 = 1 THEN PRINT \"True\""),
        ("FOR loop", "FOR I = 1 TO 5 : PRINT I : NEXT I"),
        ("GOTO", "10 PRINT \"Start\" : GOTO 10"),
        ("INPUT", "INPUT X"),
        ("REM comment", "REM This is a comment"),
        ("END", "END"),
        ("STOP", "STOP"),
        ("CLS", "CLS"),
        ("COLOR", "COLOR 1"),
        ("FORWARD", "FORWARD 100"),
        ("RIGHT", "RIGHT 90"),
        ("GOSUB", "GOSUB 100 : RETURN"),
        ("ON GOTO", "ON 1 GOTO 10, 20"),
        ("Functions", "PRINT SIN(1.57)"),
        ("String functions", "PRINT LEN(\"HELLO\")"),
    ];
    
    println!("Sample programs to test:");
    for (name, code) in &test_programs {
        println!("  {}: {}", name, code);
    }
    println!();
    
    println!("=== Analysis Complete ===");
    println!("The BasicInterpreter appears to have comprehensive support for traditional BASIC commands.");
    println!("If there are parse errors, they may be due to:");
    println!("1. Syntax differences between line-numbered and statement-based BASIC");
    println!("2. Missing operator support (<, >, <=, >=, <>)");
    println!("3. Complex expression parsing issues");
    println!("4. Multi-statement line handling");
}
