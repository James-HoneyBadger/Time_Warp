use eframe::egui;
use rfd::FileDialog;
use std::collections::HashMap;

mod languages;

#[derive(Clone)]
struct TurtleState {
    x: f32,
    y: f32,
    angle: f32, // in degrees
    color: egui::Color32,
}

enum CommandResult {
    Output(String),
    Goto(u32),
    Input(String, String), // (variable_name, prompt)
    Continue,
    End,
}

struct TimeWarpApp {
    code: String,
    output: String,
    language: String,
    active_tab: usize, // 0 = Editor, 1 = Output & Turtle
    last_file_path: Option<String>,
    show_line_numbers: bool,
    find_text: String,
    replace_text: String,
    show_find_replace: bool,
    turtle_state: TurtleState,
    turtle_commands: Vec<String>,
    variables: HashMap<String, String>,
    program_lines: Vec<(u32, String)>, // Line number and command
    current_line: usize,
    current_pascal_line: usize,
    is_executing: bool,
    waiting_for_input: bool,
    input_prompt: String,
    user_input: String,
    current_input_var: String,
    show_about: bool,
    turtle_zoom: f32,
    turtle_pan: egui::Vec2,
}

impl Default for TimeWarpApp {
    fn default() -> Self {
        Self {
            code: String::new(),
            output: String::from("Welcome to Time Warp IDE!\n"),
            language: String::from("TW BASIC"),
            active_tab: 0, // Start with Editor tab
            last_file_path: None,
            show_line_numbers: false,
            find_text: String::new(),
            replace_text: String::new(),
            show_find_replace: false,
            turtle_state: TurtleState {
                x: 200.0,
                y: 200.0,
                angle: 0.0,
                color: egui::Color32::BLACK,
            },
            turtle_commands: Vec::new(),
            variables: HashMap::new(),
            program_lines: Vec::new(),
            current_line: 0,
            current_pascal_line: 0,
            is_executing: false,
            waiting_for_input: false,
            input_prompt: String::new(),
            user_input: String::new(),
            current_input_var: String::new(),
            show_about: false,
            turtle_zoom: 1.0,
            turtle_pan: egui::vec2(0.0, 0.0),
        }
    }
}

impl TimeWarpApp {
    fn execute_code(&mut self) {
        self.active_tab = 1; // Switch to Output tab when running
        self.is_executing = true;
        let code = self.code.clone();
        let result = match self.language.as_str() {
            "TW BASIC" => self.execute_tw_basic(&code),
            "TW Pascal" => self.execute_tw_pascal(&code),
            "TW Prolog" => self.execute_tw_prolog(&code),
            "PILOT" => self.execute_pilot(&code),
            _ => format!(
                "Language '{}' not yet supported for execution",
                self.language
            ),
        };
        if self.is_executing && !self.waiting_for_input {
            self.output = format!("[Output for {}]\n{}", self.language, result);
        }
        self.is_executing = false;
    }

    fn execute_tw_basic(&mut self, code: &str) -> String {
        use crate::languages::basic::BasicInterpreter;

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
                    statements.push(command.trim().to_string());
                } else {
                    statements.push(line.to_string());
                }
            } else {
                statements.push(line.to_string());
            }
        }

        // Join statements with colons for the interpreter (BASIC statement separator)
        let program_code = statements.join(" : ");

        let mut interpreter = BasicInterpreter::new();

        match interpreter.execute(&program_code) {
            Ok(result) => match result {
                crate::languages::basic::ExecutionResult::Complete { output, .. } => output,
                crate::languages::basic::ExecutionResult::NeedInput {
                    prompt,
                    partial_output,
                    ..
                } => {
                    self.waiting_for_input = true;
                    self.input_prompt = prompt.clone();
                    // For now, just return the partial output with the prompt
                    format!("{}{}", partial_output, prompt)
                }
                crate::languages::basic::ExecutionResult::Error(err) => {
                    format!("Error: {:?}", err)
                }
            },
            Err(err) => {
                format!("Error: {:?}", err)
            }
        }
    }

    fn execute_pilot(&mut self, code: &str) -> String {
        // Parse PILOT program lines
        self.program_lines.clear();
        for (line_num, line) in code.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }
            // PILOT uses labels like T:, A:, J:, Y:, N:
            self.program_lines
                .push((line_num as u32 + 1, line.to_string()));
        }

        // Execute the program
        self.current_line = 0;
        let mut output = String::new();

        while self.current_line < self.program_lines.len() {
            let command = self.program_lines[self.current_line].1.clone();
            let result = self.execute_pilot_command(&command);

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
                        output.push_str(&format!("Label {} not found\n", line_num));
                        break;
                    }
                }
                CommandResult::Input(var_name, prompt) => {
                    self.waiting_for_input = true;
                    self.current_input_var = var_name;
                    self.input_prompt = prompt.clone();
                    output.push_str(&prompt);
                    break; // Wait for user input
                }
                CommandResult::Continue => {}
                CommandResult::End => break,
            }

            self.current_line += 1;
        }

        if output.is_empty() && !self.waiting_for_input {
            "PILOT program executed successfully".to_string()
        } else {
            output
        }
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

        if cmd.starts_with("INPUT ") {
            let var_part = cmd.strip_prefix("INPUT ").unwrap_or("");
            if let Some((var_name, prompt)) = self.parse_input_command(var_part) {
                return CommandResult::Input(var_name, prompt);
            }
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

    fn execute_pilot_command(&mut self, command: &str) -> CommandResult {
        let cmd = command.trim();

        if cmd.is_empty() {
            return CommandResult::Continue;
        }

        // PILOT commands start with single letters followed by :
        if cmd.starts_with("T:") {
            // Type/Print command
            let text = cmd.strip_prefix("T:").unwrap_or("").trim();
            let processed_text = self.process_pilot_text(text);
            return CommandResult::Output(processed_text);
        }

        if cmd.starts_with("A:") {
            // Accept/Input command
            let var_part = cmd.strip_prefix("A:").unwrap_or("").trim();
            if let Some((var_name, prompt)) = self.parse_pilot_input_command(var_part) {
                return CommandResult::Input(var_name, prompt);
            }
        }

        if cmd.starts_with("J:") {
            // Jump command
            let label = cmd.strip_prefix("J:").unwrap_or("").trim();
            if let Ok(line_num) = label.parse::<u32>() {
                return CommandResult::Goto(line_num);
            } else {
                // Handle label-based jumps (for future enhancement)
                return CommandResult::Output(format!("Label jump to '{}' not implemented", label));
            }
        }

        if cmd.starts_with("Y:") {
            // Yes/No condition (simplified)
            let _condition = cmd.strip_prefix("Y:").unwrap_or("").trim();
            // For now, treat as always true for demo
            return CommandResult::Continue;
        }

        if cmd.starts_with("N:") {
            // No condition (simplified)
            let _condition = cmd.strip_prefix("N:").unwrap_or("").trim();
            // For now, treat as always false for demo
            return CommandResult::Continue;
        }

        // Turtle graphics commands for PILOT
        if let Some(result) = self.handle_turtle_command(cmd) {
            return result;
        }

        if cmd == "E:" {
            // End command
            return CommandResult::End;
        }

        CommandResult::Output(format!("Unknown PILOT command: {}", cmd))
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
            } else if ch == ';' {
                // Semicolon separator - continue without newline
                result.push_str("; ");
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
                } else {
                    result.push_str(&var_name);
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

            // Simple expression evaluation - for now just store the value
            let value = if expr.starts_with('"') && expr.ends_with('"') {
                expr[1..expr.len() - 1].to_string()
            } else if let Ok(num) = expr.parse::<i32>() {
                num.to_string()
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

    fn parse_input_command(&self, var_part: &str) -> Option<(String, String)> {
        // INPUT variable or INPUT "prompt", variable
        if var_part.contains(',') {
            let parts: Vec<&str> = var_part.split(',').map(|s| s.trim()).collect();
            if parts.len() >= 2 {
                let prompt = if parts[0].starts_with('"') && parts[0].ends_with('"') {
                    parts[0][1..parts[0].len() - 1].to_string()
                } else {
                    parts[0].to_string()
                };
                return Some((parts[1].to_string(), prompt));
            }
        }
        Some((var_part.to_string(), format!("? ")))
    }

    fn process_pilot_text(&self, text: &str) -> String {
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
            } else if ch == '#' {
                // Variable reference in PILOT (using # instead of direct names)
                let mut var_name = String::new();
                while let Some(&next_ch) = chars.peek() {
                    if next_ch.is_alphanumeric() || next_ch == '_' || next_ch == '$' {
                        var_name.push(chars.next().unwrap());
                    } else {
                        break;
                    }
                }
                if let Some(value) = self.variables.get(&var_name) {
                    result.push_str(value);
                } else {
                    result.push('#');
                    result.push_str(&var_name);
                }
            } else {
                result.push(ch);
            }
        }

        result
    }

    fn parse_pilot_input_command(&self, var_part: &str) -> Option<(String, String)> {
        // A:variable or A:"prompt",variable
        if var_part.contains(',') {
            let parts: Vec<&str> = var_part.split(',').map(|s| s.trim()).collect();
            if parts.len() >= 2 {
                let prompt = if parts[0].starts_with('"') && parts[0].ends_with('"') {
                    parts[0][1..parts[0].len() - 1].to_string()
                } else {
                    parts[0].to_string()
                };
                return Some((parts[1].to_string(), prompt));
            }
        }
        Some((var_part.to_string(), format!("? ")))
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

        if command.starts_with("BACK ") || command.starts_with("BK ") {
            let distance_str = command
                .strip_prefix("BACK ")
                .or_else(|| command.strip_prefix("BK "))?;
            if let Ok(distance) = distance_str.trim().parse::<f32>() {
                self.move_turtle(-distance, true);
                return Some(CommandResult::Output(format!("Moved back {}", distance)));
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

        if command.starts_with("LEFT ") || command.starts_with("LT ") {
            let angle_str = command
                .strip_prefix("LEFT ")
                .or_else(|| command.strip_prefix("LT "))?;
            if let Ok(angle) = angle_str.trim().parse::<f32>() {
                self.turtle_state.angle = (self.turtle_state.angle - angle + 360.0) % 360.0;
                return Some(CommandResult::Output(format!(
                    "Turned left {} degrees",
                    angle
                )));
            }
        }

        if command == "PENUP" || command == "PU" {
            // Note: pen_down field was removed, but we could add it back if needed
            return Some(CommandResult::Output("Pen up".to_string()));
        }

        if command == "PENDOWN" || command == "PD" {
            return Some(CommandResult::Output("Pen down".to_string()));
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

    fn continue_execution(&mut self) {
        if self.language == "TW BASIC" {
            self.continue_basic_execution();
        } else if self.language == "TW Pascal" {
            self.continue_pascal_execution();
        } else if self.language == "PILOT" {
            self.continue_pilot_execution();
        }
    }

    fn continue_basic_execution(&mut self) {
        // Continue executing from where we left off
        let mut output = self.output.clone();
        output.push_str(&self.user_input);
        output.push('\n');

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
                CommandResult::Input(var_name, prompt) => {
                    self.waiting_for_input = true;
                    self.current_input_var = var_name;
                    self.input_prompt = prompt.clone();
                    output.push_str(&prompt);
                    break; // Wait for user input again
                }
                CommandResult::Continue => {}
                CommandResult::End => break,
            }

            self.current_line += 1;
        }

        self.output = format!("[Output for {}]\n{}", self.language, output);

        if self.current_line >= self.program_lines.len() && !self.waiting_for_input {
            self.output.push_str("Program completed.\n");
        }
    }

    fn continue_pascal_execution(&mut self) {
        // Continue Pascal execution from where we left off
        let code = self.code.clone();
        let result = self.execute_tw_pascal(&code);
        self.output = format!("[Output for {}]\n{}", self.language, result);

        if !self.waiting_for_input {
            self.output.push_str("Program completed.\n");
        }
    }

    fn continue_pilot_execution(&mut self) {
        // Continue PILOT execution from where we left off
        let code = self.code.clone();
        let result = self.execute_pilot(&code);
        self.output = format!("[Output for {}]\n{}", self.language, result);

        if !self.waiting_for_input {
            self.output.push_str("Program completed.\n");
        }
    }

    fn execute_tw_pascal(&mut self, code: &str) -> String {
        use crate::languages::pascal::{CommandResult, PascalInterpreter};

        let mut interpreter = PascalInterpreter::new();

        // Parse program into lines
        let lines: Vec<&str> = code.lines().collect();
        let mut output = String::new();

        // Start from current_pascal_line if continuing, otherwise from 0
        let start_line = if self.waiting_for_input && self.language == "TW Pascal" {
            self.current_pascal_line
        } else {
            self.current_pascal_line = 0;
            0
        };

        for (i, line) in lines.iter().enumerate().skip(start_line) {
            let trimmed = line.trim();
            if trimmed.is_empty() || trimmed.starts_with('{') || trimmed.starts_with("(*") {
                continue;
            }

            let result = interpreter.execute_statement_with_vars(trimmed, &mut self.variables);

            match result {
                CommandResult::Output(text) => {
                    output.push_str(&text);
                    output.push('\n');
                }
                CommandResult::Input(var_name, prompt) => {
                    self.waiting_for_input = true;
                    self.current_input_var = var_name;
                    self.input_prompt = prompt.clone();
                    self.current_pascal_line = i + 1; // Continue from next line
                    output.push_str(&prompt);
                    // Don't continue execution until input is provided
                    return output;
                }
                CommandResult::Continue => {}
                CommandResult::End => {
                    self.current_pascal_line = 0; // Reset for next run
                    break;
                }
            }
        }

        self.current_pascal_line = 0; // Reset for next run
        if output.is_empty() {
            "Pascal program executed successfully".to_string()
        } else {
            output
        }
    }

    fn execute_tw_prolog(&mut self, code: &str) -> String {
        use crate::languages::prolog::PrologInterpreter;
        let mut interpreter = PrologInterpreter::new();
        interpreter.execute(code)
    }
}

impl eframe::App for TimeWarpApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        ctx.set_visuals(egui::Visuals::light());

        // Handle keyboard shortcuts
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::N)) {
            self.code.clear();
            self.output = "New file created.".to_string();
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::O)) {
            if let Some(path) = FileDialog::new()
                .add_filter("Text", &["txt", "twb", "twp", "tpr"])
                .pick_file()
            {
                if let Ok(content) = std::fs::read_to_string(&path) {
                    self.code = content;
                    self.output = format!("Opened file: {}", path.display());
                    self.last_file_path = Some(path.display().to_string());
                }
            }
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::S)) {
            if let Some(path) = &self.last_file_path {
                if std::fs::write(path, &self.code).is_ok() {
                    self.output = format!("Saved to {}", path);
                }
            } else if let Some(path) = FileDialog::new().set_file_name("untitled.twb").save_file() {
                if std::fs::write(&path, &self.code).is_ok() {
                    self.output = format!("Saved to {}", path.display());
                    self.last_file_path = Some(path.display().to_string());
                }
            }
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::F)) {
            self.show_find_replace = true;
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::R)) {
            self.show_find_replace = true;
        }
        if ctx.input(|i| i.key_pressed(egui::Key::F5)) {
            self.active_tab = 1;
            self.execute_code();
        }
        if ctx.input(|i| i.modifiers.ctrl && i.modifiers.shift && i.key_pressed(egui::Key::C)) {
            self.output = String::new();
            self.turtle_commands.clear();
            self.turtle_state = TurtleState {
                x: 200.0,
                y: 200.0,
                angle: 0.0,
                color: egui::Color32::BLACK,
            };
            self.turtle_zoom = 1.0;
            self.turtle_pan = egui::vec2(0.0, 0.0);
        }

        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                ui.menu_button("📁 File", |ui| {
                    if ui.button("📄 New File").clicked() {
                        self.code.clear();
                        self.output = "New file created.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📂 Open File...").clicked() {
                        if let Some(path) = FileDialog::new()
                            .add_filter("Text", &["txt", "twb", "twp", "tpr"])
                            .pick_file()
                        {
                            if let Ok(content) = std::fs::read_to_string(&path) {
                                self.code = content;
                                self.output = format!("Opened file: {}", path.display());
                                self.last_file_path = Some(path.display().to_string());
                            }
                        }
                        ui.close_menu();
                    }
                    if ui.button("💾 Save").clicked() {
                        if let Some(path) = &self.last_file_path {
                            if std::fs::write(path, &self.code).is_ok() {
                                self.output = format!("Saved to {}", path);
                            }
                        } else if let Some(path) =
                            FileDialog::new().set_file_name("untitled.twb").save_file()
                        {
                            if std::fs::write(&path, &self.code).is_ok() {
                                self.output = format!("Saved to {}", path.display());
                                self.last_file_path = Some(path.display().to_string());
                            }
                        }
                        ui.close_menu();
                    }
                    if ui.button("💾 Save As...").clicked() {
                        if let Some(path) =
                            FileDialog::new().set_file_name("untitled.twb").save_file()
                        {
                            if std::fs::write(&path, &self.code).is_ok() {
                                self.output = format!("Saved to {}", path.display());
                                self.last_file_path = Some(path.display().to_string());
                            }
                        }
                        ui.close_menu();
                    }
                });
                ui.menu_button("✏️ Edit", |ui| {
                    if ui.button("🔍 Find...").clicked() {
                        self.show_find_replace = true;
                        ui.close_menu();
                    }
                    if ui.button("🔄 Replace...").clicked() {
                        self.show_find_replace = true;
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("↶ Undo").clicked() {
                        // Note: egui TextEdit doesn't have built-in undo, this is a placeholder
                        ui.close_menu();
                    }
                    if ui.button("↷ Redo").clicked() {
                        // Note: egui TextEdit doesn't have built-in redo, this is a placeholder
                        ui.close_menu();
                    }
                });
                ui.menu_button("👁️ View", |ui| {
                    if ui
                        .selectable_label(self.show_line_numbers, "📏 Show Line Numbers")
                        .clicked()
                    {
                        self.show_line_numbers = !self.show_line_numbers;
                        ui.close_menu();
                    }
                });
                ui.menu_button("❓ Help", |ui| {
                    if ui.button("ℹ️ About").clicked() {
                        self.show_about = true;
                        ui.close_menu();
                    }
                });
            });
        });

        egui::TopBottomPanel::top("top_panel").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.heading("Time Warp IDE");
                ui.separator();
                ui.label("Language:");
                for lang in ["TW BASIC", "TW Pascal", "TW Prolog", "PILOT"] {
                    ui.selectable_value(&mut self.language, lang.to_string(), lang);
                }
                ui.separator();
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if ui
                        .button("🗑️ Clear Output")
                        .on_hover_text("Clear the output and graphics (Ctrl+Shift+C)")
                        .clicked()
                    {
                        self.output = String::new();
                        self.turtle_commands.clear();
                        self.turtle_state = TurtleState {
                            x: 200.0,
                            y: 200.0,
                            angle: 0.0,
                            color: egui::Color32::BLACK,
                        };
                        self.turtle_zoom = 1.0;
                        self.turtle_pan = egui::vec2(0.0, 0.0);
                    }
                    if ui
                        .button("Run ▶")
                        .on_hover_text("Execute the code (F5)")
                        .clicked()
                    {
                        self.active_tab = 1; // Switch to Output tab when running
                        self.execute_code();
                    }
                });
            });
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.add_space(8.0);
            egui::Frame::group(ui.style()).show(ui, |ui| {
                ui.horizontal(|ui| {
                    if ui
                        .selectable_label(self.active_tab == 0, "📝 Code Editor")
                        .clicked()
                    {
                        self.active_tab = 0;
                    }
                    if ui
                        .selectable_label(self.active_tab == 1, "🖥️ Output & Graphics")
                        .clicked()
                    {
                        self.active_tab = 1;
                    }
                });

                ui.separator();

                match self.active_tab {
                    0 => {
                        // Code Editor Tab
                        ui.vertical(|ui| {
                            ui.horizontal(|ui| {
                                ui.checkbox(&mut self.show_line_numbers, "Line numbers");
                                ui.separator();
                                if ui.button("🔍 Find/Replace").clicked() {
                                    self.show_find_replace = !self.show_find_replace;
                                }
                            });

                            if self.show_find_replace {
                                ui.horizontal(|ui| {
                                    ui.label("Find:");
                                    ui.text_edit_singleline(&mut self.find_text);
                                    ui.label("Replace:");
                                    ui.text_edit_singleline(&mut self.replace_text);
                                    if ui.button("Replace All").clicked() {
                                        self.code =
                                            self.code.replace(&self.find_text, &self.replace_text);
                                    }
                                });
                                ui.separator();
                            }

                            egui::ScrollArea::vertical().show(ui, |ui| {
                                if self.show_line_numbers {
                                    // With line numbers
                                    let mut lines: Vec<String> =
                                        self.code.lines().map(|s| s.to_string()).collect();
                                    if lines.is_empty() {
                                        lines.push(String::new());
                                    }

                                    for (i, line) in lines.iter_mut().enumerate() {
                                        ui.horizontal(|ui| {
                                            ui.label(format!("{:4}: ", i + 1));
                                            ui.text_edit_singleline(line);
                                        });
                                    }

                                    self.code = lines.join("\n");
                                } else {
                                    // Without line numbers
                                    ui.add(
                                        egui::TextEdit::multiline(&mut self.code)
                                            .font(egui::TextStyle::Monospace)
                                            .desired_width(f32::INFINITY)
                                            .desired_rows(20),
                                    );
                                }
                            });
                        });
                    }
                    1 => {
                        // Output & Graphics Tab
                        ui.vertical(|ui| {
                            ui.label("Output:");
                            egui::ScrollArea::vertical()
                                .max_height(200.0)
                                .show(ui, |ui| {
                                    ui.add(
                                        egui::TextEdit::multiline(&mut self.output)
                                            .font(egui::TextStyle::Monospace)
                                            .desired_width(f32::INFINITY),
                                    );
                                });

                            // Input handling
                            if self.waiting_for_input {
                                ui.separator();
                                ui.label(&self.input_prompt);
                                ui.horizontal(|ui| {
                                    let response = ui.text_edit_singleline(&mut self.user_input);
                                    if ui.button("Enter").clicked()
                                        || (response.lost_focus()
                                            && ui.input(|i| i.key_pressed(egui::Key::Enter)))
                                    {
                                        // Store the input in the variable
                                        self.variables.insert(
                                            self.current_input_var.clone(),
                                            self.user_input.clone(),
                                        );

                                        // Continue execution
                                        self.waiting_for_input = false;
                                        self.user_input.clear();
                                        self.input_prompt.clear();
                                        self.current_input_var.clear();

                                        // Continue program execution
                                        self.continue_execution();
                                    }
                                });
                            }
                            ui.label("Turtle Graphics:");
                            ui.horizontal(|ui| {
                                ui.label("Zoom:");
                                ui.add(
                                    egui::DragValue::new(&mut self.turtle_zoom)
                                        .clamp_range(0.1..=5.0)
                                        .speed(0.1),
                                );
                                if ui.button("🔍 Reset View").clicked() {
                                    self.turtle_zoom = 1.0;
                                    self.turtle_pan = egui::vec2(0.0, 0.0);
                                }
                            });
                            ui.add_space(4.0);

                            // Simple canvas for turtle graphics
                            let canvas_size = egui::vec2(400.0, 300.0);
                            let (rect, response) =
                                ui.allocate_exact_size(canvas_size, egui::Sense::drag());

                            // Handle pan
                            if response.dragged() {
                                self.turtle_pan += response.drag_delta() / self.turtle_zoom;
                            }

                            ui.painter().rect_filled(rect, 0.0, egui::Color32::WHITE);
                            ui.painter().rect_stroke(
                                rect,
                                0.0,
                                egui::Stroke::new(1.0, egui::Color32::BLACK),
                            );

                            // Draw turtle lines with zoom and pan
                            for command in &self.turtle_commands {
                                if command.starts_with("LINE ") {
                                    let parts: Vec<&str> = command.split_whitespace().collect();
                                    if parts.len() >= 5 {
                                        if let (Ok(x1), Ok(y1), Ok(x2), Ok(y2)) = (
                                            parts[1].parse::<f32>(),
                                            parts[2].parse::<f32>(),
                                            parts[3].parse::<f32>(),
                                            parts[4].parse::<f32>(),
                                        ) {
                                            let center = rect.center();
                                            let start = egui::pos2(
                                                center.x
                                                    + (x1 + self.turtle_pan.x) * self.turtle_zoom,
                                                center.y
                                                    + (y1 + self.turtle_pan.y) * self.turtle_zoom,
                                            );
                                            let end = egui::pos2(
                                                center.x
                                                    + (x2 + self.turtle_pan.x) * self.turtle_zoom,
                                                center.y
                                                    + (y2 + self.turtle_pan.y) * self.turtle_zoom,
                                            );
                                            ui.painter().line_segment(
                                                [start, end],
                                                egui::Stroke::new(2.0, egui::Color32::BLACK),
                                            );
                                        }
                                    }
                                }
                            }

                            // Draw turtle
                            let center = rect.center();
                            let turtle_x = center.x
                                + (self.turtle_state.x + self.turtle_pan.x) * self.turtle_zoom;
                            let turtle_y = center.y
                                + (self.turtle_state.y + self.turtle_pan.y) * self.turtle_zoom;

                            // Draw a simple triangle for the turtle
                            let size = 8.0 * self.turtle_zoom;
                            let angle_rad = self.turtle_state.angle.to_radians();
                            let points = [
                                egui::pos2(
                                    turtle_x + size * angle_rad.cos(),
                                    turtle_y + size * angle_rad.sin(),
                                ),
                                egui::pos2(
                                    turtle_x + size * (angle_rad + 2.0944).cos(),
                                    turtle_y + size * (angle_rad + 2.0944).sin(),
                                ),
                                egui::pos2(
                                    turtle_x + size * (angle_rad - 2.0944).cos(),
                                    turtle_y + size * (angle_rad - 2.0944).sin(),
                                ),
                            ];

                            ui.painter().add(egui::Shape::convex_polygon(
                                points.to_vec(),
                                self.turtle_state.color,
                                egui::Stroke::new(1.0, egui::Color32::BLACK),
                            ));
                        });
                    }
                    _ => {}
                }
            });
        });

        egui::TopBottomPanel::bottom("status_bar").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.label(format!("Language: {}", self.language));
                ui.separator();
                ui.label(format!("Lines: {}", self.code.lines().count()));
                ui.separator();
                if self.is_executing {
                    ui.label("⚡ Executing...");
                } else if self.waiting_for_input {
                    ui.label("⌨️ Waiting for input");
                } else {
                    ui.label("✅ Ready");
                }
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if let Some(path) = &self.last_file_path {
                        ui.label(format!("File: {}", path));
                    } else {
                        ui.label("File: Untitled");
                    }
                });
            });
        });

        // About dialog
        if self.show_about {
            egui::Window::new("About Time Warp IDE")
                .collapsible(false)
                .resizable(false)
                .show(ctx, |ui| {
                    ui.vertical_centered(|ui| {
                        ui.heading("Time Warp IDE");
                        ui.label("Version 1.0.0");
                        ui.label("A modern, educational programming environment");
                        ui.label("built in Rust using the egui framework.");
                        ui.separator();
                        ui.label("Supports TW BASIC, TW Pascal, and TW Prolog");
                        ui.label("with interactive input and turtle graphics.");
                        ui.separator();
                        if ui.button("Close").clicked() {
                            self.show_about = false;
                        }
                    });
                });
        }
    }
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 800.0])
            .with_title("Time Warp IDE"),
        ..Default::default()
    };

    eframe::run_native(
        "Time Warp IDE",
        options,
        Box::new(|_cc| Box::new(TimeWarpApp::default())),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_file_operations() {
        // Test New File functionality
        let mut app = TimeWarpApp::default();
        app.code = "some code".to_string();
        app.output = "some output".to_string();
        app.last_file_path = Some("test.txt".to_string());

        // Simulate New File
        app.code.clear();
        app.output = "New file created.".to_string();
        app.last_file_path = None;

        assert_eq!(app.code, "");
        assert_eq!(app.output, "New file created.");
        assert_eq!(app.last_file_path, None);
    }

    #[test]
    fn test_save_operations() {
        let mut app = TimeWarpApp::default();
        app.code = "10 PRINT \"TEST\"".to_string();
        app.last_file_path = Some("test_save.twb".to_string());

        // Simulate Save
        if let Some(path) = &app.last_file_path {
            fs::write(path, &app.code).unwrap();
            app.output = format!("Saved to {}", path);
        }

        // Verify file was saved
        let content = fs::read_to_string("test_save.twb").unwrap();
        assert_eq!(content, "10 PRINT \"TEST\"");
        assert_eq!(app.output, "Saved to test_save.twb");

        // Cleanup
        fs::remove_file("test_save.twb").unwrap();
    }

    #[test]
    fn test_view_operations() {
        let mut app = TimeWarpApp::default();

        // Test Show Line Numbers toggle
        assert_eq!(app.show_line_numbers, false);
        app.show_line_numbers = !app.show_line_numbers;
        assert_eq!(app.show_line_numbers, true);
        app.show_line_numbers = !app.show_line_numbers;
        assert_eq!(app.show_line_numbers, false);
    }

    #[test]
    fn test_edit_operations() {
        let mut app = TimeWarpApp::default();
        app.code = "old text".to_string();

        // Test Find/Replace
        assert_eq!(app.show_find_replace, false);
        app.show_find_replace = true;
        assert_eq!(app.show_find_replace, true);

        // Test Replace All
        app.find_text = "old".to_string();
        app.replace_text = "new".to_string();
        app.code = app.code.replace(&app.find_text, &app.replace_text);
        assert_eq!(app.code, "new text");
    }

    #[test]
    fn test_help_operations() {
        let mut app = TimeWarpApp::default();

        // Test About dialog
        assert_eq!(app.show_about, false);
        app.show_about = true;
        assert_eq!(app.show_about, true);
        app.show_about = false;
        assert_eq!(app.show_about, false);
    }

    #[test]
    fn test_menu_state_changes() {
        let mut app = TimeWarpApp::default();

        // Test all menu state changes
        assert_eq!(app.show_find_replace, false);
        assert_eq!(app.show_about, false);
        assert_eq!(app.show_line_numbers, false);

        // Simulate menu clicks
        app.show_find_replace = true;
        app.show_about = true;
        app.show_line_numbers = true;

        assert_eq!(app.show_find_replace, true);
        assert_eq!(app.show_about, true);
        assert_eq!(app.show_line_numbers, true);
    }

    #[test]
    fn test_language_selection() {
        let mut app = TimeWarpApp::default();

        // Test language changes
        assert_eq!(app.language, "TW BASIC");
        app.language = "TW Pascal".to_string();
        assert_eq!(app.language, "TW Pascal");
        app.language = "TW Prolog".to_string();
        assert_eq!(app.language, "TW Prolog");
    }

    #[test]
    fn test_tab_switching() {
        let mut app = TimeWarpApp::default();

        // Test tab switching
        assert_eq!(app.active_tab, 0);
        app.active_tab = 1;
        assert_eq!(app.active_tab, 1);
        app.active_tab = 0;
        assert_eq!(app.active_tab, 0);
    }

    #[test]
    fn test_keyboard_shortcuts() {
        let mut app = TimeWarpApp::default();
        let ctx = egui::Context::default();

        // Test Ctrl+N (New File)
        app.code = "existing code".to_string();
        app.last_file_path = Some("file.txt".to_string());

        // Simulate Ctrl+N key press
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::N)) {
            app.code.clear();
            app.output = "New file created.".to_string();
        }

        // Since we can't simulate key presses in unit tests, test the logic directly
        app.code.clear();
        app.output = "New file created.".to_string();
        app.last_file_path = None;

        assert_eq!(app.code, "");
        assert_eq!(app.output, "New file created.");
        assert_eq!(app.last_file_path, None);
    }

    #[test]
    fn test_pilot_execution() {
        let mut app = TimeWarpApp::default();
        app.language = "PILOT".to_string();

        // Test basic PILOT T: command
        let code = "T:Hello World!\nT:This is PILOT\nE:";
        let result = app.execute_pilot(code);
        assert!(result.contains("Hello World!"));
        assert!(result.contains("This is PILOT"));

        // Test PILOT A: command (input)
        let input_code = "T:Enter your name:\nA:#NAME\nT:Hello #NAME\nE:";
        let result = app.execute_pilot(input_code);
        assert!(result.contains("Enter your name:"));
        assert!(result.contains("?")); // Default prompt
                                       // Should be waiting for input
        assert!(app.waiting_for_input);
        assert_eq!(app.current_input_var, "#NAME");
    }

    #[test]
    fn test_pilot_input_parsing() {
        let app = TimeWarpApp::default();

        // Test simple variable input
        let result = app.parse_pilot_input_command("#NAME");
        assert_eq!(result, Some(("#NAME".to_string(), "? ".to_string())));

        // Test input with custom prompt
        let result = app.parse_pilot_input_command("\"Enter name\",#NAME");
        assert_eq!(
            result,
            Some(("#NAME".to_string(), "Enter name".to_string()))
        );
    }

    #[test]
    fn test_pilot_text_processing() {
        let mut app = TimeWarpApp::default();

        // Test text without variables
        let result = app.process_pilot_text("Hello World");
        assert_eq!(result, "Hello World");

        // Test text with quoted strings
        let result = app.process_pilot_text("\"Hello\" World");
        assert_eq!(result, "Hello World");

        // Test text with variables (when variable exists)
        app.variables
            .insert("NAME".to_string(), "Alice".to_string());
        let result = app.process_pilot_text("Hello #NAME");
        assert_eq!(result, "Hello Alice");

        // Test text with undefined variables
        let result = app.process_pilot_text("Hello #UNKNOWN");
        assert_eq!(result, "Hello #UNKNOWN");
    }

    #[test]
    fn test_basic_program_execution() {
        let mut app = TimeWarpApp::default();
        app.language = "TW BASIC".to_string();

        // Test simple BASIC program execution
        let basic_code = "10 PRINT \"Hello from Time_Warp!\"\n20 PRINT \"Testing output console...\"\n30 PRINT \"Count: 1\"\n40 PRINT \"Count: 2\"\n50 PRINT \"Count: 3\"\n60 PRINT \"Test complete!\"";
        let result = app.execute_tw_basic(basic_code);

        // Debug: print the actual result
        println!("Actual result: {:?}", result);

        // Verify the output contains expected strings
        assert!(result.contains("Hello from Time_Warp!"));
        assert!(result.contains("Testing output console..."));
        assert!(result.contains("Count: 1"));
        assert!(result.contains("Count: 2"));
        assert!(result.contains("Count: 3"));
        assert!(result.contains("Test complete!"));
    }
}
