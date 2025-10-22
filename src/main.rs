use eframe::egui;
use rfd::FileDialog;
use std::collections::HashMap;

#[derive(Clone)]
struct TurtleState {
    x: f32,
    y: f32,
    angle: f32, // in degrees
    pen_down: bool,
    color: egui::Color32,
}

struct TimeWarpApp {
    code: String,
    output: String,
    language: String,
    active_tab: usize, // 0 = Editor, 1 = Output & Turtle
    code_history: Vec<String>,
    code_history_index: usize,
    last_file_path: Option<String>,
    variables: HashMap<String, String>,
    show_line_numbers: bool,
    find_text: String,
    replace_text: String,
    show_find_replace: bool,
    turtle_state: TurtleState,
    turtle_commands: Vec<String>,
    is_executing: bool,
    waiting_for_input: bool,
    input_prompt: String,
    user_input: String,
    current_input_var: String,
    output_scroll: usize,
}

impl Default for TimeWarpApp {
    fn default() -> Self {
        Self {
            code: String::new(),
            output: String::from("Welcome to Time Warp IDE!\n"),
            language: String::from("TW BASIC"),
            active_tab: 0, // Start with Editor tab
            code_history: vec![String::new()],
            code_history_index: 0,
            last_file_path: None,
            variables: HashMap::new(),
            show_line_numbers: false,
            find_text: String::new(),
            replace_text: String::new(),
            show_find_replace: false,
            turtle_state: TurtleState {
                x: 200.0,
                y: 200.0,
                angle: 0.0,
                pen_down: true,
                color: egui::Color32::BLACK,
            },
            turtle_commands: Vec::new(),
            is_executing: false,
            waiting_for_input: false,
            input_prompt: String::new(),
            user_input: String::new(),
            current_input_var: String::new(),
            output_scroll: 0,
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
            _ => format!("Language '{}' not yet supported for execution", self.language),
        };
        if self.is_executing && !self.waiting_for_input {
            self.output = format!("[Output for {}]\n{}", self.language, result);
        }
        self.is_executing = false;
    }

    fn execute_tw_basic(&mut self, code: &str) -> String {
        let mut output = String::new();
        for line in code.lines() {
            let line = line.trim();
            if line.is_empty() || line.starts_with("REM") {
                continue;
            }
            if line.starts_with("PRINT ") {
                if let Some(text) = line.strip_prefix("PRINT ") {
                    output.push_str(&text.replace("\"", ""));
                    output.push('\n');
                }
            } else if line.starts_with("LET ") {
                // Simple variable assignment
                output.push_str("Variable assigned\n");
            } else if line.starts_with("FORWARD ") || line.starts_with("RIGHT ") {
                // Turtle graphics commands
                self.turtle_commands.push(line.to_string());
                output.push_str("Turtle command executed\n");
            }
        }
        if output.is_empty() {
            "No executable code found".to_string()
        } else {
            output
        }
    }

    fn execute_tw_pascal(&mut self, _code: &str) -> String {
        "TW Pascal execution not yet implemented".to_string()
    }

    fn execute_tw_prolog(&mut self, _code: &str) -> String {
        "TW Prolog execution not yet implemented".to_string()
    }
}

impl eframe::App for TimeWarpApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        ctx.set_visuals(egui::Visuals::light());

        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                ui.menu_button("�� File", |ui| {
                    if ui.button("📄 New File").clicked() {
                        self.code.clear();
                        self.output = "New file created.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📂 Open File...").clicked() {
                        if let Some(path) = FileDialog::new()
                            .add_filter("Text", &["txt", "twb", "twp", "tpr"])
                            .pick_file() {
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
                        } else if let Some(path) = FileDialog::new()
                            .set_file_name("untitled.twb")
                            .save_file() {
                            if std::fs::write(&path, &self.code).is_ok() {
                                self.output = format!("Saved to {}", path.display());
                                self.last_file_path = Some(path.display().to_string());
                            }
                        }
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
                for lang in ["TW BASIC", "TW Pascal", "TW Prolog"] {
                    ui.selectable_value(&mut self.language, lang.to_string(), lang);
                }
                ui.separator();
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if ui.button("Run ▶").clicked() {
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
                    if ui.selectable_label(self.active_tab == 0, "📝 Code Editor").clicked() {
                        self.active_tab = 0;
                    }
                    if ui.selectable_label(self.active_tab == 1, "🖥️ Output & Graphics").clicked() {
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
                                        self.code = self.code.replace(&self.find_text, &self.replace_text);
                                    }
                                });
                                ui.separator();
                            }

                            egui::ScrollArea::vertical().show(ui, |ui| {
                                if self.show_line_numbers {
                                    // With line numbers
                                    let mut lines: Vec<String> = self.code.lines().map(|s| s.to_string()).collect();
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
                                            .desired_rows(20)
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
                                            .desired_width(f32::INFINITY)
                                    );
                                });

                            ui.separator();
                            ui.label("Turtle Graphics:");
                            ui.add_space(4.0);

                            // Simple canvas for turtle graphics
                            let canvas_size = egui::vec2(400.0, 300.0);
                            let (rect, _response) = ui.allocate_exact_size(canvas_size, egui::Sense::hover());

                            ui.painter().rect_filled(rect, 0.0, egui::Color32::WHITE);
                            ui.painter().rect_stroke(rect, 0.0, egui::Stroke::new(1.0, egui::Color32::BLACK));

                            // Draw turtle
                            let center = rect.center();
                            let turtle_x = center.x + self.turtle_state.x;
                            let turtle_y = center.y + self.turtle_state.y;

                            // Draw a simple triangle for the turtle
                            let size = 8.0;
                            let angle_rad = self.turtle_state.angle.to_radians();
                            let points = [
                                egui::pos2(
                                    turtle_x + size * angle_rad.cos(),
                                    turtle_y + size * angle_rad.sin()
                                ),
                                egui::pos2(
                                    turtle_x + size * (angle_rad + 2.0944).cos(),
                                    turtle_y + size * (angle_rad + 2.0944).sin()
                                ),
                                egui::pos2(
                                    turtle_x + size * (angle_rad - 2.0944).cos(),
                                    turtle_y + size * (angle_rad - 2.0944).sin()
                                ),
                            ];

                            ui.painter().add(egui::Shape::convex_polygon(
                                points.to_vec(),
                                self.turtle_state.color,
                                egui::Stroke::new(1.0, egui::Color32::BLACK)
                            ));
                        });
                    }
                    _ => {}
                }
            });
        });
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
