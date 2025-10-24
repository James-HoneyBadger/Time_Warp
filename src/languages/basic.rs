use std::collections::HashMap;
// use std::f64::consts::PI; // Commented out - not currently used
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // Keywords
    Let,
    Print,
    Writeln,
    Readln,
    If,
    Then,
    Else,
    Is,
    End,
    Stop,
    Cls,
    Color,
    Forward,
    Back,
    Left,
    Right,
    Penup,
    Pendown,
    GraphicsForward,
    GraphicsRight,
    Input,
    Dim,
    Data,
    Read,
    Restore,
    Def,
    Fn,
    For,
    To,
    Step,
    Next,
    Goto,
    Gosub,
    Return,
    Rem,
    On,
    And,
    Or,
    Not,
    Sin,
    Cos,
    Tan,
    Sqr,
    Abs,
    Int,
    Log,
    Exp,
    Atn,
    Rnd,
    Randomize,
    Len,
    Mid,
    LeftStr,
    RightStr,
    Chr,
    Asc,
    Val,
    Str,
    Instr,
    Fix,
    Cint,
    Csng,
    Cdbl,
    Tab,
    Spc,

    // File I/O
    Open,
    Close,
    PrintHash,
    InputHash,
    Eof,
    Lof,
    Seek,
    Get,
    Put,

    // Graphics
    Line,
    Circle,
    Pset,
    Preset,
    Paint,
    Draw,

    // Sound
    Beep,
    Sound,

    // Screen Control
    Locate,
    Screen,
    Width,
    ColorBg,
    Palette,

    // Error Handling
    OnError,
    Resume,
    Erl,
    Err,

    // Control Flow
    While,
    Wend,
    Select,
    Case,
    Default,
    Error,
    As,

    // System
    System,
    Files,
    Kill,
    Name,
    Chdir,
    Mkdir,
    Rmdir,

    // Array
    Erase,
    Option,
    Base,

    // Operators
    Plus,
    Minus,
    Multiply,
    Divide,
    Mod,
    Power,
    Equal,
    NotEqual,
    Less,
    LessEqual,
    Greater,
    GreaterEqual,

    // Punctuation
    LParen,
    RParen,
    Comma,
    Semicolon,
    Colon,
    Dollar,

    // Literals
    Number(f64),
    String(String),
    Identifier(String),
    EndOfFile,
}

#[derive(Debug, Clone)]
pub enum Expression {
    Number(f64),
    String(String),
    Variable(String),
    BinaryOp {
        left: Box<Expression>,
        operator: BinaryOperator,
        right: Box<Expression>,
    },
    UnaryOp {
        operator: UnaryOperator,
        operand: Box<Expression>,
    },
    FunctionCall {
        name: String,
        arguments: Vec<Expression>,
    },
    ArrayAccess {
        name: String,
        index: Box<Expression>,
    },
    Tab(Box<Expression>),
    Spc(Box<Expression>),
}

#[derive(Debug, Clone)]
pub enum BinaryOperator {
    Plus,
    Minus,
    Multiply,
    Divide,
    Mod,
    Power,
    Equal,
    NotEqual,
    Less,
    LessEqual,
    Greater,
    GreaterEqual,
    And,
    Or,
}

#[derive(Debug, Clone)]
pub enum UnaryOperator {
    Not,
    Minus,
}

#[derive(Debug, Clone)]
pub enum CaseCondition {
    Value(Expression),
    Range { start: Expression, end: Expression },
    Is { operator: String, value: Expression },
}

#[derive(Debug, Clone)]
pub enum Statement {
    Let {
        variable: String,
        expression: Expression,
    },
    Print {
        expressions: Vec<Expression>,
        separator: PrintSeparator,
    },
    Writeln {
        expressions: Vec<Expression>,
        separator: PrintSeparator,
    },
    Readln {
        prompt: Option<String>,
        variables: Vec<String>,
    },
    If {
        condition: Expression,
        then_statements: Vec<Statement>,
        else_statements: Option<Vec<Statement>>,
    },
    For {
        variable: String,
        start: Expression,
        end: Expression,
        step: Option<Expression>,
    },
    Next {
        variable: Option<String>,
    },
    Goto {
        line_number: usize,
    },
    Gosub {
        line_number: usize,
    },
    Return,
    On {
        expression: Expression,
        line_numbers: Vec<usize>,
        is_gosub: bool,
    },
    Input {
        prompt: Option<String>,
        variables: Vec<String>,
    },
    Dim {
        arrays: Vec<(String, Expression)>, // (name, size)
    },
    Data {
        values: Vec<String>,
    },
    Read {
        variables: Vec<String>,
    },
    Restore,
    Def {
        name: String,
        parameter: String,
        expression: Expression,
    },
    End,
    Stop,
    Cls,
    Color {
        color: Expression,
    },
    Forward {
        distance: Expression,
    },
    Back {
        distance: Expression,
    },
    Left {
        angle: Expression,
    },
    Right {
        angle: Expression,
    },
    Penup,
    Pendown,
    GraphicsForward {
        distance: Expression,
    },
    GraphicsRight {
        angle: Expression,
    },
    Rem,

    // File I/O
    Open {
        file_number: Expression,
        file_name: Expression,
        mode: String,
    },
    Close {
        file_numbers: Vec<Expression>,
    },
    PrintHash {
        file_number: Expression,
        expressions: Vec<Expression>,
        separator: PrintSeparator,
    },
    InputHash {
        file_number: Expression,
        variables: Vec<String>,
    },

    // Graphics
    Line {
        x1: Expression,
        y1: Expression,
        x2: Expression,
        y2: Expression,
        color: Option<Expression>,
        style: Option<String>,
    },
    Circle {
        x: Expression,
        y: Expression,
        radius: Expression,
        color: Option<Expression>,
        start_angle: Option<Expression>,
        end_angle: Option<Expression>,
    },
    Pset {
        x: Expression,
        y: Expression,
        color: Option<Expression>,
    },
    Preset {
        x: Expression,
        y: Expression,
        color: Option<Expression>,
    },
    Paint {
        x: Expression,
        y: Expression,
        paint_color: Option<Expression>,
        border_color: Option<Expression>,
    },
    Draw {
        commands: Expression,
    },

    // Sound
    Beep,
    Sound {
        frequency: Expression,
        duration: Expression,
    },

    // Screen Control
    Locate {
        row: Expression,
        column: Expression,
    },
    Screen {
        mode: Expression,
    },
    Width {
        width: Expression,
    },
    ColorBg {
        foreground: Option<Expression>,
        background: Option<Expression>,
    },
    Palette {
        attribute: Expression,
        color: Expression,
    },

    // Error Handling
    OnError {
        line_number: Option<usize>,
    },
    Resume {
        line_number: Option<usize>,
    },

    // Control Flow
    While {
        condition: Expression,
    },
    Wend,
    Select {
        expression: Expression,
    },
    Case {
        conditions: Vec<CaseCondition>,
    },
    Default,
    EndSelect,

    // System
    System,
    Files {
        pattern: Option<Expression>,
    },
    Kill {
        file_name: Expression,
    },
    Name {
        old_name: Expression,
        new_name: Expression,
    },
    Chdir {
        path: Expression,
    },
    Mkdir {
        path: Expression,
    },
    Rmdir {
        path: Expression,
    },

    // Array
    Erase {
        arrays: Vec<String>,
    },
    OptionBase {
        base: Expression,
    },
}

#[derive(Debug, Clone)]
pub enum PrintSeparator {
    Comma,
    Semicolon,
    None,
}

#[derive(Debug, Clone)]
pub struct Program {
    pub statements: Vec<Statement>,
}

#[derive(Debug, Clone)]
pub struct Parser {
    tokens: Vec<Token>,
    position: usize,
    current_token: Option<Token>,
}

#[derive(Debug)]
pub struct Tokenizer {
    input: String,
    position: usize,
}

impl Tokenizer {
    pub fn new(input: &str) -> Self {
        Tokenizer {
            input: input.to_string(),
            position: 0,
        }
    }

    pub fn tokenize(&mut self) -> Result<Vec<Token>, InterpreterError> {
        let mut tokens = Vec::new();
        while self.position < self.input.len() {
            let ch = self.input.as_bytes()[self.position] as char;
            match ch {
                ' ' | '\t' | '\n' | '\r' => {
                    self.position += 1;
                    continue;
                }
                '0'..='9' => {
                    let start = self.position;
                    while self.position < self.input.len()
                        && self.input.as_bytes()[self.position].is_ascii_digit()
                    {
                        self.position += 1;
                    }
                    let num_str = &self.input[start..self.position];
                    if let Ok(num) = num_str.parse::<f64>() {
                        tokens.push(Token::Number(num));
                    } else {
                        return Err(InterpreterError::ParseError(format!(
                            "Invalid number: {}",
                            num_str
                        )));
                    }
                }
                '"' => {
                    self.position += 1;
                    let start = self.position;
                    while self.position < self.input.len()
                        && self.input.as_bytes()[self.position] as char != '"'
                    {
                        self.position += 1;
                    }
                    if self.position >= self.input.len() {
                        return Err(InterpreterError::ParseError(
                            "Unterminated string".to_string(),
                        ));
                    }
                    let str_val = self.input[start..self.position].to_string();
                    self.position += 1;
                    tokens.push(Token::String(str_val));
                }
                'A'..='Z' | 'a'..='z' => {
                    let start = self.position;
                    while self.position < self.input.len()
                        && (self.input.as_bytes()[self.position].is_ascii_alphanumeric()
                            || self.input.as_bytes()[self.position] == b'_'
                            || self.input.as_bytes()[self.position] == b'$')
                    {
                        self.position += 1;
                    }
                    let ident = self.input[start..self.position].to_uppercase();
                    let token = match ident.as_str() {
                        "LET" => Token::Let,
                        "PRINT" => Token::Print,
                        "WRITELN" => Token::Writeln,
                        "READLN" => Token::Readln,
                        "IF" => Token::If,
                        "THEN" => Token::Then,
                        "IS" => Token::Is,
                        "ELSE" => Token::Else,
                        "END" => Token::End,
                        "STOP" => Token::Stop,
                        "CLS" => Token::Cls,
                        "COLOR" => Token::Color,
                        "FORWARD" => Token::Forward,
                        "FD" => Token::Forward,
                        "BACK" => Token::Back,
                        "BK" => Token::Back,
                        "LEFT" => Token::Left,
                        "LT" => Token::Left,
                        "RIGHT" => Token::Right,
                        "RT" => Token::Right,
                        "PENUP" => Token::Penup,
                        "PU" => Token::Penup,
                        "PENDOWN" => Token::Pendown,
                        "PD" => Token::Pendown,
                        "GRAPHICSFORWARD" => Token::GraphicsForward,
                        "GRAPHICSRIGHT" => Token::GraphicsRight,
                        "INPUT" => Token::Input,
                        "DIM" => Token::Dim,
                        "DATA" => Token::Data,
                        "READ" => Token::Read,
                        "RESTORE" => Token::Restore,
                        "DEF" => Token::Def,
                        "FN" => Token::Fn,
                        "FOR" => Token::For,
                        "TO" => Token::To,
                        "STEP" => Token::Step,
                        "NEXT" => Token::Next,
                        "GOTO" => Token::Goto,
                        "GOSUB" => Token::Gosub,
                        "RETURN" => Token::Return,
                        "REM" => Token::Rem,
                        "ON" => Token::On,
                        "AND" => Token::And,
                        "OR" => Token::Or,
                        "NOT" => Token::Not,
                        "SIN" => Token::Sin,
                        "COS" => Token::Cos,
                        "TAN" => Token::Tan,
                        "SQR" => Token::Sqr,
                        "ABS" => Token::Abs,
                        "INT" => Token::Int,
                        "LOG" => Token::Log,
                        "EXP" => Token::Exp,
                        "ATN" => Token::Atn,
                        "RND" => Token::Rnd,
                        "RANDOMIZE" => Token::Randomize,
                        "LEN" => Token::Len,
                        "MID" => Token::Mid,
                        "LEFT" => Token::LeftStr,
                        "RIGHT" => Token::RightStr,
                        "CHR" => Token::Chr,
                        "ASC" => Token::Asc,
                        "VAL" => Token::Val,
                        "STR" => Token::Str,
                        "INSTR" => Token::Instr,
                        "FIX" => Token::Fix,
                        "CINT" => Token::Cint,
                        "CSNG" => Token::Csng,
                        "CDBL" => Token::Cdbl,
                        "TAB" => Token::Tab,
                        "SPC" => Token::Spc,
                        "OPEN" => Token::Open,
                        "CLOSE" => Token::Close,
                        "PRINT#" => Token::PrintHash,
                        "INPUT#" => Token::InputHash,
                        "EOF" => Token::Eof,
                        "LOF" => Token::Lof,
                        "SEEK" => Token::Seek,
                        "GET" => Token::Get,
                        "PUT" => Token::Put,
                        "LINE" => Token::Line,
                        "CIRCLE" => Token::Circle,
                        "PSET" => Token::Pset,
                        "PRESET" => Token::Preset,
                        "PAINT" => Token::Paint,
                        "DRAW" => Token::Draw,
                        "BEEP" => Token::Beep,
                        "SOUND" => Token::Sound,
                        "LOCATE" => Token::Locate,
                        "SCREEN" => Token::Screen,
                        "WIDTH" => Token::Width,
                        "PALETTE" => Token::Palette,
                        "ONERROR" => Token::OnError,
                        "RESUME" => Token::Resume,
                        "ERL" => Token::Erl,
                        "ERR" => Token::Err,
                        "WHILE" => Token::While,
                        "WEND" => Token::Wend,
                        "SELECT" => Token::Select,
                        "CASE" => Token::Case,
                        "DEFAULT" => Token::Default,
                        "ERROR" => Token::Error,
                        "AS" => Token::As,
                        "SYSTEM" => Token::System,
                        "FILES" => Token::Files,
                        "KILL" => Token::Kill,
                        "NAME" => Token::Name,
                        "CHDIR" => Token::Chdir,
                        "MKDIR" => Token::Mkdir,
                        "RMDIR" => Token::Rmdir,
                        "ERASE" => Token::Erase,
                        "OPTION" => Token::Option,
                        "BASE" => Token::Base,
                        "MOD" => Token::Mod,
                        _ => Token::Identifier(ident),
                    };
                    tokens.push(token);
                }
                '+' => {
                    tokens.push(Token::Plus);
                    self.position += 1;
                }
                '-' => {
                    tokens.push(Token::Minus);
                    self.position += 1;
                }
                '*' => {
                    tokens.push(Token::Multiply);
                    self.position += 1;
                }
                '/' => {
                    tokens.push(Token::Divide);
                    self.position += 1;
                }
                '=' => {
                    tokens.push(Token::Equal);
                    self.position += 1;
                }
                '<' => {
                    if self.position + 1 < self.input.len()
                        && self.input.as_bytes()[self.position + 1] == b'='
                    {
                        tokens.push(Token::LessEqual);
                        self.position += 2;
                    } else if self.position + 1 < self.input.len()
                        && self.input.as_bytes()[self.position + 1] == b'>'
                    {
                        tokens.push(Token::NotEqual);
                        self.position += 2;
                    } else {
                        tokens.push(Token::Less);
                        self.position += 1;
                    }
                }
                '>' => {
                    if self.position + 1 < self.input.len()
                        && self.input.as_bytes()[self.position + 1] == b'='
                    {
                        tokens.push(Token::GreaterEqual);
                        self.position += 2;
                    } else {
                        tokens.push(Token::Greater);
                        self.position += 1;
                    }
                }
                ':' => {
                    tokens.push(Token::Colon);
                    self.position += 1;
                }
                '$' => {
                    tokens.push(Token::Dollar);
                    self.position += 1;
                }
                '(' => {
                    tokens.push(Token::LParen);
                    self.position += 1;
                }
                ')' => {
                    tokens.push(Token::RParen);
                    self.position += 1;
                }
                ',' => {
                    tokens.push(Token::Comma);
                    self.position += 1;
                }
                ';' => {
                    tokens.push(Token::Semicolon);
                    self.position += 1;
                }
                '^' => {
                    tokens.push(Token::Power);
                    self.position += 1;
                }
                _ => {
                    return Err(InterpreterError::ParseError(format!(
                        "Unexpected character: {}",
                        ch
                    )));
                }
            }
        }
        tokens.push(Token::EndOfFile);
        Ok(tokens)
    }
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        let current_token = if tokens.is_empty() {
            None
        } else {
            Some(tokens[0].clone())
        };
        Self {
            tokens,
            position: 0,
            current_token,
        }
    }

    fn advance(&mut self) {
        self.position += 1;
        if self.position >= self.tokens.len() {
            self.current_token = None;
        } else {
            self.current_token = Some(self.tokens[self.position].clone());
        }
    }

    fn expect(&mut self, expected: &Token) -> Result<(), InterpreterError> {
        if let Some(ref token) = self.current_token {
            if token == expected {
                self.advance();
                Ok(())
            } else {
                Err(InterpreterError::ParseError(format!(
                    "Expected {:?}, found {:?}",
                    expected, token
                )))
            }
        } else {
            Err(InterpreterError::ParseError(format!(
                "Expected {:?}, found end of input",
                expected
            )))
        }
    }

    pub fn parse_program(&mut self) -> Result<Program, InterpreterError> {
        let mut statements = Vec::new();

        while let Some(ref token) = self.current_token {
            if let Token::EndOfFile = token {
                break;
            }

            let statement = self.parse_statement()?;
            statements.push(statement);

            // Skip optional colon or end of line
            if let Some(Token::Colon) = self.current_token {
                self.advance();
            }
        }

        Ok(Program { statements })
    }

    fn parse_statement(&mut self) -> Result<Statement, InterpreterError> {
        // Handle optional line number at the beginning of the statement
        if let Some(Token::Number(_)) = self.current_token {
            self.advance(); // Skip the line number
        }

        match self.current_token {
            Some(Token::Let) => self.parse_let_statement(),
            Some(Token::Print) => self.parse_print_statement(),
            Some(Token::Writeln) => self.parse_writeln_statement(),
            Some(Token::Readln) => self.parse_readln_statement(),
            Some(Token::If) => self.parse_if_statement(),
            Some(Token::For) => self.parse_for_statement(),
            Some(Token::Next) => self.parse_next_statement(),
            Some(Token::Goto) => self.parse_goto_statement(),
            Some(Token::Gosub) => self.parse_gosub_statement(),
            Some(Token::Return) => self.parse_return_statement(),
            Some(Token::On) => self.parse_on_statement(),
            Some(Token::Input) => self.parse_input_statement(),
            Some(Token::Dim) => self.parse_dim_statement(),
            Some(Token::Data) => self.parse_data_statement(),
            Some(Token::Read) => self.parse_read_statement(),
            Some(Token::Restore) => self.parse_restore_statement(),
            Some(Token::End) => self.parse_end_statement(),
            Some(Token::Stop) => self.parse_stop_statement(),
            Some(Token::Cls) => self.parse_cls_statement(),
            Some(Token::Color) => self.parse_color_statement(),
            Some(Token::Forward) => self.parse_turtle_forward_statement(),
            Some(Token::Back) => self.parse_turtle_back_statement(),
            Some(Token::Left) => self.parse_turtle_left_statement(),
            Some(Token::Right) => self.parse_turtle_right_statement(),
            Some(Token::Penup) => self.parse_penup_statement(),
            Some(Token::Pendown) => self.parse_pendown_statement(),
            Some(Token::GraphicsForward) => self.parse_forward_statement(),
            Some(Token::GraphicsRight) => self.parse_right_statement(),
            Some(Token::Rem) => self.parse_rem_statement(),

            // File I/O
            Some(Token::Open) => self.parse_open_statement(),
            Some(Token::Close) => self.parse_close_statement(),
            Some(Token::PrintHash) => self.parse_print_hash_statement(),
            Some(Token::InputHash) => self.parse_input_hash_statement(),

            // Graphics
            Some(Token::Line) => self.parse_line_statement(),
            Some(Token::Circle) => self.parse_circle_statement(),
            Some(Token::Pset) => self.parse_pset_statement(),
            Some(Token::Preset) => self.parse_preset_statement(),
            Some(Token::Paint) => self.parse_paint_statement(),
            Some(Token::Draw) => self.parse_draw_statement(),

            // Sound
            Some(Token::Beep) => self.parse_beep_statement(),
            Some(Token::Sound) => self.parse_sound_statement(),

            // Screen Control
            Some(Token::Locate) => self.parse_locate_statement(),
            Some(Token::Screen) => self.parse_screen_statement(),
            Some(Token::Width) => self.parse_width_statement(),
            Some(Token::Palette) => self.parse_palette_statement(),

            // Error Handling
            Some(Token::OnError) => self.parse_on_error_statement(),
            Some(Token::Resume) => self.parse_resume_statement(),

            // Control Flow
            Some(Token::While) => self.parse_while_statement(),
            Some(Token::Wend) => self.parse_wend_statement(),
            Some(Token::Select) => self.parse_select_statement(),
            Some(Token::Case) => self.parse_case_statement(),
            Some(Token::Default) => self.parse_default_statement(),

            // System
            Some(Token::System) => self.parse_system_statement(),
            Some(Token::Files) => self.parse_files_statement(),
            Some(Token::Kill) => self.parse_kill_statement(),
            Some(Token::Name) => self.parse_name_statement(),
            Some(Token::Chdir) => self.parse_chdir_statement(),
            Some(Token::Mkdir) => self.parse_mkdir_statement(),
            Some(Token::Rmdir) => self.parse_rmdir_statement(),

            // Array
            Some(Token::Erase) => self.parse_erase_statement(),
            Some(Token::Option) => self.parse_option_statement(),

            _ => {
                match self.current_token {
                    Some(Token::Identifier(ref id)) => {
                        // Check for common mistakes
                        let suggestion = if id.to_uppercase().starts_with("PRINT") && id.len() > 5 {
                            "Did you mean 'PRINT <expression>'? PRINT requires a space after the keyword."
                        } else if id.to_uppercase().starts_with("LET") && id.len() > 3 {
                            "Did you mean 'LET <variable> = <expression>'? LET requires a space after the keyword."
                        } else if id.to_uppercase().starts_with("IF") && id.len() > 2 {
                            "Did you mean 'IF <condition> THEN <statement>'? IF requires spaces."
                        } else {
                            "Unknown statement. Check your syntax and ensure keywords are properly separated."
                        };
                        Err(InterpreterError::ParseError(format!(
                            "Unknown statement '{}'. {}",
                            id, suggestion
                        )))
                    }
                    _ => Err(InterpreterError::ParseError(format!(
                        "Unexpected token in statement: {:?}",
                        self.current_token
                    ))),
                }
            }
        }
    }

    fn parse_let_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume LET
        let var_name = self.parse_identifier()?;
        self.expect(&Token::Equal)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Let {
            variable: var_name,
            expression,
        })
    }

    fn parse_print_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PRINT
        let (expressions, separator) = self.parse_print_expressions()?;

        Ok(Statement::Print {
            expressions,
            separator,
        })
    }

    fn parse_writeln_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume WRITELN
        let mut expressions = Vec::new();
        let mut separator = PrintSeparator::None;

        while let Some(ref token) = self.current_token {
            match token {
                Token::Colon | Token::EndOfFile => break,
                Token::Comma => {
                    separator = PrintSeparator::Comma;
                    self.advance();
                    break;
                }
                Token::Semicolon => {
                    separator = PrintSeparator::Semicolon;
                    self.advance();
                    break;
                }
                _ => {
                    let expr = self.parse_expression()?;
                    expressions.push(expr);
                }
            }
        }

        Ok(Statement::Writeln {
            expressions,
            separator,
        })
    }

    fn parse_readln_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume READLN
        let mut prompt = None;
        let mut variables = Vec::new();

        // Check for optional prompt
        if let Some(Token::String(ref s)) = self.current_token {
            prompt = Some(s.clone());
            self.advance();
            if let Some(Token::Comma) = self.current_token {
                self.advance();
            }
        }

        // Parse variable list
        while let Some(ref token) = self.current_token {
            match token {
                Token::Identifier(ref var) => {
                    variables.push(var.clone());
                    self.advance();
                    if let Some(Token::Comma) = self.current_token {
                        self.advance();
                    } else {
                        break;
                    }
                }
                _ => break,
            }
        }

        Ok(Statement::Readln { prompt, variables })
    }

    fn parse_turtle_forward_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume FORWARD
        let distance = self.parse_expression()?;
        Ok(Statement::Forward { distance })
    }

    fn parse_turtle_back_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume BACK
        let distance = self.parse_expression()?;
        Ok(Statement::Back { distance })
    }

    fn parse_turtle_left_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume LEFT
        let angle = self.parse_expression()?;
        Ok(Statement::Left { angle })
    }

    fn parse_turtle_right_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume RIGHT
        let angle = self.parse_expression()?;
        Ok(Statement::Right { angle })
    }

    fn parse_penup_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PENUP
        Ok(Statement::Penup)
    }

    fn parse_pendown_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PENDOWN
        Ok(Statement::Pendown)
    }

    fn parse_if_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume IF
        let condition = self.parse_expression()?;
        self.expect(&Token::Then)?;

        let mut then_statements = Vec::new();
        while let Some(ref token) = self.current_token {
            match token {
                Token::Else => {
                    self.advance();
                    let else_statements = self.parse_statement_list()?;
                    return Ok(Statement::If {
                        condition,
                        then_statements,
                        else_statements: Some(else_statements),
                    });
                }
                Token::Colon | Token::EndOfFile => break,
                _ => {
                    let stmt = self.parse_statement()?;
                    then_statements.push(stmt);
                }
            }
        }

        Ok(Statement::If {
            condition,
            then_statements,
            else_statements: None,
        })
    }

    fn parse_for_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume FOR
        let variable = self.parse_identifier()?;
        self.expect(&Token::Equal)?;
        let start = self.parse_expression()?;
        self.expect(&Token::To)?;
        let end = self.parse_expression()?;

        let step = if let Some(Token::Step) = self.current_token {
            self.advance();
            Some(self.parse_expression()?)
        } else {
            None
        };

        // For now, we'll collect statements until NEXT
        // This is a simplified version - a full implementation would need to handle nested structures
        // let statements = Vec::new(); // TODO: Parse statements until NEXT

        Ok(Statement::For {
            variable,
            start,
            end,
            step,
        })
    }

    fn parse_next_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume NEXT
        let variable = if let Some(Token::Identifier(_)) = self.current_token {
            Some(self.parse_identifier()?)
        } else {
            None
        };
        Ok(Statement::Next { variable })
    }

    fn parse_goto_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume GOTO
        if let Some(Token::Number(line_num)) = self.current_token {
            let line_number = line_num as usize;
            self.advance();
            Ok(Statement::Goto { line_number })
        } else {
            Err(InterpreterError::ParseError(
                "Expected line number after GOTO".to_string(),
            ))
        }
    }

    fn parse_gosub_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume GOSUB
        if let Some(Token::Number(line_num)) = self.current_token {
            let line_number = line_num as usize;
            self.advance();
            Ok(Statement::Gosub { line_number })
        } else {
            Err(InterpreterError::ParseError(
                "Expected line number after GOSUB".to_string(),
            ))
        }
    }

    fn parse_return_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume RETURN
        Ok(Statement::Return)
    }

    fn parse_on_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume ON
        let expression = self.parse_expression()?;

        let is_gosub = if let Some(Token::Gosub) = self.current_token {
            self.advance();
            true
        } else if let Some(Token::Goto) = self.current_token {
            self.advance();
            false
        } else {
            return Err(InterpreterError::ParseError(
                "Expected GOTO or GOSUB after ON expression".to_string(),
            ));
        };

        let mut line_numbers = Vec::new();
        loop {
            if let Some(Token::Number(line_num)) = self.current_token {
                line_numbers.push(line_num as usize);
                self.advance();
            } else {
                return Err(InterpreterError::ParseError(
                    "Expected line number in ON statement".to_string(),
                ));
            }

            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }

        Ok(Statement::On {
            expression,
            line_numbers,
            is_gosub,
        })
    }

    fn parse_input_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume INPUT
        let prompt = if let Some(Token::String(_)) = self.current_token {
            let prompt_str = self.parse_string_literal()?;
            Some(prompt_str)
        } else {
            None
        };

        // Handle optional semicolon or comma separator after prompt
        if prompt.is_some() {
            if let Some(Token::Semicolon) | Some(Token::Comma) = self.current_token {
                self.advance();
            }
        }

        let mut variables = Vec::new();
        while let Some(Token::Identifier(_)) = self.current_token {
            let var = self.parse_identifier()?;
            variables.push(var);
            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }

        Ok(Statement::Input { prompt, variables })
    }

    fn parse_dim_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume DIM
        let mut arrays = Vec::new();

        loop {
            let name = self.parse_identifier()?;
            self.expect(&Token::LParen)?;
            let size = self.parse_expression()?;
            self.expect(&Token::RParen)?;

            arrays.push((name, size));

            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }

        Ok(Statement::Dim { arrays })
    }

    fn parse_data_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume DATA
        let mut values = Vec::new();

        while let Some(ref token) = self.current_token {
            match token {
                Token::String(s) => {
                    values.push(s.clone());
                    self.advance();
                }
                Token::Number(n) => {
                    values.push(n.to_string());
                    self.advance();
                }
                Token::Identifier(id) => {
                    values.push(id.clone());
                    self.advance();
                }
                Token::Comma => {
                    self.advance();
                }
                _ => break,
            }
        }

        Ok(Statement::Data { values })
    }

    fn parse_read_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume READ
        let mut variables = Vec::new();

        loop {
            let var = self.parse_identifier()?;
            variables.push(var);

            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }

        Ok(Statement::Read { variables })
    }

    fn parse_restore_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume RESTORE
        Ok(Statement::Restore)
    }

    fn parse_end_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume END
        if let Some(Token::Select) = self.current_token {
            self.advance(); // consume SELECT
            Ok(Statement::EndSelect)
        } else {
            Ok(Statement::End)
        }
    }

    fn parse_stop_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume STOP
        Ok(Statement::Stop)
    }

    fn parse_cls_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume CLS
        Ok(Statement::Cls)
    }

    fn parse_color_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume COLOR
        let color = self.parse_expression()?;
        Ok(Statement::Color { color })
    }

    fn parse_forward_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume FORWARD
        let distance = self.parse_expression()?;
        Ok(Statement::GraphicsForward { distance })
    }

    fn parse_right_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume RIGHT
        let angle = self.parse_expression()?;
        Ok(Statement::GraphicsRight { angle })
    }

    fn parse_rem_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume REM
                        // Skip to end of line
        while let Some(ref token) = self.current_token {
            if let Token::EndOfFile = token {
                break;
            }
            self.advance();
        }
        Ok(Statement::Rem)
    }

    // File I/O
    fn parse_open_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume OPEN
        let file_name = self.parse_expression()?;
        self.expect(&Token::For)?;
        self.expect(&Token::Input)?;
        // TODO: Parse full OPEN syntax
        Ok(Statement::Open {
            file_number: Expression::Number(1.0), // Default file number
            file_name,
            mode: "I".to_string(), // Input mode
        })
    }

    fn parse_close_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume CLOSE
        let mut file_numbers = Vec::new();
        if let Some(Token::Number(n)) = self.current_token {
            file_numbers.push(Expression::Number(n));
            self.advance();
        }
        Ok(Statement::Close { file_numbers })
    }

    fn parse_print_hash_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PRINT#
        let file_number = self.parse_expression()?;
        let (expressions, separator) = self.parse_print_expressions()?;
        Ok(Statement::PrintHash {
            file_number,
            expressions,
            separator,
        })
    }

    fn parse_input_hash_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume INPUT#
        let file_number = self.parse_expression()?;
        let mut variables = Vec::new();
        while let Some(Token::Identifier(ref var)) = self.current_token {
            variables.push(var.clone());
            self.advance();
            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }
        Ok(Statement::InputHash {
            file_number,
            variables,
        })
    }

    // Graphics
    fn parse_line_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume LINE
        self.expect(&Token::LParen)?;
        let x1 = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let y1 = self.parse_expression()?;
        self.expect(&Token::RParen)?;
        self.expect(&Token::Minus)?;
        self.expect(&Token::LParen)?;
        let x2 = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let y2 = self.parse_expression()?;
        self.expect(&Token::RParen)?;
        let color = if let Some(Token::Comma) = self.current_token {
            self.advance();
            Some(self.parse_expression()?)
        } else {
            None
        };
        Ok(Statement::Line {
            x1,
            y1,
            x2,
            y2,
            color,
            style: None,
        })
    }

    fn parse_circle_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume CIRCLE
        self.expect(&Token::LParen)?;
        let x = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let y = self.parse_expression()?;
        self.expect(&Token::RParen)?;
        self.expect(&Token::Comma)?;
        let radius = self.parse_expression()?;
        let color = if let Some(Token::Comma) = self.current_token {
            self.advance();
            Some(self.parse_expression()?)
        } else {
            None
        };
        Ok(Statement::Circle {
            x,
            y,
            radius,
            color,
            start_angle: None,
            end_angle: None,
        })
    }

    fn parse_pset_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PSET
        self.expect(&Token::LParen)?;
        let x = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let y = self.parse_expression()?;
        self.expect(&Token::RParen)?;
        let color = if let Some(Token::Comma) = self.current_token {
            self.advance();
            Some(self.parse_expression()?)
        } else {
            None
        };
        Ok(Statement::Pset { x, y, color })
    }

    fn parse_preset_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PRESET
        self.expect(&Token::LParen)?;
        let x = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let y = self.parse_expression()?;
        self.expect(&Token::RParen)?;
        let color = if let Some(Token::Comma) = self.current_token {
            self.advance();
            Some(self.parse_expression()?)
        } else {
            None
        };
        Ok(Statement::Preset { x, y, color })
    }

    fn parse_paint_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PAINT
        self.expect(&Token::LParen)?;
        let x = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let y = self.parse_expression()?;
        self.expect(&Token::RParen)?;
        Ok(Statement::Paint {
            x,
            y,
            paint_color: None,
            border_color: None,
        })
    }

    fn parse_draw_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume DRAW
        let commands = self.parse_expression()?;
        Ok(Statement::Draw { commands })
    }

    // Sound
    fn parse_beep_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume BEEP
        Ok(Statement::Beep)
    }

    fn parse_sound_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume SOUND
        let frequency = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let duration = self.parse_expression()?;
        Ok(Statement::Sound {
            frequency,
            duration,
        })
    }

    // Screen Control
    fn parse_locate_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume LOCATE
        let row = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let column = self.parse_expression()?;
        Ok(Statement::Locate { row, column })
    }

    fn parse_screen_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume SCREEN
        let mode = self.parse_expression()?;
        Ok(Statement::Screen { mode })
    }

    fn parse_width_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume WIDTH
        let width = self.parse_expression()?;
        Ok(Statement::Width { width })
    }

    fn parse_palette_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PALETTE
        let attribute = self.parse_expression()?;
        self.expect(&Token::Comma)?;
        let color = self.parse_expression()?;
        Ok(Statement::Palette { attribute, color })
    }

    // Error Handling
    fn parse_on_error_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume ON
        self.expect(&Token::Error)?;
        let line_number = if let Some(Token::Goto) = self.current_token {
            self.advance();
            Some(self.parse_line_number()?)
        } else {
            None
        };
        Ok(Statement::OnError { line_number })
    }

    fn parse_resume_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume RESUME
        let line_number = if let Some(Token::Number(_)) = self.current_token {
            Some(self.parse_line_number()?)
        } else {
            None
        };
        Ok(Statement::Resume { line_number })
    }

    // Control Flow
    fn parse_while_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume WHILE
        let condition = self.parse_expression()?;
        Ok(Statement::While { condition })
    }

    fn parse_wend_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume WEND
        Ok(Statement::Wend)
    }

    fn parse_select_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume SELECT
        self.expect(&Token::Case)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Select { expression })
    }

    fn parse_case_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume CASE
        let mut conditions = Vec::new();

        // Check for "IS" condition
        if let Some(Token::Is) = self.current_token {
            self.advance(); // consume IS
            let operator = match self.current_token {
                Some(Token::Equal) => "=",
                Some(Token::Greater) => ">",
                Some(Token::Less) => "<",
                Some(Token::GreaterEqual) => ">=",
                Some(Token::LessEqual) => "<=",
                Some(Token::NotEqual) => "<>",
                _ => {
                    return Err(InterpreterError::ParseError(
                        "Expected comparison operator after IS".to_string(),
                    ))
                }
            };
            self.advance(); // consume operator
            let value = self.parse_expression()?;
            conditions.push(CaseCondition::Is {
                operator: operator.to_string(),
                value,
            });
        } else {
            // Parse value or range
            loop {
                let start = self.parse_expression()?;
                if let Some(Token::To) = self.current_token {
                    self.advance(); // consume TO
                    let end = self.parse_expression()?;
                    conditions.push(CaseCondition::Range { start, end });
                } else {
                    conditions.push(CaseCondition::Value(start));
                }

                if let Some(Token::Comma) = self.current_token {
                    self.advance();
                } else {
                    break;
                }
            }
        }
        Ok(Statement::Case { conditions })
    }

    fn parse_default_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume DEFAULT
        Ok(Statement::Default)
    }

    // System
    fn parse_system_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume SYSTEM
        Ok(Statement::System)
    }

    fn parse_files_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume FILES
        let pattern = if let Some(Token::String(_)) = self.current_token {
            Some(self.parse_expression()?)
        } else {
            None
        };
        Ok(Statement::Files { pattern })
    }

    fn parse_kill_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume KILL
        let file_name = self.parse_expression()?;
        Ok(Statement::Kill { file_name })
    }

    fn parse_name_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume NAME
        let old_name = self.parse_expression()?;
        self.expect(&Token::As)?;
        let new_name = self.parse_expression()?;
        Ok(Statement::Name { old_name, new_name })
    }

    fn parse_chdir_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume CHDIR
        let path = self.parse_expression()?;
        Ok(Statement::Chdir { path })
    }

    fn parse_mkdir_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume MKDIR
        let path = self.parse_expression()?;
        Ok(Statement::Mkdir { path })
    }

    fn parse_rmdir_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume RMDIR
        let path = self.parse_expression()?;
        Ok(Statement::Rmdir { path })
    }

    // Array
    fn parse_erase_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume ERASE
        let mut arrays = Vec::new();
        loop {
            if let Some(Token::Identifier(ref id)) = self.current_token {
                arrays.push(id.clone());
                self.advance();
            }
            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }
        Ok(Statement::Erase { arrays })
    }

    fn parse_option_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume OPTION
        self.expect(&Token::Base)?;
        let base = self.parse_expression()?;
        Ok(Statement::OptionBase { base })
    }

    fn parse_expression(&mut self) -> Result<Expression, InterpreterError> {
        self.parse_logical_or()
    }

    fn parse_print_expressions(
        &mut self,
    ) -> Result<(Vec<Expression>, PrintSeparator), InterpreterError> {
        let mut expressions = Vec::new();

        // Parse first expression or TAB/SPC function
        if let Some(ref token) = self.current_token {
            if !matches!(
                token,
                Token::Colon | Token::EndOfFile | Token::Comma | Token::Semicolon
            ) {
                let expr = self.parse_print_item()?;
                expressions.push(expr);
            }
        }

        // Parse remaining expressions separated by commas or semicolons
        let mut separator = PrintSeparator::None;
        while let Some(ref token) = self.current_token {
            match token {
                Token::Colon | Token::EndOfFile => break,
                Token::Comma => {
                    separator = PrintSeparator::Comma;
                    self.advance();
                    if let Some(ref token) = self.current_token {
                        if !matches!(token, Token::Colon | Token::EndOfFile) {
                            let expr = self.parse_print_item()?;
                            expressions.push(expr);
                        }
                    }
                }
                Token::Semicolon => {
                    separator = PrintSeparator::Semicolon;
                    self.advance();
                    if let Some(ref token) = self.current_token {
                        if !matches!(token, Token::Colon | Token::EndOfFile) {
                            let expr = self.parse_print_item()?;
                            expressions.push(expr);
                        }
                    }
                }
                _ => break, // No more separators
            }
        }

        Ok((expressions, separator))
    }

    fn parse_print_item(&mut self) -> Result<Expression, InterpreterError> {
        // Check for TAB or SPC functions
        if let Some(Token::Tab) = self.current_token {
            self.advance(); // consume TAB
            self.expect(&Token::LParen)?;
            let expr = self.parse_expression()?;
            self.expect(&Token::RParen)?;
            Ok(Expression::Tab(Box::new(expr)))
        } else if let Some(Token::Spc) = self.current_token {
            self.advance(); // consume SPC
            self.expect(&Token::LParen)?;
            let expr = self.parse_expression()?;
            self.expect(&Token::RParen)?;
            Ok(Expression::Spc(Box::new(expr)))
        } else {
            // Regular expression
            self.parse_expression()
        }
    }

    fn parse_line_number(&mut self) -> Result<usize, InterpreterError> {
        if let Some(Token::Number(line_num)) = self.current_token {
            let line = line_num as usize;
            self.advance();
            Ok(line)
        } else {
            Err(InterpreterError::ParseError(
                "Expected line number".to_string(),
            ))
        }
    }

    fn parse_logical_or(&mut self) -> Result<Expression, InterpreterError> {
        let mut left = self.parse_logical_and()?;

        while let Some(Token::Or) = self.current_token {
            self.advance();
            let right = self.parse_logical_and()?;
            left = Expression::BinaryOp {
                left: Box::new(left),
                operator: BinaryOperator::Or,
                right: Box::new(right),
            };
        }

        Ok(left)
    }

    fn parse_logical_and(&mut self) -> Result<Expression, InterpreterError> {
        let mut left = self.parse_comparison()?;

        while let Some(Token::And) = self.current_token {
            self.advance();
            let right = self.parse_comparison()?;
            left = Expression::BinaryOp {
                left: Box::new(left),
                operator: BinaryOperator::And,
                right: Box::new(right),
            };
        }

        Ok(left)
    }

    fn parse_comparison(&mut self) -> Result<Expression, InterpreterError> {
        let mut left = self.parse_additive()?;

        while let Some(ref token) = self.current_token {
            let operator = match token {
                Token::Equal => Some(BinaryOperator::Equal),
                Token::NotEqual => Some(BinaryOperator::NotEqual),
                Token::Less => Some(BinaryOperator::Less),
                Token::LessEqual => Some(BinaryOperator::LessEqual),
                Token::Greater => Some(BinaryOperator::Greater),
                Token::GreaterEqual => Some(BinaryOperator::GreaterEqual),
                _ => None,
            };

            if let Some(op) = operator {
                self.advance();
                let right = self.parse_additive()?;
                left = Expression::BinaryOp {
                    left: Box::new(left),
                    operator: op,
                    right: Box::new(right),
                };
            } else {
                break;
            }
        }

        Ok(left)
    }

    fn parse_additive(&mut self) -> Result<Expression, InterpreterError> {
        let mut left = self.parse_multiplicative()?;

        while let Some(ref token) = self.current_token {
            let operator = match token {
                Token::Plus => Some(BinaryOperator::Plus),
                Token::Minus => Some(BinaryOperator::Minus),
                _ => None,
            };

            if let Some(op) = operator {
                self.advance();
                let right = self.parse_multiplicative()?;
                left = Expression::BinaryOp {
                    left: Box::new(left),
                    operator: op,
                    right: Box::new(right),
                };
            } else {
                break;
            }
        }

        Ok(left)
    }

    fn parse_multiplicative(&mut self) -> Result<Expression, InterpreterError> {
        let mut left = self.parse_unary()?;

        while let Some(ref token) = self.current_token {
            let operator = match token {
                Token::Multiply => Some(BinaryOperator::Multiply),
                Token::Divide => Some(BinaryOperator::Divide),
                Token::Mod => Some(BinaryOperator::Mod),
                _ => None,
            };

            if let Some(op) = operator {
                self.advance();
                let right = self.parse_unary()?;
                left = Expression::BinaryOp {
                    left: Box::new(left),
                    operator: op,
                    right: Box::new(right),
                };
            } else {
                break;
            }
        }

        Ok(left)
    }

    fn parse_unary(&mut self) -> Result<Expression, InterpreterError> {
        if let Some(Token::Minus) = self.current_token {
            self.advance();
            let expr = self.parse_power()?;
            Ok(Expression::UnaryOp {
                operator: UnaryOperator::Minus,
                operand: Box::new(expr),
            })
        } else if let Some(Token::Not) = self.current_token {
            self.advance();
            let expr = self.parse_power()?;
            Ok(Expression::UnaryOp {
                operator: UnaryOperator::Not,
                operand: Box::new(expr),
            })
        } else {
            self.parse_power()
        }
    }

    fn parse_power(&mut self) -> Result<Expression, InterpreterError> {
        let mut left = self.parse_primary()?;

        if let Some(Token::Power) = self.current_token {
            self.advance();
            let right = self.parse_unary()?; // Right associative
            left = Expression::BinaryOp {
                left: Box::new(left),
                operator: BinaryOperator::Power,
                right: Box::new(right),
            };
        }

        Ok(left)
    }

    fn parse_primary(&mut self) -> Result<Expression, InterpreterError> {
        match self.current_token.clone() {
            Some(Token::Number(n)) => {
                self.advance();
                Ok(Expression::Number(n))
            }
            Some(Token::String(s)) => {
                let string_val = s.clone();
                self.advance();
                Ok(Expression::String(string_val))
            }
            Some(Token::Identifier(ref id)) => {
                let ident = id.clone();
                self.advance();

                // Check if it's a function call
                if let Some(Token::LParen) = self.current_token {
                    self.advance();
                    let mut arguments = Vec::new();

                    if let Some(Token::RParen) = self.current_token {
                        self.advance();
                    } else {
                        loop {
                            let arg = self.parse_expression()?;
                            arguments.push(arg);

                            if let Some(Token::Comma) = self.current_token {
                                self.advance();
                            } else {
                                self.expect(&Token::RParen)?;
                                break;
                            }
                        }
                    }

                    Ok(Expression::FunctionCall {
                        name: ident,
                        arguments,
                    })
                } else if let Some(Token::LParen) = self.current_token {
                    // Array access
                    self.advance();
                    let index = self.parse_expression()?;
                    self.expect(&Token::RParen)?;
                    Ok(Expression::ArrayAccess {
                        name: ident,
                        index: Box::new(index),
                    })
                } else {
                    Ok(Expression::Variable(ident))
                }
            }
            Some(Token::LParen) => {
                self.advance();
                let expr = self.parse_expression()?;
                self.expect(&Token::RParen)?;
                Ok(expr)
            }
            _ => Err(InterpreterError::ParseError(format!(
                "Unexpected token in expression: {:?}",
                self.current_token
            ))),
        }
    }

    fn parse_identifier(&mut self) -> Result<String, InterpreterError> {
        if let Some(Token::Identifier(id)) = self.current_token.clone() {
            self.advance();
            Ok(id)
        } else {
            Err(InterpreterError::ParseError(
                "Expected identifier".to_string(),
            ))
        }
    }

    fn parse_string_literal(&mut self) -> Result<String, InterpreterError> {
        if let Some(Token::String(s)) = self.current_token.clone() {
            self.advance();
            Ok(s)
        } else {
            Err(InterpreterError::ParseError(
                "Expected string literal".to_string(),
            ))
        }
    }

    fn parse_statement_list(&mut self) -> Result<Vec<Statement>, InterpreterError> {
        let mut statements = Vec::new();

        while let Some(ref token) = self.current_token {
            match token {
                Token::Colon | Token::EndOfFile => break,
                _ => {
                    let stmt = self.parse_statement()?;
                    statements.push(stmt);
                }
            }
        }

        Ok(statements)
    }
}

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub enum InterpreterError {
    ParseError(String),
    TypeError(String),
    RuntimeError(String),
}

#[derive(Clone)]
#[allow(dead_code)]
pub enum ExecutionResult {
    Complete {
        output: String,
        graphics_commands: Vec<GraphicsCommand>,
    },
    NeedInput {
        variable_name: String,
        prompt: String,
        partial_output: String,
        partial_graphics: Vec<GraphicsCommand>,
    },
    Error(InterpreterError),
}

#[derive(Clone)]
#[allow(dead_code)]
pub struct GraphicsCommand {
    pub command: String,
    pub value: f32,
    pub color: Option<u32>,
}

pub struct BasicInterpreter {
    variables: HashMap<String, Value>,
    arrays: HashMap<String, Vec<Value>>,
    functions: HashMap<String, FunctionDefinition>,
    current_line: usize,
    pending_input: Option<(String, String)>, // (var, prompt)
    data_pointer: usize,
    data: Vec<String>,
    for_loops: Vec<ForLoop>,
    gosub_stack: Vec<usize>,
    text_color: u8,
    // files: HashMap<u8, FileHandle>,
    random_seed: u64,
    instruction_count: usize,
    pub max_instructions: usize,
    current_program: Option<Program>, // Store the parsed program for continuation
    current_output: String,           // Accumulate output across executions
    error_handler: Option<usize>,     // Line number for error handling
    loop_stack: Vec<usize>,           // Stack for WHILE loops
    select_value: Option<Value>,      // Current SELECT CASE value
    array_base: usize,                // Array base (0 or 1)
    print_position: usize,            // Current print position for comma tabulation
}

#[derive(Clone)]
enum Value {
    Number(f64),
    String(String),
}

#[derive(Clone)]
struct ForLoop {
    variable: String,
    end: f64,
    step: f64,
    line: usize,
}

#[derive(Clone)]
struct FunctionDefinition {
    parameter: String,
    expression: Expression,
}

impl BasicInterpreter {
    pub fn new() -> Self {
        Self {
            variables: HashMap::new(),
            arrays: HashMap::new(),
            functions: HashMap::new(),
            current_line: 0,
            pending_input: None,
            data_pointer: 0,
            data: Vec::new(),
            for_loops: Vec::new(),
            gosub_stack: Vec::new(),
            text_color: 7,
            random_seed: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            instruction_count: 0,
            max_instructions: 10000, // Default limit to prevent infinite loops
            current_program: None,
            current_output: String::new(),
            error_handler: None,
            loop_stack: Vec::new(),
            select_value: None,
            array_base: 0,
            print_position: 0,
        }
    }

    fn evaluate_expression(&mut self, expression: &Expression) -> Result<Value, InterpreterError> {
        match expression {
            Expression::Number(n) => Ok(Value::Number(*n)),
            Expression::String(s) => Ok(Value::String(s.clone())),
            Expression::Variable(name) => {
                if let Some(value) = self.variables.get(name) {
                    Ok(value.clone())
                } else {
                    Ok(Value::Number(0.0)) // Default to 0 for undefined variables
                }
            }
            Expression::UnaryOp { operator, operand } => {
                let operand_val = self.evaluate_expression(operand)?;
                match operator {
                    UnaryOperator::Not => match operand_val {
                        Value::Number(n) => {
                            if n == 0.0 {
                                Ok(Value::Number(1.0))
                            } else {
                                Ok(Value::Number(0.0))
                            }
                        }
                        _ => Err(InterpreterError::TypeError(
                            "NOT requires numeric operand".to_string(),
                        )),
                    },
                    UnaryOperator::Minus => match operand_val {
                        Value::Number(n) => Ok(Value::Number(-n)),
                        _ => Err(InterpreterError::TypeError(
                            "Unary minus requires numeric operand".to_string(),
                        )),
                    },
                }
            }
            Expression::BinaryOp {
                left,
                operator,
                right,
            } => {
                let left_val = self.evaluate_expression(left)?;
                let right_val = self.evaluate_expression(right)?;
                match (left_val, right_val) {
                    (Value::Number(l), Value::Number(r)) => {
                        let result = match operator {
                            BinaryOperator::Plus => l + r,
                            BinaryOperator::Minus => l - r,
                            BinaryOperator::Multiply => l * r,
                            BinaryOperator::Divide => {
                                if r == 0.0 {
                                    return Err(InterpreterError::RuntimeError(
                                        "Division by zero".to_string(),
                                    ));
                                }
                                l / r
                            }
                            BinaryOperator::Mod => l % r,
                            BinaryOperator::Power => l.powf(r),
                            BinaryOperator::Equal => {
                                if l == r {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::NotEqual => {
                                if l != r {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::Less => {
                                if l < r {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::LessEqual => {
                                if l <= r {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::Greater => {
                                if l > r {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::GreaterEqual => {
                                if l >= r {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::And => {
                                if l != 0.0 && r != 0.0 {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                            BinaryOperator::Or => {
                                if l != 0.0 || r != 0.0 {
                                    1.0
                                } else {
                                    0.0
                                }
                            }
                        };
                        Ok(Value::Number(result))
                    }
                    _ => Err(InterpreterError::TypeError(
                        "Type mismatch in binary operation".to_string(),
                    )),
                }
            }
            Expression::FunctionCall { name, arguments } => {
                let mut arg_values = Vec::new();
                for arg in arguments {
                    arg_values.push(self.evaluate_expression(arg)?);
                }
                self.evaluate_function(name, &arg_values)
            }
            Expression::ArrayAccess { name, index } => {
                let index_val = self.evaluate_expression(index)?;
                match index_val {
                    Value::Number(idx) => {
                        if let Some(array) = self.arrays.get(name) {
                            let idx_usize = idx as usize;
                            if idx_usize < array.len() {
                                Ok(array[idx_usize].clone())
                            } else {
                                Err(InterpreterError::RuntimeError(format!(
                                    "Array index out of bounds: {}",
                                    idx
                                )))
                            }
                        } else {
                            Err(InterpreterError::RuntimeError(format!(
                                "Array not defined: {}",
                                name
                            )))
                        }
                    }
                    _ => Err(InterpreterError::TypeError(
                        "Array index must be numeric".to_string(),
                    )),
                }
            }
            Expression::Tab(expr) => {
                // TAB is handled specially in PRINT statements, not evaluated as a regular expression
                Err(InterpreterError::RuntimeError(
                    "TAB can only be used in PRINT statements".to_string(),
                ))
            }
            Expression::Spc(expr) => {
                // SPC is handled specially in PRINT statements, not evaluated as a regular expression
                Err(InterpreterError::RuntimeError(
                    "SPC can only be used in PRINT statements".to_string(),
                ))
            }
        }
    }

    fn evaluate_function(
        &mut self,
        name: &str,
        arguments: &[Value],
    ) -> Result<Value, InterpreterError> {
        match name.to_uppercase().as_str() {
            "SIN" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.to_radians().sin()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "SIN requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "SIN requires 1 argument".to_string(),
                    ))
                }
            }
            "COS" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.to_radians().cos()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "COS requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "COS requires 1 argument".to_string(),
                    ))
                }
            }
            "TAN" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.to_radians().tan()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "TAN requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "TAN requires 1 argument".to_string(),
                    ))
                }
            }
            "SQR" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.sqrt()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "SQR requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "SQR requires 1 argument".to_string(),
                    ))
                }
            }
            "ABS" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.abs()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "ABS requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "ABS requires 1 argument".to_string(),
                    ))
                }
            }
            "INT" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.floor()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "INT requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "INT requires 1 argument".to_string(),
                    ))
                }
            }
            "LOG" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        if n > 0.0 {
                            Ok(Value::Number(n.ln()))
                        } else {
                            Err(InterpreterError::RuntimeError(
                                "LOG requires positive argument".to_string(),
                            ))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "LOG requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "LOG requires 1 argument".to_string(),
                    ))
                }
            }
            "EXP" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.exp()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "EXP requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "EXP requires 1 argument".to_string(),
                    ))
                }
            }
            "ATN" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::Number(n.atan()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "ATN requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "ATN requires 1 argument".to_string(),
                    ))
                }
            }
            "RND" => {
                if arguments.is_empty() {
                    // Simple random number between 0 and 1
                    let random_val =
                        (self.random_seed as f64 * 9301.0 + 49297.0) % 233280.0 / 233280.0;
                    self.random_seed = (self.random_seed * 9301 + 49297) % 233280;
                    Ok(Value::Number(random_val))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "RND takes no arguments".to_string(),
                    ))
                }
            }
            "RANDOMIZE" => {
                if arguments.len() == 1 {
                    if let Value::Number(seed) = arguments[0] {
                        self.random_seed = seed as u64;
                        Ok(Value::Number(0.0))
                    } else {
                        Err(InterpreterError::TypeError(
                            "RANDOMIZE requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "RANDOMIZE requires 1 argument".to_string(),
                    ))
                }
            }
            "LEN" => {
                if arguments.len() == 1 {
                    if let Value::String(s) = &arguments[0] {
                        Ok(Value::Number(s.len() as f64))
                    } else {
                        Err(InterpreterError::TypeError(
                            "LEN requires string argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "LEN requires 1 argument".to_string(),
                    ))
                }
            }
            "MID" => {
                if arguments.len() == 3 {
                    if let (Value::String(s), Value::Number(start), Value::Number(length)) =
                        (&arguments[0], &arguments[1], &arguments[2])
                    {
                        let start_idx = *start as usize;
                        let len = *length as usize;
                        if start_idx < s.len() {
                            let end_idx = (start_idx + len).min(s.len());
                            Ok(Value::String(s[start_idx..end_idx].to_string()))
                        } else {
                            Ok(Value::String(String::new()))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "MID requires string, number, number arguments".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "MID requires 3 arguments".to_string(),
                    ))
                }
            }
            "LEFT" => {
                if arguments.len() == 2 {
                    if let (Value::String(s), Value::Number(length)) =
                        (&arguments[0], &arguments[1])
                    {
                        let len = *length as usize;
                        if len >= s.len() {
                            Ok(Value::String(s.clone()))
                        } else {
                            Ok(Value::String(s[..len].to_string()))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "LEFT requires string, number arguments".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "LEFT requires 2 arguments".to_string(),
                    ))
                }
            }
            "RIGHT" => {
                if arguments.len() == 2 {
                    if let (Value::String(s), Value::Number(length)) =
                        (&arguments[0], &arguments[1])
                    {
                        let len = *length as usize;
                        if len >= s.len() {
                            Ok(Value::String(s.clone()))
                        } else {
                            let start = s.len() - len;
                            Ok(Value::String(s[start..].to_string()))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "RIGHT requires string, number arguments".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "RIGHT requires 2 arguments".to_string(),
                    ))
                }
            }
            "CHR" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        if n >= 0.0 && n <= 255.0 {
                            Ok(Value::String((n as u8 as char).to_string()))
                        } else {
                            Err(InterpreterError::RuntimeError(
                                "CHR argument must be between 0 and 255".to_string(),
                            ))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "CHR requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "CHR requires 1 argument".to_string(),
                    ))
                }
            }
            "ASC" => {
                if arguments.len() == 1 {
                    if let Value::String(s) = &arguments[0] {
                        if !s.is_empty() {
                            Ok(Value::Number(s.as_bytes()[0] as f64))
                        } else {
                            Err(InterpreterError::RuntimeError(
                                "ASC requires non-empty string".to_string(),
                            ))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "ASC requires string argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "ASC requires 1 argument".to_string(),
                    ))
                }
            }
            "VAL" => {
                if arguments.len() == 1 {
                    if let Value::String(s) = &arguments[0] {
                        if let Ok(num) = s.trim().parse::<f64>() {
                            Ok(Value::Number(num))
                        } else {
                            Ok(Value::Number(0.0))
                        }
                    } else {
                        Err(InterpreterError::TypeError(
                            "VAL requires string argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "VAL requires 1 argument".to_string(),
                    ))
                }
            }
            "STR" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        Ok(Value::String(n.to_string()))
                    } else {
                        Err(InterpreterError::TypeError(
                            "STR requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "STR requires 1 argument".to_string(),
                    ))
                }
            }
            "TAB" => {
                if arguments.len() == 1 {
                    if let Value::Number(n) = arguments[0] {
                        let column = n as usize;
                        // TAB function returns spaces to reach the specified column
                        // This is a simplified implementation - in real BASIC it would
                        // position relative to current cursor position
                        let spaces = if column > 0 {
                            " ".repeat(column)
                        } else {
                            String::new()
                        };
                        Ok(Value::String(spaces))
                    } else {
                        Err(InterpreterError::TypeError(
                            "TAB requires numeric argument".to_string(),
                        ))
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "TAB requires 1 argument".to_string(),
                    ))
                }
            }
            _ => Err(InterpreterError::RuntimeError(format!(
                "Unknown function: {}",
                name
            ))),
        }
    }

    fn execute_statement(
        &mut self,
        statement: &Statement,
        graphics_commands: &mut Vec<GraphicsCommand>,
    ) -> Result<Option<String>, InterpreterError> {
        match *statement {
            Statement::Let {
                ref variable,
                ref expression,
            } => {
                let value = self.evaluate_expression(expression)?;
                self.variables.insert(variable.clone(), value);
                Ok(None)
            }
            Statement::Print {
                ref expressions,
                ref separator,
            } => {
                // Reset print position at start of PRINT statement (GW-BASIC behavior)
                self.print_position = 0;
                let mut result = String::new();

                for (i, expr) in expressions.iter().enumerate() {
                    if i > 0 {
                        // Handle comma tabulation like GW-BASIC (every 14 characters)
                        match separator {
                            PrintSeparator::Comma => {
                                let tab_width = 14;
                                let spaces_needed = tab_width - (self.print_position % tab_width);
                                for _ in 0..spaces_needed {
                                    result.push(' ');
                                    self.print_position += 1;
                                }
                            }
                            PrintSeparator::Semicolon => {
                                // No spacing for semicolon
                            }
                            PrintSeparator::None => {
                                result.push(' ');
                                self.print_position += 1;
                            }
                        }
                    }

                    // Handle TAB and SPC functions specially
                    match expr {
                        Expression::Tab(tab_expr) => {
                            let tab_value = self.evaluate_expression(tab_expr)?;
                            if let Value::Number(n) = tab_value {
                                let target_column = n as usize;
                                while self.print_position < target_column {
                                    result.push(' ');
                                    self.print_position += 1;
                                }
                            } else {
                                return Err(InterpreterError::TypeError(
                                    "TAB argument must be numeric".to_string(),
                                ));
                            }
                        }
                        Expression::Spc(spc_expr) => {
                            let spc_value = self.evaluate_expression(spc_expr)?;
                            if let Value::Number(n) = spc_value {
                                let spaces = n as usize;
                                for _ in 0..spaces {
                                    result.push(' ');
                                    self.print_position += 1;
                                }
                            } else {
                                return Err(InterpreterError::TypeError(
                                    "SPC argument must be numeric".to_string(),
                                ));
                            }
                        }
                        _ => {
                            let value = self.evaluate_expression(expr)?;
                            let value_str = match value {
                                Value::Number(n) => format!("{}", n),
                                Value::String(s) => s,
                            };

                            result.push_str(&value_str);
                            self.print_position += value_str.len();
                        }
                    }
                }

                self.current_output.push_str(&result);

                // Add newline unless the separator is semicolon (GW-BASIC behavior)
                if !matches!(separator, PrintSeparator::Semicolon) {
                    self.current_output.push('\n');
                    self.print_position = 0; // Reset position after newline
                }

                Ok(None)
            }
            Statement::Writeln {
                ref expressions,
                ref separator,
            } => {
                let mut result = String::new();
                for (i, expr) in expressions.iter().enumerate() {
                    if i > 0 {
                        match separator {
                            PrintSeparator::Comma => result.push('\t'),
                            PrintSeparator::Semicolon => {}
                            PrintSeparator::None => result.push(' '),
                        }
                    }
                    let value = self.evaluate_expression(expr)?;
                    match value {
                        Value::Number(n) => result.push_str(&format!("{}", n)),
                        Value::String(s) => result.push_str(&s),
                    }
                }
                self.current_output.push_str(&result);
                self.current_output.push('\n');
                Ok(None)
            }
            Statement::Readln {
                ref prompt,
                ref variables,
            } => {
                if let Some(prompt_text) = prompt {
                    self.current_output.push_str(prompt_text);
                } else {
                    self.current_output.push_str("? ");
                }
                // For now, return the prompt - input handling would need more complex logic
                Ok(Some(format!(
                    "Input required for variables: {:?}",
                    variables
                )))
            }
            Statement::Forward { ref distance } => {
                let dist_value = self.evaluate_expression(distance)?;
                if let Value::Number(dist) = dist_value {
                    graphics_commands.push(GraphicsCommand {
                        command: "FORWARD".to_string(),
                        value: dist as f32,
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Moved forward {}", dist));
                    self.current_output.push('\n');
                }
                Ok(None)
            }
            Statement::Back { ref distance } => {
                let dist_value = self.evaluate_expression(distance)?;
                if let Value::Number(dist) = dist_value {
                    graphics_commands.push(GraphicsCommand {
                        command: "FORWARD".to_string(),
                        value: -(dist as f32),
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Moved back {}", dist));
                    self.current_output.push('\n');
                }
                Ok(None)
            }
            Statement::Left { ref angle } => {
                let angle_value = self.evaluate_expression(angle)?;
                if let Value::Number(ang) = angle_value {
                    graphics_commands.push(GraphicsCommand {
                        command: "TURN".to_string(),
                        value: -(ang as f32),
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Turned left {} degrees", ang));
                    self.current_output.push('\n');
                }
                Ok(None)
            }
            Statement::Right { ref angle } => {
                let angle_value = self.evaluate_expression(angle)?;
                if let Value::Number(ang) = angle_value {
                    graphics_commands.push(GraphicsCommand {
                        command: "TURN".to_string(),
                        value: ang as f32,
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Turned right {} degrees", ang));
                    self.current_output.push('\n');
                }
                Ok(None)
            }
            Statement::Penup => {
                graphics_commands.push(GraphicsCommand {
                    command: "PENUP".to_string(),
                    value: 0.0,
                    color: None,
                });
                self.current_output.push_str("Pen up\n");
                Ok(None)
            }
            Statement::Pendown => {
                graphics_commands.push(GraphicsCommand {
                    command: "PENDOWN".to_string(),
                    value: 0.0,
                    color: None,
                });
                self.current_output.push_str("Pen down\n");
                Ok(None)
            }
            Statement::If {
                ref condition,
                ref then_statements,
                ref else_statements,
            } => {
                let condition_value = self.evaluate_expression(condition)?;
                let condition_met = match condition_value {
                    Value::Number(n) => n != 0.0,
                    Value::String(s) => !s.is_empty(),
                };
                if condition_met {
                    for stmt in then_statements {
                        let result = self.execute_statement(stmt, graphics_commands)?;
                        if result.is_some() {
                            return Ok(result);
                        }
                    }
                } else if let Some(else_stmts) = else_statements {
                    for stmt in else_stmts {
                        let result = self.execute_statement(stmt, graphics_commands)?;
                        if result.is_some() {
                            return Ok(result);
                        }
                    }
                }
                Ok(None)
            }
            Statement::For {
                ref variable,
                ref start,
                ref end,
                ref step,
            } => {
                let start_val = self.evaluate_expression(start)?;
                let end_val = self.evaluate_expression(end)?;
                let step_val = if let Some(ref s) = *step {
                    self.evaluate_expression(s)?
                } else {
                    Value::Number(1.0)
                };
                match (start_val, end_val, step_val) {
                    (Value::Number(s), Value::Number(e), Value::Number(st)) => {
                        self.variables.insert(variable.clone(), Value::Number(s));
                        self.for_loops.push(ForLoop {
                            variable: variable.clone(),
                            end: e,
                            step: st,
                            line: self.current_line,
                        });
                        Ok(None)
                    }
                    _ => Err(InterpreterError::TypeError(
                        "FOR loop requires numeric values".to_string(),
                    )),
                }
            }
            Statement::Next { ref variable } => {
                if let Some(loop_info) = self.for_loops.last_mut() {
                    if let Some(ref var) = *variable {
                        if *var != loop_info.variable {
                            return Err(InterpreterError::RuntimeError(
                                "NEXT variable doesn't match FOR".to_string(),
                            ));
                        }
                    }
                    if let Some(Value::Number(current_val)) =
                        self.variables.get(&loop_info.variable)
                    {
                        let next_val = current_val + loop_info.step;
                        let should_continue = if loop_info.step > 0.0 {
                            next_val <= loop_info.end
                        } else {
                            next_val >= loop_info.end
                        };
                        if should_continue {
                            self.variables
                                .insert(loop_info.variable.clone(), Value::Number(next_val));
                            self.current_line = loop_info.line + 1; // Jump to statement after FOR
                            return Ok(Some("CONTINUE_LOOP".to_string()));
                        } else {
                            self.for_loops.pop();
                        }
                    } else {
                        return Err(InterpreterError::RuntimeError(
                            "FOR loop variable not found".to_string(),
                        ));
                    }
                } else {
                    return Err(InterpreterError::RuntimeError(
                        "NEXT without FOR".to_string(),
                    ));
                }
                Ok(None)
            }
            Statement::Goto { line_number } => Ok(Some(format!("GOTO {}", line_number))),
            Statement::Gosub { line_number } => {
                self.gosub_stack.push(self.current_line);
                Ok(Some(format!("GOTO {}", line_number)))
            }
            Statement::Return => {
                if let Some(return_line) = self.gosub_stack.pop() {
                    self.current_line = return_line;
                    return Ok(Some("CONTINUE_LOOP".to_string()));
                } else {
                    return Err(InterpreterError::RuntimeError(
                        "RETURN without GOSUB".to_string(),
                    ));
                }
            }
            Statement::On {
                ref expression,
                ref line_numbers,
                is_gosub,
            } => {
                let expr_val = self.evaluate_expression(expression)?;
                match expr_val {
                    Value::Number(n) => {
                        let index = n as usize;
                        if index > 0 && index <= line_numbers.len() {
                            let target_line = line_numbers[index - 1];
                            if is_gosub {
                                self.gosub_stack.push(self.current_line);
                            }
                            Ok(Some(format!("GOTO {}", target_line)))
                        } else {
                            Ok(None)
                        }
                    }
                    _ => Err(InterpreterError::TypeError(
                        "ON requires numeric expression".to_string(),
                    )),
                }
            }
            Statement::Input {
                ref prompt,
                ref variables,
            } => {
                if let Some(p) = prompt {
                    self.current_output.push_str(p);
                    self.current_output.push('?');
                    self.current_output.push(' ');
                }
                self.pending_input =
                    Some((variables.join(","), prompt.clone().unwrap_or_default()));
                Ok(None)
            }
            Statement::Dim { ref arrays } => {
                for (name, size_expr) in arrays {
                    let size_val = self.evaluate_expression(size_expr)?;
                    match size_val {
                        Value::Number(size) => {
                            let size_usize = size as usize;
                            let array = vec![Value::Number(0.0); size_usize];
                            self.arrays.insert(name.clone(), array);
                        }
                        _ => {
                            return Err(InterpreterError::TypeError(
                                "DIM requires numeric size".to_string(),
                            ))
                        }
                    }
                }
                Ok(None)
            }
            Statement::Data { ref values } => {
                for value in values {
                    self.data.push(value.clone());
                }
                Ok(None)
            }
            Statement::Read { ref variables } => {
                for var in variables {
                    if self.data_pointer < self.data.len() {
                        let value_str = &self.data[self.data_pointer];
                        self.data_pointer += 1;
                        // Try to parse as number, otherwise treat as string
                        if let Ok(num) = value_str.parse::<f64>() {
                            self.variables.insert(var.clone(), Value::Number(num));
                        } else {
                            self.variables
                                .insert(var.clone(), Value::String(value_str.clone()));
                        }
                    } else {
                        return Err(InterpreterError::RuntimeError(
                            "READ without DATA".to_string(),
                        ));
                    }
                }
                Ok(None)
            }
            Statement::Restore => {
                self.data_pointer = 0;
                Ok(None)
            }
            Statement::End => Ok(Some("END".to_string())),
            Statement::Stop => Ok(Some("END".to_string())),
            Statement::Cls => {
                graphics_commands.push(GraphicsCommand {
                    command: "CLS".to_string(),
                    value: 0.0,
                    color: None,
                });
                Ok(None)
            }
            Statement::Color { ref color } => {
                let color_val = self.evaluate_expression(color)?;
                match color_val {
                    Value::Number(c) => {
                        self.text_color = c as u8;
                        graphics_commands.push(GraphicsCommand {
                            command: "COLOR".to_string(),
                            value: c as f32,
                            color: Some(c as u32),
                        });
                    }
                    _ => {
                        return Err(InterpreterError::TypeError(
                            "COLOR requires numeric value".to_string(),
                        ))
                    }
                }
                Ok(None)
            }
            Statement::GraphicsForward { ref distance } => {
                let dist_val = self.evaluate_expression(distance)?;
                match dist_val {
                    Value::Number(d) => {
                        graphics_commands.push(GraphicsCommand {
                            command: "FORWARD".to_string(),
                            value: d as f32,
                            color: None,
                        });
                    }
                    _ => {
                        return Err(InterpreterError::TypeError(
                            "FORWARD requires numeric distance".to_string(),
                        ))
                    }
                }
                Ok(None)
            }
            Statement::GraphicsRight { ref angle } => {
                let angle_val = self.evaluate_expression(angle)?;
                match angle_val {
                    Value::Number(a) => {
                        graphics_commands.push(GraphicsCommand {
                            command: "RIGHT".to_string(),
                            value: a as f32,
                            color: None,
                        });
                    }
                    _ => {
                        return Err(InterpreterError::TypeError(
                            "RIGHT requires numeric angle".to_string(),
                        ))
                    }
                }
                Ok(None)
            }
            Statement::Rem { .. } => Ok(None),

            // File I/O
            Statement::Open { .. } => {
                // TODO: Implement file opening
                self.current_output.push_str("OPEN not yet implemented\n");
                Ok(None)
            }
            Statement::Close { .. } => {
                // TODO: Implement file closing
                self.current_output.push_str("CLOSE not yet implemented\n");
                Ok(None)
            }
            Statement::PrintHash { .. } => {
                // TODO: Implement file printing
                self.current_output.push_str("PRINT# not yet implemented\n");
                Ok(None)
            }
            Statement::InputHash { .. } => {
                // TODO: Implement file input
                self.current_output.push_str("INPUT# not yet implemented\n");
                Ok(None)
            }

            // Graphics
            Statement::Line {
                ref x1,
                ref y1,
                ref x2,
                ref y2,
                ref color,
                ..
            } => {
                let x1_val = self.evaluate_expression(x1)?;
                let y1_val = self.evaluate_expression(y1)?;
                let x2_val = self.evaluate_expression(x2)?;
                let y2_val = self.evaluate_expression(y2)?;
                if let (
                    Value::Number(x1),
                    Value::Number(y1),
                    Value::Number(x2),
                    Value::Number(y2),
                ) = (x1_val, y1_val, x2_val, y2_val)
                {
                    graphics_commands.push(GraphicsCommand {
                        command: "LINE".to_string(),
                        value: 0.0,
                        color: color
                            .as_ref()
                            .and_then(|c| self.evaluate_expression(c).ok())
                            .and_then(|v| {
                                if let Value::Number(n) = v {
                                    Some(n as u32)
                                } else {
                                    None
                                }
                            }),
                    });
                    // Store line coordinates for rendering
                    self.current_output.push_str(&format!(
                        "Drew line from ({}, {}) to ({}, {})\n",
                        x1, y1, x2, y2
                    ));
                }
                Ok(None)
            }
            Statement::Circle {
                ref x,
                ref y,
                ref radius,
                ref color,
                ..
            } => {
                let x_val = self.evaluate_expression(x)?;
                let y_val = self.evaluate_expression(y)?;
                let r_val = self.evaluate_expression(radius)?;
                if let (Value::Number(x), Value::Number(y), Value::Number(r)) =
                    (x_val, y_val, r_val)
                {
                    graphics_commands.push(GraphicsCommand {
                        command: "CIRCLE".to_string(),
                        value: r as f32,
                        color: color
                            .as_ref()
                            .and_then(|c| self.evaluate_expression(c).ok())
                            .and_then(|v| {
                                if let Value::Number(n) = v {
                                    Some(n as u32)
                                } else {
                                    None
                                }
                            }),
                    });
                    self.current_output
                        .push_str(&format!("Drew circle at ({}, {}) radius {}\n", x, y, r));
                }
                Ok(None)
            }
            Statement::Pset {
                ref x,
                ref y,
                ref color,
            } => {
                let x_val = self.evaluate_expression(x)?;
                let y_val = self.evaluate_expression(y)?;
                if let (Value::Number(x), Value::Number(y)) = (x_val, y_val) {
                    graphics_commands.push(GraphicsCommand {
                        command: "PSET".to_string(),
                        value: 0.0,
                        color: color
                            .as_ref()
                            .and_then(|c| self.evaluate_expression(c).ok())
                            .and_then(|v| {
                                if let Value::Number(n) = v {
                                    Some(n as u32)
                                } else {
                                    None
                                }
                            }),
                    });
                    self.current_output
                        .push_str(&format!("Set pixel at ({}, {})\n", x, y));
                }
                Ok(None)
            }
            Statement::Preset {
                ref x,
                ref y,
                ref color,
            } => {
                let x_val = self.evaluate_expression(x)?;
                let y_val = self.evaluate_expression(y)?;
                if let (Value::Number(x), Value::Number(y)) = (x_val, y_val) {
                    graphics_commands.push(GraphicsCommand {
                        command: "PRESET".to_string(),
                        value: 0.0,
                        color: color
                            .as_ref()
                            .and_then(|c| self.evaluate_expression(c).ok())
                            .and_then(|v| {
                                if let Value::Number(n) = v {
                                    Some(n as u32)
                                } else {
                                    None
                                }
                            }),
                    });
                    self.current_output
                        .push_str(&format!("Reset pixel at ({}, {})\n", x, y));
                }
                Ok(None)
            }
            Statement::Paint { .. } => {
                // TODO: Implement paint
                self.current_output.push_str("PAINT not yet implemented\n");
                Ok(None)
            }
            Statement::Draw { .. } => {
                // TODO: Implement draw
                self.current_output.push_str("DRAW not yet implemented\n");
                Ok(None)
            }

            // Sound
            Statement::Beep => {
                graphics_commands.push(GraphicsCommand {
                    command: "BEEP".to_string(),
                    value: 0.0,
                    color: None,
                });
                self.current_output.push_str("Beep!\n");
                Ok(None)
            }
            Statement::Sound {
                ref frequency,
                ref duration,
            } => {
                let freq_val = self.evaluate_expression(frequency)?;
                let dur_val = self.evaluate_expression(duration)?;
                if let (Value::Number(freq), Value::Number(dur)) = (freq_val, dur_val) {
                    graphics_commands.push(GraphicsCommand {
                        command: "SOUND".to_string(),
                        value: freq as f32,
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Sound: {}Hz for {} ticks\n", freq, dur));
                }
                Ok(None)
            }

            // Screen Control
            Statement::Locate {
                ref row,
                ref column,
            } => {
                let row_val = self.evaluate_expression(row)?;
                let col_val = self.evaluate_expression(column)?;
                if let (Value::Number(r), Value::Number(c)) = (row_val, col_val) {
                    graphics_commands.push(GraphicsCommand {
                        command: "LOCATE".to_string(),
                        value: r as f32,
                        color: Some(c as u32),
                    });
                    self.current_output
                        .push_str(&format!("Cursor positioned at row {}, column {}\n", r, c));
                }
                Ok(None)
            }
            Statement::Screen { ref mode } => {
                let mode_val = self.evaluate_expression(mode)?;
                if let Value::Number(m) = mode_val {
                    graphics_commands.push(GraphicsCommand {
                        command: "SCREEN".to_string(),
                        value: m as f32,
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Screen mode set to {}\n", m));
                }
                Ok(None)
            }
            Statement::Width { ref width } => {
                let width_val = self.evaluate_expression(width)?;
                if let Value::Number(w) = width_val {
                    graphics_commands.push(GraphicsCommand {
                        command: "WIDTH".to_string(),
                        value: w as f32,
                        color: None,
                    });
                    self.current_output
                        .push_str(&format!("Width set to {}\n", w));
                }
                Ok(None)
            }
            Statement::ColorBg {
                ref foreground,
                ref background,
            } => {
                if let Some(ref fg) = foreground {
                    let fg_val = self.evaluate_expression(fg)?;
                    if let Value::Number(f) = fg_val {
                        graphics_commands.push(GraphicsCommand {
                            command: "COLOR_FG".to_string(),
                            value: f as f32,
                            color: Some(f as u32),
                        });
                    }
                }
                if let Some(ref bg) = background {
                    let bg_val = self.evaluate_expression(bg)?;
                    if let Value::Number(b) = bg_val {
                        graphics_commands.push(GraphicsCommand {
                            command: "COLOR_BG".to_string(),
                            value: b as f32,
                            color: Some(b as u32),
                        });
                    }
                }
                self.current_output.push_str("Colors updated\n");
                Ok(None)
            }
            Statement::Palette { .. } => {
                // TODO: Implement palette
                self.current_output
                    .push_str("PALETTE not yet implemented\n");
                Ok(None)
            }

            // Error Handling
            Statement::OnError { ref line_number } => {
                self.error_handler = *line_number;
                self.current_output
                    .push_str(&format!("Error handler set to line {:?}\n", line_number));
                Ok(None)
            }
            Statement::Resume { ref line_number } => {
                if let Some(line) = line_number {
                    self.current_line = *line;
                }
                self.current_output.push_str("Resumed execution\n");
                Ok(None)
            }

            // Control Flow
            Statement::While { ref condition } => {
                let cond_val = self.evaluate_expression(condition)?;
                if let Value::Number(n) = cond_val {
                    if n != 0.0 {
                        // Push current line onto loop stack and continue
                        self.loop_stack.push(self.current_line);
                        Ok(None)
                    } else {
                        // Skip to WEND
                        self.skip_to_wend()?;
                        Ok(None)
                    }
                } else {
                    Err(InterpreterError::TypeError(
                        "WHILE condition must be numeric".to_string(),
                    ))
                }
            }
            Statement::Wend => {
                // Jump back to WHILE
                if let Some(while_line) = self.loop_stack.pop() {
                    self.current_line = while_line;
                    return Ok(Some("CONTINUE_LOOP".to_string()));
                } else {
                    return Err(InterpreterError::RuntimeError(
                        "WEND without WHILE".to_string(),
                    ));
                }
            }
            Statement::Select { ref expression } => {
                let val = self.evaluate_expression(expression)?;
                self.select_value = Some(val);
                Ok(None)
            }
            Statement::Case { ref conditions } => {
                if let Some(ref select_val) = self.select_value {
                    let select_val = select_val.clone();
                    for condition in conditions {
                        let matches = match condition {
                            CaseCondition::Value(ref expr) => {
                                let case_val = self.evaluate_expression(expr)?;
                                self.values_equal(&select_val, &case_val)
                            }
                            CaseCondition::Range { ref start, ref end } => {
                                let start_val = self.evaluate_expression(start)?;
                                let end_val = self.evaluate_expression(end)?;
                                match (&select_val, &start_val, &end_val) {
                                    (Value::Number(s), Value::Number(st), Value::Number(e)) => {
                                        *s >= *st && *s <= *e
                                    }
                                    _ => false,
                                }
                            }
                            CaseCondition::Is {
                                ref operator,
                                ref value,
                            } => {
                                let case_val = self.evaluate_expression(value)?;
                                match (&select_val, &case_val) {
                                    (Value::Number(s), Value::Number(c)) => {
                                        match operator.as_str() {
                                            "=" => (s - c).abs() < f64::EPSILON,
                                            ">" => *s > *c,
                                            "<" => *s < *c,
                                            ">=" => *s >= *c,
                                            "<=" => *s <= *c,
                                            "<>" => (s - c).abs() >= f64::EPSILON,
                                            _ => false,
                                        }
                                    }
                                    _ => false,
                                }
                            }
                        };
                        if matches {
                            // Execute this case
                            return Ok(None);
                        }
                    }
                    // No match, skip to next CASE or DEFAULT
                    self.skip_to_next_case()?;
                }
                Ok(None)
            }
            Statement::Default => {
                // Execute default case
                Ok(None)
            }
            Statement::EndSelect => {
                // Clear select value
                self.select_value = None;
                Ok(None)
            }

            // System
            Statement::System => {
                self.current_output.push_str("System exit requested\n");
                Ok(Some("END".to_string()))
            }
            Statement::Files { .. } => {
                // TODO: Implement directory listing
                self.current_output.push_str("FILES not yet implemented\n");
                Ok(None)
            }
            Statement::Kill { .. } => {
                // TODO: Implement file deletion
                self.current_output.push_str("KILL not yet implemented\n");
                Ok(None)
            }
            Statement::Name { .. } => {
                // TODO: Implement file renaming
                self.current_output.push_str("NAME not yet implemented\n");
                Ok(None)
            }
            Statement::Chdir { .. } => {
                // TODO: Implement directory change
                self.current_output.push_str("CHDIR not yet implemented\n");
                Ok(None)
            }
            Statement::Mkdir { .. } => {
                // TODO: Implement directory creation
                self.current_output.push_str("MKDIR not yet implemented\n");
                Ok(None)
            }
            Statement::Rmdir { .. } => {
                // TODO: Implement directory removal
                self.current_output.push_str("RMDIR not yet implemented\n");
                Ok(None)
            }

            Statement::Def {
                ref name,
                ref parameter,
                ref expression,
            } => {
                // Store the function definition
                self.functions.insert(
                    name.clone(),
                    FunctionDefinition {
                        parameter: parameter.clone(),
                        expression: expression.clone(),
                    },
                );
                Ok(None)
            }

            // Array
            Statement::Erase { ref arrays } => {
                for array in arrays {
                    self.arrays.remove(array);
                }
                self.current_output
                    .push_str(&format!("Erased arrays: {:?}\n", arrays));
                Ok(None)
            }
            Statement::OptionBase { ref base } => {
                let base_val = self.evaluate_expression(base)?;
                if let Value::Number(b) = base_val {
                    self.array_base = b as usize;
                    self.current_output
                        .push_str(&format!("Array base set to {}\n", b));
                }
                Ok(None)
            }
        }
    }

    pub fn provide_input(&mut self, input: &str) {
        if let Some((var_name, _)) = self.pending_input.take() {
            // Parse the input and set the variable
            let variables: Vec<&str> = var_name.split(',').map(|s| s.trim()).collect();
            let input_values: Vec<&str> = input.split(',').map(|s| s.trim()).collect();

            for (i, var) in variables.iter().enumerate() {
                if let Some(input_val) = input_values.get(i) {
                    // Try to parse as number, otherwise treat as string
                    if let Ok(num) = input_val.parse::<f64>() {
                        self.variables.insert(var.to_string(), Value::Number(num));
                    } else {
                        self.variables
                            .insert(var.to_string(), Value::String(input_val.to_string()));
                    }
                }
            }

            // Echo the input value(s) to output
            for (i, input_val) in input_values.iter().enumerate() {
                if i > 0 {
                    self.current_output.push_str("  "); // Two spaces between multiple inputs
                }
                self.current_output.push_str(input_val);
            }
            self.current_output.push('\n');
        }
    }

    pub fn execute(&mut self, code: &str) -> Result<ExecutionResult, InterpreterError> {
        if code.is_empty() {
            // Continue execution of current program
            if self.current_program.is_some() {
                return self.execute_program();
            } else {
                return Ok(ExecutionResult::Complete {
                    output: self.current_output.clone(),
                    graphics_commands: Vec::new(),
                });
            }
        }

        // Reset state for new execution
        self.pending_input = None;
        self.data_pointer = 0;
        self.data.clear();
        self.for_loops.clear();
        self.gosub_stack.clear();
        self.instruction_count = 0; // Reset instruction counter
        self.current_line = 0; // Reset to beginning
        self.current_output.clear(); // Clear accumulated output

        // Tokenize the input
        let mut tokenizer = Tokenizer::new(code);
        let tokens = tokenizer.tokenize()?;

        // Parse into AST
        let mut parser = Parser::new(tokens);
        let program = parser.parse_program()?;

        // Store the program for potential continuation
        self.current_program = Some(program);

        // Execute the program
        self.execute_program()
    }

    fn execute_program(&mut self) -> Result<ExecutionResult, InterpreterError> {
        let mut graphics_commands = Vec::new();

        while self.current_line < self.current_program.as_ref().unwrap().statements.len() {
            // Check for instruction limit to prevent infinite loops
            self.instruction_count += 1;
            if self.instruction_count > self.max_instructions {
                return Err(InterpreterError::RuntimeError(format!(
                    "Execution timeout: exceeded {} instructions",
                    self.max_instructions
                )));
            }

            let statement =
                self.current_program.as_ref().unwrap().statements[self.current_line].clone();

            let result = self.execute_statement(&statement, &mut graphics_commands)?;

            // Handle special results
            match result {
                Some(ref res) => {
                    if res.starts_with("GOTO ") {
                        if let Ok(line_num) = res[5..].parse::<usize>() {
                            if line_num < self.current_program.as_ref().unwrap().statements.len() {
                                self.current_line = line_num;
                                continue;
                            } else {
                                return Err(InterpreterError::RuntimeError(format!(
                                    "Line {} not found",
                                    line_num
                                )));
                            }
                        }
                    } else if res == "CONTINUE_LOOP" {
                        // NEXT caused loop continuation, don't increment current_line
                        continue;
                    } else if res == "END" {
                        // END or STOP statement
                        break;
                    } else {
                        self.current_output.push_str(res);
                        self.current_output.push('\n');
                    }
                }
                None => {}
            }

            // Check if we need input
            if let Some((var, prompt)) = &self.pending_input {
                // Increment current_line so continuation starts from next statement
                self.current_line += 1;
                return Ok(ExecutionResult::NeedInput {
                    variable_name: var.clone(),
                    prompt: prompt.clone(),
                    partial_output: self.current_output.clone(),
                    partial_graphics: graphics_commands.clone(),
                });
            }

            self.current_line += 1;
        }
        Ok(ExecutionResult::Complete {
            output: self.current_output.clone(),
            graphics_commands,
        })
    }

    fn skip_to_wend(&mut self) -> Result<(), InterpreterError> {
        // Skip to matching WEND
        let mut nesting = 1;
        while self.current_line < self.current_program.as_ref().unwrap().statements.len() {
            match &self.current_program.as_ref().unwrap().statements[self.current_line] {
                Statement::While { .. } => nesting += 1,
                Statement::Wend => {
                    nesting -= 1;
                    if nesting == 0 {
                        return Ok(());
                    }
                }
                _ => {}
            }
            self.current_line += 1;
        }
        Err(InterpreterError::RuntimeError(
            "WEND without WHILE".to_string(),
        ))
    }

    fn values_equal(&self, a: &Value, b: &Value) -> bool {
        match (a, b) {
            (Value::Number(x), Value::Number(y)) => (x - y).abs() < 1e-10,
            (Value::String(x), Value::String(y)) => x == y,
            _ => false,
        }
    }

    fn skip_to_next_case(&mut self) -> Result<(), InterpreterError> {
        // Skip to next CASE or END SELECT
        while self.current_line < self.current_program.as_ref().unwrap().statements.len() {
            match &self.current_program.as_ref().unwrap().statements[self.current_line] {
                Statement::Case { .. } | Statement::EndSelect => return Ok(()),
                _ => {}
            }
            self.current_line += 1;
        }
        Err(InterpreterError::RuntimeError(
            "END SELECT without SELECT CASE".to_string(),
        ))
    }
}
