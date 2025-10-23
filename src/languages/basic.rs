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
            _ => Err(InterpreterError::ParseError(format!(
                "Unexpected token in statement: {:?}",
                self.current_token
            ))),
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
        let mut expressions = Vec::new();

        // Parse first expression
        if let Some(ref token) = self.current_token {
            if !matches!(
                token,
                Token::Colon | Token::EndOfFile | Token::Comma | Token::Semicolon
            ) {
                let expr = self.parse_expression()?;
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
                            let expr = self.parse_expression()?;
                            expressions.push(expr);
                        }
                    }
                }
                Token::Semicolon => {
                    separator = PrintSeparator::Semicolon;
                    self.advance();
                    if let Some(ref token) = self.current_token {
                        if !matches!(token, Token::Colon | Token::EndOfFile) {
                            let expr = self.parse_expression()?;
                            expressions.push(expr);
                        }
                    }
                }
                _ => break, // No more separators
            }
        }

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
        Ok(Statement::End)
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

    fn parse_expression(&mut self) -> Result<Expression, InterpreterError> {
        self.parse_logical_or()
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

impl BasicInterpreter {
    pub fn new() -> Self {
        Self {
            variables: HashMap::new(),
            arrays: HashMap::new(),
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
        output: &mut String,
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
                output.push_str(&result);
                output.push('\n');
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
                output.push_str(&result);
                output.push('\n');
                Ok(None)
            }
            Statement::Readln {
                ref prompt,
                ref variables,
            } => {
                if let Some(prompt_text) = prompt {
                    output.push_str(prompt_text);
                } else {
                    output.push_str("? ");
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
                    output.push_str(&format!("Moved forward {}", dist));
                    output.push('\n');
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
                    output.push_str(&format!("Moved back {}", dist));
                    output.push('\n');
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
                    output.push_str(&format!("Turned left {} degrees", ang));
                    output.push('\n');
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
                    output.push_str(&format!("Turned right {} degrees", ang));
                    output.push('\n');
                }
                Ok(None)
            }
            Statement::Penup => {
                graphics_commands.push(GraphicsCommand {
                    command: "PENUP".to_string(),
                    value: 0.0,
                    color: None,
                });
                output.push_str("Pen up\n");
                Ok(None)
            }
            Statement::Pendown => {
                graphics_commands.push(GraphicsCommand {
                    command: "PENDOWN".to_string(),
                    value: 0.0,
                    color: None,
                });
                output.push_str("Pen down\n");
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
                        let result = self.execute_statement(stmt, output, graphics_commands)?;
                        if result.is_some() {
                            return Ok(result);
                        }
                    }
                } else if let Some(else_stmts) = else_statements {
                    for stmt in else_stmts {
                        let result = self.execute_statement(stmt, output, graphics_commands)?;
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
                            self.current_line = loop_info.line;
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
                    output.push_str(p);
                    output.push('?');
                    output.push(' ');
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
        }
    }

    pub fn execute(&mut self, code: &str) -> Result<ExecutionResult, InterpreterError> {
        self.pending_input = None;
        self.data_pointer = 0;
        self.data.clear();
        self.for_loops.clear();
        self.gosub_stack.clear();
        self.instruction_count = 0; // Reset instruction counter

        // Tokenize the input
        let mut tokenizer = Tokenizer::new(code);
        let tokens = tokenizer.tokenize()?;

        // Parse into AST
        let mut parser = Parser::new(tokens);
        let program = parser.parse_program()?;

        // Execute the program
        self.execute_program(&program)
    }

    fn execute_program(&mut self, program: &Program) -> Result<ExecutionResult, InterpreterError> {
        let mut output = String::new();
        let mut graphics_commands = Vec::new();

        while self.current_line < program.statements.len() {
            // Check for instruction limit to prevent infinite loops
            self.instruction_count += 1;
            if self.instruction_count > self.max_instructions {
                return Err(InterpreterError::RuntimeError(format!(
                    "Execution timeout: exceeded {} instructions",
                    self.max_instructions
                )));
            }

            let statement = &program.statements[self.current_line];

            let result = self.execute_statement(statement, &mut output, &mut graphics_commands)?;

            // Handle special results
            match result {
                Some(ref res) => {
                    if res.starts_with("GOTO ") {
                        if let Ok(line_num) = res[5..].parse::<usize>() {
                            if line_num < program.statements.len() {
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
                        output.push_str(res);
                        output.push('\n');
                    }
                }
                None => {}
            }

            // Check if we need input
            if let Some((var, prompt)) = &self.pending_input {
                return Ok(ExecutionResult::NeedInput {
                    variable_name: var.clone(),
                    prompt: prompt.clone(),
                    partial_output: output.clone(),
                    partial_graphics: graphics_commands.clone(),
                });
            }

            self.current_line += 1;
        }
        Ok(ExecutionResult::Complete {
            output,
            graphics_commands,
        })
    }
}
