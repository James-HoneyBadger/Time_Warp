use crate::interpreter::Interpreter;
use crate::languages::basic::InterpreterError;

fn highlight_basic_syntax(text: &str, theme: &Theme) -> egui::text::LayoutJob {
    let mut job = egui::text::LayoutJob::default();

    let (keyword_color, string_color, number_color, comment_color, default_color) = match theme {
        Theme::Light => (
            egui::Color32::from_rgb(0, 0, 255),    // Blue keywords
            egui::Color32::from_rgb(163, 21, 21),  // Dark red strings
            egui::Color32::from_rgb(0, 128, 0),    // Green numbers
            egui::Color32::from_rgb(0, 128, 0),    // Green comments
            egui::Color32::BLACK,                  // Black default
        ),
        Theme::Dark => (
            egui::Color32::from_rgb(86, 156, 214), // Light blue keywords
            egui::Color32::from_rgb(206, 145, 120), // Orange strings
            egui::Color32::from_rgb(181, 206, 168), // Light green numbers
            egui::Color32::from_rgb(106, 153, 85),  // Green comments
            egui::Color32::from_rgb(212, 212, 212), // Light gray default
        ),
        Theme::Retro => (
            egui::Color32::from_rgb(255, 255, 0),  // Yellow keywords
            egui::Color32::from_rgb(255, 0, 255),  // Magenta strings
            egui::Color32::from_rgb(0, 255, 255),  // Cyan numbers
            egui::Color32::from_rgb(0, 255, 0),    // Green comments
            egui::Color32::from_rgb(255, 255, 255), // White default
        ),
    };

    let basic_keywords = [
        "PRINT", "INPUT", "IF", "THEN", "ELSE", "FOR", "TO", "STEP", "NEXT", "WHILE", "WEND",
        "GOTO", "GOSUB", "RETURN", "END", "STOP", "LET", "DIM", "DEF", "FN", "REM", "DATA",
        "READ", "RESTORE", "ON", "CLS", "LOCATE", "COLOR", "LINE", "CIRCLE", "PSET", "PRESET",
        "SCREEN", "WIDTH", "KEY", "BEEP", "SOUND", "PLAY", "TIMER", "RANDOMIZE", "RND", "INT",
        "ABS", "SGN", "SIN", "COS", "TAN", "ATN", "EXP", "LOG", "SQR", "LEN", "LEFT$", "RIGHT$",
        "MID$", "CHR$", "ASC", "STR$", "VAL", "INSTR", "AND", "OR", "NOT", "XOR", "MOD",
    ];

    let mut i = 0;
    let chars: Vec<char> = text.chars().collect();

    while i < chars.len() {
        let ch = chars[i];

        // Check for REM comments (REM can be at start of line or after line number)
        if (i == 0 || chars[i-1].is_whitespace() || chars[i-1].is_digit(10)) &&
           i + 2 < chars.len() &&
           chars[i..i+3].iter().collect::<String>().to_uppercase() == "REM" {
            // REM comment - color the rest of the line
            let start = i;
            while i < chars.len() && chars[i] != '\n' {
                i += 1;
            }
            let comment_text = &text[start..i];
            job.append(comment_text, 0.0, egui::text::TextFormat {
                color: comment_color,
                ..Default::default()
            });
            continue;
        }

        // Check for strings
        if ch == '"' {
            let start = i;
            i += 1;
            while i < chars.len() && chars[i] != '"' {
                i += 1;
            }
            if i < chars.len() {
                i += 1; // Include closing quote
            }
            let string_text = &text[start..i];
            job.append(string_text, 0.0, egui::text::TextFormat {
                color: string_color,
                ..Default::default()
            });
            continue;
        }

        // Check for numbers
        if ch.is_digit(10) || (ch == '.' && i + 1 < chars.len() && chars[i + 1].is_digit(10)) {
            let start = i;
            while i < chars.len() && (chars[i].is_digit(10) || chars[i] == '.') {
                i += 1;
            }
            let number_text = &text[start..i];
            job.append(number_text, 0.0, egui::text::TextFormat {
                color: number_color,
                ..Default::default()
            });
            continue;
        }

        // Check for keywords (word boundaries)
        if ch.is_alphabetic() {
            let start = i;
            while i < chars.len() && (chars[i].is_alphabetic() || chars[i] == '$') {
                i += 1;
            }
            let word = &text[start..i];
            let upper_word = word.to_uppercase();
            if basic_keywords.contains(&upper_word.as_str()) {
                job.append(word, 0.0, egui::text::TextFormat {
                    color: keyword_color,
                    ..Default::default()
                });
            } else {
                job.append(word, 0.0, egui::text::TextFormat {
                    color: default_color,
                    ..Default::default()
                });
            }
            continue;
        }

        // Default character
        job.append(&text[i..i+1], 0.0, egui::text::TextFormat {
            color: default_color,
            ..Default::default()
        });
        i += 1;
    }

    job
}

fn get_basic_completions(text: &str, cursor_pos: usize) -> Vec<String> {
    let basic_keywords = [
        "PRINT", "INPUT", "IF", "THEN", "ELSE", "FOR", "TO", "STEP", "NEXT", "WHILE", "WEND",
        "GOTO", "GOSUB", "RETURN", "END", "STOP", "LET", "DIM", "DEF", "FN", "REM", "DATA",
        "READ", "RESTORE", "ON", "CLS", "LOCATE", "COLOR", "LINE", "CIRCLE", "PSET", "PRESET",
        "SCREEN", "WIDTH", "KEY", "BEEP", "SOUND", "PLAY", "TIMER", "RANDOMIZE", "RND", "INT",
        "ABS", "SGN", "SIN", "COS", "TAN", "ATN", "EXP", "LOG", "SQR", "LEN", "LEFT$", "RIGHT$",
        "MID$", "CHR$", "ASC", "STR$", "VAL", "INSTR", "AND", "OR", "NOT", "XOR", "MOD",
    ];

    // Find the word being typed at cursor position
    let chars: Vec<char> = text.chars().collect();
    let mut word_start = cursor_pos;

    // Find start of current word
    while word_start > 0 && (chars[word_start - 1].is_alphanumeric() || chars[word_start - 1] == '_' || chars[word_start - 1] == '$') {
        word_start -= 1;
    }

    let current_word = &text[word_start..cursor_pos];
    if current_word.is_empty() {
        return Vec::new();
    }

    let current_upper = current_word.to_uppercase();

    // Get matching keywords
    let mut suggestions: Vec<String> = basic_keywords
        .iter()
        .filter(|kw| kw.starts_with(&current_upper))
        .map(|s| s.to_string())
        .collect();

    // TODO: Add variable names from the code
    // For now, just return keyword suggestions
    suggestions.sort();
    suggestions
}

#[derive(Clone)]
struct OpenFile {
    name: String,
    path: Option<String>,
    code: String,
    language: Language,
}

#[derive(Clone, PartialEq)]
enum Language {
    Basic,
    Pascal,
    Prolog,
}

pub struct TimeWarpApp {
    open_files: Vec<OpenFile>,
    current_tab: usize,
    output: String,
    interpreter: Interpreter,
    main_tab: MainTab,
    user_input: String,
    graphics_commands: Vec<GraphicsCommand>,
    execution_state: ExecutionState,
    theme: Theme,
    font_family: FontFamily,
    // Code completion state
    completion_active: bool,
    completion_suggestions: Vec<String>,
    completion_selected: usize,
    completion_start_pos: usize,
}

#[derive(Clone, PartialEq)]
enum MainTab {
    Editor,
    Output,
}

#[derive(Clone, PartialEq)]
enum Theme {
    Light,
    Dark,
    Retro,
}

#[derive(Clone, PartialEq)]
enum FontFamily {
    Proportional,
    Monospace,
}

#[derive(Clone, PartialEq)]
enum ExecutionState {
    Idle,
    Running,
    WaitingForInput(String), // prompt
}

#[derive(Clone)]
struct GraphicsCommand {
    command: String,
    x: f32,
    angle: f32,
}

impl Default for TimeWarpApp {
    fn default() -> Self {
        let sample = OpenFile {
            name: "tw_basic_sample.twb".to_string(),
            path: None,
            code: include_str!("../examples/tw_basic_sample.twb").to_string(),
            language: Language::Basic,
        };
        Self {
            open_files: vec![sample],
            current_tab: 0,
            output: String::new(),
            interpreter: Interpreter::new(),
            main_tab: MainTab::Editor,
            user_input: String::new(),
            graphics_commands: Vec::new(),
            execution_state: ExecutionState::Idle,
            theme: Theme::Retro,
            font_family: FontFamily::Monospace,
            completion_active: false,
            completion_suggestions: Vec::new(),
            completion_selected: 0,
            completion_start_pos: 0,
        }
    }
}

impl eframe::App for TimeWarpApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.apply_theme_and_font(ctx);
        self.show_menu_bar(ctx);
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.vertical(|ui| {
                ui.horizontal(|ui| {
                    ui.selectable_value(&mut self.main_tab, MainTab::Editor, "Code Editor");
                    ui.selectable_value(&mut self.main_tab, MainTab::Output, "Output & Graphics");
                });
                match self.main_tab {
                    MainTab::Editor => self.show_editor(ui),
                    MainTab::Output => self.show_output_and_graphics(ui),
                }
            });
        });
        self.show_status_bar(ctx);
    }
}

impl TimeWarpApp {
    fn show_menu_bar(&mut self, ctx: &egui::Context) {
        egui::TopBottomPanel::top("menu_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                self.file_menu(ui);
                self.edit_menu(ui);
                self.view_menu(ui);
                self.run_menu(ui);
                self.tools_menu(ui);
                self.help_menu(ui);
            });
        });
    }

    fn file_menu(&mut self, ui: &mut egui::Ui) {
        ui.menu_button("File", |ui| {
            if ui.button("New File").clicked() {
                self.new_file();
                ui.close_menu();
            }
            if ui.button("Open...").clicked() {
                if let Some(path) = rfd::FileDialog::new().pick_file() {
                    if let Ok(content) = std::fs::read_to_string(&path) {
                        self.open_file(path.display().to_string(), content);
                    }
                }
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Save").clicked() {
                if let Some(file) = self.open_files.get_mut(self.current_tab) {
                    if let Some(path) = &file.path {
                        let _ = std::fs::write(path, &file.code);
                    } else {
                        if let Some(path) = rfd::FileDialog::new().save_file() {
                            let _ = std::fs::write(&path, &file.code);
                            file.path = Some(path.display().to_string());
                            file.name = path.file_name().unwrap().to_string_lossy().to_string();
                        }
                    }
                }
                ui.close_menu();
            }
            if ui.button("Save As...").clicked() {
                if let Some(file) = self.open_files.get(self.current_tab) {
                    if let Some(path) = rfd::FileDialog::new().save_file() {
                        let _ = std::fs::write(&path, &file.code);
                        let mut new_file = file.clone();
                        new_file.path = Some(path.display().to_string());
                        new_file.name = path.file_name().unwrap().to_string_lossy().to_string();
                        self.open_files.push(new_file);
                        self.current_tab = self.open_files.len() - 1;
                    }
                }
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Close File").clicked() {
                if self.open_files.len() > 1 {
                    self.open_files.remove(self.current_tab);
                    if self.current_tab >= self.open_files.len() && self.current_tab > 0 {
                        self.current_tab -= 1;
                    }
                }
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Exit").clicked() {
                std::process::exit(0);
            }
        });
    }

    fn edit_menu(&mut self, ui: &mut egui::Ui) {
        ui.menu_button("Edit", |ui| {
            if ui.button("Undo").clicked() {
                // TODO: Implement undo
                ui.close_menu();
            }
            if ui.button("Redo").clicked() {
                // TODO: Implement redo
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Cut").clicked() {
                // TODO: Implement cut
                ui.close_menu();
            }
            if ui.button("Copy").clicked() {
                // TODO: Implement copy
                ui.close_menu();
            }
            if ui.button("Paste").clicked() {
                // TODO: Implement paste
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Find...").clicked() {
                // TODO: Implement find
                ui.close_menu();
            }
            if ui.button("Replace...").clicked() {
                // TODO: Implement replace
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Select All").clicked() {
                // TODO: Implement select all
                ui.close_menu();
            }
        });
    }

    fn view_menu(&mut self, ui: &mut egui::Ui) {
        ui.menu_button("View", |ui| {
            ui.menu_button("Theme", |ui| {
                if ui.selectable_label(matches!(self.theme, Theme::Light), "Light").clicked() {
                    self.theme = Theme::Light;
                    ui.close_menu();
                }
                if ui.selectable_label(matches!(self.theme, Theme::Dark), "Dark").clicked() {
                    self.theme = Theme::Dark;
                    ui.close_menu();
                }
                if ui.selectable_label(matches!(self.theme, Theme::Retro), "Retro").clicked() {
                    self.theme = Theme::Retro;
                    ui.close_menu();
                }
            });
            ui.menu_button("Font", |ui| {
                if ui.selectable_label(matches!(self.font_family, FontFamily::Proportional), "Proportional").clicked() {
                    self.font_family = FontFamily::Proportional;
                    ui.close_menu();
                }
                if ui.selectable_label(matches!(self.font_family, FontFamily::Monospace), "Monospace").clicked() {
                    self.font_family = FontFamily::Monospace;
                    ui.close_menu();
                }
            });
            ui.separator();
            if ui.button("Zoom In").clicked() {
                // TODO: Implement zoom
                ui.close_menu();
            }
            if ui.button("Zoom Out").clicked() {
                // TODO: Implement zoom
                ui.close_menu();
            }
            if ui.button("Reset Zoom").clicked() {
                // TODO: Implement reset zoom
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Toggle Line Numbers").clicked() {
                // TODO: Implement toggle line numbers
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Switch to Editor").clicked() {
                self.main_tab = MainTab::Editor;
                ui.close_menu();
            }
            if ui.button("Switch to Output").clicked() {
                self.main_tab = MainTab::Output;
                ui.close_menu();
            }
        });
    }

    fn run_menu(&mut self, ui: &mut egui::Ui) {
        ui.menu_button("Run", |ui| {
            if ui.button("Execute Program").clicked() {
                if let Some(file) = self.open_files.get(self.current_tab) {
                    match file.language {
                        Language::Basic => {
                            let result = self.interpreter.execute_tw_basic(&file.code);
                            self.handle_execution_result(result);
                        }
                        Language::Pascal => {
                            self.output = "Pascal execution not implemented.".to_string();
                            self.main_tab = MainTab::Output;
                        }
                        Language::Prolog => {
                            self.output = "Prolog execution not implemented.".to_string();
                            self.main_tab = MainTab::Output;
                        }
                    }
                }
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Stop Execution").clicked() {
                // TODO: Implement stop
                self.execution_state = ExecutionState::Idle;
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Clear Output").clicked() {
                self.output.clear();
                self.graphics_commands.clear();
                ui.close_menu();
            }
        });
    }

    fn tools_menu(&mut self, ui: &mut egui::Ui) {
        ui.menu_button("Tools", |ui| {
            ui.menu_button("Language", |ui| {
                if ui.button("TW BASIC").clicked() {
                    if let Some(file) = self.open_files.get_mut(self.current_tab) {
                        file.language = Language::Basic;
                    }
                    ui.close_menu();
                }
                if ui.button("TW Pascal").clicked() {
                    if let Some(file) = self.open_files.get_mut(self.current_tab) {
                        file.language = Language::Pascal;
                    }
                    ui.close_menu();
                }
                if ui.button("TW Prolog").clicked() {
                    if let Some(file) = self.open_files.get_mut(self.current_tab) {
                        file.language = Language::Prolog;
                    }
                    ui.close_menu();
                }
            });
            ui.separator();
            if ui.button("Format Code").clicked() {
                // TODO: Implement code formatting
                ui.close_menu();
            }
            if ui.button("Check Syntax").clicked() {
                // TODO: Implement syntax checking
                ui.close_menu();
            }
            ui.separator();
            if ui.button("Load Sample Programs").clicked() {
                // TODO: Implement sample loader
                ui.close_menu();
            }
        });
    }

    fn help_menu(&mut self, ui: &mut egui::Ui) {
        ui.menu_button("Help", |ui| {
            if ui.button("About Time Warp IDE").clicked() {
                self.output = "Time Warp IDE\nA modern, educational programming environment\nBuilt in Rust using egui\n\nSupports TW BASIC, TW Pascal, and TW Prolog".to_string();
                self.main_tab = MainTab::Output;
                ui.close_menu();
            }
            ui.separator();
            if ui.button("TW BASIC Reference").clicked() {
                self.output = r#"TW BASIC Language Reference
=====================================

PROGRAM STRUCTURE:
REM comment          - Comment line
LET var = expr       - Variable assignment
END                  - End program execution
STOP                 - Stop program execution

INPUT/OUTPUT:
PRINT expr           - Display expression
INPUT var            - Read input into variable
CLS                  - Clear screen

CONTROL FLOW:
IF condition THEN stmt - Conditional execution
FOR var = start TO end [STEP step] - Start loop
NEXT var             - End loop
GOTO line            - Jump to line number
GOSUB line           - Call subroutine
RETURN               - Return from subroutine
ON expr GOTO/GOSUB line1,line2,... - Multi-way branch

GRAPHICS:
COLOR n              - Set drawing color (0-15)
LINE x1,y1,x2,y2      - Draw line
CIRCLE x,y,r         - Draw circle
PSET x,y             - Set pixel
PRESET x,y           - Reset pixel
SCREEN mode          - Set screen/graphics mode
WIDTH cols           - Set screen width

MATH FUNCTIONS:
ABS(x)               - Absolute value
INT(x)               - Integer part
SGN(x)               - Sign function (-1, 0, 1)
SIN(x) COS(x) TAN(x) - Trigonometric functions
ATN(x)               - Arctangent
EXP(x) LOG(x)        - Exponential and logarithm
SQR(x)               - Square root
RND                  - Random number (0-1)

STRING FUNCTIONS:
LEN(s$)              - String length
LEFT$(s$,n)          - Left n characters
RIGHT$(s$,n)         - Right n characters
MID$(s$,start[,len]) - Substring
CHR$(n)              - Character from ASCII code
ASC(s$)              - ASCII code of character
STR$(x)              - Number to string
VAL(s$)              - String to number
INSTR(start,s$,find$)- Find substring position

LOGICAL OPERATORS:
AND OR NOT           - Logical operations
XOR                  - Exclusive OR

GRAPHICS TURTLE:
FORWARD n            - Move turtle forward n units
RIGHT n              - Turn turtle right n degrees

SPECIAL FEATURES:
RANDOMIZE            - Seed random number generator
TIMER                 - Get system time
BEEP                 - Sound beep
SOUND freq,duration  - Play sound
PLAY string          - Play musical notes
KEY code             - Check key status
LOCATE row,col       - Position cursor

DATA HANDLING:
DATA value1,value2,..- Define data values
READ var             - Read next data value
RESTORE [line]       - Reset data pointer

ARRAYS:
DIM array(size)      - Declare array
array(index)         - Access array element

FUNCTIONS:
DEF FN name(param) = expr - Define function
FN name(value)      - Call function

ERROR HANDLING:
ON ERROR GOTO line   - Error handler (future feature)

EXAMPLES:
10 PRINT "Hello World"
20 LET X = 42
30 IF X > 40 THEN PRINT "Large"
40 FOR I = 1 TO 10
50 PRINT I
60 NEXT I
70 END
"#.to_string();
                self.main_tab = MainTab::Output;
                ui.close_menu();
            }
            if ui.button("Getting Started").clicked() {
                self.output = r#"GETTING STARTED WITH TW BASIC
================================

1. BASIC PROGRAMS:
   - Start with line numbers (10, 20, 30...)
   - End with END statement
   - Use REM for comments

2. YOUR FIRST PROGRAM:
   10 PRINT "Hello, World!"
   20 END

3. VARIABLES:
   - Numbers: X = 42, PI = 3.14159
   - Strings: NAME$ = "Alice"
   - Arrays: DIM SCORES(10)

4. INPUT AND OUTPUT:
   10 PRINT "What is your name?"
   20 INPUT NAME$
   30 PRINT "Hello, "; NAME$

5. LOOPS:
   10 FOR I = 1 TO 5
   20 PRINT "Count: "; I
   30 NEXT I

6. CONDITIONS:
   10 INPUT X
   20 IF X > 10 THEN PRINT "Big" ELSE PRINT "Small"

7. GRAPHICS:
   10 CLS
   20 COLOR 1
   30 LINE 10,10,100,100
   40 CIRCLE 50,50,25

8. FUNCTIONS:
   10 PRINT ABS(-5)
   20 PRINT SIN(3.14159/2)
   30 PRINT LEN("HELLO")

TIPS:
- Use the editor to write programs
- Click "Execute Program" to run
- Check the Output tab for results
- Use Help > TW BASIC Reference for full documentation
- Syntax highlighting helps identify keywords
- Code completion suggests commands as you type
"#.to_string();
                self.main_tab = MainTab::Output;
                ui.close_menu();
            }
        });
    }
    fn show_editor(&mut self, ui: &mut egui::Ui) {
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                for (i, file) in self.open_files.iter().enumerate() {
                    let selected = i == self.current_tab;
                    if ui.selectable_label(selected, &file.name).clicked() {
                        self.current_tab = i;
                    }
                    ui.label(" ");
                    if ui.small_button("×").clicked() {
                        self.open_files.remove(i);
                        if self.current_tab >= self.open_files.len() && self.current_tab > 0 {
                            self.current_tab -= 1;
                        }
                        return; // Restart the loop
                    }
                    ui.separator();
                }
                if ui.button("+").clicked() {
                    self.new_file();
                }
            });

            if let Some(file) = self.open_files.get_mut(self.current_tab) {
                egui::ScrollArea::vertical().show(ui, |ui| {
                    let lines: Vec<&str> = file.code.lines().collect();
                    let line_count = lines.len().max(1);
                    let line_numbers = (1..=line_count).map(|n| format!("{:4} ", n)).collect::<String>();

                    ui.horizontal(|ui| {
                        ui.vertical(|ui| {
                            ui.add(
                                egui::TextEdit::multiline(&mut line_numbers.as_str())
                                    .interactive(false)
                                    .desired_width(50.0)
                                    .desired_rows(line_count),
                            );
                        });
                        ui.vertical(|ui| {
                            // Use syntax highlighting for BASIC files
                            if file.language == Language::Basic {
                                let mut layouter = |ui: &egui::Ui, string: &str, _wrap_width: f32| {
                                    let layout_job = highlight_basic_syntax(string, &self.theme);
                                    ui.fonts(|f| f.layout_job(layout_job))
                                };

                                let text_edit = egui::TextEdit::multiline(&mut file.code)
                                    .layouter(&mut layouter)
                                    .desired_width(f32::INFINITY)
                                    .desired_rows(line_count);

                                let response = ui.add(text_edit);

                                // Handle code completion for BASIC
                                if response.has_focus() {
                                    // Simple completion trigger: show suggestions when typing letters
                                    let should_show_completion = file.code.chars().last().map_or(false, |c| c.is_alphabetic());

                                    if should_show_completion {
                                        let suggestions = get_basic_completions(&file.code, file.code.len());
                                        if !suggestions.is_empty() {
                                            self.completion_active = true;
                                            self.completion_suggestions = suggestions;
                                            self.completion_selected = 0;
                                            // Find the start of the current word
                                            let chars: Vec<char> = file.code.chars().collect();
                                            let mut word_start = file.code.len();
                                            while word_start > 0 && (chars[word_start - 1].is_alphanumeric() || chars[word_start - 1] == '_' || chars[word_start - 1] == '$') {
                                                word_start -= 1;
                                            }
                                            self.completion_start_pos = word_start;
                                        } else {
                                            self.completion_active = false;
                                        }
                                    } else {
                                        self.completion_active = false;
                                    }

                                    // Handle keyboard input for completion navigation
                                    if self.completion_active {
                                        let input = ui.input(|i| i.clone());
                                        if input.key_pressed(egui::Key::ArrowDown) {
                                            self.completion_selected = (self.completion_selected + 1) % self.completion_suggestions.len();
                                        } else if input.key_pressed(egui::Key::ArrowUp) {
                                            if self.completion_selected == 0 {
                                                self.completion_selected = self.completion_suggestions.len() - 1;
                                            } else {
                                                self.completion_selected -= 1;
                                            }
                                        } else if input.key_pressed(egui::Key::Enter) || input.key_pressed(egui::Key::Tab) {
                                            // Insert the selected completion
                                            let selected = &self.completion_suggestions[self.completion_selected];
                                            let start_byte = file.code.char_indices().nth(self.completion_start_pos)
                                                .map(|(pos, _)| pos).unwrap_or(0);
                                            file.code.replace_range(start_byte.., selected);
                                            self.completion_active = false;
                                        } else if input.key_pressed(egui::Key::Escape) {
                                            self.completion_active = false;
                                        }
                                    }

                                    // Show completion popup
                                    if self.completion_active && !self.completion_suggestions.is_empty() {
                                        let popup_id = egui::Id::new("completion_popup");
                                        egui::popup::show_tooltip_at_pointer(ui.ctx(), popup_id, |ui| {
                                            ui.set_max_width(200.0);
                                            for (i, suggestion) in self.completion_suggestions.iter().enumerate() {
                                                let selected = i == self.completion_selected;
                                                if ui.selectable_label(selected, suggestion).clicked() {
                                                    // Insert the completion
                                                    let selected = &self.completion_suggestions[i];
                                                    let start_byte = file.code.char_indices().nth(self.completion_start_pos)
                                                        .map(|(pos, _)| pos).unwrap_or(0);
                                                    file.code.replace_range(start_byte.., selected);
                                                    self.completion_active = false;
                                                }
                                            }
                                        });
                                    }
                                } else {
                                    self.completion_active = false;
                                }
                            } else {
                                // Plain text for other languages
                                ui.add(
                                    egui::TextEdit::multiline(&mut file.code)
                                        .desired_width(f32::INFINITY)
                                        .desired_rows(line_count),
                                );
                            }
                        });
                    });
                });
            }
        });
    }

    fn show_output_and_graphics(&mut self, ui: &mut egui::Ui) {
        ui.vertical(|ui| {
            ui.label("Output:");
            egui::ScrollArea::vertical().show(ui, |ui| {
                ui.add(
                    egui::TextEdit::multiline(&mut self.output)
                        .desired_width(f32::INFINITY)
                        .desired_rows(10),
                );
            });

            ui.separator();
            ui.label("Graphics Canvas:");
            let canvas_size = egui::vec2(400.0, 300.0);
            let (response, painter) = ui.allocate_painter(canvas_size, egui::Sense::hover());
            let rect = response.rect;
            painter.rect_filled(rect, 0.0, egui::Color32::WHITE);
            // Draw graphics commands here
            let mut x = rect.center().x;
            let mut y = rect.center().y;
            let mut angle = 0.0;
            for cmd in &self.graphics_commands {
                match cmd.command.as_str() {
                    "FORWARD" => {
                        let rad = angle * std::f32::consts::PI / 180.0;
                        let new_x = x + cmd.x * rad.cos();
                        let new_y = y + cmd.x * rad.sin();
                        painter.line_segment([egui::pos2(x, y), egui::pos2(new_x, new_y)], egui::Stroke::new(2.0, egui::Color32::BLACK));
                        x = new_x;
                        y = new_y;
                    }
                    "RIGHT" => {
                        angle += cmd.angle;
                    }
                    _ => {}
                }
            }

            ui.separator();
            if let ExecutionState::WaitingForInput(prompt) = &self.execution_state {
                ui.label(format!("Input required: {}", prompt));
            }
            ui.label("User Input:");
            ui.horizontal(|ui| {
                ui.text_edit_singleline(&mut self.user_input);
                if ui.button("Submit").clicked() && matches!(self.execution_state, ExecutionState::WaitingForInput(_)) {
                    self.interpreter.provide_input(self.user_input.clone());
                    self.user_input.clear();
                    // Continue execution
                    if let Some(file) = self.open_files.get(self.current_tab) {
                        if matches!(file.language, Language::Basic) {
                            let result = self.interpreter.execute_tw_basic(&file.code);
                            self.handle_execution_result(result);
                        }
                    }
                }
            });
        });
    }

    fn handle_execution_result(&mut self, result: Result<crate::languages::basic::ExecutionResult, InterpreterError>) {
        match result {
            Ok(execution_result) => match execution_result {
                crate::languages::basic::ExecutionResult::Complete { output, graphics_commands } => {
                    self.output = output;
                    self.graphics_commands = graphics_commands.into_iter().map(|cmd| GraphicsCommand {
                        command: cmd.command,
                        x: cmd.value,
                        angle: cmd.value,
                    }).collect();
                    self.execution_state = ExecutionState::Idle;
                    self.main_tab = MainTab::Output;
                }
                crate::languages::basic::ExecutionResult::NeedInput { prompt, partial_output, partial_graphics } => {
                    self.output = partial_output;
                    self.graphics_commands = partial_graphics.into_iter().map(|cmd| GraphicsCommand {
                        command: cmd.command,
                        x: cmd.value,
                        angle: cmd.value,
                    }).collect();
                    self.execution_state = ExecutionState::WaitingForInput(prompt);
                    self.main_tab = MainTab::Output;
                }
                crate::languages::basic::ExecutionResult::Error(error) => {
                    self.output = format!("Execution Error: {:?}", error);
                    self.execution_state = ExecutionState::Idle;
                    self.main_tab = MainTab::Output;
                }
            }
            Err(error) => {
                self.output = format!("Interpreter Error: {:?}", error);
                self.execution_state = ExecutionState::Idle;
                self.main_tab = MainTab::Output;
            }
        }
    }

    fn apply_theme_and_font(&self, ctx: &egui::Context) {
        let visuals = match self.theme {
            Theme::Light => egui::Visuals::light(),
            Theme::Dark => egui::Visuals::dark(),
            Theme::Retro => {
                let mut retro = egui::Visuals::dark();
                retro.override_text_color = Some(egui::Color32::from_rgb(0, 255, 0)); // Green text
                retro.widgets.noninteractive.bg_fill = egui::Color32::from_rgb(0, 0, 0); // Black background
                retro.widgets.inactive.bg_fill = egui::Color32::from_rgb(20, 20, 20);
                retro.widgets.hovered.bg_fill = egui::Color32::from_rgb(40, 40, 40);
                retro.widgets.active.bg_fill = egui::Color32::from_rgb(60, 60, 60);
                retro.widgets.open.bg_fill = egui::Color32::from_rgb(30, 30, 30);
                retro
            }
        };

        // Apply font family
        let fonts = egui::FontDefinitions::default();
        // TODO: Implement proper font loading for different families
        // For now, keep default fonts

        ctx.set_visuals(visuals);
        ctx.set_fonts(fonts);
    }

    fn show_status_bar(&mut self, ctx: &egui::Context) {
        egui::TopBottomPanel::bottom("status").show(ctx, |ui| {
            ui.horizontal(|ui| {
                if let Some(file) = self.open_files.get(self.current_tab) {
                    ui.label(format!("File: {}", file.name));
                    ui.separator();
                    let lang = match file.language {
                        Language::Basic => "TW BASIC",
                        Language::Pascal => "TW Pascal",
                        Language::Prolog => "TW Prolog",
                    };
                    ui.label(format!("Language: {}", lang));
                    ui.separator();
                    ui.label(format!("Lines: {}", file.code.lines().count()));
                }
            });
        });
    }

    fn new_file(&mut self) {
        let new_file = OpenFile {
            name: format!("Untitled {}", self.open_files.len() + 1),
            path: None,
            code: String::new(),
            language: Language::Basic,
        };
        self.open_files.push(new_file);
        self.current_tab = self.open_files.len() - 1;
    }

    fn open_file(&mut self, path: String, content: String) {
        let name = std::path::Path::new(&path)
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_string();
        let language = if name.ends_with(".twb") {
            Language::Basic
        } else if name.ends_with(".twp") {
            Language::Pascal
        } else if name.ends_with(".tpr") {
            Language::Prolog
        } else {
            Language::Basic
        };
        let file = OpenFile {
            name,
            path: Some(path),
            code: content,
            language,
        };
        self.open_files.push(file);
        self.current_tab = self.open_files.len() - 1;
    }
}
