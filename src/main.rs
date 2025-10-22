use eframe::egui;use eframe::egui;use eframe::egui;

use rfd::FileDialog;

use std::collections::HashMap;use rfd::FileDialog;use rfd::FileDialog;



#[derive(Clone)]use std::collections::HashMap;use std::collections::HashMap;

struct TurtleState {

    x: f32,

    y: f32,

    angle: f32, // in degrees#[derive(Clone)]#[derive(Clone)]

    pen_down: bool,

    color: egui::Color32,struct TurtleState {struct TurtleState {

}

    x: f32,    x: f32,

struct TimeWarpApp {

    code: String,    y: f32,    y: f32,

    output: String,

    language: String,    angle: f32, // in degrees    angle: f32, // in degrees

    active_tab: usize, // 0 = Editor, 1 = Output & Turtle

    code_history: Vec<String>,    pen_down: bool,    pen_down: bool,

    code_history_index: usize,

    last_file_path: Option<String>,    color: egui::Color32,    color: egui::Color32,

    variables: HashMap<String, String>,

    show_line_numbers: bool,}}

    find_text: String,

    replace_text: String,

    show_find_replace: bool,

    turtle_state: TurtleState,struct TimeWarpApp {struct TimeWarpApp {

    turtle_commands: Vec<String>,

    is_executing: bool,    code: String,    code: String,

    waiting_for_input: bool,

    input_prompt: String,    output: String,    output: String,

    user_input: String,

    current_input_var: String,    language: String,    language: String,

    output_scroll: usize,

}    active_tab: usize, // 0 = Editor, 1 = Output & Turtle    active_tab: usize, // 0 = Editor, 1 = Output & Turtle



impl Default for TimeWarpApp {    code_history: Vec<String>,    code_history: Vec<String>,

    fn default() -> Self {

        Self {    code_history_index: usize,    code_history_index: usize,

            code: String::new(),

            output: String::from("Welcome to Time Warp IDE!\n"),    last_file_path: Option<String>,    last_file_path: Option<String>,

            language: String::from("TW BASIC"),

            active_tab: 0, // Start with Editor tab    variables: HashMap<String, String>,    variables: HashMap<String, String>,

            code_history: vec![String::new()],

            code_history_index: 0,    show_line_numbers: bool,    show_line_numbers: bool,

            last_file_path: None,

            variables: HashMap::new(),    find_text: String,    find_text: String,

            show_line_numbers: false,

            find_text: String::new(),    replace_text: String,    replace_text: String,

            replace_text: String::new(),

            show_find_replace: false,    show_find_replace: bool,    show_find_replace: bool,

            turtle_state: TurtleState {

                x: 200.0,    turtle_state: TurtleState,    turtle_state: TurtleState,

                y: 200.0,

                angle: 0.0,    turtle_commands: Vec<String>,    turtle_commands: Vec<String>,

                pen_down: true,

                color: egui::Color32::BLACK,    is_executing: bool,    is_executing: bool,

            },

            turtle_commands: Vec::new(),    waiting_for_input: bool,    waiting_for_input: bool,

            is_executing: false,

            waiting_for_input: false,    input_prompt: String,    input_prompt: String,

            input_prompt: String::new(),

            user_input: String::new(),    user_input: String,    user_input: String,

            current_input_var: String::new(),

            output_scroll: 0,    current_input_var: String,    current_input_var: String,

        }

    }    output_scroll: usize,    output_scroll: usize,

}

}}

impl TimeWarpApp {

    fn execute_code(&mut self) {

        self.active_tab = 1; // Switch to Output tab when running

        self.is_executing = true;impl Default for TimeWarpApp {impl Default for TimeWarpApp {

        let code = self.code.clone();

        let result = match self.language.as_str() {    fn default() -> Self {    fn default() -> Self {

            "TW BASIC" => self.execute_tw_basic(&code),

            "TW Pascal" => self.execute_tw_pascal(&code),        Self {        Self {

            "TW Prolog" => self.execute_tw_prolog(&code),

            _ => format!("Language '{}' not yet supported for execution", self.language),            code: String::new(),            code: String::new(),

        };

        if self.is_executing && !self.waiting_for_input {            output: String::from("Welcome to Time Warp IDE!\n"),            output: String::from("Welcome to Time Warp IDE!\n"),

            self.output = format!("[Output for {}]\n{}", self.language, result);

        }            language: String::from("TW BASIC"),            language: String::from("TW BASIC"),

        self.is_executing = false;

    }            active_tab: 0, // Start with Editor tab            active_tab: 0, // Start with Editor tab



    fn execute_tw_basic(&mut self, code: &str) -> String {            code_history: vec![String::new()],            code_history: vec![String::new()],

        let mut output = String::new();

        for line in code.lines() {            code_history_index: 0,            code_history_index: 0,

            let line = line.trim();

            if line.is_empty() || line.starts_with("REM") {            last_file_path: None,            last_file_path: None,

                continue;

            }            variables: HashMap::new(),            variables: HashMap::new(),

            if line.starts_with("PRINT ") {

                if let Some(text) = line.strip_prefix("PRINT ") {            show_line_numbers: false,            show_line_numbers: false,

                    output.push_str(&text.replace("\"", ""));

                    output.push('\n');            find_text: String::new(),            find_text: String::new(),

                }

            } else if line.starts_with("LET ") {            replace_text: String::new(),            replace_text: String::new(),

                // Simple variable assignment

                output.push_str("Variable assigned\n");            show_find_replace: false,            show_find_replace: false,

            } else if line.starts_with("FORWARD ") || line.starts_with("RIGHT ") {

                // Turtle graphics commands            turtle_state: TurtleState {            turtle_state: TurtleState {

                self.turtle_commands.push(line.to_string());

                output.push_str("Turtle command executed\n");                x: 200.0,                x: 200.0,

            }

        }                y: 200.0,                y: 200.0,

        if output.is_empty() {

            "No executable code found".to_string()                angle: 0.0,                angle: 0.0,

        } else {

            output                pen_down: true,                pen_down: true,

        }

    }                color: egui::Color32::BLACK,                color: egui::Color32::BLACK,



    fn execute_tw_pascal(&mut self, _code: &str) -> String {            },            },

        "TW Pascal execution not yet implemented".to_string()

    }            turtle_commands: Vec::new(),            turtle_commands: Vec::new(),



    fn execute_tw_prolog(&mut self, _code: &str) -> String {            is_executing: false,            is_executing: false,

        "TW Prolog execution not yet implemented".to_string()

    }            waiting_for_input: false,            waiting_for_input: false,

}

            input_prompt: String::new(),            input_prompt: String::new(),

impl eframe::App for TimeWarpApp {

    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {            user_input: String::new(),            user_input: String::new(),

        ctx.set_visuals(egui::Visuals::light());

            current_input_var: String::new(),            current_input_var: String::new(),

        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {

            egui::menu::bar(ui, |ui| {            output_scroll: 0,            output_scroll: 0,

                ui.menu_button("📁 File", |ui| {

                    if ui.button("📄 New File").clicked() {        }        }

                        self.code.clear();

                        self.output = "New file created.".to_string();    }    }

                        ui.close_menu();

                    }}}

                    if ui.button("📂 Open File...").clicked() {

                        if let Some(path) = FileDialog::new()

                            .add_filter("Text", &["txt", "twb", "twp", "tpr"])

                            .pick_file() {impl TimeWarpApp {impl TimeWarpApp {

                            if let Ok(content) = std::fs::read_to_string(&path) {

                                self.code = content;    fn execute_code(&mut self) {    fn execute_code(&mut self) {

                                self.output = format!("Opened file: {}", path.display());

                                self.last_file_path = Some(path.display().to_string());        self.is_executing = true;        self.is_executing = true;

                            }

                        }        let code = self.code.clone(); // Clone to avoid borrowing conflict        let code = self.code.clone(); // Clone to avoid borrowing conflict

                        ui.close_menu();

                    }        let result = match self.language.as_str() {        let result = match self.language.as_str() {

                    if ui.button("💾 Save").clicked() {

                        if let Some(path) = &self.last_file_path {            "TW BASIC" => self.execute_tw_basic(&code),            "TW BASIC" => self.execute_tw_basic(&code),

                            if std::fs::write(path, &self.code).is_ok() {

                                self.output = format!("Saved to {}", path);            "TW Pascal" => self.execute_tw_pascal(&code),            "TW Pascal" => self.execute_tw_pascal(&code),

                            }

                        } else if let Some(path) = FileDialog::new()            "TW Prolog" => self.execute_tw_prolog(&code),            "TW Prolog" => self.execute_tw_prolog(&code),

                            .set_file_name("untitled.twb")

                            .save_file() {            _ => format!("Language '{}' not yet supported for execution", self.language),            _ => format!("Language '{}' not yet supported for execution", self.language),

                            if std::fs::write(&path, &self.code).is_ok() {

                                self.output = format!("Saved to {}", path.display());        };        };

                                self.last_file_path = Some(path.display().to_string());

                            }        if self.is_executing && !self.waiting_for_input {  // Only show result if not stopped and not waiting for input        if self.is_executing && !self.waiting_for_input {  // Only show result if not stopped and not waiting for input

                        }

                        ui.close_menu();            self.output = format!("[Output for {}]\n{}", self.language, result);            self.output = format!("[Output for {}]\n{}", self.language, result);

                    }

                });        }        }

            });

        });        self.is_executing = false;        self.is_executing = false;



        egui::TopBottomPanel::top("top_panel").show(ctx, |ui| {    }    }

            ui.horizontal(|ui| {

                ui.heading("Time Warp IDE");

                ui.separator();

                ui.label("Language:");    fn execute_tw_basic(&mut self, code: &str) -> String {    fn execute_tw_basic(&mut self, code: &str) -> String {

                for lang in ["TW BASIC", "TW Pascal", "TW Prolog"] {

                    ui.selectable_value(&mut self.language, lang.to_string(), lang);        let mut output = Vec::new();        let mut output = Vec::new();

                }

                ui.separator();        let mut lines = Vec::new();        let mut lines = Vec::new();

                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {

                    if ui.button("Run ▶").clicked() {        let mut line_numbers = std::collections::HashMap::new();        let mut line_numbers = std::collections::HashMap::new();

                        self.active_tab = 1; // Switch to Output tab when running

                        self.execute_code();        let mut _current_line = 0;        let mut _current_line = 0;

                    }

                });        let mut for_stack = Vec::new();        let mut for_stack = Vec::new();

            });

        });        let mut gosub_stack = Vec::new();        let mut gosub_stack = Vec::new();



        egui::CentralPanel::default().show(ctx, |ui| {

            ui.add_space(8.0);

            egui::Frame::group(ui.style()).show(ui, |ui| {        // Parse program - handle both line-numbered and non-line-numbered code        // Parse program - handle both line-numbered and non-line-numbered code

                ui.horizontal(|ui| {

                    if ui.selectable_label(self.active_tab == 0, "📝 Code Editor").clicked() {        for (line_idx, line) in code.lines().enumerate() {        for (line_idx, line) in code.lines().enumerate() {

                        self.active_tab = 0;

                    }            let line = line.trim();            let line = line.trim();

                    if ui.selectable_label(self.active_tab == 1, "🖥️ Output & Graphics").clicked() {

                        self.active_tab = 1;            if line.is_empty() || line.starts_with("REM") || line.starts_with("'") {            if line.is_empty() || line.starts_with("REM") || line.starts_with("'") {

                    }

                });                continue;                continue;



                ui.separator();            }            }



                match self.active_tab {            // Check if it's a line-numbered BASIC program

                    0 => {            if let Some(space_pos) = line.find(' ') {

                        // Code Editor Tab                if let Ok(line_num) = line[..space_pos].parse::<u32>() {

                        ui.vertical(|ui| {                    let command = line[space_pos..].trim();

                            ui.horizontal(|ui| {                    lines.push((line_num, command.to_string()));

                                ui.checkbox(&mut self.show_line_numbers, "Line numbers");                    line_numbers.insert(line_num, line_idx);

                                ui.separator();                    continue;

                                if ui.button("🔍 Find/Replace").clicked() {                }

                                    self.show_find_replace = !self.show_find_replace;            }

                                }

                            });            // Non-line-numbered code (PILOT, Logo, or modern BASIC)

            lines.push((line_idx as u32, line.to_string()));

                            if self.show_find_replace {        }

                                ui.horizontal(|ui| {

                                    ui.label("Find:");        // Sort by line number for line-numbered programs

                                    ui.text_edit_singleline(&mut self.find_text);        if lines.iter().any(|(num, _)| *num > 0) {

                                    ui.label("Replace:");            lines.sort_by_key(|(num, _)| *num);

                                    ui.text_edit_singleline(&mut self.replace_text);        }

                                    if ui.button("Replace All").clicked() {

                                        self.code = self.code.replace(&self.find_text, &self.replace_text);        let mut i = 0;

                                    }        while i < lines.len() {

                                });            let (line_num, command) = &lines[i];

                                ui.separator();            _current_line = *line_num;

                            }

            let cmd_upper = command.to_uppercase();

                            egui::ScrollArea::vertical().show(ui, |ui| {            let cmd_trim = command.trim();

                                if self.show_line_numbers {

                                    // With line numbers            // GW BASIC Commands

                                    let mut lines: Vec<String> = self.code.lines().map(|s| s.to_string()).collect();            if cmd_upper.starts_with("PRINT") || cmd_upper.starts_with("?") {

                                    if lines.is_empty() {                let print_cmd = if cmd_upper.starts_with("?") { 

                                        lines.push(String::new());                    if command.len() > 1 { &command[1..] } else { "" }

                                    }                } else { 

                    if command.len() > 6 { &command[6..] } else { "" }

                                    for (i, line) in lines.iter_mut().enumerate() {                };

                                        ui.horizontal(|ui| {                self.execute_print(&mut output, print_cmd.trim());

                                            ui.label(format!("{:4}: ", i + 1));            }

                                            ui.text_edit_singleline(line);            else if cmd_upper.starts_with("LET ") {

                                        });                let args = if command.len() > 4 { &command[4..] } else { "" };

                                    }                self.execute_let(&mut output, args);

            }

                                    self.code = lines.join("\n");            else if cmd_upper.starts_with("INPUT") {

                                } else {                let args = if command.len() > 6 { &command[6..] } else { "" };

                                    // Without line numbers                self.execute_input(&mut output, args);

                                    ui.add(            }

                                        egui::TextEdit::multiline(&mut self.code)            else if cmd_upper.starts_with("IF ") {

                                            .font(egui::TextStyle::Monospace)                if let Some(then_pos) = cmd_upper.find(" THEN ") {

                                            .desired_width(f32::INFINITY)                    let condition = if command.len() > 3 && then_pos > 3 { &command[3..then_pos] } else { "" };

                                            .desired_rows(20)                    let then_part = if command.len() > then_pos + 6 { &command[then_pos + 6..] } else { "" };

                                    );                    if self.evaluate_condition(condition) {

                                }                        if let Ok(line_num) = then_part.trim().parse::<u32>() {

                            });                            // GOTO line number

                        });                            if let Some(&new_i) = line_numbers.get(&line_num) {

                    }                                i = new_i;

                    1 => {                                continue;

                        // Output & Graphics Tab                            }

                        ui.vertical(|ui| {                        } else {

                            ui.label("Output:");                            // Execute inline command

                            egui::ScrollArea::vertical()                            self.execute_basic_command(&mut output, then_part.trim());

                                .max_height(200.0)                        }

                                .show(ui, |ui| {                    }

                                    ui.add(                }

                                        egui::TextEdit::multiline(&mut self.output)            }

                                            .font(egui::TextStyle::Monospace)            else if cmd_upper.starts_with("GOTO ") {

                                            .desired_width(f32::INFINITY)                if let Ok(line_num) = command[5..].trim().parse::<u32>() {

                                    );                    if let Some(&new_i) = line_numbers.get(&line_num) {

                                });                        i = new_i;

                        continue;

                            ui.separator();                    }

                            ui.label("Turtle Graphics:");                }

                            ui.add_space(4.0);            }

            else if cmd_upper.starts_with("GOSUB ") {

                            // Simple canvas for turtle graphics                if let Ok(line_num) = command[6..].trim().parse::<u32>() {

                            let canvas_size = egui::vec2(400.0, 300.0);                    gosub_stack.push(i);

                            let (rect, _response) = ui.allocate_exact_size(canvas_size, egui::Sense::hover());                    if let Some(&new_i) = line_numbers.get(&line_num) {

                        i = new_i;

                            ui.painter().rect_filled(rect, 0.0, egui::Color32::WHITE);                        continue;

                            ui.painter().rect_stroke(rect, 0.0, egui::Stroke::new(1.0, egui::Color32::BLACK));                    }

                }

                            // Draw turtle            }

                            let center = rect.center();            else if cmd_upper == "RETURN" {

                            let turtle_x = center.x + self.turtle_state.x;                if let Some(return_i) = gosub_stack.pop() {

                            let turtle_y = center.y + self.turtle_state.y;                    i = return_i;

                    continue;

                            // Draw a simple triangle for the turtle                }

                            let size = 8.0;            }

                            let angle_rad = self.turtle_state.angle.to_radians();            else if cmd_upper.starts_with("FOR ") {

                            let points = [                let args = if command.len() > 4 { &command[4..] } else { "" };

                                egui::pos2(                self.execute_for(&mut output, args, &mut for_stack);

                                    turtle_x + size * angle_rad.cos(),            }

                                    turtle_y + size * angle_rad.sin()            else if cmd_upper == "NEXT" {

                                ),                if self.execute_next(&mut output, &mut for_stack) {

                                egui::pos2(                    // Continue with the loop

                                    turtle_x + size * (angle_rad + 2.0944).cos(),                    continue;

                                    turtle_y + size * (angle_rad + 2.0944).sin()                }

                                ),            }

                                egui::pos2(            else if cmd_upper.starts_with("WHILE ") {

                                    turtle_x + size * (angle_rad - 2.0944).cos(),                // Simple WHILE implementation

                                    turtle_y + size * (angle_rad - 2.0944).sin()                let condition = if command.len() > 6 { &command[6..] } else { "" };

                                ),                if !self.evaluate_condition(condition) {

                            ];                    // Skip to WEND

                    let mut nest_level = 1;

                            ui.painter().add(egui::Shape::convex_polygon(                    while i + 1 < lines.len() && nest_level > 0 {

                                points.to_vec(),                        i += 1;

                                self.turtle_state.color,                        let (_, next_cmd) = &lines[i];

                                egui::Stroke::new(1.0, egui::Color32::BLACK)                        if next_cmd.to_uppercase().starts_with("WHILE ") {

                            ));                            nest_level += 1;

                        });                        } else if next_cmd.to_uppercase() == "WEND" {

                    }                            nest_level -= 1;

                    _ => {}                        }

                }                    }

            });                }

        });            }

    }            else if cmd_upper == "WEND" {

}                // Find matching WHILE and check condition

                let mut while_i = i;

fn main() -> eframe::Result<()> {                let mut nest_level = 1;

    let options = eframe::NativeOptions {                while while_i > 0 && nest_level > 0 {

        viewport: egui::ViewportBuilder::default()                    while_i -= 1;

            .with_inner_size([1200.0, 800.0])                    let (_, while_cmd) = &lines[while_i];

            .with_title("Time Warp IDE"),                    if while_cmd.to_uppercase() == "WEND" {

        ..Default::default()                        nest_level += 1;

    };                    } else if while_cmd.to_uppercase().starts_with("WHILE ") {

                        nest_level -= 1;

    eframe::run_native(                    }

        "Time Warp IDE",                }

        options,                if while_i < i {

        Box::new(|_cc| Box::new(TimeWarpApp::default())),                    let (_, while_cmd) = &lines[while_i];

    )                    if while_cmd.to_uppercase().starts_with("WHILE ") {

}                        let condition = if while_cmd.len() > 6 { &while_cmd[6..] } else { "" };
                        if self.evaluate_condition(condition) {
                            i = while_i;
                            continue;
                        }
                    }
                }
            }
            else if cmd_upper.starts_with("CLS") {
                output.clear();
                output.push("Screen cleared.".to_string());
            }
            else if cmd_upper.starts_with("COLOR ") {
                let color_part = if command.len() > 6 { &command[6..] } else { "" };
                if let Ok(color) = color_part.trim().parse::<u8>() {
                    output.push(format!("Color set to {}", color));
                }
            }
            else if cmd_upper.starts_with("BEEP") {
                output.push("BEEP!".to_string());
            }
            else if cmd_upper.starts_with("SOUND ") {
                let sound_part = if command.len() > 6 { &command[6..] } else { "" };
                output.push(format!("Sound: {}", sound_part));
            }

            // PILOT Commands
            else if cmd_trim.starts_with("T:") {
                let text = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                output.push(format!("QUESTION: {}", text));
            }
            else if cmd_trim.starts_with("A:") {
                // PILOT ACCEPT command - set up interactive input like INPUT
                let prompt_text = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                let args = if prompt_text.is_empty() { "" } else { prompt_text };
                self.execute_input(&mut output, args);
            }
            else if cmd_trim.starts_with("J:") {
                let jump_target = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                if let Ok(line_num) = jump_target.parse::<u32>() {
                    if let Some(&new_i) = line_numbers.get(&line_num) {
                        i = new_i;
                        continue;
                    }
                }
            }
            else if cmd_trim.starts_with("M:") {
                let match_text = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                output.push(format!("MATCH: {}", match_text));
            }
            else if cmd_trim.starts_with("U:") {
                let use_text = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                output.push(format!("USE: {}", use_text));
            }
            else if cmd_trim.starts_with("Y:") {
                let yes_text = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                output.push(format!("YES: {}", yes_text));
            }
            else if cmd_trim.starts_with("N:") {
                let no_text = if cmd_trim.len() > 2 { &cmd_trim[2..].trim() } else { "" };
                output.push(format!("NO: {}", no_text));
            }

            // Logo Commands
            else if cmd_upper.starts_with("FORWARD ") || cmd_upper.starts_with("FD ") {
                let distance = if cmd_upper.starts_with("FORWARD ") {
                    if command.len() > 8 { &command[8..] } else { "" }
                } else {
                    if command.len() > 3 { &command[3..] } else { "" }
                };
                if let Ok(dist) = distance.trim().parse::<f32>() {
                    self.execute_turtle_command(&format!("FORWARD {}", dist));
                    output.push(format!("Turtle forward {}", dist));
                }
            }
            else if cmd_upper.starts_with("BACKWARD ") || cmd_upper.starts_with("BK ") {
                let distance = if cmd_upper.starts_with("BACKWARD ") {
                    if command.len() > 9 { &command[9..] } else { "" }
                } else {
                    if command.len() > 3 { &command[3..] } else { "" }
                };
                if let Ok(dist) = distance.trim().parse::<f32>() {
                    self.execute_turtle_command(&format!("BACKWARD {}", dist));
                    output.push(format!("Turtle backward {}", dist));
                }
            }
            else if cmd_upper.starts_with("RIGHT ") || cmd_upper.starts_with("RT ") {
                let angle = if cmd_upper.starts_with("RIGHT ") {
                    if command.len() > 6 { &command[6..] } else { "" }
                } else {
                    if command.len() > 3 { &command[3..] } else { "" }
                };
                if let Ok(ang) = angle.trim().parse::<f32>() {
                    self.execute_turtle_command(&format!("RIGHT {}", ang));
                    output.push(format!("Turtle right {}", ang));
                }
            }
            else if cmd_upper.starts_with("LEFT ") || cmd_upper.starts_with("LT ") {
                let angle = if cmd_upper.starts_with("LEFT ") {
                    if command.len() > 5 { &command[5..] } else { "" }
                } else {
                    if command.len() > 3 { &command[3..] } else { "" }
                };
                if let Ok(ang) = angle.trim().parse::<f32>() {
                    self.execute_turtle_command(&format!("LEFT {}", ang));
                    output.push(format!("Turtle left {}", ang));
                }
            }
            else if cmd_upper == "PENUP" || cmd_upper == "PU" {
                self.execute_turtle_command("PENUP");
                output.push("Pen up".to_string());
            }
            else if cmd_upper == "PENDOWN" || cmd_upper == "PD" {
                self.execute_turtle_command("PENDOWN");
                output.push("Pen down".to_string());
            }
            else if cmd_upper == "HOME" {
                self.execute_turtle_command("HOME");
                output.push("Turtle home".to_string());
            }
            else if cmd_upper == "CLEARSCREEN" || cmd_upper == "CS" {
                self.execute_turtle_command("CLEARSCREEN");
                output.push("Screen cleared".to_string());
            }
            else if cmd_upper.starts_with("SETPENCOLOR ") || cmd_upper.starts_with("SETPC ") {
                let color = if cmd_upper.starts_with("SETPENCOLOR ") {
                    if command.len() > 12 { &command[12..] } else { "" }
                } else {
                    if command.len() > 6 { &command[6..] } else { "" }
                };
                output.push(format!("Pen color set to {}", color));
            }
            else if cmd_upper.starts_with("MAKE ") {
                // Logo variable assignment
                let rest = if command.len() > 5 { &command[5..] } else { "" };
                if let Some(quote_pos) = rest.find('"') {
                    let var_name = &rest[..quote_pos].trim();
                    if let Some(end_quote) = rest[quote_pos + 1..].find('"') {
                        let value = &rest[quote_pos + 1..quote_pos + 1 + end_quote];
                        self.variables.insert(var_name.to_string(), value.to_string());
                        output.push(format!("{} = \"{}\"", var_name, value));
                    }
                }
            }
            else if cmd_upper.starts_with("REPEAT ") {
                // Simple REPEAT implementation
                if command.len() > 7 {
                    if let Some(space_pos) = command[7..].find(' ') {
                        if let Ok(count) = command[7..7 + space_pos].trim().parse::<u32>() {
                            let repeat_cmd = if command.len() > 7 + space_pos + 1 { &command[7 + space_pos + 1..] } else { "" };
                            for _ in 0..count {
                                self.execute_basic_command(&mut output, repeat_cmd.trim());
                            }
                        }
                    }
                }
            }

            // Unknown command
            else if !command.is_empty() {
                output.push(format!("Unknown command: {}", command));
            }

            i += 1;
        }

        output.join("\n")
    }

    fn execute_print(&mut self, output: &mut Vec<String>, args: &str) {
        if args.trim().is_empty() {
            output.push("".to_string());
            return;
        }

        if let Some(quote_start) = args.find('"') {
            if let Some(quote_end) = args[quote_start + 1..].find('"') {
                let text = &args[quote_start + 1..quote_start + 1 + quote_end];
                output.push(text.to_string());
                return;
            }
        }

        // Handle variable printing
        let var_name = args.trim();
        if let Some(value) = self.variables.get(var_name) {
            output.push(value.clone());
        } else {
            output.push(format!("Undefined variable: {}", var_name));
        }
    }

    fn execute_let(&mut self, output: &mut Vec<String>, args: &str) {
        if let Some(eq_pos) = args.find('=') {
            let var_part = &args[..eq_pos].trim();
            let value_part = args[eq_pos + 1..].trim();
            if let Some(var_name) = var_part.split_whitespace().last() {
                self.variables.insert(var_name.to_string(), value_part.to_string());
                output.push(format!("{} = {}", var_name, value_part));
            }
        }
    }

    fn execute_input(&mut self, output: &mut Vec<String>, args: &str) {
        // Set up interactive input
        let prompt = if args.contains('"') {
            if let Some(quote_start) = args.find('"') {
                if let Some(quote_end) = args[quote_start + 1..].find('"') {
                    args[quote_start + 1..quote_start + 1 + quote_end].to_string()
                } else {
                    "Input:".to_string()
                }
            } else {
                "Input:".to_string()
            }
        } else {
            "Input:".to_string()
        };

        // Extract variable name from INPUT command (e.g., "INPUT A" -> "A")
        let var_name = args.split_whitespace()
            .find(|&word| !word.starts_with('"') && !word.ends_with('"'))
            .unwrap_or("INPUT")
            .to_string();

        // Set the input prompt and waiting state
        self.input_prompt = prompt;
        self.current_input_var = var_name;
        self.waiting_for_input = true;

        output.push(format!("{} ", self.input_prompt));
        // Continue execution - input will be processed later
    }

    fn evaluate_condition(&self, condition: &str) -> bool {
        // Simple condition evaluation
        if condition.contains("= ") {
            let parts: Vec<&str> = condition.split("= ").collect();
            if parts.len() == 2 {
                let left = parts[0].trim();
                let right = parts[1].trim();

                if let Some(left_val) = self.variables.get(left) {
                    return left_val == right;
                }
            }
        }
        // Default to true for simple conditions
        true
    }

    fn execute_basic_command(&mut self, output: &mut Vec<String>, command: &str) {
        let cmd_upper = command.to_uppercase();
        if cmd_upper.starts_with("PRINT") {
            self.execute_print(output, &command[6..]);
        } else if cmd_upper.starts_with("LET ") {
            self.execute_let(output, &command[4..]);
        }
        // Add other commands as needed
    }

    fn execute_for(&mut self, output: &mut Vec<String>, args: &str, for_stack: &mut Vec<(String, f32, f32, f32)>) {
        // Simple FOR loop implementation: FOR I = 1 TO 10
        let parts: Vec<&str> = args.split_whitespace().collect();
        if parts.len() >= 5 && parts[1] == "=" && parts[3] == "TO" {
            let var_name = parts[0];
            if let (Ok(start), Ok(end)) = (parts[2].parse::<f32>(), parts[4].parse::<f32>()) {
                self.variables.insert(var_name.to_string(), start.to_string());
                for_stack.push((var_name.to_string(), start, end, 1.0)); // step = 1
                output.push(format!("FOR {} = {} TO {}", var_name, start, end));
            }
        }
    }

    fn execute_next(&mut self, output: &mut Vec<String>, for_stack: &mut Vec<(String, f32, f32, f32)>) -> bool {
        if let Some((var_name, current, end, step)) = for_stack.last().cloned() {
            let new_current = current + step;
            if new_current <= end {
                // Update the last element
                if let Some(last) = for_stack.last_mut() {
                    last.1 = new_current;
                    self.variables.insert(var_name.clone(), new_current.to_string());
                    output.push(format!("NEXT {} = {}", var_name, new_current));
                    return true; // Continue loop
                }
            } else {
                // End of loop - remove it
                for_stack.pop();
                output.push(format!("END FOR {}", var_name));
            }
        }
        false
    }

    fn execute_tw_pascal(&mut self, code: &str) -> String {
        let mut output = Vec::new();

        for line in code.lines() {
            let line = line.trim();
            if line.is_empty() || line.to_lowercase().starts_with("(*") || line.starts_with("{") {
                continue;
            }

            let line_lower = line.to_lowercase();

            // Turbo Pascal I/O
            if line_lower.starts_with("writeln(") {
                if let Some(quote_start) = line.find('\'') {
                    if let Some(quote_end) = line[quote_start + 1..].find('\'') {
                        let text = &line[quote_start + 1..quote_start + 1 + quote_end];
                        output.push(text.to_string());
                    }
                } else if line.contains(");") {
                    // Handle variable output
                    if line.len() > 10 { // "writeln(" + ");" = 10 chars
                        let var_part = &line[8..line.len() - 2]; // Remove "writeln(" and ");"
                        if let Some(value) = self.variables.get(var_part.trim()) {
                            output.push(value.clone());
                        } else {
                            output.push(format!("Undefined variable: {}", var_part.trim()));
                        }
                    }
                }
            }
            else if line_lower.starts_with("write(") {
                if let Some(quote_start) = line.find('\'') {
                    if let Some(quote_end) = line[quote_start + 1..].find('\'') {
                        let text = &line[quote_start + 1..quote_start + 1 + quote_end];
                        output.push(text.to_string());
                    }
                }
            }
            else if line_lower.starts_with("readln(") {
                if line.len() > 8 { // "readln(" + ")" = 8 chars
                    let var_part = &line[7..line.len() - 1]; // Remove "readln(" and ")"
                    // Set up interactive input for Pascal readln
                    self.input_prompt = format!("Enter value for {}:", var_part.trim());
                    self.current_input_var = var_part.trim().to_string();
                    self.waiting_for_input = true;
                    output.push(format!("{} ", self.input_prompt));
                    // Continue execution - input will be processed later
                }
            }

            // Turbo Pascal control structures
            else if line_lower.starts_with("if ") {
                output.push(format!("IF statement: {}", line));
            }
            else if line_lower.starts_with("for ") {
                output.push(format!("FOR loop: {}", line));
            }
            else if line_lower.starts_with("while ") {
                output.push(format!("WHILE loop: {}", line));
            }
            else if line_lower.starts_with("repeat") {
                output.push("REPEAT loop started".to_string());
            }
            else if line_lower == "until" {
                output.push("REPEAT loop ended".to_string());
            }
            else if line_lower.starts_with("case ") {
                output.push(format!("CASE statement: {}", line));
            }

            // Turbo Pascal procedures and functions
            else if line_lower.starts_with("procedure ") {
                if let Some(paren_pos) = line.find('(') {
                    if line.len() > 10 && paren_pos > 10 {
                        let proc_name = &line[10..paren_pos].trim();
                        output.push(format!("Procedure defined: {}", proc_name));
                    }
                } else {
                    if line.len() > 10 {
                        let proc_name = &line[10..].trim();
                        output.push(format!("Procedure defined: {}", proc_name));
                    }
                }
            }
            else if line_lower.starts_with("function ") {
                if let Some(paren_pos) = line.find('(') {
                    if line.len() > 9 && paren_pos > 9 {
                        let func_name = &line[9..paren_pos].trim();
                        output.push(format!("Function defined: {}", func_name));
                    }
                }
            }

            // Turbo Pascal variable declarations
            else if line_lower.starts_with("var ") {
                let var_part = if line.len() > 4 { &line[4..] } else { "" };
                output.push(format!("Variable declaration: {}", var_part));
            }
            else if line_lower.starts_with("const ") {
                let const_part = if line.len() > 6 { &line[6..] } else { "" };
                output.push(format!("Constant declaration: {}", const_part));
            }
            else if line_lower.starts_with("type ") {
                let type_part = if line.len() > 5 { &line[5..] } else { "" };
                output.push(format!("Type declaration: {}", type_part));
            }

            // Turbo Pascal program structure
            else if line_lower.starts_with("program ") {
                if let Some(semi_pos) = line.find(';') {
                    if line.len() > 8 && semi_pos > 8 {
                        let prog_name = &line[8..semi_pos].trim();
                        output.push(format!("Program: {}", prog_name));
                    }
                }
            }
            else if line_lower.starts_with("begin") {
                output.push("Block begin".to_string());
            }
            else if line_lower == "end." || line_lower == "end;" {
                output.push("Block/Program end".to_string());
            }

            // Turbo Pascal built-in functions
            else if line_lower.contains("length(") {
                output.push("String length function called".to_string());
            }
            else if line_lower.contains("pos(") {
                output.push("String position function called".to_string());
            }
            else if line_lower.contains("copy(") {
                output.push("String copy function called".to_string());
            }
            else if line_lower.contains("sqrt(") {
                output.push("Square root function called".to_string());
            }
            else if line_lower.contains("sin(") || line_lower.contains("cos(") || line_lower.contains("arctan(") {
                output.push("Trigonometric function called".to_string());
            }

            // Assignment
            else if line.contains(":=") {
                let parts: Vec<&str> = line.split(":=").collect();
                if parts.len() == 2 {
                    let var_name = parts[0].trim();
                    let value = parts[1].trim().trim_end_matches(';');
                    self.variables.insert(var_name.to_string(), value.to_string());
                    output.push(format!("{} := {}", var_name, value));
                }
            }

            // Unknown Pascal code
            else if !line.is_empty() && !line.ends_with(';') && !line.ends_with('.') {
                output.push(format!("Pascal statement: {}", line));
            }
        }

        output.join("\n")
    }

    fn execute_tw_prolog(&mut self, code: &str) -> String {
        let mut output = Vec::new();
        let mut predicates = std::collections::HashMap::new();

        for line in code.lines() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('%') || line.starts_with("/*") {
                continue;
            }

            // Turbo Prolog domains (type declarations)
            if line.to_lowercase().starts_with("domains") {
                output.push("DOMAINS section:".to_string());
            }
            else if line.to_lowercase().starts_with("predicates") {
                output.push("PREDICATES section:".to_string());
            }
            else if line.to_lowercase().starts_with("goal") {
                output.push("GOAL section:".to_string());
            }
            else if line.to_lowercase().starts_with("clauses") {
                output.push("CLAUSES section:".to_string());
            }

            // Turbo Prolog domain declarations
            else if line.contains("=") && !line.contains(":-") && !line.contains("(") {
                output.push(format!("Domain: {}", line));
            }

            // Turbo Prolog predicate declarations
            else if line.contains("(") && line.contains(")") && !line.contains(":-") && !line.contains(".") {
                let pred_name = if let Some(paren_pos) = line.find('(') {
                    &line[..paren_pos].trim()
                } else {
                    line
                };
                output.push(format!("Predicate declared: {}", pred_name));
                predicates.insert(pred_name.to_string(), Vec::new());
            }

            // Turbo Prolog facts and rules
            else if line.contains(":-") {
                let parts: Vec<&str> = line.split(":-").collect();
                if parts.len() == 2 {
                    let head = parts[0].trim();
                    let body = parts[1].trim().trim_end_matches('.');
                    output.push(format!("Rule: {} :- {}", head, body));

                    // Store the rule
                    if let Some(pred_name) = head.split('(').next() {
                        if let Some(rules) = predicates.get_mut(pred_name.trim()) {
                            rules.push(format!("{} :- {}", head, body));
                        }
                    }
                }
            }
            else if line.ends_with('.') && line.contains('(') {
                let fact = line.trim_end_matches('.');
                output.push(format!("Fact: {}", fact));

                // Store the fact
                if let Some(pred_name) = fact.split('(').next() {
                    if let Some(facts) = predicates.get_mut(pred_name.trim()) {
                        facts.push(fact.to_string());
                    }
                }
            }

            // Turbo Prolog queries/goals
            else if line.ends_with('.') && !line.contains('(') && !line.contains(":-") {
                let query = line.trim_end_matches('.');
                output.push(format!("Query: {}", query));

                // Simple query resolution simulation
                if let Some(pred_name) = query.split('(').next() {
                    if let Some(rules_facts) = predicates.get(pred_name.trim()) {
                        if !rules_facts.is_empty() {
                            output.push(format!("  Found {} clause(s) for {}", rules_facts.len(), pred_name));
                            for clause in rules_facts {
                                output.push(format!("    {}", clause));
                            }
                        } else {
                            output.push(format!("  No clauses found for {}", pred_name));
                        }
                    } else {
                        output.push(format!("  Unknown predicate: {}", pred_name));
                    }
                }
            }

            // Turbo Prolog built-in predicates
            else if line.to_lowercase().contains("write(") {
                let content = if let Some(start) = line.find('"') {
                    if let Some(end) = line[start + 1..].find('"') {
                        &line[start + 1..start + 1 + end]
                    } else {
                        "unknown"
                    }
                } else {
                    "variable"
                };
                output.push(format!("WRITE: {}", content));
            }
            else if line.to_lowercase().contains("nl") {
                output.push("NEWLINE".to_string());
            }
            else if line.to_lowercase().contains("readln(") {
                // Set up interactive input for Prolog readln
                self.input_prompt = "Enter value for readln:".to_string();
                self.current_input_var = "READLN".to_string(); // Generic variable for Prolog
                self.waiting_for_input = true;
                output.push(format!("{} ", self.input_prompt));
                // Continue execution - input will be processed later
            }

            // Turbo Prolog arithmetic and comparison
            else if line.contains("+") || line.contains("-") || line.contains("*") || line.contains("/") {
                output.push(format!("Arithmetic expression: {}", line));
            }
            else if line.contains("=") || line.contains(">") || line.contains("<") {
                output.push(format!("Comparison: {}", line));
            }

            // Unknown Prolog code
            else if !line.is_empty() && !line.ends_with('.') {
                output.push(format!("Prolog statement: {}", line));
            }
        }

        output.join("\n")
    }

    fn find_and_replace(&mut self) {
        if !self.find_text.is_empty() {
            self.code = self.code.replace(&self.find_text, &self.replace_text);
            self.output = format!("Replaced '{}' with '{}'", self.find_text, self.replace_text);
        }
    }

    fn check_syntax(&mut self) -> String {
        match self.language.as_str() {
            "TW BASIC" => self.check_basic_syntax(&self.code),
            "TW Pascal" => self.check_pascal_syntax(&self.code),
            "TW Prolog" => self.check_prolog_syntax(&self.code),
            _ => format!("Syntax checking not implemented for {}", self.language),
        }
    }

    fn check_basic_syntax(&self, code: &str) -> String {
        let mut errors = Vec::new();

        for (line_num, line) in code.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            // Check for line numbers in BASIC
            if !line.chars().next().unwrap_or(' ').is_ascii_digit() && !line.to_uppercase().starts_with("REM") {
                errors.push(format!("Line {}: BASIC programs should start with line numbers", line_num + 1));
            }

            // Check PRINT statements
            if line.to_uppercase().contains("PRINT") && !line.contains("\"") && !line.chars().all(|c| c.is_alphanumeric() || c.is_whitespace() || c == '=' || c == '"') {
                errors.push(format!("Line {}: PRINT statement syntax error", line_num + 1));
            }
        }

        if errors.is_empty() {
            "Syntax check passed!".to_string()
        } else {
            format!("Syntax errors found:\n{}", errors.join("\n"))
        }
    }

    fn check_pascal_syntax(&self, code: &str) -> String {
        let mut errors = Vec::new();

        for (line_num, line) in code.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            if line.to_lowercase().starts_with("writeln") {
                if !line.contains("(") || !line.contains(")") {
                    errors.push(format!("Line {}: writeln statement missing parentheses", line_num + 1));
                }
            }
        }

        if errors.is_empty() {
            "Syntax check passed!".to_string()
        } else {
            format!("Syntax errors found:\n{}", errors.join("\n"))
        }
    }

    fn check_prolog_syntax(&self, code: &str) -> String {
        let mut errors = Vec::new();

        for (line_num, line) in code.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('%') {
                continue;
            }

            // Check for proper Prolog syntax
            if line.contains(":-") {
                // Rule syntax
                if !line.ends_with('.') {
                    errors.push(format!("Line {}: Rule must end with a period", line_num + 1));
                }
            } else if line.ends_with('.') && line.contains('(') {
                // Fact syntax - should be fine
            } else if line.ends_with('.') && !line.contains('(') && !line.contains(":-") {
                // Query syntax - should be fine
            } else if !line.ends_with('.') && !line.to_lowercase().starts_with("domains") &&
                      !line.to_lowercase().starts_with("predicates") &&
                      !line.to_lowercase().starts_with("goal") &&
                      !line.to_lowercase().starts_with("clauses") {
                errors.push(format!("Line {}: Prolog statements should end with a period", line_num + 1));
            }
        }

        if errors.is_empty() {
            "Syntax check passed!".to_string()
        } else {
            format!("Syntax errors found:\n{}", errors.join("\n"))
        }
    }

    fn execute_turtle_command(&mut self, command: &str) {
        let cmd = command.to_uppercase();
        if cmd.starts_with("FORWARD") || cmd.starts_with("FD") {
            if let Some(distance_str) = cmd.split_whitespace().nth(1) {
                if let Ok(distance) = distance_str.parse::<f32>() {
                    let rad_angle = self.turtle_state.angle.to_radians();
                    let new_x = self.turtle_state.x + distance * rad_angle.cos();
                    let new_y = self.turtle_state.y + distance * rad_angle.sin();

                    if self.turtle_state.pen_down {
                        self.turtle_commands.push(format!("line {} {} {} {}", self.turtle_state.x, self.turtle_state.y, new_x, new_y));
                    }

                    self.turtle_state.x = new_x;
                    self.turtle_state.y = new_y;

                    self.output.push_str(&format!("Turtle: forward {}\n", distance));
                }
            }
        } else if cmd.starts_with("RIGHT") || cmd.starts_with("RT") {
            if let Some(angle_str) = cmd.split_whitespace().nth(1) {
                if let Ok(angle) = angle_str.parse::<f32>() {
                    self.turtle_state.angle += angle;
                    self.output.push_str(&format!("Turtle: right {}\n", angle));
                }
            }
        } else if cmd.starts_with("LEFT") || cmd.starts_with("LT") {
            if let Some(angle_str) = cmd.split_whitespace().nth(1) {
                if let Ok(angle) = angle_str.parse::<f32>() {
                    self.turtle_state.angle -= angle;
                    self.output.push_str(&format!("Turtle: left {}\n", angle));
                }
            }
        } else if cmd == "PENUP" || cmd == "PU" {
            self.turtle_state.pen_down = false;
            self.output.push_str("Turtle: pen up\n");
        } else if cmd == "PENDOWN" || cmd == "PD" {
            self.turtle_state.pen_down = true;
            self.output.push_str("Turtle: pen down\n");
        } else if cmd.starts_with("HOME") {
            self.turtle_state.x = 200.0;
            self.turtle_state.y = 200.0;
            self.turtle_state.angle = 0.0;
            self.output.push_str("Turtle: home\n");
        } else if cmd.starts_with("CLEARSCREEN") || cmd == "CS" {
            self.turtle_commands.clear();
            self.turtle_state.x = 200.0;
            self.turtle_state.y = 200.0;
            self.turtle_state.angle = 0.0;
            self.output.push_str("Turtle: clear screen\n");
        }
    }

    fn clear_turtle_graphics(&mut self) {
        self.turtle_commands.clear();
        self.turtle_state = TurtleState {
            x: 200.0,
            y: 200.0,
            angle: 0.0,
            pen_down: true,
            color: egui::Color32::BLACK,
        };
        self.output = "Turtle graphics cleared.".to_string();
    }

    fn stop_execution(&mut self) {
        if self.is_executing {
            self.is_executing = false;
            self.output = "Program execution stopped by user.".to_string();
        }
    }

    fn process_user_input(&mut self) {
        // Store the input in the appropriate variable based on context
        if !self.user_input.is_empty() {
            // Add the input to output for confirmation
            self.output.push_str(&format!("\n> {}", self.user_input));

            // Store in the variable that was waiting for input
            if !self.current_input_var.is_empty() {
                self.variables.insert(self.current_input_var.clone(), self.user_input.clone());
                self.output.push_str(&format!("\nStored in variable: {}", self.current_input_var));
            } else {
                // Fallback for cases where variable name wasn't captured
                self.variables.insert("INPUT".to_string(), self.user_input.clone());
            }

            // Reset input state
            self.waiting_for_input = false;
            self.input_prompt.clear();
            self.user_input.clear();
            self.current_input_var.clear();

            // Re-run execution with input value available
            self.execute_code();
        }
    }
}

impl eframe::App for TimeWarpApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Track code changes for Undo/Redo
        if self.code_history.is_empty() || self.code != self.code_history[self.code_history_index] {
            if self.code_history_index + 1 < self.code_history.len() {
                self.code_history.truncate(self.code_history_index + 1);
            }
            self.code_history.push(self.code.clone());
            self.code_history_index = self.code_history.len() - 1;
        }
        // Light theme for a more educational/clean look
        ctx.set_visuals(egui::Visuals::light());

        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                // === FILE MENU ===
                ui.menu_button("📁 File", |ui| {
                    if ui.button("📄 New File").clicked() {
                        self.code.clear();
                        self.output = "New file created.".to_string();
                        self.code_history = vec![String::new()];
                        self.code_history_index = 0;
                        self.last_file_path = None;
                        ui.close_menu();
                    }
                    if ui.button("📂 Open File...").clicked() {
                        if let Some(path) = FileDialog::new().add_filter("Text", &["txt", "tw", "bas", "logo", "pas", "plg"]).pick_file() {
                            if let Ok(content) = std::fs::read_to_string(&path) {
                                self.code = content;
                                self.output = format!("Opened file: {}", path.display());
                                self.code_history = vec![self.code.clone()];
                                self.code_history_index = 0;
                                self.last_file_path = Some(path.display().to_string());
                            } else {
                                self.output = format!("Failed to open file: {}", path.display());
                            }
                        }
                        ui.close_menu();
                    }
                    if ui.button("💾 Save").clicked() {
                        let mut saved = false;
                        if let Some(path) = &self.last_file_path {
                            if std::fs::write(path, &self.code).is_ok() {
                                self.output = format!("Saved to {}", path);
                                saved = true;
                            }
                        }
                        if !saved {
                            if let Some(path) = FileDialog::new().set_file_name("untitled.tw").save_file() {
                                if std::fs::write(&path, &self.code).is_ok() {
                                    self.output = format!("Saved to {}", path.display());
                                    self.last_file_path = Some(path.display().to_string());
                                } else {
                                    self.output = format!("Failed to save file: {}", path.display());
                                }
                            }
                        }
                        ui.close_menu();
                    }
                    if ui.button("💾 Save As...").clicked() {
                        if let Some(path) = FileDialog::new().set_file_name("untitled.tw").save_file() {
                            if std::fs::write(&path, &self.code).is_ok() {
                                self.output = format!("Saved to {}", path.display());
                                self.last_file_path = Some(path.display().to_string());
                            } else {
                                self.output = format!("Failed to save file: {}", path.display());
                            }
                        }
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("🚪 Exit").clicked() {
                        std::process::exit(0);
                    }
                });
                // === EDIT MENU ===
                ui.menu_button("✏️ Edit", |ui| {
                    if ui.button("↩️ Undo").clicked() {
                        if self.code_history_index > 0 {
                            self.code_history_index -= 1;
                            self.code = self.code_history[self.code_history_index].clone();
                            self.output = "Undo".to_string();
                        }
                        ui.close_menu();
                    }
                    if ui.button("↪️ Redo").clicked() {
                        if self.code_history_index + 1 < self.code_history.len() {
                            self.code_history_index += 1;
                            self.code = self.code_history[self.code_history_index].clone();
                            self.output = "Redo".to_string();
                        }
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("✂️ Cut").clicked() {
                        ctx.output_mut(|o| o.copied_text = self.code.clone());
                        self.code.clear();
                        self.output = "Cut".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📋 Copy").clicked() {
                        ctx.output_mut(|o| o.copied_text = self.code.clone());
                        self.output = "Copy".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📄 Paste").clicked() {
                        // Note: Clipboard access requires platform-specific implementation
                        // For now, this is a placeholder
                        self.output = "Paste not implemented in this version".to_string();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("🔍 Find/Replace...").clicked() {
                        self.show_find_replace = true;
                        ui.close_menu();
                    }
                    if ui.button("🔍 Find Next").clicked() {
                        self.output = "Find Next not implemented.".to_string();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("💬 Toggle Comment").clicked() {
                        // Simple toggle: add/remove // at line start
                        let mut new_code = String::new();
                        for line in self.code.lines() {
                            if line.trim_start().starts_with("//") {
                                new_code.push_str(line.trim_start_matches("//"));
                            } else {
                                new_code.push_str(&format!("//{}", line));
                            }
                            new_code.push('\n');
                        }
                        self.code = new_code;
                        self.output = "Toggle Comment".to_string();
                        ui.close_menu();
                    }
                    if ui.button("⬅️ Decrease Indent").clicked() {
                        let mut new_code = String::new();
                        for line in self.code.lines() {
                            if line.starts_with("    ") {
                                new_code.push_str(&line[4..]);
                            } else {
                                new_code.push_str(line);
                            }
                            new_code.push('\n');
                        }
                        self.code = new_code;
                        self.output = "Decrease Indent".to_string();
                        ui.close_menu();
                    }
                    if ui.button("➡️ Increase Indent").clicked() {
                        let mut new_code = String::new();
                        for line in self.code.lines() {
                            new_code.push_str("    ");
                            new_code.push_str(line);
                            new_code.push('\n');
                        }
                        self.code = new_code;
                        self.output = "Increase Indent".to_string();
                        ui.close_menu();
                    }
                });
                // === VIEW MENU ===
                ui.menu_button("👁️ View", |ui| {
                    if ui.button("🔢 Toggle Line Numbers").clicked() {
                        self.show_line_numbers = !self.show_line_numbers;
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("🧹 Clear All").clicked() {
                        self.code.clear();
                        self.output.clear();
                        self.code_history = vec![String::new()];
                        self.code_history_index = 0;
                        ui.close_menu();
                    }
                    if ui.button("📝 Clear Code Editor").clicked() {
                        self.code.clear();
                        self.code_history = vec![String::new()];
                        self.code_history_index = 0;
                        ui.close_menu();
                    }
                    if ui.button("📊 Clear Output").clicked() {
                        self.output.clear();
                        ui.close_menu();
                    }
                });
                // === RUN MENU ===
                ui.menu_button("▶️ Run", |ui| {
                    if ui.button("🚀 Run Program").clicked() {
                        self.execute_code();
                        ui.close_menu();
                    }
                    if ui.button("🛑 Stop Program").clicked() {
                        self.stop_execution();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("🧪 Run Tests").clicked() {
                        self.output = "Run Tests not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📝 Check Syntax").clicked() {
                        self.output = self.check_syntax();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("🔄 Restart Interpreter").clicked() {
                        self.output = "Restart Interpreter not implemented.".to_string();
                        ui.close_menu();
                    }
                });
                // === LANGUAGE MENU ===
                ui.menu_button("💻 Language", |ui| {
                    for lang in ["TW BASIC", "TW Pascal", "TW Prolog", "Auto-Detect"] {
                        if ui.button(lang).clicked() {
                            self.language = lang.to_string();
                            self.output = format!("Language set to {}", lang);
                            ui.close_menu();
                        }
                    }
                });
                // === TOOLS MENU ===
                ui.menu_button("🛠️ Tools", |ui| {
                    if ui.button("🎨 Theme Selector...").clicked() {
                        self.output = "Theme Selector not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("🔤 Font Settings...").clicked() {
                        self.output = "Font Settings not implemented.".to_string();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("📦 Plugin Manager").clicked() {
                        self.output = "Plugin Manager not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("⚙️ Settings...").clicked() {
                        self.output = "Settings not implemented.".to_string();
                        ui.close_menu();
                    }
                    ui.separator();
                    if ui.button("📊 System Info").clicked() {
                        self.output = "System Info not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("🧪 Test Suite").clicked() {
                        self.output = "Test Suite not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📋 Generate Report").clicked() {
                        self.output = "Generate Report not implemented.".to_string();
                        ui.close_menu();
                    }
                });
                // === HELP MENU ===
                ui.menu_button("❓ Help", |ui| {
                    if ui.button("ℹ️ About Time_Warp IDE").clicked() {
                        self.output = "Time_Warp IDE v1.3.0\nEducational programming environment supporting multiple languages.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("📚 Documentation").clicked() {
                        self.output = "Documentation not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("🌐 Online Resources").clicked() {
                        self.output = "Online Resources not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("🆘 Report Issue").clicked() {
                        self.output = "Report Issue not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("💡 Feature Request").clicked() {
                        self.output = "Feature Request not implemented.".to_string();
                        ui.close_menu();
                    }
                    if ui.button("🔄 Check for Updates").clicked() {
                        self.output = "Check for Updates not implemented.".to_string();
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
                ui.set_min_height(500.0);

                // Tab buttons
                ui.horizontal(|ui| {
                    if ui.selectable_label(self.active_tab == 0, "📝 Code Editor").clicked() {
                        self.active_tab = 0;
                    }
                    if ui.selectable_label(self.active_tab == 1, "🖥️ Output & Graphics").clicked() {
                        self.active_tab = 1;
                    }
                });

                ui.separator();

                // Tab content
                match self.active_tab {
                    0 => { // Code Editor Tab
                        ui.heading("Code Editor");
                        ui.add_space(4.0);
                        ui.label(format!("Editing in {} mode", self.language));
                        ui.add_space(4.0);

                        // Show Find/Replace dialog if enabled
                        if self.show_find_replace {
                            egui::Window::new("Find/Replace")
                                .collapsible(false)
                                .resizable(false)
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
                                        if ui.button("Replace All").clicked() {
                                            self.find_and_replace();
                                            self.show_find_replace = false;
                                        }
                                        if ui.button("Cancel").clicked() {
                                            self.show_find_replace = false;
                                        }
                                    });
                                });
                        }

                        // Code editor with optional line numbers
                        if self.show_line_numbers {
                            let lines: Vec<&str> = self.code.lines().collect();

                            egui::ScrollArea::vertical().show(ui, |ui| {
                                for (i, line) in lines.iter().enumerate() {
                                    ui.horizontal(|ui| {
                                        ui.label(format!("{:4}: ", i + 1));
                                        ui.label(*line);
                                    });
                                }
                            });

                            // Separate editor for modifications when line numbers are shown
                            ui.separator();
                            ui.label("Edit below:");
                            if ui.text_edit_multiline(&mut self.code).changed() {
                                // Code was edited, could refresh line numbers display
                            }
                        } else {
                            ui.text_edit_multiline(&mut self.code);
                        }
                    }
                    1 => { // Output & Graphics Tab - Combined Interactive Canvas
                        ui.heading("Interactive Output & Graphics Console");
                        ui.add_space(4.0);

                        // Create a single large canvas for both text output and turtle graphics
                        let canvas_size = egui::Vec2::new(ui.available_width(), 600.0);
                        let (response, painter) = ui.allocate_painter(canvas_size, egui::Sense::click_and_drag().union(egui::Sense::focusable_noninteractive()));

                        let rect = response.rect;

                        // Handle focus for input
                        if self.waiting_for_input {
                            response.request_focus();
                        }

                        // Split canvas: top half for text output, bottom half for turtle graphics
                        let text_area_height = 250.0;
                        let graphics_area_height = rect.height() - text_area_height - 10.0; // 10px gap

                        let text_rect = egui::Rect::from_min_size(
                            rect.min,
                            egui::Vec2::new(rect.width(), text_area_height)
                        );

                        let graphics_rect = egui::Rect::from_min_size(
                            egui::Pos2::new(rect.min.x, rect.min.y + text_area_height + 10.0),
                            egui::Vec2::new(rect.width(), graphics_area_height)
                        );

                        // === TEXT OUTPUT AREA ===
                        // Draw text area background
                        let text_bg_color = if response.has_focus() && self.waiting_for_input {
                            egui::Color32::from_rgb(30, 30, 45)
                        } else {
                            egui::Color32::from_rgb(20, 20, 30)
                        };
                        painter.rect_filled(text_rect, 4.0, text_bg_color);

                        // Draw text area border
                        let text_border_color = if response.has_focus() && self.waiting_for_input {
                            egui::Color32::from_rgb(150, 150, 180)
                        } else {
                            egui::Color32::from_rgb(100, 100, 120)
                        };
                        painter.rect_stroke(text_rect, 4.0, egui::Stroke::new(2.0, text_border_color));

                        // Prepare text layout
                        let font_id = egui::FontId::monospace(14.0);
                        let text_color = egui::Color32::from_rgb(200, 200, 220);

                        // Split output into lines and handle scrolling
                        let lines: Vec<&str> = self.output.lines().collect();
                        let line_height = 18.0;
                        let max_visible_lines = ((text_rect.height() - 80.0) / line_height) as usize; // Leave space for input area
                        let total_lines = lines.len();

                        // Update scroll position based on content changes
                        if total_lines > max_visible_lines {
                            if self.output_scroll >= total_lines.saturating_sub(max_visible_lines) {
                                self.output_scroll = total_lines.saturating_sub(max_visible_lines);
                            }
                        } else {
                            self.output_scroll = 0;
                        }

                        // Handle scrolling with mouse wheel (only in text area)
                        let scroll_delta = ui.input(|i| i.scroll_delta.y);
                        if scroll_delta > 0.0 && self.output_scroll > 0 {
                            self.output_scroll = self.output_scroll.saturating_sub(1);
                        } else if scroll_delta < 0.0 && self.output_scroll < total_lines.saturating_sub(max_visible_lines) {
                            self.output_scroll += 1;
                        }

                        // Draw visible lines in text area
                        let mut y_pos = text_rect.min.y + 10.0;
                        for (i, line) in lines.iter().enumerate() {
                            if i >= self.output_scroll && i < self.output_scroll + max_visible_lines {
                                let text_pos = egui::Pos2::new(text_rect.min.x + 10.0, y_pos);
                                painter.text(text_pos, egui::Align2::LEFT_TOP, *line, font_id.clone(), text_color);
                                y_pos += line_height;
                            }
                        }

                        // Handle input mode in text area
                        if self.waiting_for_input {
                            // Draw input prompt and cursor
                            let prompt_text = format!("{} {}", self.input_prompt, self.user_input);
                            let prompt_pos = egui::Pos2::new(text_rect.min.x + 10.0, text_rect.max.y - 30.0);
                            painter.text(prompt_pos, egui::Align2::LEFT_TOP, &prompt_text, font_id.clone(), egui::Color32::YELLOW);

                            // Draw blinking cursor
                            let cursor_x = text_rect.min.x + 10.0 + painter.layout(prompt_text, font_id.clone(), text_color, f32::INFINITY).size().x;
                            let cursor_y = text_rect.max.y - 30.0;
                            let time = ui.input(|i| i.time);
                            let cursor_visible = (time * 2.0).sin() > 0.0;
                            if cursor_visible {
                                painter.line_segment(
                                    [egui::Pos2::new(cursor_x, cursor_y), egui::Pos2::new(cursor_x, cursor_y + 14.0)],
                                    egui::Stroke::new(2.0, egui::Color32::WHITE),
                                );
                            }

                            // Handle keyboard input only when canvas has focus
                            if response.has_focus() {
                                ui.input(|i| {
                                    for event in &i.events {
                                        match event {
                                            egui::Event::Text(text) => {
                                                self.user_input.push_str(text);
                                            }
                                            egui::Event::Key { key, pressed: true, modifiers: _, repeat: _ } => {
                                                match key {
                                                    egui::Key::Enter => {
                                                        self.process_user_input();
                                                    }
                                                    egui::Key::Backspace => {
                                                        self.user_input.pop();
                                                    }
                                                    egui::Key::Escape => {
                                                        self.waiting_for_input = false;
                                                        self.input_prompt.clear();
                                                        self.user_input.clear();
                                                        self.current_input_var.clear();
                                                    }
                                                    _ => {}
                                                }
                                            }
                                            _ => {}
                                        }
                                    }
                                });
                            }

                            // Instructions
                            let instr_pos = egui::Pos2::new(text_rect.min.x + 10.0, text_rect.max.y - 50.0);
                            painter.text(instr_pos, egui::Align2::LEFT_TOP, "Click text area and type your input, press Enter to submit, Esc to cancel", egui::FontId::default(), egui::Color32::GRAY);
                        } else {
                            // Show ready message
                            let ready_pos = egui::Pos2::new(text_rect.min.x + 10.0, text_rect.max.y - 30.0);
                            painter.text(ready_pos, egui::Align2::LEFT_TOP, "Ready for program execution... Click text area to focus for input when prompted", egui::FontId::default(), egui::Color32::GRAY);
                        }

                        // === TURTLE GRAPHICS AREA ===
                        // Draw graphics area background
                        painter.rect_filled(graphics_rect, 4.0, egui::Color32::WHITE);

                        // Draw graphics area border
                        painter.rect_stroke(graphics_rect, 4.0, egui::Stroke::new(2.0, egui::Color32::from_rgb(100, 100, 120)));

                        // Draw grid lines
                        let grid_spacing = 20.0;
                        let mut x = graphics_rect.min.x;
                        while x <= graphics_rect.max.x {
                            painter.line_segment(
                                [egui::Pos2::new(x, graphics_rect.min.y), egui::Pos2::new(x, graphics_rect.max.y)],
                                egui::Stroke::new(1.0, egui::Color32::LIGHT_GRAY),
                            );
                            x += grid_spacing;
                        }
                        let mut y = graphics_rect.min.y;
                        while y <= graphics_rect.max.y {
                            painter.line_segment(
                                [egui::Pos2::new(graphics_rect.min.x, y), egui::Pos2::new(graphics_rect.max.x, y)],
                                egui::Stroke::new(1.0, egui::Color32::LIGHT_GRAY),
                            );
                            y += grid_spacing;
                        }

                        // Draw turtle commands (lines)
                        for command in &self.turtle_commands {
                            if command.starts_with("line ") {
                                let parts: Vec<&str> = command.split_whitespace().collect();
                                if parts.len() >= 5 {
                                    if let (Ok(x1), Ok(y1), Ok(x2), Ok(y2)) = (
                                        parts[1].parse::<f32>(),
                                        parts[2].parse::<f32>(),
                                        parts[3].parse::<f32>(),
                                        parts[4].parse::<f32>(),
                                    ) {
                                        let start_pos = egui::Pos2::new(graphics_rect.min.x + x1, graphics_rect.min.y + y1);
                                        let end_pos = egui::Pos2::new(graphics_rect.min.x + x2, graphics_rect.min.y + y2);
                                        painter.line_segment(
                                            [start_pos, end_pos],
                                            egui::Stroke::new(2.0, self.turtle_state.color),
                                        );
                                    }
                                }
                            }
                        }

                        // Draw turtle (small triangle)
                        let turtle_size = 8.0;
                        let turtle_x = graphics_rect.min.x + self.turtle_state.x;
                        let turtle_y = graphics_rect.min.y + self.turtle_state.y;
                        let angle_rad = self.turtle_state.angle.to_radians();

                        let points = [
                            egui::Pos2::new(
                                turtle_x + turtle_size * angle_rad.cos(),
                                turtle_y + turtle_size * angle_rad.sin(),
                            ),
                            egui::Pos2::new(
                                turtle_x + turtle_size * 0.5 * (angle_rad + std::f32::consts::PI * 2.0 / 3.0).cos(),
                                turtle_y + turtle_size * 0.5 * (angle_rad + std::f32::consts::PI * 2.0 / 3.0).sin(),
                            ),
                            egui::Pos2::new(
                                turtle_x + turtle_size * 0.5 * (angle_rad - std::f32::consts::PI * 2.0 / 3.0).cos(),
                                turtle_y + turtle_size * 0.5 * (angle_rad - std::f32::consts::PI * 2.0 / 3.0).sin(),
                            ),
                        ];

                        painter.add(egui::Shape::convex_polygon(
                            points.to_vec(),
                            egui::Color32::RED,
                            egui::Stroke::new(1.0, egui::Color32::BLACK),
                        ));
                    }
                    _ => {} // Handle any other tab indices (shouldn't happen)
                }
            });
        });
    }
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "Time Warp IDE",
        options,
        Box::new(|_cc| Box::new(TimeWarpApp::default())),
    )
}
