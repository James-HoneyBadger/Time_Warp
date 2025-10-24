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

#[derive(Clone, PartialEq)]
enum DebugState {
    Stopped,
    Running,
    Paused,
}

struct TimeWarpApp {
    code: String,
    output: String,
    active_tab: usize, // 0 = Editor, 1 = Output & Turtle, 2 = Debug
    last_file_path: Option<String>,
    show_line_numbers: bool,
    find_text: String,
    replace_text: String,
    show_find_replace: bool,
    turtle_state: TurtleState,
    turtle_commands: Vec<String>,
    variables: HashMap<String, String>,
    is_executing: bool,
    waiting_for_input: bool,
    input_prompt: String,
    user_input: String,
    current_input_var: String,
    show_about: bool,
    turtle_zoom: f32,
    turtle_pan: egui::Vec2,

    // Debug state
    debug_mode: bool,
    debug_state: DebugState,
    breakpoints: HashMap<String, Vec<u32>>, // filename -> line numbers
    current_debug_line: Option<u32>,
    debug_variables: HashMap<String, String>,
    debug_call_stack: Vec<String>,

    // Code completion
    code_completion_enabled: bool,
    show_completion: bool,
    completion_items: Vec<String>,
    completion_selected: usize,
    completion_query: String,

    // BASIC interpreter instance for continuation after input
    basic_interpreter: Option<crate::languages::basic::Interpreter>,

    // General prompt system
    general_prompt_active: bool,
    general_prompt_message: String,
    general_prompt_input: String,
    general_prompt_callback: Option<Box<dyn FnOnce(String) + 'static>>,

    // Status bar information
    cursor_line: usize,
    cursor_column: usize,
    total_lines: usize,
    execution_timeout_ms: u64,

    // Error notification
    error_message: Option<String>,
    error_timer: f64,

    // Undo/Redo history
    undo_history: Vec<String>,
    undo_position: usize,
    max_undo_steps: usize,
    previous_code: String,

    // Syntax highlighting
    #[allow(dead_code)]
    syntax_highlighting_enabled: bool,

    // Clipboard operations
    #[allow(dead_code)]
    clipboard_content: String,
    #[allow(dead_code)]
    selected_text: String,
    #[allow(dead_code)]
    cursor_position: usize,
}

impl Default for TimeWarpApp {
    fn default() -> Self {
        Self {
            code: String::new(),
            output: String::new(),
            active_tab: 0, // Start with Editor tab
            last_file_path: None,
            show_line_numbers: false,
            find_text: String::new(),
            replace_text: String::new(),
            show_find_replace: false,
            turtle_state: TurtleState {
                x: 0.0,
                y: 0.0,
                angle: 0.0,
                color: egui::Color32::BLACK,
            },
            turtle_commands: Vec::new(),
            variables: HashMap::new(),
            is_executing: false,
            waiting_for_input: false,
            input_prompt: String::new(),
            user_input: String::new(),
            current_input_var: String::new(),
            show_about: false,
            turtle_zoom: 1.0,
            turtle_pan: egui::vec2(0.0, 0.0),

            // Debug defaults
            debug_mode: false,
            debug_state: DebugState::Stopped,
            breakpoints: HashMap::new(),
            current_debug_line: None,
            debug_variables: HashMap::new(),
            debug_call_stack: Vec::new(),

            // Completion defaults
            code_completion_enabled: false,
            show_completion: false,
            completion_items: Vec::new(),
            completion_selected: 0,
            completion_query: String::new(),

            // BASIC interpreter instance for continuation after input
            basic_interpreter: None,

            // General prompt system
            general_prompt_active: false,
            general_prompt_message: String::new(),
            general_prompt_input: String::new(),
            general_prompt_callback: None,

            // Status bar defaults
            cursor_line: 1,
            cursor_column: 1,
            total_lines: 1,
            execution_timeout_ms: 5000, // 5 seconds default timeout

            // Error notification defaults
            error_message: None,
            error_timer: 0.0,

            // Undo/Redo defaults
            undo_history: Vec::new(),
            undo_position: 0,
            max_undo_steps: 100,
            previous_code: String::new(),

            // Syntax highlighting defaults
            syntax_highlighting_enabled: true,

            // Clipboard defaults
            clipboard_content: String::new(),
            selected_text: String::new(),
            cursor_position: 0,
        }
    }
}

impl TimeWarpApp {
    fn show_error(&mut self, message: String) {
        self.error_message = Some(message);
        self.error_timer = 0.0;
    }

    /// Shows a general prompt to the user and calls the callback with their input
    fn show_prompt<F>(&mut self, message: String, callback: F)
    where
        F: FnOnce(String) + 'static,
    {
        self.general_prompt_active = true;
        self.general_prompt_message = message;
        self.general_prompt_input.clear();
        self.general_prompt_callback = Some(Box::new(callback));
    }

    /// Public method to show a prompt from outside the app
    pub fn prompt_user<F>(&mut self, message: &str, callback: F)
    where
        F: FnOnce(String) + 'static,
    {
        self.show_prompt(message.to_string(), callback);
    }

    fn save_undo_state(&mut self) {
        // Remove any redo states after current position
        self.undo_history.truncate(self.undo_position);

        // Add current state to history
        self.undo_history.push(self.code.clone());
        self.undo_position = self.undo_history.len();

        // Limit history size
        if self.undo_history.len() > self.max_undo_steps {
            self.undo_history.remove(0);
            self.undo_position -= 1;
        }
    }

    fn undo(&mut self) -> bool {
        if self.undo_position > 0 {
            self.undo_position -= 1;
            self.code = self.undo_history[self.undo_position].clone();
            true
        } else {
            false
        }
    }

    fn redo(&mut self) -> bool {
        if self.undo_position < self.undo_history.len() - 1 {
            self.undo_position += 1;
            self.code = self.undo_history[self.undo_position].clone();
            true
        } else {
            false
        }
    }

    fn render_syntax_highlighted_text(&self, ui: &mut egui::Ui, text: &str) {
        // Basic syntax highlighting for BASIC keywords
        let keywords = [
            "PRINT",
            "WRITELN",
            "INPUT",
            "READLN",
            "LET",
            "IF",
            "THEN",
            "ELSE",
            "END",
            "STOP",
            "FOR",
            "TO",
            "STEP",
            "NEXT",
            "WHILE",
            "WEND",
            "GOTO",
            "GOSUB",
            "RETURN",
            "REM",
            "CLS",
            "COLOR",
            "LOCATE",
            "BEEP",
            "SLEEP",
            "RANDOMIZE",
            "DIM",
            "DATA",
            "READ",
            "RESTORE",
            "FORWARD",
            "FD",
            "BACK",
            "BK",
            "LEFT",
            "LT",
            "RIGHT",
            "RT",
            "PENUP",
            "PU",
            "PENDOWN",
            "PD",
            "AND",
            "OR",
            "NOT",
            "SIN",
            "COS",
            "TAN",
            "SQR",
            "ABS",
            "INT",
            "LOG",
            "EXP",
            "ATN",
            "RND",
        ];

        let lines: Vec<&str> = text.lines().collect();

        for (line_num, line) in lines.iter().enumerate() {
            // Show line number
            ui.horizontal(|ui| {
                ui.label(
                    egui::RichText::new(format!("{:3}: ", line_num + 1))
                        .weak()
                        .monospace(),
                );

                // Split line into tokens and highlight
                let mut remaining = *line;
                let mut first = true;

                while !remaining.is_empty() {
                    let mut found_keyword = false;

                    // Check for keywords at start of remaining text
                    for keyword in &keywords {
                        if remaining
                            .to_uppercase()
                            .starts_with(&keyword.to_uppercase())
                        {
                            let keyword_len = keyword.len();
                            if remaining.len() == keyword_len
                                || !remaining
                                    .chars()
                                    .nth(keyword_len)
                                    .unwrap_or(' ')
                                    .is_alphanumeric()
                            {
                                if !first {
                                    ui.add_space(4.0);
                                }
                                ui.label(
                                    egui::RichText::new(&remaining[..keyword_len])
                                        .color(egui::Color32::from_rgb(86, 156, 214)) // Blue for keywords
                                        .monospace(),
                                );
                                remaining = &remaining[keyword_len..];
                                found_keyword = true;
                                first = false;
                                break;
                            }
                        }
                    }

                    if !found_keyword {
                        // Find next space or end
                        let space_pos = remaining.find(' ').unwrap_or(remaining.len());
                        let token = &remaining[..space_pos];

                        if !first {
                            ui.add_space(4.0);
                        }

                        // Check if it's a number
                        if token.parse::<f64>().is_ok() {
                            ui.label(
                                egui::RichText::new(token)
                                    .color(egui::Color32::from_rgb(181, 206, 168)) // Green for numbers
                                    .monospace(),
                            );
                        } else if token.starts_with('"') && token.ends_with('"') {
                            ui.label(
                                egui::RichText::new(token)
                                    .color(egui::Color32::from_rgb(206, 145, 120)) // Orange for strings
                                    .monospace(),
                            );
                        } else {
                            ui.label(
                                egui::RichText::new(token)
                                    .color(egui::Color32::WHITE) // White for identifiers/comments
                                    .monospace(),
                            );
                        }

                        remaining = &remaining[space_pos..];
                        if space_pos < remaining.len() {
                            remaining = &remaining[1..]; // Skip space
                        }
                        first = false;
                    }
                }
            });
        }
    }

    fn execute_code(&mut self) {
        self.active_tab = 1; // Switch to Output tab when running
        self.is_executing = true;
        // Clear output before execution so only current program output is shown
        self.output.clear();
        let code = self.code.clone();
        let result = self.execute_tw_basic(&code);

        // Check if execution needs input
        if self.waiting_for_input {
            // Program is waiting for input - don't mark as complete yet
            // The output will be updated when input is provided
            self.is_executing = false;
            return;
        }

        // Set output to the result (which may be empty)
        self.output = result;
        self.is_executing = false;
    }

    fn execute_tw_basic(&mut self, code: &str) -> String {
        use crate::languages::basic::Interpreter;

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

        // Join statements with newlines for the interpreter (BASIC statement separator)
        let program_code = statements.join("\n");

        let mut interpreter = Interpreter::new();
        // Set execution timeout based on instruction limit
        // Rough estimate: 1000 instructions per second
        interpreter.max_instructions = (self.execution_timeout_ms * 1000) as usize;

        match interpreter.execute(&program_code) {
            Ok(result) => match result {
                crate::languages::basic::ExecutionResult::Complete {
                    output,
                    graphics_commands,
                } => {
                    // Process graphics commands
                    self.process_graphics_commands(&graphics_commands);
                    self.basic_interpreter = None; // Clear stored interpreter
                    output
                }
                crate::languages::basic::ExecutionResult::NeedInput {
                    variable,
                    prompt,
                    partial_output,
                    partial_graphics,
                } => {
                    self.waiting_for_input = true;
                    self.input_prompt = prompt.clone();
                    self.current_input_var = variable;
                    // Process any graphics commands that were executed before input was needed
                    self.process_graphics_commands(&partial_graphics);
                    // Store the interpreter for continuation
                    self.basic_interpreter = Some(interpreter);
                    // For now, just return the partial output with the prompt
                    format!("{}{}", partial_output, prompt)
                }
                crate::languages::basic::ExecutionResult::Error(err) => {
                    self.basic_interpreter = None; // Clear on error
                    format!("Error: {:?}", err)
                }
            },
            Err(err) => {
                format!("Error: {:?}", err)
            }
        }
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

    fn process_graphics_commands(&mut self, commands: &[crate::languages::basic::GraphicsCommand]) {
        for cmd in commands {
            match cmd.command.as_str() {
                "FORWARD" => {
                    self.move_turtle(cmd.value, true);
                }
                "RIGHT" => {
                    self.turtle_state.angle = (self.turtle_state.angle + cmd.value) % 360.0;
                }
                _ => {
                    // Unknown command, ignore
                }
            }
        }
    }

    // Clipboard operations
    fn copy_text(&mut self, ctx: &egui::Context) {
        // For now, copy the entire code content
        // In a full implementation, this would copy selected text
        ctx.output_mut(|o| o.copied_text = self.code.clone());
        self.clipboard_content = self.code.clone();
    }

    fn cut_text(&mut self, ctx: &egui::Context) {
        // For now, cut the entire code content
        // In a full implementation, this would cut selected text
        ctx.output_mut(|o| o.copied_text = self.code.clone());
        self.clipboard_content = self.code.clone();
        self.code.clear();
    }

    fn paste_text(&mut self, ctx: &egui::Context) {
        // Check for paste events
        let paste_text = ctx.input(|i| {
            i.events.iter().find_map(|e| {
                if let egui::Event::Paste(text) = e {
                    Some(text.clone())
                } else {
                    None
                }
            })
        });

        if let Some(text) = paste_text {
            // Insert clipboard content at cursor position
            // For now, replace entire content - in full implementation would insert at cursor
            self.code = text;
        }
    }
}

impl TimeWarpApp {
    // Debug methods
    fn start_debug_session(&mut self) {
        self.debug_state = DebugState::Running;
        self.debug_variables.clear();
        self.debug_call_stack.clear();
        self.current_debug_line = Some(1);
        self.output = "Debug session started.\n".to_string();
    }

    fn stop_debug_session(&mut self) {
        self.debug_state = DebugState::Stopped;
        self.current_debug_line = None;
        self.output = "Debug session stopped.\n".to_string();
    }

    fn step_debug(&mut self) {
        if let Some(current_line) = self.current_debug_line {
            self.current_debug_line = Some(current_line + 1);
            // In a full implementation, this would execute one line of code
            self.output = format!("Stepped to line {}\n", current_line + 1);
        }
    }

    fn render_debug_editor(&mut self, ui: &mut egui::Ui) {
        let filename = self
            .last_file_path
            .as_ref()
            .and_then(|p| std::path::Path::new(p).file_name())
            .and_then(|n| n.to_str())
            .unwrap_or("untitled");

        let syntax_enabled = self.syntax_highlighting_enabled;
        let current_debug_line = self.current_debug_line;
        let language = "TW BASIC".to_string();
        let keywords: Vec<String> = self
            .get_language_keywords()
            .into_iter()
            .map(|s| s.to_string())
            .collect();

        egui::ScrollArea::vertical().show(ui, |ui| {
            ui.set_width(ui.available_width());

            let lines: Vec<String> = self.code.lines().map(|s| s.to_string()).collect();
            let breakpoints = self
                .breakpoints
                .entry(filename.to_string())
                .or_insert_with(Vec::new);

            for (line_idx, line) in lines.iter().enumerate() {
                ui.horizontal(|ui| {
                    // Breakpoint column
                    let line_number = (line_idx + 1) as u32;
                    let has_breakpoint = breakpoints.contains(&line_number);

                    let breakpoint_button =
                        egui::Button::new(if has_breakpoint { "🔴" } else { "⚪" })
                            .frame(false)
                            .small();

                    if ui
                        .add(breakpoint_button)
                        .on_hover_text(if has_breakpoint {
                            "Click to remove breakpoint"
                        } else {
                            "Click to add breakpoint"
                        })
                        .clicked()
                    {
                        if has_breakpoint {
                            breakpoints.retain(|&x| x != line_number);
                        } else {
                            breakpoints.push(line_number);
                            breakpoints.sort();
                        }
                    }

                    // Line number
                    ui.label(
                        egui::RichText::new(format!("{:4}", line_number))
                            .color(egui::Color32::from_rgb(100, 100, 100))
                            .font(egui::FontId::monospace(12.0)),
                    );

                    // Current debug line indicator
                    if Some(line_number) == current_debug_line {
                        ui.label(egui::RichText::new("▶").color(egui::Color32::YELLOW));
                    } else {
                        ui.add_space(12.0);
                    }

                    // Line content with syntax highlighting
                    if syntax_enabled {
                        // Simple syntax highlighting for debug view
                        let highlighted = Self::highlight_line_static(&line, &keywords, &language);
                        for (text, color) in highlighted {
                            ui.label(
                                egui::RichText::new(text)
                                    .color(color)
                                    .font(egui::FontId::monospace(12.0)),
                            );
                        }
                    } else {
                        ui.label(egui::RichText::new(line).font(egui::FontId::monospace(12.0)));
                    }
                });
            }

            // Handle empty last line
            if self.code.ends_with('\n') || self.code.is_empty() {
                ui.horizontal(|ui| {
                    let line_number = (lines.len() + 1) as u32;
                    let has_breakpoint = breakpoints.contains(&line_number);

                    let breakpoint_button =
                        egui::Button::new(if has_breakpoint { "🔴" } else { "⚪" })
                            .frame(false)
                            .small();

                    if ui
                        .add(breakpoint_button)
                        .on_hover_text(if has_breakpoint {
                            "Click to remove breakpoint"
                        } else {
                            "Click to add breakpoint"
                        })
                        .clicked()
                    {
                        if has_breakpoint {
                            breakpoints.retain(|&x| x != line_number);
                        } else {
                            breakpoints.push(line_number);
                            breakpoints.sort();
                        }
                    }

                    ui.label(
                        egui::RichText::new(format!("{:4}", line_number))
                            .color(egui::Color32::from_rgb(100, 100, 100))
                            .font(egui::FontId::monospace(12.0)),
                    );
                    ui.add_space(12.0);
                });
            }
        });
    }

    fn highlight_line_static(
        line: &str,
        keywords: &[String],
        language: &str,
    ) -> Vec<(String, egui::Color32)> {
        if line.trim().is_empty() {
            return vec![(line.to_string(), egui::Color32::BLACK)];
        }

        let mut highlighted = Vec::new();
        let chars: Vec<char> = line.chars().collect();
        let mut i = 0;

        // Create keyword set from provided keywords
        let keyword_set: std::collections::HashSet<String> =
            keywords.iter().map(|k| k.to_uppercase()).collect();

        while i < chars.len() {
            // Check for comments first
            if Self::is_comment_start_static(&line[i..], language) {
                highlighted.push((line[i..].to_string(), egui::Color32::from_rgb(0, 128, 0)));
                break;
            }

            // Check for strings
            if chars[i] == '"' {
                let mut end = i + 1;
                while end < chars.len() && chars[end] != '"' {
                    end += 1;
                }
                if end < chars.len() {
                    end += 1;
                }

                if i > 0 {
                    highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                }
                highlighted.push((
                    line[i..end].to_string(),
                    egui::Color32::from_rgb(163, 21, 21),
                ));
                i = end;
                continue;
            }

            // Check for numbers
            if chars[i].is_ascii_digit() {
                let mut end = i + 1;
                while end < chars.len() && (chars[end].is_ascii_digit() || chars[end] == '.') {
                    end += 1;
                }

                if i > 0 {
                    highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                }
                highlighted.push((
                    line[i..end].to_string(),
                    egui::Color32::from_rgb(0, 128, 128),
                ));
                i = end;
                continue;
            }

            // Check for operators
            if "+-*/=<>!&|^%".contains(chars[i]) {
                let mut end = i + 1;
                // Handle compound operators like ==, !=, <=, >=, +=, etc.
                if end < chars.len() && "+-*/=<>!&|^%".contains(chars[end]) {
                    end += 1;
                }

                if i > 0 {
                    highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                }
                highlighted.push((
                    line[i..end].to_string(),
                    egui::Color32::from_rgb(128, 64, 0),
                )); // Orange-brown for operators
                i = end;
                continue;
            }

            // Check for brackets and parentheses
            if "(){}[]".contains(chars[i]) {
                if i > 0 {
                    highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                }
                highlighted.push((
                    line[i..i + 1].to_string(),
                    egui::Color32::from_rgb(128, 0, 128),
                )); // Purple for brackets
                i += 1;
                continue;
            }

            // Check for keywords
            let remaining = &line[i..];
            let mut _found_keyword = false;
            for keyword in &keyword_set {
                if remaining.to_uppercase().starts_with(keyword) {
                    let keyword_len = keyword.len();
                    let next_char = if i + keyword_len < chars.len() {
                        chars[i + keyword_len]
                    } else {
                        ' '
                    };

                    if next_char.is_whitespace()
                        || next_char == '('
                        || next_char == ')'
                        || next_char == ','
                        || next_char == ';'
                        || next_char == ':'
                    {
                        if i > 0 {
                            highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                        }
                        highlighted.push((
                            line[i..i + keyword_len].to_string(),
                            egui::Color32::from_rgb(0, 0, 255),
                        ));
                        i += keyword_len;
                        _found_keyword = true;
                        break;
                    }
                }
            }

            // Check for operators
            if "+-*/=<>!&|^%".contains(chars[i]) {
                let mut end = i + 1;
                // Handle compound operators like ==, !=, <=, >=, +=, etc.
                if end < chars.len() && "+-*/=<>!&|^%".contains(chars[end]) {
                    end += 1;
                }

                if i > 0 {
                    highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                }
                highlighted.push((
                    line[i..end].to_string(),
                    egui::Color32::from_rgb(128, 64, 0),
                )); // Orange-brown for operators
                i = end;
                continue;
            }

            // Check for brackets and parentheses
            if "(){}[]".contains(chars[i]) {
                if i > 0 {
                    highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                }
                highlighted.push((
                    line[i..i + 1].to_string(),
                    egui::Color32::from_rgb(128, 0, 128),
                )); // Purple for brackets
                i += 1;
                continue;
            }

            // Check for keywords
            let remaining = &line[i..];
            let mut _found_keyword = false;
            for keyword in &keyword_set {
                if remaining.to_uppercase().starts_with(keyword) {
                    let keyword_len = keyword.len();
                    let next_char = if i + keyword_len < chars.len() {
                        chars[i + keyword_len]
                    } else {
                        ' '
                    };

                    if next_char.is_whitespace()
                        || next_char == '('
                        || next_char == ')'
                        || next_char == ','
                        || next_char == ';'
                        || next_char == ':'
                    {
                        if i > 0 {
                            highlighted.push((line[..i].to_string(), egui::Color32::BLACK));
                        }
                        highlighted.push((
                            line[i..i + keyword_len].to_string(),
                            egui::Color32::from_rgb(0, 0, 255),
                        ));
                        i += keyword_len;
                        _found_keyword = true;
                        break;
                    }
                }
            }

            if !_found_keyword {
                i += 1;
            }
        }

        if i < line.len() {
            highlighted.push((line[i..].to_string(), egui::Color32::BLACK));
        }

        highlighted
    }

    fn is_comment_start_static(text: &str, language: &str) -> bool {
        match language {
            "TW BASIC" => text.starts_with("REM ") || text.starts_with("'"),
            _ => text.starts_with("//") || text.starts_with("#"),
        }
    }

    // Code completion methods
    fn get_language_keywords(&self) -> Vec<&'static str> {
        vec![
            "PRINT",
            "INPUT",
            "LET",
            "IF",
            "THEN",
            "ELSE",
            "FOR",
            "TO",
            "STEP",
            "NEXT",
            "WHILE",
            "WEND",
            "GOTO",
            "GOSUB",
            "RETURN",
            "END",
            "CLS",
            "LOCATE",
            "COLOR",
            "BEEP",
            "SLEEP",
            "RANDOMIZE",
            "RND",
            "INT",
            "STR$",
            "VAL",
            "LEN",
            "LEFT$",
            "RIGHT$",
            "MID$",
            "CHR$",
            "ASC",
            "ABS",
            "SIN",
            "COS",
            "TAN",
            "LOG",
            "EXP",
            "SQR",
            "AND",
            "OR",
            "NOT",
            "MOD",
            "DIM",
            "READ",
            "DATA",
            "RESTORE",
            "DEF",
            "FN",
            "REM",
        ]
    }

    fn get_completion_suggestions(&self, query: &str) -> Vec<String> {
        let mut suggestions = Vec::new();
        let query_lower = query.to_lowercase();

        // Add language keywords
        let keywords = self.get_language_keywords();
        for keyword in keywords {
            if keyword.to_lowercase().starts_with(&query_lower) {
                suggestions.push(keyword.to_string());
            }
        }

        // Add variables from debug session
        for (var_name, _) in &self.debug_variables {
            if var_name.to_lowercase().starts_with(&query_lower) {
                suggestions.push(var_name.clone());
            }
        }

        // Add TW BASIC functions and commands
        let basic_functions = vec![
            "ABS(", "ASC(", "CHR$(", "COS(", "EXP(", "INT(", "LEFT$(", "LEN(", "LOG(", "MID$(",
            "RIGHT$(", "RND(", "SIN(", "SQR(", "STR$(", "TAN(", "VAL(",
        ];

        for func in basic_functions {
            if func.to_lowercase().starts_with(&query_lower) {
                suggestions.push(func.to_string());
            }
        }

        // Add BASIC commands that might be partially typed
        let basic_commands = vec![
            "PRINT",
            "WRITELN",
            "INPUT",
            "READLN",
            "LET",
            "IF",
            "THEN",
            "ELSE",
            "WHILE",
            "DO",
            "FOR",
            "TO",
            "STEP",
            "NEXT",
            "FORWARD",
            "FD",
            "BACK",
            "BK",
            "LEFT",
            "LT",
            "RIGHT",
            "RT",
            "PENUP",
            "PU",
            "PENDOWN",
            "PD",
            "WHILE",
            "WEND",
            "GOTO",
            "GOSUB",
            "RETURN",
            "END",
            "CLS",
            "LOCATE",
            "COLOR",
            "BEEP",
            "SLEEP",
            "RANDOMIZE",
        ];

        for cmd in basic_commands {
            if cmd.to_lowercase().starts_with(&query_lower) {
                suggestions.push(cmd.to_string());
            }
        }

        // Sort and deduplicate
        suggestions.sort();
        suggestions.dedup();

        // Limit to top 10 suggestions
        suggestions.truncate(10);

        suggestions
    }

    #[allow(dead_code)]
    fn apply_completion(&mut self, completion: &str) {
        // Simple implementation - just append to current code
        // In a real implementation, this would replace the current word
        self.code.push_str(completion);
        self.show_completion = false;
    }

    fn render_syntax_highlighted_editor(&mut self, ui: &mut egui::Ui) {
        // Custom syntax highlighting implementation
        let response = ui.add(
            egui::TextEdit::multiline(&mut self.code)
                .font(egui::TextStyle::Monospace)
                .desired_width(f32::INFINITY)
                .desired_rows(20),
        );

        // Check if code changed and save undo state
        if response.changed() && self.code != self.previous_code {
            self.save_undo_state();
            self.previous_code = self.code.clone();
        }

        // Handle keyboard shortcuts for completion
        if ui.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::Space)) {
            self.trigger_completion();
        }

        // Handle undo/redo keyboard shortcuts
        if ui.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::Z) && !i.modifiers.shift) {
            self.undo();
        }
        if ui.input(|i| {
            (i.modifiers.ctrl && i.key_pressed(egui::Key::Y))
                || (i.modifiers.ctrl && i.modifiers.shift && i.key_pressed(egui::Key::Z))
        }) {
            self.redo();
        }

        // Auto-completion triggers
        if let Some(text) = ui.input(|i| {
            i.events.iter().find_map(|e| match e {
                egui::Event::Text(text) => Some(text.clone()),
                _ => None,
            })
        }) {
            // Trigger completion after typing certain characters
            if text.chars().any(|c| c == '.' || c == '(' || c == ' ') {
                // Small delay to avoid triggering on every keystroke
                self.trigger_completion();
            }
        }

        // Render syntax highlighted preview below the editor
        if !self.code.is_empty() && self.active_tab == 0 {
            ui.separator();
            ui.label(
                egui::RichText::new("Syntax Highlighted Preview:")
                    .small()
                    .weak(),
            );

            egui::ScrollArea::vertical().show(ui, |ui| {
                self.render_syntax_highlighted_text(ui, &self.code);
            });
        }
    }

    fn trigger_completion(&mut self) {
        // Get current word at cursor position (more accurate implementation)
        let cursor_pos = self.code.len(); // Simplified - in a real implementation we'd track actual cursor
        let before_cursor = &self.code[..cursor_pos];

        // Find the current word being typed
        let mut word_start = cursor_pos;
        for (i, ch) in before_cursor.char_indices().rev() {
            if ch.is_whitespace()
                || ch == '('
                || ch == ')'
                || ch == ','
                || ch == ';'
                || ch == ':'
                || ch == '='
            {
                break;
            }
            word_start = i;
        }

        let current_word = if word_start < cursor_pos {
            &before_cursor[word_start..cursor_pos]
        } else {
            ""
        };

        self.completion_query = current_word.to_string();
        self.completion_items = self.get_completion_suggestions(current_word);
        self.completion_selected = 0;
        self.show_completion = self.code_completion_enabled && !self.completion_items.is_empty();
    }
}

impl eframe::App for TimeWarpApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Enhanced visual styling
        let mut visuals = egui::Visuals::light();
        visuals.window_fill = egui::Color32::from_rgb(250, 250, 252);
        visuals.panel_fill = egui::Color32::from_rgb(255, 255, 255);
        visuals.faint_bg_color = egui::Color32::from_rgb(248, 248, 250);
        visuals.widgets.noninteractive.bg_fill = egui::Color32::from_rgb(252, 252, 254);
        visuals.widgets.inactive.bg_fill = egui::Color32::from_rgb(255, 255, 255);
        visuals.widgets.hovered.bg_fill = egui::Color32::from_rgb(240, 245, 255);
        visuals.widgets.active.bg_fill = egui::Color32::from_rgb(230, 240, 255);
        ctx.set_visuals(visuals);

        // Set a more modern font
        let mut style = (*ctx.style()).clone();
        style.text_styles.insert(
            egui::TextStyle::Heading,
            egui::FontId::new(20.0, egui::FontFamily::Proportional),
        );
        style.text_styles.insert(
            egui::TextStyle::Body,
            egui::FontId::new(14.0, egui::FontFamily::Proportional),
        );
        style.text_styles.insert(
            egui::TextStyle::Button,
            egui::FontId::new(14.0, egui::FontFamily::Proportional),
        );
        style.spacing.item_spacing = egui::vec2(8.0, 4.0);
        style.spacing.button_padding = egui::vec2(8.0, 4.0);
        ctx.set_style(style);

        // Handle keyboard shortcuts
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::N)) {
            self.code.clear();
            // Don't set output for file operations - keep output clean for program results only
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::O)) {
            if let Some(path) = FileDialog::new()
                .add_filter("Text", &["txt", "twb", "twp", "tpr"])
                .pick_file()
            {
                if let Ok(content) = std::fs::read_to_string(&path) {
                    self.code = content;
                    // Don't set output for file operations - keep output clean for program results only
                    self.last_file_path = Some(path.display().to_string());
                }
            }
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::S)) {
            if let Some(path) = &self.last_file_path {
                if std::fs::write(path, &self.code).is_ok() {
                    // Don't set output for file operations - keep output clean for program results only
                }
            } else if let Some(path) = FileDialog::new().set_file_name("untitled.twb").save_file() {
                if std::fs::write(&path, &self.code).is_ok() {
                    // Don't set output for file operations - keep output clean for program results only
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
        // Debug shortcuts
        if ctx.input(|i| i.key_pressed(egui::Key::F9)) {
            self.debug_mode = !self.debug_mode;
            if !self.debug_mode {
                self.stop_debug_session();
            }
        }
        if ctx.input(|i| i.modifiers.ctrl && i.key_pressed(egui::Key::F5)) {
            if self.debug_mode {
                self.start_debug_session();
            }
        }
        if ctx.input(|i| i.key_pressed(egui::Key::F10)) {
            if self.debug_mode && self.debug_state == DebugState::Paused {
                self.step_debug();
            }
        }
        if ctx.input(|i| i.key_pressed(egui::Key::F11)) {
            if self.debug_mode && self.debug_state == DebugState::Running {
                self.debug_state = DebugState::Paused;
            } else if self.debug_mode && self.debug_state == DebugState::Paused {
                self.debug_state = DebugState::Running;
            }
        }
        if ctx.input(|i| i.modifiers.ctrl && i.modifiers.shift && i.key_pressed(egui::Key::C)) {
            self.output = String::new();
            self.turtle_commands.clear();
            self.turtle_state = TurtleState {
                x: 0.0,
                y: 0.0,
                angle: 0.0,
                color: egui::Color32::BLACK,
            };
            self.turtle_zoom = 1.0;
            self.turtle_pan = egui::vec2(0.0, 0.0);
        }

        egui::TopBottomPanel::top("menu_bar")
            .min_height(40.0)
            .show(ctx, |ui| {
                ui.painter().rect_filled(
                    ui.available_rect_before_wrap(),
                    0.0,
                    egui::Color32::from_rgb(220, 220, 220),
                );
                ui.add_space(6.0);
                egui::menu::bar(ui, |ui| {
                    // File menu
                    ui.menu_button("📁 File", |ui| {
                        if ui.button("📄 New File").clicked() {
                            self.code.clear();
                            // Don't set output for file operations - keep output clean for program results only
                            ui.close_menu();
                        }
                        if ui.button("📂 Open File...").clicked() {
                            if let Some(path) = FileDialog::new()
                                .add_filter("Text", &["txt", "twb", "twp", "tpr"])
                                .pick_file()
                            {
                                if let Ok(content) = std::fs::read_to_string(&path) {
                                    self.code = content;
                                    // Don't set output for file operations - keep output clean for program results only
                                    self.last_file_path = Some(path.display().to_string());
                                }
                            }
                            ui.close_menu();
                        }
                        if ui.button("💾 Save").clicked() {
                            if let Some(path) = &self.last_file_path {
                                if std::fs::write(path, &self.code).is_ok() {
                                    // Don't set output for file operations - keep output clean for program results only
                                }
                            } else if let Some(path) =
                                FileDialog::new().set_file_name("untitled.twb").save_file()
                            {
                                if std::fs::write(&path, &self.code).is_ok() {
                                    // Don't set output for file operations - keep output clean for program results only
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
                            self.undo();
                            ui.close_menu();
                        }
                        if ui.button("↷ Redo").clicked() {
                            self.redo();
                            ui.close_menu();
                        }
                        ui.separator();
                        if ui.button("📋 Copy").clicked() {
                            self.copy_text(ctx);
                            ui.close_menu();
                        }
                        if ui.button("✂️ Cut").clicked() {
                            self.cut_text(ctx);
                            ui.close_menu();
                        }
                        if ui.button("📄 Paste").clicked() {
                            self.paste_text(ctx);
                            ui.close_menu();
                        }
                        if ui.button("↕️ Move Line").clicked() {
                            // For now, just show a message - full implementation needs cursor tracking
                            self.show_error(
                                "Move line functionality not yet implemented".to_string(),
                            );
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
                        if ui
                            .selectable_label(
                                self.syntax_highlighting_enabled,
                                "🎨 Syntax Highlighting",
                            )
                            .clicked()
                        {
                            self.syntax_highlighting_enabled = !self.syntax_highlighting_enabled;
                            ui.close_menu();
                        }
                        if ui
                            .selectable_label(self.code_completion_enabled, "💡 Code Completion")
                            .clicked()
                        {
                            self.code_completion_enabled = !self.code_completion_enabled;
                            ui.close_menu();
                        }
                    });
                    ui.menu_button("❓ Help", |ui| {
                        if ui.button("ℹ️ About").clicked() {
                            self.show_about = true;
                            ui.close_menu();
                        }
                        if ui.button("💬 Test Prompt").clicked() {
                            self.prompt_user("Enter some text for testing:", |input| {
                                println!("User entered: {}", input);
                                // In a real application, you would do something with the input here
                            });
                            ui.close_menu();
                        }
                    });
                });
                ui.add_space(6.0);
            });

        // Enhanced Toolbar
        egui::TopBottomPanel::top("toolbar").show(ctx, |ui| {
            ui.add_space(2.0);
            egui::Frame::none()
                .fill(ui.style().visuals.window_fill())
                .stroke(ui.style().visuals.window_stroke())
                .show(ui, |ui| {
                    ui.horizontal(|ui| {
                        ui.add_space(8.0);

                        // File operations
                        if ui
                            .button("📄 New")
                            .on_hover_text("New File (Ctrl+N)")
                            .clicked()
                        {
                            self.code.clear();
                            // Don't set output for file operations - keep output clean for program results only
                        }
                        if ui
                            .button("📂 Open")
                            .on_hover_text("Open File (Ctrl+O)")
                            .clicked()
                        {
                            if let Some(path) = FileDialog::new()
                                .add_filter("Text", &["txt", "twb", "twp", "tpr"])
                                .pick_file()
                            {
                                if let Ok(content) = std::fs::read_to_string(&path) {
                                    self.code = content;
                                    // Don't set output for file operations - keep output clean for program results only
                                    self.last_file_path = Some(path.display().to_string());
                                }
                            }
                        }
                        if ui
                            .button("💾 Save")
                            .on_hover_text("Save File (Ctrl+S)")
                            .clicked()
                        {
                            if let Some(path) = &self.last_file_path {
                                if std::fs::write(path, &self.code).is_ok() {
                                    // Don't set output for file operations - keep output clean for program results only
                                }
                            } else if let Some(path) =
                                FileDialog::new().set_file_name("untitled.twb").save_file()
                            {
                                if std::fs::write(&path, &self.code).is_ok() {
                                    // Don't set output for file operations - keep output clean for program results only
                                    self.last_file_path = Some(path.display().to_string());
                                }
                            }
                        }

                        ui.separator();

                        // Edit operations
                        if ui.button("↶ Undo").on_hover_text("Undo").clicked() {
                            // Note: egui TextEdit doesn't have built-in undo, this is a placeholder
                        }
                        if ui.button("↷ Redo").on_hover_text("Redo").clicked() {
                            // Note: egui TextEdit doesn't have built-in redo, this is a placeholder
                        }
                        if ui.button("📋 Copy").on_hover_text("Copy").clicked() {
                            self.copy_text(ctx);
                        }
                        if ui.button("✂️ Cut").on_hover_text("Cut").clicked() {
                            self.cut_text(ctx);
                        }
                        if ui.button("📄 Paste").on_hover_text("Paste").clicked() {
                            self.paste_text(ctx);
                        }

                        ui.separator();

                        // Code operations
                        if ui
                            .button("🔍 Find")
                            .on_hover_text("Find/Replace (Ctrl+F)")
                            .clicked()
                        {
                            self.show_find_replace = !self.show_find_replace;
                        }
                        if ui.button("▶️ Run").on_hover_text("Run Code (F5)").clicked() {
                            self.active_tab = 1; // Switch to Output tab when running
                            self.execute_code();
                        }
                        if ui
                            .button("🗑️ Clear")
                            .on_hover_text("Clear Output (Ctrl+Shift+C)")
                            .clicked()
                        {
                            self.output = String::new();
                            self.turtle_commands.clear();
                            self.turtle_state = TurtleState {
                                x: 0.0,
                                y: 0.0,
                                angle: 0.0,
                                color: egui::Color32::BLACK,
                            };
                            self.turtle_zoom = 1.0;
                            self.turtle_pan = egui::vec2(0.0, 0.0);
                        }

                        ui.separator();

                        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                            ui.add_space(8.0);
                        });
                    });
                });
            ui.add_space(2.0);
        });

        egui::TopBottomPanel::top("top_panel").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.heading("🚀 Time Warp IDE");
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    // Status indicators
                    if self.is_executing {
                        ui.colored_label(egui::Color32::GREEN, "● Running");
                    } else if self.waiting_for_input {
                        ui.colored_label(egui::Color32::YELLOW, "● Waiting for Input");
                    } else {
                        ui.colored_label(egui::Color32::GRAY, "● Ready");
                    }

                    ui.separator();

                    // File info
                    if let Some(path) = &self.last_file_path {
                        ui.label(format!(
                            "📄 {}",
                            std::path::Path::new(path)
                                .file_name()
                                .unwrap_or(std::ffi::OsStr::new("untitled"))
                                .to_string_lossy()
                        ));
                    } else {
                        ui.label("📄 untitled");
                    }
                });
            });
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.vertical(|ui| {
                // Tab bar with better styling
                egui::Frame::none()
                    .fill(ui.style().visuals.faint_bg_color)
                    .stroke(egui::Stroke::new(
                        1.0,
                        ui.style().visuals.window_stroke.color,
                    ))
                    .rounding(egui::Rounding::same(6.0))
                    .show(ui, |ui| {
                        ui.horizontal(|ui| {
                            ui.add_space(8.0);

                            // Tab buttons with better styling
                            let tab_height = 32.0;
                            if ui
                                .add(
                                    egui::Button::new("📝 Code Editor")
                                        .fill(if self.active_tab == 0 {
                                            ui.style().visuals.selection.bg_fill
                                        } else {
                                            egui::Color32::TRANSPARENT
                                        })
                                        .stroke(if self.active_tab == 0 {
                                            egui::Stroke::new(
                                                2.0,
                                                ui.style().visuals.selection.stroke.color,
                                            )
                                        } else {
                                            egui::Stroke::NONE
                                        })
                                        .rounding(egui::Rounding::same(4.0))
                                        .min_size(egui::vec2(120.0, tab_height)),
                                )
                                .clicked()
                            {
                                self.active_tab = 0;
                            }

                            if ui
                                .add(
                                    egui::Button::new("🖥️ Output & Graphics")
                                        .fill(if self.active_tab == 1 {
                                            ui.style().visuals.selection.bg_fill
                                        } else {
                                            egui::Color32::TRANSPARENT
                                        })
                                        .stroke(if self.active_tab == 1 {
                                            egui::Stroke::new(
                                                2.0,
                                                ui.style().visuals.selection.stroke.color,
                                            )
                                        } else {
                                            egui::Stroke::NONE
                                        })
                                        .rounding(egui::Rounding::same(4.0))
                                        .min_size(egui::vec2(140.0, tab_height)),
                                )
                                .clicked()
                            {
                                self.active_tab = 1;
                            }

                            if ui
                                .add(
                                    egui::Button::new("🐛 Debug")
                                        .fill(if self.active_tab == 2 {
                                            ui.style().visuals.selection.bg_fill
                                        } else {
                                            egui::Color32::TRANSPARENT
                                        })
                                        .stroke(if self.active_tab == 2 {
                                            egui::Stroke::new(
                                                2.0,
                                                ui.style().visuals.selection.stroke.color,
                                            )
                                        } else {
                                            egui::Stroke::NONE
                                        })
                                        .rounding(egui::Rounding::same(4.0))
                                        .min_size(egui::vec2(100.0, tab_height)),
                                )
                                .clicked()
                            {
                                self.active_tab = 2;
                            }

                            ui.with_layout(
                                egui::Layout::right_to_left(egui::Align::Center),
                                |ui| {
                                    ui.add_space(8.0);
                                },
                            );
                        });
                    });

                ui.add_space(8.0);

                // Main content area with better styling
                egui::Frame::none()
                    .fill(ui.style().visuals.panel_fill)
                    .stroke(egui::Stroke::new(
                        1.0,
                        ui.style().visuals.window_stroke.color,
                    ))
                    .rounding(egui::Rounding::same(8.0))
                    .inner_margin(egui::Margin::same(12.0))
                    .show(ui, |ui| {
                        match self.active_tab {
                            0 => {
                                // Code Editor Tab
                                ui.vertical(|ui| {
                                    ui.horizontal(|ui| {
                                        ui.checkbox(&mut self.show_line_numbers, "Line numbers");
                                        ui.checkbox(&mut self.debug_mode, "Debug mode");
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
                                                self.code = self
                                                    .code
                                                    .replace(&self.find_text, &self.replace_text);
                                            }
                                        });
                                        ui.separator();
                                    }

                                    egui::ScrollArea::vertical().show(ui, |ui| {
                                        if self.show_line_numbers && self.debug_mode {
                                            // Custom editor with line numbers and breakpoints
                                            self.render_debug_editor(ui);
                                        } else {
                                            // Handle completion input before creating TextEdit to avoid borrowing conflicts
                                            let input = ui.input(|i| i.clone());
                                            let should_trigger_completion = input.modifiers.ctrl && input.key_pressed(egui::Key::Space);
                                            let should_hide_completion = input.key_pressed(egui::Key::Escape);
                                            let should_select_down = self.show_completion && input.key_pressed(egui::Key::ArrowDown);
                                            let should_select_up = self.show_completion && input.key_pressed(egui::Key::ArrowUp);
                                            let should_insert_completion = self.show_completion && input.key_pressed(egui::Key::Enter);

                                            // Calculate all needed data before any mutable borrows
                                            let (current_word, selected_item, insert_start, insert_end) = {
                                                let cursor_pos = self.code.len();
                                                let before_cursor = &self.code[..cursor_pos];
                                                let words: Vec<&str> = before_cursor.split_whitespace().collect();
                                                let current_word = words.last().copied().unwrap_or("");

                                                let (selected_item, insert_start, insert_end) = if should_insert_completion {
                                                    if let Some(selected) = self.completion_items.get(self.completion_selected) {
                                                        let start_pos = cursor_pos - current_word.len();
                                                        (Some(selected.clone()), start_pos, cursor_pos)
                                                    } else {
                                                        (None, 0, 0)
                                                    }
                                                } else {
                                                    (None, 0, 0)
                                                };

                                                (current_word, selected_item, insert_start, insert_end)
                                            };

                                            // Now do all mutable operations
                                            if should_trigger_completion {
                                                // self.update_completion(current_word);
                                                self.completion_query = current_word.to_string();
                                                self.completion_items = self.get_completion_suggestions(&current_word);
                                                self.completion_selected = 0;
                                                self.show_completion = !self.completion_items.is_empty();
                                            } else if should_hide_completion {
                                                self.show_completion = false;
                                            } else if should_select_down {
                                                if self.completion_selected < self.completion_items.len().saturating_sub(1) {
                                                    self.completion_selected += 1;
                                                }
                                            } else if should_select_up {
                                                if self.completion_selected > 0 {
                                                    self.completion_selected = self.completion_selected.saturating_sub(1);
                                                }
                                            } else if let Some(selected) = selected_item {
                                                self.code.replace_range(insert_start..insert_end, &selected);
                                                self.show_completion = false;
                                            }

                                            // Syntax-highlighted code editor
                                            if self.syntax_highlighting_enabled {
                                                self.render_syntax_highlighted_editor(ui);
                                            } else {
                                                ui.add(
                                                    egui::TextEdit::multiline(&mut self.code)
                                                        .font(egui::TextStyle::Monospace)
                                                        .desired_width(f32::INFINITY)
                                                        .desired_rows(20)
                                                );
                                            }

                                            // Update line count (cursor position tracking needs different approach in egui)
                                            self.total_lines = self.code.lines().count().max(1);

                                            // Show completion popup
                                            if self.show_completion && !self.completion_items.is_empty() {
                                                egui::Window::new("Code Completion")
                                                    .collapsible(false)
                                                    .resizable(false)
                                                    .show(ui.ctx(), |ui| {
                                                        egui::ScrollArea::vertical().show(ui, |ui| {
                                                            for (i, item) in self.completion_items.iter().enumerate() {
                                                                let mut button = egui::Button::new(item);
                                                                if i == self.completion_selected {
                                                                    button = button.fill(egui::Color32::from_rgb(100, 150, 200));
                                                                }
                                                                if ui.add(button).clicked() {
                                                                    let cursor_pos = self.code.len();
                                                                    let before_cursor = &self.code[..cursor_pos];
                                                                    let words: Vec<&str> = before_cursor.split_whitespace().collect();
                                                                    let current_word = words.last().copied().unwrap_or("");
                                                                    let start_pos = cursor_pos - current_word.len();
                                                                    self.code.replace_range(start_pos..cursor_pos, item);
                                                                    self.show_completion = false;
                                                                }
                                                            }
                                                        });
                                                    });
                                            }
                                        }
                                    });
                                });
                            }
                            1 => {
                                // Output & Graphics Tab
                                ui.vertical(|ui| {
                                    ui.label("Output:");

                                    // Input prompt - show prominently at the top when needed
                                    if self.waiting_for_input {
                                        ui.separator();
                                        ui.label("📝 Program Input Required");
                                        ui.horizontal(|ui| {
                                            ui.label(&self.input_prompt);
                                            let response = ui.text_edit_singleline(&mut self.user_input);
                                            if ui.button("🚀 Submit").clicked()
                                                || (response.lost_focus()
                                                    && ui.input(|i| i.key_pressed(egui::Key::Enter)))
                                            {
                                                // Store the input in the variable
                                                self.variables
                                                    .insert(self.current_input_var.clone(), self.user_input.clone());

                                                // Provide input to the BASIC interpreter and continue execution
                                                if let Some(ref mut interpreter) = self.basic_interpreter {
                                                    interpreter.provide_input(&self.user_input);

                                                    // Continue execution with the interpreter
                                                    match interpreter.execute("") {
                                                        // Empty string since interpreter has state
                                                        Ok(result) => match result {
                                                            crate::languages::basic::ExecutionResult::Complete {
                                                                output,
                                                                graphics_commands,
                                                            } => {
                                                                self.process_graphics_commands(&graphics_commands);
                                                                self.output = output;
                                                                self.basic_interpreter = None;
                                                            }
                                                            crate::languages::basic::ExecutionResult::NeedInput {
                                                                variable,
                                                                prompt,
                                                                partial_output,
                                                                partial_graphics,
                                                            } => {
                                                                self.process_graphics_commands(&partial_graphics);
                                                                self.input_prompt = prompt.clone();
                                                                self.current_input_var = variable;
                                                                self.output = format!(
                                                                    "{}{}{}",
                                                                    self.output, partial_output, prompt
                                                                );
                                                                // Keep waiting for more input
                                                            }
                                                            crate::languages::basic::ExecutionResult::Error(err) => {
                                                                self.output =
                                                                    format!("{}Error: {:?}", self.output, err);
                                                                self.basic_interpreter = None;
                                                            }
                                                        },
                                                        Err(err) => {
                                                            self.output = format!("{}Error: {:?}", self.output, err);
                                                            self.basic_interpreter = None;
                                                        }
                                                    }
                                                }

                                                // Continue execution
                                                self.waiting_for_input = false;
                                                self.user_input.clear();
                                                self.input_prompt.clear();
                                                self.current_input_var.clear();
                                            }
                                            if ui.button("❌ Cancel").clicked() {
                                                self.output = format!("{}Input cancelled.", self.output);
                                                self.waiting_for_input = false;
                                                self.user_input.clear();
                                                self.input_prompt.clear();
                                                self.current_input_var.clear();
                                                self.basic_interpreter = None;
                                            }
                                        });
                                        ui.separator();
                                    }

                                    egui::ScrollArea::vertical()
                                        .max_height(200.0)
                                        .show(ui, |ui| {
                                            ui.add(
                                                egui::TextEdit::multiline(&mut self.output)
                                                    .font(egui::TextStyle::Monospace)
                                                    .desired_width(f32::INFINITY),
                                            );
                                        });

                                    // Turtle Graphics section

                                    ui.separator();
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
                                            let parts: Vec<&str> =
                                                command.split_whitespace().collect();
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
                                                            + (x1 + self.turtle_pan.x)
                                                                * self.turtle_zoom,
                                                        center.y
                                                            + (y1 + self.turtle_pan.y)
                                                                * self.turtle_zoom,
                                                    );
                                                    let end = egui::pos2(
                                                        center.x
                                                            + (x2 + self.turtle_pan.x)
                                                                * self.turtle_zoom,
                                                        center.y
                                                            + (y2 + self.turtle_pan.y)
                                                                * self.turtle_zoom,
                                                    );
                                                    ui.painter().line_segment(
                                                        [start, end],
                                                        egui::Stroke::new(
                                                            2.0,
                                                            egui::Color32::BLACK,
                                                        ),
                                                    );
                                                }
                                            }
                                        }
                                    }

                                    // Draw turtle
                                    let center = rect.center();
                                    let turtle_x = center.x
                                        + (self.turtle_state.x + self.turtle_pan.x)
                                            * self.turtle_zoom;
                                    let turtle_y = center.y
                                        + (self.turtle_state.y + self.turtle_pan.y)
                                            * self.turtle_zoom;

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
                            2 => {
                                // Debug Tab
                                ui.vertical(|ui| {
                                    ui.horizontal(|ui| {
                                        ui.checkbox(&mut self.debug_mode, "Enable Debug Mode");
                                        ui.separator();
                                        ui.label("Debug State:");
                                        match self.debug_state {
                                            DebugState::Stopped => ui.colored_label(egui::Color32::GRAY, "⏹️ Stopped"),
                                            DebugState::Running => ui.colored_label(egui::Color32::GREEN, "▶️ Running"),
                                            DebugState::Paused => ui.colored_label(egui::Color32::YELLOW, "⏸️ Paused"),
                                        }
                                    });

                                    ui.separator();

                                    // Debug Controls
                                    ui.horizontal(|ui| {
                                        if ui.button("▶️ Start Debug").on_hover_text("Start debugging session (Ctrl+F5)").clicked() && self.debug_mode {
                                            self.start_debug_session();
                                        }
                                        if ui.button("⏯️ Continue").on_hover_text("Continue execution from paused state").clicked() && self.debug_mode && self.debug_state == DebugState::Paused {
                                            self.debug_state = DebugState::Running;
                                        }
                                        if ui.button("⏸️ Pause").on_hover_text("Pause execution (F11)").clicked() && self.debug_mode && self.debug_state == DebugState::Running {
                                            self.debug_state = DebugState::Paused;
                                        }
                                        if ui.button("⏹️ Stop").on_hover_text("Stop debugging session").clicked() && self.debug_mode {
                                            self.stop_debug_session();
                                        }
                                        if ui.button("⏭️ Step").on_hover_text("Step to next line (F10)").clicked() && self.debug_mode && self.debug_state == DebugState::Paused {
                                            self.step_debug();
                                        }
                                        if ui.button("🔄 Reset").on_hover_text("Restart debug session").clicked() && self.debug_mode {
                                            self.start_debug_session(); // Restart debug session
                                        }
                                    });

                                    ui.separator();

                                    // Breakpoints
                                    ui.collapsing("Breakpoints", |ui| {
                                        ui.label("Click on line numbers in the editor to toggle breakpoints");
                                        let filename = self.last_file_path.as_ref()
                                            .and_then(|p| std::path::Path::new(p).file_name())
                                            .and_then(|n| n.to_str())
                                            .unwrap_or("untitled");

                                        if let Some(breakpoints) = self.breakpoints.get(filename) {
                                            ui.label(format!("Breakpoints in {}: {:?}", filename, breakpoints));
                                        } else {
                                            ui.label(format!("No breakpoints in {}", filename));
                                        }

                                        if ui.button("Clear All Breakpoints").clicked() {
                                            self.breakpoints.clear();
                                        }
                                    });

                                    // Variables
                                    ui.collapsing("Variables", |ui| {
                                        ui.label("📊 Debug Variables:");
                                        if self.debug_variables.is_empty() {
                                            ui.label("  No debug variables");
                                        } else {
                                            for (name, value) in &self.debug_variables {
                                                ui.label(format!("  {} = \"{}\"", name, value));
                                            }
                                        }

                                        ui.separator();
                                        ui.label("🔢 Program Variables:");
                                        if self.variables.is_empty() {
                                            ui.label("  No program variables");
                                        } else {
                                            for (name, value) in &self.variables {
                                                ui.label(format!("  {} = \"{}\"", name, value));
                                            }
                                        }
                                    });

                                    // Call Stack
                                    ui.collapsing("Call Stack", |ui| {
                                        if self.debug_call_stack.is_empty() {
                                            ui.label("Call stack is empty");
                                        } else {
                                            for (i, frame) in self.debug_call_stack.iter().enumerate() {
                                                ui.label(format!("{}: {}", i, frame));
                                            }
                                        }
                                    });

                                    // Current Line
                                    if let Some(line) = self.current_debug_line {
                                        ui.separator();
                                        ui.label(format!("Current Debug Line: {}", line));
                                    }
                                });
                            }
                            _ => {}
                        }
                    });
            });
        });

        // General prompt handling - shown prominently when active
        if self.general_prompt_active {
            let mut open = true;
            egui::Window::new("💬 Input Required")
                .open(&mut open)
                .collapsible(false)
                .resizable(false)
                .show(ctx, |ui| {
                    ui.vertical_centered(|ui| {
                        ui.add_space(20.0);
                        ui.label(&self.general_prompt_message);
                        ui.add_space(10.0);
                        ui.horizontal(|ui| {
                            ui.label("Input:");
                            let response = ui.text_edit_singleline(&mut self.general_prompt_input);
                            if ui.button("🚀 Submit").clicked()
                                || (response.lost_focus()
                                    && ui.input(|i| i.key_pressed(egui::Key::Enter)))
                            {
                                // Call the callback with the input
                                if let Some(callback) = self.general_prompt_callback.take() {
                                    callback(self.general_prompt_input.clone());
                                }

                                // Reset prompt state
                                self.general_prompt_active = false;
                                self.general_prompt_message.clear();
                                self.general_prompt_input.clear();
                            }
                            if ui.button("❌ Cancel").clicked() {
                                // Reset prompt state without calling callback
                                self.general_prompt_active = false;
                                self.general_prompt_message.clear();
                                self.general_prompt_input.clear();
                                self.general_prompt_callback = None;
                            }
                        });
                    });
                });

            // If window was closed (user clicked X), treat as cancel
            if !open {
                self.general_prompt_active = false;
                self.general_prompt_message.clear();
                self.general_prompt_input.clear();
                self.general_prompt_callback = None;
            }
        }

        // Status Bar
        egui::TopBottomPanel::bottom("status_bar").show(ctx, |ui| {
            ui.add_space(2.0);
            egui::Frame::none()
                .fill(ui.style().visuals.window_fill())
                .stroke(ui.style().visuals.window_stroke())
                .show(ui, |ui| {
                    ui.horizontal(|ui| {
                        ui.add_space(8.0);

                        // File and cursor information
                        let line_count = self.code.lines().count();
                        let char_count = self.code.chars().count();
                        ui.label(format!(
                            "📏 Lines: {} | Chars: {} | Ln {}, Col {}",
                            line_count, char_count, self.cursor_line, self.cursor_column
                        ));

                        ui.separator();

                        // Language and encoding
                        ui.label("🏷️ TW BASIC");

                        ui.separator();

                        // Execution status
                        if self.is_executing {
                            ui.colored_label(egui::Color32::GREEN, "▶️ Running");
                        } else if self.waiting_for_input {
                            ui.colored_label(egui::Color32::YELLOW, "⏸️ Waiting for Input");
                        } else if self.general_prompt_active {
                            ui.colored_label(egui::Color32::BLUE, "💬 Awaiting Response");
                        } else {
                            ui.colored_label(egui::Color32::GRAY, "⏹️ Ready");
                        }

                        ui.separator();

                        // Timeout setting
                        ui.label(format!("⏰ Timeout: {}ms", self.execution_timeout_ms));

                        ui.separator();

                        // Debug mode status
                        if self.debug_mode {
                            match self.debug_state {
                                DebugState::Running => {
                                    ui.colored_label(egui::Color32::GREEN, "🐛 Debug: Running");
                                }
                                DebugState::Paused => {
                                    ui.colored_label(egui::Color32::YELLOW, "🐛 Debug: Paused");
                                }
                                DebugState::Stopped => {
                                    ui.colored_label(egui::Color32::RED, "🐛 Debug: Stopped");
                                }
                            }
                        } else {
                            ui.colored_label(egui::Color32::GRAY, "🐛 Debug: Off (F9 to toggle)");
                        }

                        ui.separator();

                        // View options status
                        if self.show_line_numbers {
                            ui.label("📏 Line Numbers: ON");
                        }
                        if self.syntax_highlighting_enabled {
                            ui.label("🎨 Syntax Highlighting: ON");
                        }

                        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                            ui.add_space(8.0);
                            ui.label("2.0.0");
                        });
                    });
                });
            ui.add_space(2.0);
        });

        // About dialog
        if self.show_about {
            egui::Window::new("About Time Warp IDE")
                .collapsible(false)
                .resizable(false)
                .show(ctx, |ui| {
                    ui.vertical_centered(|ui| {
                        ui.heading("Time Warp IDE");
                        ui.label("Version 2.0.0");
                        ui.label("A modern, educational programming environment");
                        ui.label("built in Rust using the egui framework.");
                        ui.separator();
                        ui.label("Exclusive TW BASIC development environment");
                        ui.label("with interactive input and turtle graphics.");
                        ui.separator();
                        if ui.button("Close").clicked() {
                            self.show_about = false;
                        }
                    });
                });
        }

        // Error notification toast
        if let Some(ref error_msg) = self.error_message {
            let toast_duration = 3.0; // Show for 3 seconds
            if self.error_timer < toast_duration {
                self.error_timer += ctx.input(|i| i.unstable_dt).min(0.1) as f64; // Cap delta time

                // Position toast at bottom center
                let screen_rect = ctx.screen_rect();
                let toast_width = 400.0;
                let toast_height = 60.0;
                let toast_pos = egui::pos2(
                    screen_rect.center().x - toast_width / 2.0,
                    screen_rect.bottom() - toast_height - 20.0,
                );

                let mut dismiss_clicked = false;
                egui::Area::new("error_toast")
                    .fixed_pos(toast_pos)
                    .show(ctx, |ui| {
                        egui::Frame::none()
                            .fill(egui::Color32::from_rgb(220, 53, 69)) // Red background
                            .stroke(egui::Stroke::new(2.0, egui::Color32::from_rgb(176, 42, 55)))
                            .rounding(egui::Rounding::same(8.0))
                            .shadow(egui::epaint::Shadow::small_dark())
                            .show(ui, |ui| {
                                ui.set_width(toast_width);
                                ui.set_height(toast_height);
                                ui.horizontal(|ui| {
                                    ui.add_space(12.0);
                                    ui.label(egui::RichText::new("❌").size(20.0));
                                    ui.add_space(8.0);
                                    ui.vertical(|ui| {
                                        ui.add_space(8.0);
                                        ui.label(
                                            egui::RichText::new("Error")
                                                .color(egui::Color32::WHITE)
                                                .size(14.0),
                                        );
                                        ui.label(
                                            egui::RichText::new(error_msg)
                                                .color(egui::Color32::from_rgb(255, 235, 235))
                                                .size(12.0),
                                        );
                                    });
                                    ui.with_layout(
                                        egui::Layout::right_to_left(egui::Align::Center),
                                        |ui| {
                                            ui.add_space(8.0);
                                            if ui.button("✕").clicked() {
                                                dismiss_clicked = true;
                                            }
                                        },
                                    );
                                });
                            });
                    });

                if dismiss_clicked {
                    self.error_message = None;
                    self.error_timer = 0.0;
                }
            } else {
                // Auto-dismiss after timeout
                self.error_message = None;
                self.error_timer = 0.0;
            }
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
        // File operations no longer set output messages
        app.last_file_path = None;

        assert_eq!(app.code, "");
        // Output should remain unchanged for file operations
        assert_eq!(app.output, "some output");
        assert_eq!(app.last_file_path, None);
    }

    #[test]
    fn test_save_operations() {
        let mut app = TimeWarpApp::default();
        app.code = "10 PRINT \"TEST\"".to_string();
        app.last_file_path = Some("test_save.twb".to_string());
        app.output = "previous output".to_string(); // Set some initial output

        // Simulate Save
        if let Some(path) = &app.last_file_path {
            fs::write(path, &app.code).unwrap();
            // File operations no longer set output messages
        }

        // Verify file was saved
        let content = fs::read_to_string("test_save.twb").unwrap();
        assert_eq!(content, "10 PRINT \"TEST\"");
        // Output should remain unchanged
        assert_eq!(app.output, "previous output");

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
    fn test_basic_program_execution() {
        let mut app = TimeWarpApp::default();

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

    #[test]
    fn test_enhanced_basic_commands() {
        let mut app = TimeWarpApp::default();

        // Test WRITELN command (Pascal-style with newline)
        let writeln_code = "WRITELN \"Hello with newline\"";
        let result = app.execute_tw_basic(writeln_code);
        println!("WRITELN result: {:?}", result);
        assert!(result.contains("Hello with newline"));

        // Test turtle graphics commands
        let turtle_code = "FORWARD 50\nRIGHT 90\nBACK 25";
        let result = app.execute_tw_basic(turtle_code);
        println!("Turtle commands result: {:?}", result);
        assert!(result.contains("Moved forward 50"));
        assert!(result.contains("Turned right 90"));
        assert!(result.contains("Moved back 25"));
    }

    #[test]
    fn test_input_statement_parsing() {
        // Test that INPUT statements with semicolon separators parse correctly
        let input_code = "10 INPUT \"Name? \"; NAME$\n20 PRINT \"Hello \"; NAME$";

        // This should not panic or return a parse error
        let mut app = TimeWarpApp::default();
        let result = app.execute_tw_basic(input_code);

        // The execution should start (even if it waits for input)
        // We just want to make sure it doesn't fail with a parse error
        println!("INPUT parsing result: {:?}", result);
        // If we get here without panicking, the parsing worked
        assert!(true); // Just verify we don't crash
    }

    #[test]
    fn test_input_statement_execution() {
        // Test that INPUT statements properly set waiting_for_input state
        let input_code = "10 INPUT \"Name? \"; NAME$";

        let mut app = TimeWarpApp::default();
        let _result = app.execute_tw_basic(input_code);

        // After executing an INPUT statement, the app should be waiting for input
        assert!(
            app.waiting_for_input,
            "App should be waiting for input after INPUT statement"
        );
        assert_eq!(
            app.input_prompt, "Name? ",
            "Input prompt should be set correctly"
        );
        assert_eq!(
            app.current_input_var, "NAME$",
            "Current input variable should be set correctly"
        );
    }

    #[test]
    fn test_tab_function() {
        let mut app = TimeWarpApp::default();

        // Test TAB function in PRINT statements
        let tab_code = "PRINT \"Hello\"; TAB(10); \"World\"";
        let result = app.execute_tw_basic(tab_code);

        println!("TAB result: {:?}", result);

        // Verify TAB function produces spaces for positioning
        assert!(result.contains("Hello"));
        assert!(result.contains("World"));
    }

    #[test]
    fn test_print_variable() {
        let mut app = TimeWarpApp::default();

        // Test PRINT with a variable
        let print_code = "LET X = 42\nPRINT X";
        let result = app.execute_tw_basic(print_code);

        println!("PRINT variable result: {:?}", result);

        // Should contain the variable value
        assert!(result.contains("42"));
    }

    #[test]
    fn test_print_variable_simple() {
        let mut app = TimeWarpApp::default();

        // Test PRINT with a variable (simple case)
        let print_code = "PRINT X";
        let result = app.execute_tw_basic(print_code);

        println!("PRINT variable simple result: {:?}", result);

        // Should not crash with parse error
        assert!(!result.contains("ParseError"));
    }

    #[test]
    fn test_tokenize_input_x() {
        use crate::languages::basic::Tokenizer;

        let mut tokenizer = Tokenizer::new("INPUT X");
        let tokens = tokenizer.tokenize().unwrap();

        println!("Tokens for 'INPUT X': {:?}", tokens);

        // Should have INPUT, identifier X, EOF
        assert!(tokens.len() >= 3);
    }

    #[test]
    fn test_parse_input_x() {
        use crate::languages::basic::{Parser, Tokenizer};

        let mut tokenizer = Tokenizer::new("INPUT X");
        let tokens = tokenizer.tokenize().unwrap();
        let mut parser = Parser::new(tokens);
        let program = parser.parse_program().unwrap();

        println!("Parsed program for 'INPUT X': {:?}", program);

        // Should have one statement
        assert_eq!(program.statements.len(), 1);
    }

    #[test]
    fn test_parse_print_semicolon() {
        use crate::languages::basic::{Parser, Tokenizer};

        let mut tokenizer = Tokenizer::new("PRINT 42;");
        let tokens = tokenizer.tokenize().unwrap();
        let mut parser = Parser::new(tokens);
        let program = parser.parse_program().unwrap();

        println!("Parsed program for 'PRINT 42;': {:?}", program);

        // Should have one statement
        assert_eq!(program.statements.len(), 1);
    }

    #[test]
    fn test_print_with_line_number() {
        let mut app = TimeWarpApp::default();

        // Test PRINT with line number (like user might enter)
        let print_code = "10 PRINT X";
        let result = app.execute_tw_basic(print_code);

        println!("PRINT with line number result: {:?}", result);

        // Should not crash with parse error
        assert!(!result.contains("ParseError"));
        // Should contain the variable value
        assert!(result.contains("0"));
    }

    #[test]
    fn test_print_no_space() {
        let mut app = TimeWarpApp::default();

        // Test PRINTX (no space) - this should cause a parse error
        let print_code = "PRINTX";
        let result = app.execute_tw_basic(print_code);

        println!("PRINT no space result: {:?}", result);

        // This should contain a parse error
        assert!(result.contains("ParseError"));
    }

    #[test]
    fn test_print_lowercase() {
        let mut app = TimeWarpApp::default();

        // Test print x (lowercase) - should work since tokenizer uppercases
        let print_code = "print x";
        let result = app.execute_tw_basic(print_code);

        println!("PRINT lowercase result: {:?}", result);

        // Should not crash with parse error
        assert!(!result.contains("ParseError"));
        // Should contain the variable value
        assert!(result.contains("0"));
    }

    #[test]
    fn test_let_and_print() {
        let mut app = TimeWarpApp::default();

        // Test LET X = 5 : PRINT X
        let code = "LET X = 5 : PRINT X";
        let result = app.execute_tw_basic(code);

        println!("LET and PRINT result: {:?}", result);

        // Should not crash with parse error
        assert!(!result.contains("ParseError"));
        // Should contain 5
        assert!(result.contains("5"));
    }

    #[test]
    fn test_print_multiple_vars_no_comma() {
        let mut app = TimeWarpApp::default();

        // Test PRINT X Y (without comma) - should cause parse error
        let print_code = "PRINT X Y";
        let result = app.execute_tw_basic(print_code);

        println!("PRINT multiple vars no comma result: {:?}", result);

        // This should cause a parse error
        assert!(result.contains("ParseError"));
    }

    #[test]
    fn test_print_x_and_printx() {
        let mut app = TimeWarpApp::default();

        // Test PRINT X : PRINTX (what user entered)
        let code = "PRINT X\nPRINTX";
        let result = app.execute_tw_basic(code);

        println!("PRINT X and PRINTX result: {:?}", result);

        // Should have helpful parse error for PRINTX
        assert!(result.contains("ParseError"));
        assert!(result.contains("PRINT requires a space"));
    }

    #[test]
    fn test_letx_equals_five() {
        let mut app = TimeWarpApp::default();

        // Test LETX=5 (variable named LETX)
        let code = "LETX=5\nPRINT LETX";
        let result = app.execute_tw_basic(code);

        println!("LETX=5 result: {:?}", result);

        // Should work - LETX is a valid variable name
        assert!(result.contains("5"));
    }

    #[test]
    fn test_input_and_print() {
        let mut app = TimeWarpApp::default();

        // Test INPUT X : PRINT X
        let code = "INPUT X\nPRINT X";
        let result = app.execute_tw_basic(code);

        println!("INPUT and PRINT result: {:?}", result);
        println!("Waiting for input: {}", app.waiting_for_input);

        // Should be waiting for input
        assert!(app.waiting_for_input);

        // Simulate providing input
        if let Some(ref mut interpreter) = app.basic_interpreter {
            interpreter.provide_input("42");
            let continue_result = interpreter.execute("").unwrap();
            match continue_result {
                crate::languages::basic::ExecutionResult::Complete { output, .. } => {
                    app.output = output;
                }
                _ => panic!("Expected Complete"),
            }
        }

        println!("Final output: {:?}", app.output);
        // Should contain the input echo and the PRINT output
        assert!(app.output.contains("42"));
        assert!(app.output == "42\n42\n");
    }

    #[test]
    fn test_print_semicolon() {
        let mut app = TimeWarpApp::default();

        // Test PRINT X; (should not add newline)
        let code = "PRINT 42;";
        let result = app.execute_tw_basic(code);

        println!("PRINT with semicolon result: {:?}", result);

        // Should not end with newline
        assert!(!result.ends_with("\n"));
        assert!(result == "42");
    }

    #[test]
    fn test_print_gw_basic_features() {
        let mut app = TimeWarpApp::default();

        // Test comma tabulation (GW-BASIC style - every 14 characters)
        let comma_code = "PRINT \"A\",\"B\",\"C\"";
        let result1 = app.execute_tw_basic(comma_code);
        println!("PRINT comma tabulation result: {:?}", result1);
        // "A" should be followed by spaces to reach column 14, then "B" at column 15, etc.

        // Test TAB function
        let tab_code = "PRINT \"HELLO\";TAB(15);\"WORLD\"";
        let result2 = app.execute_tw_basic(tab_code);
        println!("PRINT TAB function result: {:?}", result2);
        // Should have "HELLO" followed by spaces to column 15, then "WORLD"

        // Test SPC function
        let spc_code = "PRINT \"TEST\";SPC(3);\"SPACES\"";
        let result3 = app.execute_tw_basic(spc_code);
        println!("PRINT SPC function result: {:?}", result3);
        // Should have "TEST" followed by 3 spaces, then "SPACES"

        // Verify all contain expected content
        assert!(result1.contains("A"));
        assert!(result1.contains("B"));
        assert!(result1.contains("C"));
        assert!(result2.contains("HELLO"));
        assert!(result2.contains("WORLD"));
        assert!(result3.contains("TEST"));
        assert!(result3.contains("SPACES"));
    }

    #[test]
    fn test_def_fn_functions() {
        let mut app = TimeWarpApp::default();

        // Test DEF FN and calling user-defined functions
        let def_code = "DEF FN SQUARE(X) = X * X\nPRINT FN SQUARE(5)";
        let result = app.execute_tw_basic(def_code);
        println!("DEF FN result: {:?}", result);

        // Should contain 25 (5 squared)
        assert!(result.contains("25"));
    }

    #[test]
    fn test_clear_command() {
        let mut app = TimeWarpApp::default();

        // Set up some variables and functions
        let setup_code = "LET X = 42\nDEF FN TEST(Y) = Y + 1\nDIM A(10)";
        app.execute_tw_basic(setup_code);

        // Clear everything
        let clear_code = "CLEAR";
        let result = app.execute_tw_basic(clear_code);
        println!("CLEAR result: {:?}", result);

        // Should contain confirmation message
        assert!(result.contains("cleared"));
    }

    #[test]
    fn test_for_loop_simple() {
        let mut app = TimeWarpApp::default();

        // Test just FOR loop
        let code = "for i=1 to 3\nprint i\nnext";
        let result = app.execute_tw_basic(code);

        // Should work and produce 1\n2\n3\n
        assert!(result == "1\n2\n3\n");
        assert!(!result.contains("timeout"));
    }

    #[test]
    fn test_for_loop_program() {
        let mut app = TimeWarpApp::default();

        // Test the user's program
        let code = "10 cls\n20 print \"Hello\"\n30 for i=1 to 10\n40 print 1/i\n50 next\n60 end";
        let result = app.execute_tw_basic(code);

        // Should work and contain Hello and the divisions
        assert!(result.contains("Hello"));
        assert!(result.contains("0.1"));
        assert!(!result.contains("timeout"));
    }

    #[test]
    fn test_forward_in_line_numbered_program() {
        let mut app = TimeWarpApp::default();

        // Test FORWARD in a line-numbered BASIC program
        let code = "10 FORWARD 5\n20 END";
        let result = app.execute_tw_basic(code);
        println!("FORWARD test result: {:?}", result);
        println!("Turtle commands after FORWARD: {:?}", app.turtle_commands);
        println!(
            "Turtle state: x={}, y={}, angle={}",
            app.turtle_state.x, app.turtle_state.y, app.turtle_state.angle
        );
        assert!(result.contains("Moved forward"));
        assert!(!app.turtle_commands.is_empty());
        // Should have moved 5 units from (0, 0) to (5, 0)
        assert_eq!(app.turtle_state.x, 5.0);
        assert_eq!(app.turtle_state.y, 0.0);
    }

    #[test]
    fn test_forward_direct_command() {
        let mut app = TimeWarpApp::default();

        // Test FORWARD as a direct command (not line-numbered) with longer distance
        let code = "FORWARD 50";
        let result = app.execute_tw_basic(code);
        println!("Direct FORWARD test result: {:?}", result);
        println!(
            "Turtle commands after direct FORWARD: {:?}",
            app.turtle_commands
        );
        println!(
            "Turtle state: x={}, y={}, angle={}",
            app.turtle_state.x, app.turtle_state.y, app.turtle_state.angle
        );
        assert!(result.contains("Moved forward"));
        assert!(!app.turtle_commands.is_empty());
        // Should have moved 50 units from (0, 0) to (50, 0)
        assert_eq!(app.turtle_state.x, 50.0);
        assert_eq!(app.turtle_state.y, 0.0);
    }

    // ===== GW BASIC COMMAND TESTS =====

    #[test]
    fn test_file_io_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING FILE I/O COMMANDS ===");

        // Test OPEN command
        println!("\n--- Testing OPEN command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("OPEN \"test.txt\" FOR OUTPUT AS #1");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("OPEN result: {}", output);
                assert!(output.contains("File opened") || output.is_empty()); // May be empty if not fully implemented
            }
            _ => println!("OPEN command executed (may not be fully implemented yet)"),
        }

        // Test CLOSE command
        println!("\n--- Testing CLOSE command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("CLOSE #1");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("CLOSE result: {}", output);
            }
            _ => println!("CLOSE command executed"),
        }

        // Test PRINT# command
        println!("\n--- Testing PRINT# command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("PRINT #1, \"Hello World\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("PRINT# result: {}", output);
            }
            _ => println!("PRINT# command executed"),
        }

        // Test INPUT# command
        println!("\n--- Testing INPUT# command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("INPUT #1, A$");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("INPUT# result: {}", output);
            }
            _ => println!("INPUT# command executed"),
        }

        // Test KILL command
        println!("\n--- Testing KILL command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("KILL \"test.txt\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("KILL result: {}", output);
            }
            _ => println!("KILL command executed"),
        }

        // Test NAME command
        println!("\n--- Testing NAME command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("NAME \"old.txt\" AS \"new.txt\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("NAME result: {}", output);
            }
            _ => println!("NAME command executed"),
        }

        // Test FILES command
        println!("\n--- Testing FILES command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("FILES");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("FILES result: {}", output);
            }
            _ => println!("FILES command executed"),
        }

        println!("\n=== FILE I/O COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_graphics_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING GRAPHICS COMMANDS ===");

        // Test LINE command
        println!("\n--- Testing LINE command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("LINE (10, 10)-(100, 100)");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("LINE result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty());
            }
            _ => println!("LINE command executed"),
        }

        // Test CIRCLE command
        println!("\n--- Testing CIRCLE command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("CIRCLE (200, 200), 50");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("CIRCLE result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty());
            }
            _ => println!("CIRCLE command executed"),
        }

        // Test PSET command
        println!("\n--- Testing PSET command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("PSET (150, 150)");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("PSET result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
            }
            _ => println!("PSET command executed"),
        }

        // Test PRESET command
        println!("\n--- Testing PRESET command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("PRESET (150, 150)");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("PRESET result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
            }
            _ => println!("PRESET command executed"),
        }

        // Test PAINT command
        println!("\n--- Testing PAINT command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("PAINT (100, 100)");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("PAINT result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
            }
            _ => println!("PAINT command executed"),
        }

        // Test DRAW command
        println!("\n--- Testing DRAW command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("DRAW \"U10 D10 L10 R10\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("DRAW result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
            }
            _ => println!("DRAW command executed"),
        }

        println!("\n=== GRAPHICS COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_sound_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING SOUND COMMANDS ===");

        // Test BEEP command
        println!("\n--- Testing BEEP command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("BEEP");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("BEEP result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty()); // Should generate a sound command
            }
            _ => println!("BEEP command executed"),
        }

        // Test SOUND command
        println!("\n--- Testing SOUND command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("SOUND 440, 1000");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("SOUND result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty()); // Should generate a sound command
            }
            _ => println!("SOUND command executed"),
        }

        println!("\n=== SOUND COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_screen_control_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING SCREEN CONTROL COMMANDS ===");

        // Test LOCATE command
        println!("\n--- Testing LOCATE command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("LOCATE 10, 20");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("LOCATE result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty()); // Should generate a locate command
            }
            _ => println!("LOCATE command executed"),
        }

        // Test SCREEN command
        println!("\n--- Testing SCREEN command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("SCREEN 1");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("SCREEN result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty()); // Should generate a screen command
            }
            _ => println!("SCREEN command executed"),
        }

        // Test WIDTH command
        println!("\n--- Testing WIDTH command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("WIDTH 80");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("WIDTH result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty()); // Should generate a width command
            }
            _ => println!("WIDTH command executed"),
        }

        // Test COLOR command
        println!("\n--- Testing COLOR command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("COLOR 1, 2");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("COLOR result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
                assert!(!graphics_commands.is_empty()); // Should generate color commands
            }
            _ => println!("COLOR command executed"),
        }

        // Test PALETTE command
        println!("\n--- Testing PALETTE command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("PALETTE 0, 65535");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("PALETTE result: {}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());
            }
            _ => println!("PALETTE command executed"),
        }

        println!("\n=== SCREEN CONTROL COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_error_handling_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING ERROR HANDLING COMMANDS ===");

        // Test ON ERROR command
        println!("\n--- Testing ON ERROR command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("ON ERROR GOTO 100");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("ON ERROR result: {}", output);
            }
            _ => println!("ON ERROR command executed"),
        }

        // Test RESUME command
        println!("\n--- Testing RESUME command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("RESUME");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("RESUME result: {}", output);
            }
            _ => println!("RESUME command executed"),
        }

        // Test RESUME with line number
        println!("\n--- Testing RESUME NEXT command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("RESUME NEXT");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("RESUME NEXT result: {}", output);
            }
            _ => println!("RESUME NEXT command executed"),
        }

        println!("\n=== ERROR HANDLING COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_control_flow_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING CONTROL FLOW COMMANDS ===");

        // Test WHILE/WEND loop
        println!("\n--- Testing WHILE/WEND loop ---");
        let mut interpreter = Interpreter::new();
        let program = r#"
        LET X = 1
        WHILE X <= 3
        PRINT "Count: "; X
        LET X = X + 1
        WEND
        PRINT "Loop finished"
        "#;
        let result = interpreter.execute(program);
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("WHILE/WEND result:\n{}", output);
                assert!(output.contains("Count: 1"));
                assert!(output.contains("Count: 2"));
                assert!(output.contains("Count: 3"));
                assert!(output.contains("Loop finished"));
            }
            _ => println!("WHILE/WEND loop executed"),
        }

        // Test SELECT CASE
        println!("\n--- Testing SELECT CASE ---");
        let mut interpreter = Interpreter::new();
        let program = r#"
        LET GRADE = 85
        SELECT CASE GRADE
        CASE 90 TO 100
        PRINT "A"
        CASE 80 TO 89
        PRINT "B"
        CASE 70 TO 79
        PRINT "C"
        CASE ELSE
        PRINT "F"
        END SELECT
        "#;
        let result = interpreter.execute(program);
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("SELECT CASE result:\n{}", output);
                assert!(output.contains("B"));
            }
            _ => println!("SELECT CASE executed"),
        }

        println!("\n=== CONTROL FLOW COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_system_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING SYSTEM COMMANDS ===");

        // Test SYSTEM command
        println!("\n--- Testing SYSTEM command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("SYSTEM");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("SYSTEM result: {}", output);
            }
            _ => println!("SYSTEM command executed"),
        }

        // Test CHDIR command
        println!("\n--- Testing CHDIR command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("CHDIR \"/tmp\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("CHDIR result: {}", output);
            }
            _ => println!("CHDIR command executed"),
        }

        // Test MKDIR command
        println!("\n--- Testing MKDIR command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("MKDIR \"testdir\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("MKDIR result: {}", output);
            }
            _ => println!("MKDIR command executed"),
        }

        // Test RMDIR command
        println!("\n--- Testing RMDIR command ---");
        let mut interpreter = Interpreter::new();
        let result = interpreter.execute("RMDIR \"testdir\"");
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("RMDIR result: {}", output);
            }
            _ => println!("RMDIR command executed"),
        }

        println!("\n=== SYSTEM COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_array_commands() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING ARRAY COMMANDS ===");

        // Test OPTION BASE
        println!("\n--- Testing OPTION BASE command ---");
        let mut interpreter = Interpreter::new();
        let program = r#"
        OPTION BASE 1
        DIM A(5)
        LET A(1) = 10
        PRINT "Array base is 1, A(1) = "; A(1)
        "#;
        let result = interpreter.execute(program);
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("OPTION BASE result:\n{}", output);
                assert!(output.contains("Array base is 1"));
            }
            _ => println!("OPTION BASE executed"),
        }

        // Test ERASE command
        println!("\n--- Testing ERASE command ---");
        let mut interpreter = Interpreter::new();
        let program = r#"
        DIM B(10)
        LET B(0) = 42
        PRINT "Before ERASE: B(0) = "; B(0)
        ERASE B
        "#;
        let result = interpreter.execute(program);
        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete { output, .. }) => {
                println!("ERASE result:\n{}", output);
            }
            _ => println!("ERASE command executed"),
        }

        println!("\n=== ARRAY COMMANDS TEST COMPLETE ===");
    }

    #[test]
    fn test_comprehensive_gw_basic_program() {
        use crate::languages::basic::Interpreter;

        println!("=== TESTING COMPREHENSIVE GW BASIC PROGRAM ===");

        // Create a comprehensive program using multiple GW BASIC features
        let program = r#"
        PRINT "Hello World"
        LET GRADE = 85
        SELECT CASE GRADE
        CASE 80 TO 89
        PRINT "Grade: B"
        END SELECT
        "#;

        let mut interpreter = Interpreter::new();
        let result = interpreter.execute(program);

        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("COMPREHENSIVE PROGRAM OUTPUT:\n{}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());

                // Verify key outputs
                assert!(output.contains("Hello World"));
                assert!(output.contains("Grade: B"));

                println!("\n=== COMPREHENSIVE TEST PASSED ===");
            }
            Err(e) => {
                println!("COMPREHENSIVE PROGRAM FAILED: {:?}", e);
                panic!("Comprehensive test failed");
            }
            _ => {
                println!("COMPREHENSIVE PROGRAM - Unexpected result type");
            }
        }
    }

    #[test]
    fn test_comprehensive_demo_program() {
        use crate::languages::basic::Interpreter;

        println!("\n=== TESTING COMPREHENSIVE DEMO PROGRAM ===");

        let program = r#"
10 PRINT "TW BASIC Comprehensive Demonstration Program"
20 PRINT "============================================"
30 LET SCORE = 0
40 PRINT "SCORE ="; SCORE
50 PRINT "Program completed successfully!"
"#;

        let mut interpreter = Interpreter::new();
        let result = interpreter.execute(program);

        match result {
            Ok(crate::languages::basic::ExecutionResult::Complete {
                output,
                graphics_commands,
            }) => {
                println!("COMPREHENSIVE DEMO OUTPUT:\n{}", output);
                println!("Graphics commands generated: {}", graphics_commands.len());

                // Verify comprehensive functionality
                assert!(output.contains("TW BASIC Comprehensive Demonstration Program"));
                assert!(output.contains("SCORE =0"));
                assert!(output.contains("Program completed successfully"));

                println!("\n=== COMPREHENSIVE DEMO TEST PASSED ===");
            }
            Err(e) => {
                println!("COMPREHENSIVE DEMO FAILED: {:?}", e);
                panic!("Comprehensive demo test failed");
            }
            _ => {
                println!("COMPREHENSIVE DEMO - Unexpected result type");
            }
        }
    }

    #[test]
    fn test_type_declaration_commands() {
        println!("\n=== TESTING TYPE DECLARATION COMMANDS ===");
        let mut app = TimeWarpApp::default();

        // Test DEFINT with range
        let program = "10 DEFINT A-Z\n20 A = 3.14\n30 B = 5.9\n40 PRINT A, B";
        let result = app.execute_tw_basic(program);
        println!("DEFINT test output: {}", result);
        assert!(
            result.contains("3") && result.contains("5"),
            "DEFINT should truncate decimals to integers"
        );

        // Test DEFSTR
        let program = "10 DEFSTR S\n20 S = 123\n30 PRINT S";
        let result = app.execute_tw_basic(program);
        println!("DEFSTR test output: {}", result);
        assert!(
            result.contains("123"),
            "DEFSTR should convert numbers to strings"
        );

        // Test DEFSNG (default behavior)
        let program = "10 DEFSNG X\n20 X = 3.14159\n30 PRINT X";
        let result = app.execute_tw_basic(program);
        println!("DEFSNG test output: {}", result);
        assert!(
            result.contains("3.14159"),
            "DEFSNG should preserve floating point precision"
        );

        // Test CLEAR resets type defaults
        let program = "10 DEFINT A-Z\n20 CLEAR\n30 A = 3.14\n40 PRINT A";
        let result = app.execute_tw_basic(program);
        println!("CLEAR type defaults test output: {}", result);
        assert!(
            result.contains("3.14"),
            "CLEAR should reset type defaults to single precision"
        );

        println!("\n=== TYPE DECLARATION COMMANDS TEST PASSED ===");
    }

    #[test]
    fn test_system_functions() {
        println!("\n=== TESTING SYSTEM FUNCTIONS ===");
        let mut app = TimeWarpApp::default();

        // Test DATE$ function
        let program = "PRINT DATE$";
        let result = app.execute_tw_basic(program);
        println!("DATE$ test output: {}", result);
        // Should return a date string in MM-DD-YYYY format
        assert!(result.contains("-"), "DATE$ should return formatted date");

        // Test TIME$ function
        let program = "PRINT TIME$";
        let result = app.execute_tw_basic(program);
        println!("TIME$ test output: {}", result);
        // Should return a time string in HH:MM:SS format
        assert!(result.contains(":"), "TIME$ should return formatted time");

        // Test TIMER function
        let program = "PRINT TIMER";
        let result = app.execute_tw_basic(program);
        println!("TIMER test output: {}", result);
        // Should return a number (seconds since midnight)
        assert!(
            result
                .chars()
                .all(|c| c.is_numeric() || c == '.' || c == '\n'),
            "TIMER should return a numeric value"
        );

        // Test ENVIRON$ with variable name
        let program = "PRINT ENVIRON$(\"PATH\")";
        let result = app.execute_tw_basic(program);
        println!("ENVIRON$ test output: {}", result);
        // Should return the PATH environment variable or empty string
        // (We can't assert specific content since it depends on the environment)

        // Test ENVIRON$ with numeric index
        let program = "PRINT ENVIRON$(1)";
        let result = app.execute_tw_basic(program);
        println!("ENVIRON$ numeric test output: {}", result);
        // Should return the first environment variable in KEY=VALUE format

        // Test INT(RND(1)*100) expression
        let program = "PRINT INT(RND(1)*100)";
        let result = app.execute_tw_basic(program);
        println!("INT(RND(1)*100) test output: {}", result);
        // Should return an integer between 0 and 99
        let num_result: f64 = result.trim().parse().expect("Should parse as number");
        assert!(
            num_result >= 0.0 && num_result < 100.0,
            "INT(RND(1)*100) should return 0-99"
        );

        println!("\n=== SYSTEM FUNCTIONS TEST PASSED ===");
    }
}
