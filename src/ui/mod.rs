use eframe::egui;
use rfd::FileDialog;
use std::collections::HashMap;

use crate::languages;

#[derive(Clone)]
pub struct TurtleState {
    pub x: f32,
    pub y: f32,
    pub angle: f32, // in degrees
    pub color: egui::Color32,
}

pub enum CommandResult {
    Output(String),
    Goto(u32),
    Input(String, String), // (variable_name, prompt)
    Continue,
    End,
}

pub struct TimeWarpApp {
    pub code: String,
    pub output: String,
    pub language: String,
    pub active_tab: usize, // 0 = Editor, 1 = Output & Turtle
    pub last_file_path: Option<String>,
    pub show_line_numbers: bool,
    pub find_text: String,
    pub replace_text: String,
    pub show_find_replace: bool,
    pub turtle_state: TurtleState,
    pub turtle_commands: Vec<String>,
    pub variables: HashMap<String, String>,
    pub program_lines: Vec<(u32, String)>, // Line number and command
    pub current_line: usize,
    pub current_pascal_line: usize,
    pub is_executing: bool,
    pub waiting_for_input: bool,
    pub input_prompt: String,
    pub user_input: String,
    pub current_input_var: String,
    pub show_about: bool,
    pub turtle_zoom: f32,
    pub turtle_pan: egui::Vec2,
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
    pub fn execute_code(&mut self) {
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

    pub fn execute_tw_basic(&mut self, code: &str) -> String {
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
            Err(err) => format!("Execution error: {:?}", err),
        }
    }

    pub fn execute_tw_pascal(&mut self, code: &str) -> String {
        use crate::languages::pascal::PascalInterpreter;

        let mut interpreter = PascalInterpreter::new();
        match interpreter.execute(code) {
            Ok(output) => output,
            Err(err) => format!("Error: {:?}", err),
        }
    }

    pub fn execute_tw_prolog(&mut self, code: &str) -> String {
        use crate::languages::prolog::PrologInterpreter;

        let mut interpreter = PrologInterpreter::new();
        match interpreter.execute(code) {
            Ok(output) => output,
            Err(err) => format!("Error: {:?}", err),
        }
    }

    pub fn execute_pilot(&mut self, code: &str) -> String {
        // PILOT execution logic here
        format!("PILOT execution not yet implemented for: {}", code)
    }

    pub fn handle_input(&mut self, input: String) {
        if self.waiting_for_input {
            self.user_input = input.clone();
            self.waiting_for_input = false;
            // Continue execution with the input
            // For now, just append to output
            self.output.push_str(&format!("\n{}", input));
            // In a full implementation, you'd resume the interpreter with the input
        }
    }

    pub fn clear_output(&mut self) {
        self.output = String::new();
        self.turtle_commands.clear();
        self.turtle_state = TurtleState {
            x: 200.0,
            y: 200.0,
            angle: 0.0,
            color: egui::Color32::BLACK,
        };
        self.variables.clear();
        self.program_lines.clear();
        self.current_line = 0;
        self.current_pascal_line = 0;
        self.is_executing = false;
        self.waiting_for_input = false;
        self.input_prompt = String::new();
        self.user_input = String::new();
        self.current_input_var = String::new();
    }

    pub fn reset_turtle(&mut self) {
        self.turtle_state = TurtleState {
            x: 200.0,
            y: 200.0,
            angle: 0.0,
            color: egui::Color32::BLACK,
        };
        self.turtle_commands.clear();
    }

    pub fn draw_turtle(&self, ui: &mut egui::Ui, rect: egui::Rect) {
        let painter = ui.painter();
        let center = rect.center();

        // Draw turtle as a small triangle
        let size = 10.0;
        let angle_rad = self.turtle_state.angle.to_radians();
        let tip = egui::pos2(
            center.x + angle_rad.cos() * size,
            center.y + angle_rad.sin() * size,
        );
        let left = egui::pos2(
            center.x + (angle_rad + 2.5).cos() * size * 0.5,
            center.y + (angle_rad + 2.5).sin() * size * 0.5,
        );
        let right = egui::pos2(
            center.x + (angle_rad - 2.5).cos() * size * 0.5,
            center.y + (angle_rad - 2.5).sin() * size * 0.5,
        );

        let triangle = [tip, left, right];
        painter.add(egui::Shape::convex_polygon(
            triangle.to_vec(),
            self.turtle_state.color,
            egui::Stroke::NONE,
        ));
    }

    pub fn render_ui(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
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
            self.clear_output();
        }

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.vertical(|ui| {
                // Menu bar
                ui.horizontal(|ui| {
                    ui.menu_button("File", |ui| {
                        if ui.button("New (Ctrl+N)").clicked() {
                            self.code.clear();
                            self.output = "New file created.".to_string();
                        }
                        if ui.button("Open (Ctrl+O)").clicked() {
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
                        if ui.button("Save (Ctrl+S)").clicked() {
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
                        }
                        ui.separator();
                        if ui.button("Exit").clicked() {
                            std::process::exit(0);
                        }
                    });

                    ui.menu_button("Edit", |ui| {
                        if ui.button("Find (Ctrl+F)").clicked() {
                            self.show_find_replace = true;
                        }
                        if ui.button("Replace (Ctrl+R)").clicked() {
                            self.show_find_replace = true;
                        }
                    });

                    ui.menu_button("Run", |ui| {
                        if ui.button("Run (F5)").clicked() {
                            self.active_tab = 1;
                            self.execute_code();
                        }
                        if ui.button("Clear Output (Ctrl+Shift+C)").clicked() {
                            self.clear_output();
                        }
                    });

                    ui.menu_button("Language", |ui| {
                        if ui
                            .selectable_label(self.language == "TW BASIC", "TW BASIC")
                            .clicked()
                        {
                            self.language = "TW BASIC".to_string();
                        }
                        if ui
                            .selectable_label(self.language == "TW Pascal", "TW Pascal")
                            .clicked()
                        {
                            self.language = "TW Pascal".to_string();
                        }
                        if ui
                            .selectable_label(self.language == "TW Prolog", "TW Prolog")
                            .clicked()
                        {
                            self.language = "TW Prolog".to_string();
                        }
                        if ui
                            .selectable_label(self.language == "PILOT", "PILOT")
                            .clicked()
                        {
                            self.language = "PILOT".to_string();
                        }
                    });

                    ui.menu_button("View", |ui| {
                        if ui
                            .checkbox(&mut self.show_line_numbers, "Show Line Numbers")
                            .clicked()
                        {
                            // Toggle handled by checkbox
                        }
                    });

                    ui.menu_button("Help", |ui| {
                        if ui.button("About").clicked() {
                            self.show_about = true;
                        }
                    });
                });

                ui.separator();

                // Tabs
                ui.horizontal(|ui| {
                    if ui
                        .selectable_label(self.active_tab == 0, "Editor")
                        .clicked()
                    {
                        self.active_tab = 0;
                    }
                    if ui
                        .selectable_label(self.active_tab == 1, "Output & Turtle")
                        .clicked()
                    {
                        self.active_tab = 1;
                    }
                });

                ui.separator();

                match self.active_tab {
                    0 => {
                        // Editor tab
                        ui.vertical(|ui| {
                            ui.horizontal(|ui| {
                                ui.label("Language:");
                                egui::ComboBox::from_label("")
                                    .selected_text(&self.language)
                                    .show_ui(ui, |ui| {
                                        ui.selectable_value(
                                            &mut self.language,
                                            "TW BASIC".to_string(),
                                            "TW BASIC",
                                        );
                                        ui.selectable_value(
                                            &mut self.language,
                                            "TW Pascal".to_string(),
                                            "TW Pascal",
                                        );
                                        ui.selectable_value(
                                            &mut self.language,
                                            "TW Prolog".to_string(),
                                            "TW Prolog",
                                        );
                                        ui.selectable_value(
                                            &mut self.language,
                                            "PILOT".to_string(),
                                            "PILOT",
                                        );
                                    });
                                if ui.button("Run").clicked() {
                                    self.active_tab = 1;
                                    self.execute_code();
                                }
                            });

                            ui.separator();

                            egui::ScrollArea::vertical().show(ui, |ui| {
                                ui.add(
                                    egui::TextEdit::multiline(&mut self.code)
                                        .font(egui::FontId::monospace(14.0))
                                        .desired_width(f32::INFINITY)
                                        .desired_rows(20),
                                );
                            });
                        });
                    }
                    1 => {
                        // Output & Turtle tab
                        ui.vertical(|ui| {
                            ui.horizontal(|ui| {
                                if ui.button("Clear").clicked() {
                                    self.clear_output();
                                }
                                if ui.button("Reset Turtle").clicked() {
                                    self.reset_turtle();
                                }
                                if self.waiting_for_input {
                                    ui.label(&self.input_prompt);
                                    if ui.text_edit_singleline(&mut self.user_input).lost_focus()
                                        && ui.input(|i| i.key_pressed(egui::Key::Enter))
                                    {
                                        self.handle_input(self.user_input.clone());
                                    }
                                }
                            });

                            ui.separator();

                            ui.columns(2, |columns| {
                                // Output column
                                columns[0].vertical(|ui| {
                                    ui.label("Output:");
                                    egui::ScrollArea::vertical().show(ui, |ui| {
                                        ui.add(
                                            egui::TextEdit::multiline(&mut self.output)
                                                .font(egui::FontId::monospace(12.0))
                                                .desired_width(f32::INFINITY)
                                                .desired_rows(15),
                                        );
                                    });
                                });

                                // Turtle graphics column
                                columns[1].vertical(|ui| {
                                    ui.label("Turtle Graphics:");
                                    let turtle_rect = ui.available_rect_before_wrap();
                                    self.draw_turtle(ui, turtle_rect);
                                });
                            });
                        });
                    }
                    _ => {}
                }
            });
        });

        // Find/Replace dialog
        if self.show_find_replace {
            let mut open = true;
            egui::Window::new("Find & Replace")
                .open(&mut open)
                .show(ctx, |ui| {
                    ui.horizontal(|ui| {
                        ui.label("Find:");
                        ui.text_edit_singleline(&mut self.find_text);
                    });
                    ui.horizontal(|ui| {
                        ui.label("Replace:");
                        ui.text_edit_singleline(&mut self.replace_text);
                    });
                    ui.horizontal(|ui| {
                        if ui.button("Find Next").clicked() {
                            // Implement find logic
                        }
                        if ui.button("Replace").clicked() {
                            // Implement replace logic
                        }
                        if ui.button("Replace All").clicked() {
                            // Implement replace all logic
                        }
                    });
                });
            if !open {
                self.show_find_replace = false;
            }
        }

        // About dialog
        if self.show_about {
            let mut open = true;
            egui::Window::new("About Time Warp IDE")
                .open(&mut open)
                .show(ctx, |ui| {
                    ui.label("Time Warp IDE");
                    ui.label("Version 0.1.0");
                    ui.label("An educational programming IDE supporting multiple languages with turtle graphics.");
                    ui.label("Built with Rust and egui.");
                });
            if !open {
                self.show_about = false;
            }
        }
    }
}

impl eframe::App for TimeWarpApp {
    fn update(&mut self, ctx: &egui::Context, frame: &mut eframe::Frame) {
        self.render_ui(ctx, frame);
    }
}
