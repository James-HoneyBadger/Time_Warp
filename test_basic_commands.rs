mod languages {
    include!("src/languages/basic.rs");
}

fn main() {
    let program_code = r#"PRINT "Hello from BASIC!" : WRITELN "This uses WRITELN" : FORWARD 50 : RIGHT 90 : FORWARD 50"#;

    println!("Testing program code:");
    println!("{}", program_code);
    println!("\n--- Executing ---");

    let mut interpreter = languages::basic::BasicInterpreter::new();

    match interpreter.execute(program_code) {
        Ok(result) => match result {
            languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            } => {
                println!("Execution successful!");
                println!("Output: {}", output);
                println!("Graphics commands: {:?}", graphics_commands);
            }
            languages::basic::ExecutionResult::NeedInput {
                prompt,
                partial_output,
                ..
            } => {
                println!("Execution needs input:");
                println!("Partial output: {}", partial_output);
                println!("Prompt: {}", prompt);
            }
            languages::basic::ExecutionResult::Error(err) => {
                println!("Execution error: {:?}", err);
            }
        },
        Err(err) => {
            println!("Interpreter error: {:?}", err);
        }
    }
}
