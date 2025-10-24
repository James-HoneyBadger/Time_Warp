use std::collections::HashMap;
use std::fs;

#[derive(Clone)]
struct TurtleState {
    x: f32,
    y: f32,
    angle: f32,
    color: String,
}

enum CommandResult {
    Output(String),
    Goto(u32),
    Input(String, String),
    Continue,
    End,
}

struct TestApp {
    variables: HashMap<String, String>,
    program_lines: Vec<(u32, String)>,
    current_line: usize,
    turtle_state: TurtleState,
    turtle_commands: Vec<String>,
}

impl TestApp {
    fn new() -> Self {
        Self {
            variables: HashMap::new(),
            program_lines: Vec::new(),
            current_line: 0,
            turtle_state: TurtleState {
                x: 200.0,
                y: 200.0,
                angle: 0.0,
                color: "black".to_string(),
            },
            turtle_commands: Vec::new(),
        }
    }

    fn execute_tw_basic(&mut self, code: &str) -> String {
        // Parse program lines with line numbers
        self.program_lines.clear();
        for line in code.lines() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            // Try to parse line number
            if let Some((line_num_str, command)) = line.split_once(' ') {
                if let Ok(line_num) = line_num_str.parse::<u32>() {
                    self.program_lines
                        .push((line_num, command.trim().to_string()));
                } else {
                    self.program_lines.push((0, line.to_string()));
                }
            } else {
                self.program_lines.push((0, line.to_string()));
            }
        }

        // Sort by line number
        self.program_lines.sort_by_key(|(line_num, _)| *line_num);

        // Execute the program
        self.current_line = 0;
        let mut output = String::new();

        while self.current_line < self.program_lines.len() {
            let command = self.program_lines[self.current_line].1.clone();
            let result = self.execute_basic_command(&command);

            match result {
                CommandResult::Output(text) => {
                    output.push_str(&text);
                    output.push('\n');
                }
                CommandResult::Goto(line_num) => {
                    if let Some(pos) = self
                        .program_lines
                        .iter()
                        .position(|(ln, _)| *ln == line_num)
                    {
                        self.current_line = pos;
                        continue;
                    } else {
                        output.push_str(&format!("Line {} not found\n", line_num));
                        break;
                    }
                }
                CommandResult::Continue => {}
                CommandResult::End => break,
                _ => {} // Skip other results for this test
            }

            self.current_line += 1;
        }

        output
    }

    fn execute_basic_command(&mut self, command: &str) -> CommandResult {
        let cmd = command.trim();

        if cmd.is_empty() || cmd.starts_with("REM") {
            return CommandResult::Continue;
        }

        if cmd.starts_with("PRINT ") {
            let text = cmd.strip_prefix("PRINT ").unwrap_or("");
            let processed_text = self.process_print_text(text);
            return CommandResult::Output(processed_text);
        }

        if cmd.starts_with("LET ") {
            self.handle_let_command(cmd.strip_prefix("LET ").unwrap_or(""));
            return CommandResult::Continue;
        }

        if cmd.starts_with("IF ") {
            return self.handle_if_command(cmd.strip_prefix("IF ").unwrap_or(""));
        }

        if cmd.starts_with("GOTO ") {
            if let Some(line_num_str) = cmd.strip_prefix("GOTO ") {
                if let Ok(line_num) = line_num_str.trim().parse::<u32>() {
                    return CommandResult::Goto(line_num);
                }
            }
        }

        // Turtle graphics commands
        if let Some(result) = self.handle_turtle_command(cmd) {
            return result;
        }

        if cmd == "END" {
            return CommandResult::End;
        }

        CommandResult::Output(format!("Unknown command: {}", cmd))
    }

    fn process_print_text(&self, text: &str) -> String {
        let mut result = String::new();
        let mut chars = text.chars().peekable();

        while let Some(ch) = chars.next() {
            if ch == '"' {
                // Handle quoted strings
                while let Some(ch) = chars.next() {
                    if ch == '"' {
                        break;
                    }
                    result.push(ch);
                }
            } else if ch.is_alphabetic() {
                // Variable reference
                let mut var_name = String::new();
                var_name.push(ch);
                while let Some(&next_ch) = chars.peek() {
                    if next_ch.is_alphanumeric() || next_ch == '_' || next_ch == '$' {
                        var_name.push(chars.next().unwrap());
                    } else {
                        break;
                    }
                }
                if let Some(value) = self.variables.get(&var_name) {
                    result.push_str(value);
                }
            } else {
                result.push(ch);
            }
        }

        result
    }

    fn handle_let_command(&mut self, assignment: &str) {
        if let Some((var_name, expr)) = assignment.split_once('=') {
            let var_name = var_name.trim();
            let expr = expr.trim();

            // Simple expression evaluation
            let value = if expr.starts_with('"') && expr.ends_with('"') {
                expr[1..expr.len() - 1].to_string()
            } else if let Ok(_) = expr.parse::<i32>() {
                expr.to_string()
            } else {
                // Check if it's a variable reference
                self.variables
                    .get(expr)
                    .unwrap_or(&expr.to_string())
                    .clone()
            };

            self.variables.insert(var_name.to_string(), value);
        }
    }

    fn handle_if_command(&self, condition: &str) -> CommandResult {
        if let Some((cond, then_part)) = condition.split_once(" THEN ") {
            let then_part = then_part.trim();

            if self.evaluate_condition(cond.trim()) {
                if then_part.starts_with("GOTO ") {
                    if let Some(line_num_str) = then_part.strip_prefix("GOTO ") {
                        if let Ok(line_num) = line_num_str.trim().parse::<u32>() {
                            return CommandResult::Goto(line_num);
                        }
                    }
                }
                // Could handle other THEN actions here
            }
        }
        CommandResult::Continue
    }

    fn evaluate_condition(&self, condition: &str) -> bool {
        // Simple condition evaluation
        if let Some((left, op_right)) = condition.split_once('=') {
            let (op, right) = if op_right.starts_with('=') {
                ("==", &op_right[1..])
            } else {
                ("=", op_right)
            };

            let left_val = self.get_value(left.trim());
            let right_val = self.get_value(right.trim());

            match op {
                "=" | "==" => left_val == right_val,
                "<>" => left_val != right_val,
                "<" => left_val < right_val,
                ">" => left_val > right_val,
                "<=" => left_val <= right_val,
                ">=" => left_val >= right_val,
                _ => false,
            }
        } else {
            false
        }
    }

    fn get_value(&self, expr: &str) -> String {
        if let Some(value) = self.variables.get(expr) {
            value.clone()
        } else if let Ok(_) = expr.parse::<i32>() {
            expr.to_string()
        } else {
            expr.to_string()
        }
    }

    fn handle_turtle_command(&mut self, command: &str) -> Option<CommandResult> {
        if command.starts_with("FORWARD ") || command.starts_with("FD ") {
            let distance_str = command
                .strip_prefix("FORWARD ")
                .or_else(|| command.strip_prefix("FD "))?;
            if let Ok(distance) = distance_str.trim().parse::<f32>() {
                self.move_turtle(distance, true);
                return Some(CommandResult::Output(format!("Moved forward {}", distance)));
            }
        }

        if command.starts_with("RIGHT ") || command.starts_with("RT ") {
            let angle_str = command
                .strip_prefix("RIGHT ")
                .or_else(|| command.strip_prefix("RT "))?;
            if let Ok(angle) = angle_str.trim().parse::<f32>() {
                self.turtle_state.angle = (self.turtle_state.angle + angle) % 360.0;
                return Some(CommandResult::Output(format!(
                    "Turned right {} degrees",
                    angle
                )));
            }
        }

        None
    }

    fn move_turtle(&mut self, distance: f32, draw: bool) {
        let angle_rad = self.turtle_state.angle.to_radians();
        let new_x = self.turtle_state.x + distance * angle_rad.cos();
        let new_y = self.turtle_state.y + distance * angle_rad.sin();

        if draw {
            // Store the line for rendering
            self.turtle_commands.push(format!(
                "LINE {} {} {} {}",
                self.turtle_state.x, self.turtle_state.y, new_x, new_y
            ));
        }

        self.turtle_state.x = new_x;
        self.turtle_state.y = new_y;
    }
}

fn main() {
    println!("Testing Time Warp IDE Sample Programs\n");

    // Test TW BASIC sample
    println!("=== TW BASIC Sample ===");
    let mut app = TestApp::new();
    let basic_code = fs::read_to_string("examples/tw_basic_sample.twb").unwrap_or_else(|_| {
        "10 PRINT \"Hello, TW BASIC!\"
20 LET X = 42
30 PRINT \"X = \"; X
40 FORWARD 100
50 RIGHT 90
60 FORWARD 100
70 RIGHT 90
80 FORWARD 100
90 RIGHT 90
100 FORWARD 100
110 RIGHT 90
120 PRINT \"Square drawn!\""
            .to_string()
    });

    let result = app.execute_tw_basic(&basic_code);
    println!("Output:\n{}", result);
    println!("Turtle commands: {}\n", app.turtle_commands.len());

    // Test TW BASIC game
    println!("=== TW BASIC Game (simplified) ===");
    let mut app2 = TestApp::new();
    let game_code = "10 PRINT \"Number guessing game\"
20 LET SECRET = 42
30 PRINT \"Guess the number:\"
40 LET GUESS = 50
50 IF GUESS = SECRET THEN GOTO 80
60 PRINT \"Try again\"
70 GOTO 40
80 PRINT \"Correct!\"";

    let result2 = app2.execute_tw_basic(game_code);
    println!("Output:\n{}", result2);
}

#[cfg(test)]
mod modular_basic_tests {
    use time_warp_ide::languages::basic::Interpreter;

    #[test]
    fn test_simple_print() {
        let mut interpreter = Interpreter::new();
        let program = r#"
        10 PRINT "Hello, World!"
        20 PRINT 42
        30 END
        "#;

        let result = interpreter.execute(program);
        assert!(result.is_ok());

        match result.unwrap() {
            time_warp_ide::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            } => {
                assert!(output.contains("Hello, World!"));
                assert!(output.contains("42"));
                assert_eq!(graphics_commands.len(), 0);
            }
            _ => panic!("Expected Complete result"),
        }
    }

    #[test]
    fn test_arithmetic() {
        let mut interpreter = Interpreter::new();
        let program = r#"
        10 LET X = 10 + 5 * 2
        20 PRINT X
        "#;

        let result = interpreter.execute(program);
        assert!(result.is_ok());

        match result.unwrap() {
            time_warp_ide::languages::basic::ExecutionResult::Complete { output, .. } => {
                assert!(output.contains("20")); // 10 + (5 * 2) = 20
            }
            _ => panic!("Expected Complete result"),
        }
    }

    #[test]
    fn test_int_function() {
        let mut interpreter = Interpreter::new();
        let program = r#"
        10 PRINT INT(3.7)
        20 PRINT INT(RND(1) * 100)
        "#;

        let result = interpreter.execute(program);
        assert!(result.is_ok());

        match result.unwrap() {
            time_warp_ide::languages::basic::ExecutionResult::Complete { output, .. } => {
                assert!(output.contains("3")); // INT(3.7) = 3
            }
            _ => panic!("Expected Complete result"),
        }
    }
}
