fn main() {
    let code = r#"REM TW BASIC Sample Program
REM Demonstrates GW BASIC, PILOT, and Logo features

LET X = 42
PRINT "Hello, TW BASIC!"
PRINT "X = "; X

REM PILOT-style interaction
T: What is your name?
A: NAME$
PRINT "Hello, "; NAME$

REM Logo turtle graphics
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100"#;

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
