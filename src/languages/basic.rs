use std::collections::HashMap;
use std::f64::consts::PI;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // Keywords
    Let, Print, If, Then, Else, End, Stop, Cls, Color, Input, Dim, Data, Read, Restore,
    For, To, Step, Next, Goto, Gosub, Return, Rem, On, And, Or, Not,
    Sin, Cos, Tan, Sqr, Abs, Int, Log, Exp, Atn, Rnd, Randomize,
    Len, Mid, Left, StringRight, Chr, Asc, Val, Str,
    Open, Close, FileEof,

    // Operators
    Plus, Minus, Multiply, Divide, Mod, Power,
    Equal, NotEqual, Less, LessEqual, Greater, GreaterEqual,
    Assign, // =

    // Punctuation
    LParen, RParen, Comma, Semicolon, Colon, Dollar,

    // Literals
    Number(f64),
    String(String),
    Identifier(String),

    // Graphics commands
    GraphicsForward, GraphicsRight,

    // Special
    LineNumber(usize),
    Eol, // End of line
    EndOfFile, // End of file
}

#[derive(Debug, Clone)]
pub struct Tokenizer {
    input: Vec<char>,
    position: usize,
    current_char: Option<char>,
}

impl Tokenizer {
    pub fn new(input: &str) -> Self {
        let chars: Vec<char> = input.chars().collect();
        let current_char = if chars.is_empty() { None } else { Some(chars[0]) };
        Self {
            input: chars,
            position: 0,
            current_char,
        }
    }

    fn advance(&mut self) {
        self.position += 1;
        if self.position >= self.input.len() {
            self.current_char = None;
        } else {
            self.current_char = Some(self.input[self.position]);
        }
    }

    fn peek(&self) -> Option<char> {
        if self.position + 1 >= self.input.len() {
            None
        } else {
            Some(self.input[self.position + 1])
        }
    }

    fn skip_whitespace(&mut self) {
        while let Some(ch) = self.current_char {
            if ch.is_whitespace() {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn read_number(&mut self) -> f64 {
        let mut result = String::new();
        while let Some(ch) = self.current_char {
            if ch.is_digit(10) || ch == '.' {
                result.push(ch);
                self.advance();
            } else {
                break;
            }
        }
        result.parse().unwrap_or(0.0)
    }

    fn read_string(&mut self) -> String {
        let mut result = String::new();
        self.advance(); // Skip opening quote
        while let Some(ch) = self.current_char {
            if ch == '"' {
                self.advance();
                break;
            } else {
                result.push(ch);
                self.advance();
            }
        }
        result
    }

    fn read_identifier(&mut self) -> String {
        let mut result = String::new();
        while let Some(ch) = self.current_char {
            if ch.is_alphanumeric() || ch == '_' || ch == '$' {
                result.push(ch);
                self.advance();
            } else {
                break;
            }
        }
        result
    }

    pub fn tokenize(&mut self) -> Result<Vec<Token>, InterpreterError> {
        let mut tokens = Vec::new();

        while let Some(ch) = self.current_char {
            match ch {
                ' ' | '\t' | '\n' | '\r' => {
                    self.skip_whitespace();
                }
                '"' => {
                    let string_val = self.read_string();
                    tokens.push(Token::String(string_val));
                }
                '0'..='9' => {
                    let num_val = self.read_number();
                    tokens.push(Token::Number(num_val));
                }
                'A'..='Z' | 'a'..='z' | '_' => {
                    let ident = self.read_identifier();
                    let token = match ident.to_uppercase().as_str() {
                        "LET" => Token::Let,
                        "PRINT" => Token::Print,
                        "IF" => Token::If,
                        "THEN" => Token::Then,
                        "ELSE" => Token::Else,
                        "END" => Token::End,
                        "STOP" => Token::Stop,
                        "CLS" => Token::Cls,
                        "COLOR" => Token::Color,
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
                        "LEFT" => Token::Left,
                        "RIGHT" => Token::StringRight,
                        "CHR" => Token::Chr,
                        "ASC" => Token::Asc,
                        "VAL" => Token::Val,
                        "STR" => Token::Str,
                        "OPEN" => Token::Open,
                        "CLOSE" => Token::Close,
                        "EOF" => Token::FileEof,
                        "FORWARD" => Token::GraphicsForward,
                        _ => Token::Identifier(ident),
                    };
                    tokens.push(token);
                }
                '+' => {
                    tokens.push(Token::Plus);
                    self.advance();
                }
                '-' => {
                    tokens.push(Token::Minus);
                    self.advance();
                }
                '*' => {
                    if let Some('*') = self.peek() {
                        tokens.push(Token::Power);
                        self.advance();
                        self.advance();
                    } else {
                        tokens.push(Token::Multiply);
                        self.advance();
                    }
                }
                '/' => {
                    tokens.push(Token::Divide);
                    self.advance();
                }
                '%' => {
                    tokens.push(Token::Mod);
                    self.advance();
                }
                '=' => {
                    tokens.push(Token::Equal);
                    self.advance();
                }
                '<' => {
                    if let Some('>') = self.peek() {
                        tokens.push(Token::NotEqual);
                        self.advance();
                        self.advance();
                    } else if let Some('=') = self.peek() {
                        tokens.push(Token::LessEqual);
                        self.advance();
                        self.advance();
                    } else {
                        tokens.push(Token::Less);
                        self.advance();
                    }
                }
                '>' => {
                    if let Some('=') = self.peek() {
                        tokens.push(Token::GreaterEqual);
                        self.advance();
                        self.advance();
                    } else {
                        tokens.push(Token::Greater);
                        self.advance();
                    }
                }
                '(' => {
                    tokens.push(Token::LParen);
                    self.advance();
                }
                ')' => {
                    tokens.push(Token::RParen);
                    self.advance();
                }
                ',' => {
                    tokens.push(Token::Comma);
                    self.advance();
                }
                ';' => {
                    tokens.push(Token::Semicolon);
                    self.advance();
                }
                ':' => {
                    tokens.push(Token::Colon);
                    self.advance();
                }
                '$' => {
                    tokens.push(Token::Dollar);
                    self.advance();
                }
                _ => {
                    return Err(InterpreterError::ParseError(format!("Unexpected character: {}", ch)));
                }
            }
        }

        tokens.push(Token::EndOfFile);
        Ok(tokens)
    }
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
pub enum Statement {
    Let {
        variable: String,
        expression: Expression,
    },
    Print {
        expressions: Vec<Expression>,
        separator: PrintSeparator,
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
        statements: Vec<Statement>,
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
    GraphicsForward {
        distance: Expression,
    },
    GraphicsRight {
        angle: Expression,
    },
    Rem {
        comment: String,
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

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        let current_token = if tokens.is_empty() { None } else { Some(tokens[0].clone()) };
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

    fn peek(&self) -> Option<&Token> {
        if self.position + 1 >= self.tokens.len() {
            None
        } else {
            Some(&self.tokens[self.position + 1])
        }
    }

    fn expect(&mut self, expected: &Token) -> Result<(), InterpreterError> {
        if let Some(ref token) = self.current_token {
            if token == expected {
                self.advance();
                Ok(())
            } else {
                Err(InterpreterError::ParseError(format!("Expected {:?}, found {:?}", expected, token)))
            }
        } else {
            Err(InterpreterError::ParseError(format!("Expected {:?}, found end of input", expected)))
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
            Some(Token::GraphicsForward) => self.parse_forward_statement(),
            Some(Token::Rem) => self.parse_rem_statement(),
            Some(Token::Identifier(ref id)) if id.to_uppercase() == "RIGHT" => self.parse_right_statement(),
            _ => Err(InterpreterError::ParseError(format!("Unexpected token in statement: {:?}", self.current_token))),
        }
    }

    fn parse_let_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume LET
        let var_name = self.parse_identifier()?;
        self.expect(&Token::Assign)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Let {
            variable: var_name,
            expression,
        })
    }

    fn parse_print_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume PRINT
        let mut expressions = Vec::new();
        let mut separator = PrintSeparator::None;

        while let Some(ref token) = self.current_token {
            match token {
                Token::Colon | Token::Eol | Token::EndOfFile => break,
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

        Ok(Statement::Print {
            expressions,
            separator,
        })
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
                Token::Colon | Token::Eol | Token::EndOfFile => break,
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
        self.expect(&Token::Assign)?;
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
        let statements = Vec::new(); // TODO: Parse statements until NEXT

        Ok(Statement::For {
            variable,
            start,
            end,
            step,
            statements,
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
            Err(InterpreterError::ParseError("Expected line number after GOTO".to_string()))
        }
    }

    fn parse_gosub_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.advance(); // consume GOSUB
        if let Some(Token::Number(line_num)) = self.current_token {
            let line_number = line_num as usize;
            self.advance();
            Ok(Statement::Gosub { line_number })
        } else {
            Err(InterpreterError::ParseError("Expected line number after GOSUB".to_string()))
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
            return Err(InterpreterError::ParseError("Expected GOTO or GOSUB after ON expression".to_string()));
        };
        
        let mut line_numbers = Vec::new();
        loop {
            if let Some(Token::Number(line_num)) = self.current_token {
                line_numbers.push(line_num as usize);
                self.advance();
            } else {
                return Err(InterpreterError::ParseError("Expected line number in ON statement".to_string()));
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
        let mut comment = String::new();
        while let Some(ref token) = self.current_token {
            match token {
                Token::Eol | Token::EndOfFile => break,
                Token::String(s) => {
                    comment.push_str(s);
                    self.advance();
                }
                Token::Identifier(id) => {
                    comment.push_str(id);
                    self.advance();
                }
                _ => {
                    // For other tokens, just advance
                    self.advance();
                }
            }
        }
        Ok(Statement::Rem { comment })
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
            Ok(Expression::BinaryOp {
                left: Box::new(Expression::Number(0.0)),
                operator: BinaryOperator::Minus,
                right: Box::new(expr),
            })
        } else if let Some(Token::Not) = self.current_token {
            // NOT is not implemented yet, just parse the expression
            self.advance();
            self.parse_power()
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
            _ => Err(InterpreterError::ParseError(format!("Unexpected token in expression: {:?}", self.current_token))),
        }
    }

    fn parse_identifier(&mut self) -> Result<String, InterpreterError> {
        if let Some(Token::Identifier(id)) = self.current_token.clone() {
            self.advance();
            Ok(id)
        } else {
            Err(InterpreterError::ParseError("Expected identifier".to_string()))
        }
    }

    fn parse_string_literal(&mut self) -> Result<String, InterpreterError> {
        if let Some(Token::String(s)) = self.current_token.clone() {
            self.advance();
            Ok(s)
        } else {
            Err(InterpreterError::ParseError("Expected string literal".to_string()))
        }
    }

    fn parse_statement_list(&mut self) -> Result<Vec<Statement>, InterpreterError> {
        let mut statements = Vec::new();
        
        while let Some(ref token) = self.current_token {
            match token {
                Token::Colon | Token::Eol | Token::EndOfFile => break,
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
pub enum InterpreterError {
    SyntaxError(String),
    TypeError(String),
    RuntimeError(String),
    FileError(String),
    DivisionByZero,
    UndefinedVariable(String),
    UndefinedArray(String),
    IndexOutOfBounds(String),
    InvalidFileMode(String),
    FileNotOpen(u8),
    ParseError(String),
}

#[derive(Clone)]
pub enum ExecutionResult {
    Complete { output: String, graphics_commands: Vec<GraphicsCommand> },
    NeedInput { prompt: String, partial_output: String, partial_graphics: Vec<GraphicsCommand> },
    Error(InterpreterError),
}

#[derive(Clone)]
pub struct GraphicsCommand {
    pub command: String,
    pub value: f32,
    pub x: Option<f32>,
    pub y: Option<f32>,
    pub color: Option<u32>,
}

pub struct FileHandle {
    pub file: Option<std::fs::File>,
    pub mode: String,
    pub filename: String,
    pub line_buffer: Vec<String>,
    pub current_line: usize,
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
    screen_color: u8,
    text_color: u8,
    files: HashMap<u8, FileHandle>,
    random_seed: u64,
}

#[derive(Clone)]
enum Value {
    Number(f64),
    String(String),
}

#[derive(Clone)]
struct ForLoop {
    variable: String,
    start: f64,
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
            screen_color: 0,
            text_color: 7,
            files: HashMap::new(),
            random_seed: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        }
    }

    pub fn execute(&mut self, code: &str) -> Result<ExecutionResult, InterpreterError> {
        self.current_line = 0;
        self.pending_input = None;
        self.data_pointer = 0;
        self.data.clear();
        self.for_loops.clear();
        self.gosub_stack.clear();

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
                                return Err(InterpreterError::RuntimeError(format!("Line {} not found", line_num)));
                            }
                        }
                    } else if res == "CONTINUE_LOOP" {
                        // NEXT caused loop continuation, don't increment current_line
                        continue;
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
                    prompt: prompt.clone(),
                    partial_output: output,
                    partial_graphics: graphics_commands,
                });
            }

            self.current_line += 1;
        }

        // Finished
        Ok(ExecutionResult::Complete { output, graphics_commands })
    }

    fn execute_statement(&mut self, statement: &Statement, output: &mut String, graphics_commands: &mut Vec<GraphicsCommand>) -> Result<Option<String>, InterpreterError> {
        match statement {
            Statement::Let { variable, expression } => {
                let value = self.evaluate_expression(expression)?;
                self.variables.insert(variable.clone(), value);
                Ok(None)
            }
            Statement::Print { expressions, separator } => {
                let mut result = String::new();
                for (i, expr) in expressions.iter().enumerate() {
                    if i > 0 {
                        match separator {
                            PrintSeparator::Comma => result.push('\t'),
                            PrintSeparator::Semicolon => {}, // No separator
                            PrintSeparator::None => result.push(' '),
                        }
                    }
                    let value = self.evaluate_expression(expr)?;
                    match value {
                        Value::Number(n) => result.push_str(&n.to_string()),
                        Value::String(s) => result.push_str(&s),
                    }
                }
                Ok(Some(result))
            }
            Statement::If { condition, then_statements, else_statements } => {
                let condition_value = self.evaluate_expression(condition)?;
                let condition_met = match condition_value {
                    Value::Number(n) => n != 0.0,
                    Value::String(s) => !s.is_empty(),
                };

                if condition_met {
                    // Execute then statements inline
                    for stmt in then_statements {
                        let result = self.execute_statement(stmt, output, graphics_commands)?;
                        if result.is_some() {
                            return Ok(result);
                        }
                    }
                } else if let Some(else_stmts) = else_statements {
                    // Execute else statements inline
                    for stmt in else_stmts {
                        let result = self.execute_statement(stmt, output, graphics_commands)?;
                        if result.is_some() {
                            return Ok(result);
                        }
                    }
                }
                Ok(None)
            }
            Statement::For { variable, start, end, step, statements } => {
                let start_val = self.evaluate_expression(start)?;
                let end_val = self.evaluate_expression(end)?;
                let step_val = step.as_ref()
                    .map(|s| self.evaluate_expression(s))
                    .unwrap_or(Ok(Value::Number(1.0)))?;

                let (start_num, end_num, step_num) = match (start_val, end_val, step_val) {
                    (Value::Number(s), Value::Number(e), Value::Number(st)) => (s, e, st),
                    _ => return Err(InterpreterError::TypeError("FOR loop requires numeric values".to_string())),
                };

                // Initialize loop variable
                self.variables.insert(variable.clone(), Value::Number(start_num));

                // Add to loop stack
                self.for_loops.push(ForLoop {
                    variable: variable.clone(),
                    start: start_num,
                    end: end_num,
                    step: step_num,
                    line: self.current_line,
                });

                Ok(None)
            }
            Statement::Next { variable } => {
                if let Some(loop_info) = self.for_loops.last_mut() {
                    // Check if variable matches (if specified)
                    if let Some(var_name) = variable {
                        if var_name != &loop_info.variable {
                            return Err(InterpreterError::RuntimeError(format!("NEXT {} does not match FOR {}", var_name, loop_info.variable)));
                        }
                    }

                    // Get current value
                    let current_val = match self.variables.get(&loop_info.variable) {
                        Some(Value::Number(n)) => *n,
                        _ => return Err(InterpreterError::RuntimeError(format!("Variable {} not found or not numeric", loop_info.variable))),
                    };

                    // Calculate next value
                    let next_val = current_val + loop_info.step;

                    // Check if loop should continue
                    let should_continue = if loop_info.step > 0.0 {
                        next_val <= loop_info.end
                    } else {
                        next_val >= loop_info.end
                    };

                    if should_continue {
                        // Update variable and continue loop
                        self.variables.insert(loop_info.variable.clone(), Value::Number(next_val));
                        self.current_line = loop_info.line; // Go back to FOR statement
                        return Ok(Some("CONTINUE_LOOP".to_string()));
                    } else {
                        // Loop finished, remove from stack
                        self.for_loops.pop();
                    }
                } else {
                    return Err(InterpreterError::RuntimeError("NEXT without FOR".to_string()));
                }
                Ok(None)
            }
            Statement::Goto { line_number } => {
                Ok(Some(format!("GOTO {}", line_number)))
            }
            Statement::Gosub { line_number } => {
                self.gosub_stack.push(self.current_line);
                Ok(Some(format!("GOTO {}", line_number)))
            }
            Statement::Return => {
                if let Some(return_line) = self.gosub_stack.pop() {
                    self.current_line = return_line;
                    return Ok(Some("CONTINUE_LOOP".to_string()));
                } else {
                    return Err(InterpreterError::RuntimeError("RETURN without GOSUB".to_string()));
                }
            }
            Statement::On { expression, line_numbers, is_gosub } => {
                let index_val = self.evaluate_expression(expression)?;
                let index = match index_val {
                    Value::Number(n) => n as usize,
                    _ => return Err(InterpreterError::TypeError("ON expression must evaluate to a number".to_string())),
                };
                
                if index == 0 || index > line_numbers.len() {
                    // Index out of range, continue to next statement
                    Ok(None)
                } else {
                    let target_line = line_numbers[index - 1]; // 1-based indexing
                    if *is_gosub {
                        self.gosub_stack.push(self.current_line);
                    }
                    Ok(Some(format!("GOTO {}", target_line)))
                }
            }
            Statement::Input { prompt, variables } => {
                let prompt_text = prompt.clone().unwrap_or_else(|| "Input:".to_string());
                if let Some(var) = variables.first() {
                    self.pending_input = Some((var.clone(), prompt_text));
                }
                Ok(None)
            }
            Statement::Dim { arrays } => {
                for (name, size_expr) in arrays {
                    let size_val = self.evaluate_expression(size_expr)?;
                    match size_val {
                        Value::Number(size) => {
                            let size_usize = size as usize;
                            self.arrays.insert(name.clone(), vec![Value::Number(0.0); size_usize + 1]);
                        }
                        _ => return Err(InterpreterError::TypeError("Array size must be numeric".to_string())),
                    }
                }
                Ok(None)
            }
            Statement::Data { values } => {
                self.data.extend(values.iter().cloned());
                Ok(None)
            }
            Statement::Read { variables } => {
                for var in variables {
                    if self.data_pointer < self.data.len() {
                        let data_value = &self.data[self.data_pointer];
                        self.data_pointer += 1;
                        if let Ok(num) = data_value.parse::<f64>() {
                            self.variables.insert(var.clone(), Value::Number(num));
                        } else {
                            self.variables.insert(var.clone(), Value::String(data_value.clone()));
                        }
                    } else {
                        return Err(InterpreterError::RuntimeError("READ without DATA".to_string()));
                    }
                }
                Ok(None)
            }
            Statement::Restore => {
                self.data_pointer = 0;
                Ok(None)
            }
            Statement::End => {
                Ok(Some("Program ended.".to_string()))
            }
            Statement::Stop => {
                Ok(Some("Program stopped.".to_string()))
            }
            Statement::Cls => {
                graphics_commands.push(GraphicsCommand {
                    command: "CLS".to_string(),
                    value: 0.0,
                    x: None,
                    y: None,
                    color: Some(self.screen_color as u32),
                });
                Ok(None)
            }
            Statement::Color { color } => {
                let color_val = self.evaluate_expression(color)?;
                match color_val {
                    Value::Number(c) => {
                        self.text_color = c as u8;
                        graphics_commands.push(GraphicsCommand {
                            command: "COLOR".to_string(),
                            value: c as f32,
                            x: None,
                            y: None,
                            color: Some(c as u32),
                        });
                    }
                    _ => return Err(InterpreterError::TypeError("COLOR requires numeric value".to_string())),
                }
                Ok(None)
            }
            Statement::GraphicsForward { distance } => {
                let dist_val = self.evaluate_expression(distance)?;
                match dist_val {
                    Value::Number(d) => {
                        graphics_commands.push(GraphicsCommand {
                            command: "FORWARD".to_string(),
                            value: d as f32,
                            x: None,
                            y: None,
                            color: None,
                        });
                    }
                    _ => return Err(InterpreterError::TypeError("FORWARD requires numeric distance".to_string())),
                }
                Ok(None)
            }
            Statement::GraphicsRight { angle } => {
                let angle_val = self.evaluate_expression(angle)?;
                match angle_val {
                    Value::Number(a) => {
                        graphics_commands.push(GraphicsCommand {
                            command: "RIGHT".to_string(),
                            value: a as f32,
                            x: None,
                            y: None,
                            color: None,
                        });
                    }
                    _ => return Err(InterpreterError::TypeError("RIGHT requires numeric angle".to_string())),
                }
                Ok(None)
            }
            Statement::Rem { .. } => {
                // Comments are ignored
                Ok(None)
            }
        }
    }

    fn evaluate_expression(&mut self, expression: &Expression) -> Result<Value, InterpreterError> {
        match expression {
            Expression::Number(n) => Ok(Value::Number(*n)),
            Expression::String(s) => Ok(Value::String(s.clone())),
            Expression::Variable(name) => {
                match self.variables.get(name) {
                    Some(value) => Ok(value.clone()),
                    None => Err(InterpreterError::UndefinedVariable(name.clone())),
                }
            }
            Expression::BinaryOp { left, operator, right } => {
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
                                    return Err(InterpreterError::DivisionByZero);
                                }
                                l / r
                            }
                            BinaryOperator::Mod => l % r,
                            BinaryOperator::Power => l.powf(r),
                            BinaryOperator::Equal => if l == r { 1.0 } else { 0.0 },
                            BinaryOperator::NotEqual => if l != r { 1.0 } else { 0.0 },
                            BinaryOperator::Less => if l < r { 1.0 } else { 0.0 },
                            BinaryOperator::LessEqual => if l <= r { 1.0 } else { 0.0 },
                            BinaryOperator::Greater => if l > r { 1.0 } else { 0.0 },
                            BinaryOperator::GreaterEqual => if l >= r { 1.0 } else { 0.0 },
                            BinaryOperator::And => if l != 0.0 && r != 0.0 { 1.0 } else { 0.0 },
                            BinaryOperator::Or => if l != 0.0 || r != 0.0 { 1.0 } else { 0.0 },
                        };
                        Ok(Value::Number(result))
                    }
                    (Value::String(l), Value::String(r)) => {
                        match operator {
                            BinaryOperator::Plus => Ok(Value::String(l + &r)),
                            BinaryOperator::Equal => Ok(Value::Number(if l == r { 1.0 } else { 0.0 })),
                            BinaryOperator::NotEqual => Ok(Value::Number(if l != r { 1.0 } else { 0.0 })),
                            _ => Err(InterpreterError::TypeError("Invalid operation on strings".to_string())),
                        }
                    }
                    _ => Err(InterpreterError::TypeError("Type mismatch in binary operation".to_string())),
                }
            }
            Expression::FunctionCall { name, arguments } => {
                self.evaluate_function_call(name, arguments)
            }
            Expression::ArrayAccess { name, index } => {
                let index_val = self.evaluate_expression(index)?;
                match index_val {
                    Value::Number(idx) => {
                        let idx_usize = idx as usize;
                        match self.arrays.get(name) {
                            Some(array) => {
                                if idx_usize < array.len() {
                                    Ok(array[idx_usize].clone())
                                } else {
                                    Err(InterpreterError::IndexOutOfBounds(format!("Array {} index {} out of bounds", name, idx_usize)))
                                }
                            }
                            None => Err(InterpreterError::UndefinedArray(name.clone())),
                        }
                    }
                    _ => Err(InterpreterError::TypeError("Array index must be numeric".to_string())),
                }
            }
        }
    }

    fn evaluate_function_call(&mut self, name: &str, arguments: &[Expression]) -> Result<Value, InterpreterError> {
        match name.to_uppercase().as_str() {
            "SIN" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("SIN requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.sin())),
                    _ => Err(InterpreterError::TypeError("SIN requires numeric argument".to_string())),
                }
            }
            "COS" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("COS requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.cos())),
                    _ => Err(InterpreterError::TypeError("COS requires numeric argument".to_string())),
                }
            }
            "TAN" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("TAN requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.tan())),
                    _ => Err(InterpreterError::TypeError("TAN requires numeric argument".to_string())),
                }
            }
            "SQR" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("SQR requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.sqrt())),
                    _ => Err(InterpreterError::TypeError("SQR requires numeric argument".to_string())),
                }
            }
            "ABS" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("ABS requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.abs())),
                    _ => Err(InterpreterError::TypeError("ABS requires numeric argument".to_string())),
                }
            }
            "INT" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("INT requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.floor())),
                    _ => Err(InterpreterError::TypeError("INT requires numeric argument".to_string())),
                }
            }
            "LOG" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("LOG requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => {
                        if n <= 0.0 {
                            return Err(InterpreterError::RuntimeError("LOG requires positive argument".to_string()));
                        }
                        Ok(Value::Number(n.ln()))
                    }
                    _ => Err(InterpreterError::TypeError("LOG requires numeric argument".to_string())),
                }
            }
            "EXP" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("EXP requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.exp())),
                    _ => Err(InterpreterError::TypeError("EXP requires numeric argument".to_string())),
                }
            }
            "ATN" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("ATN requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::Number(n.atan())),
                    _ => Err(InterpreterError::TypeError("ATN requires numeric argument".to_string())),
                }
            }
            "RND" => {
                if arguments.len() > 1 {
                    return Err(InterpreterError::RuntimeError("RND takes at most 1 argument".to_string()));
                }
                // Generate random number between 0 and 1
                use std::time::{SystemTime, UNIX_EPOCH};
                let seed = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() as u64;
                let random_val = (seed % 1000000) as f64 / 1000000.0;
                Ok(Value::Number(random_val))
            }
            "LEN" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("LEN requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::String(s) => Ok(Value::Number(s.len() as f64)),
                    _ => Err(InterpreterError::TypeError("LEN requires string argument".to_string())),
                }
            }
            "CHR" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("CHR requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => {
                        if let Some(ch) = char::from_u32(n as u32) {
                            Ok(Value::String(ch.to_string()))
                        } else {
                            Err(InterpreterError::RuntimeError("CHR argument out of range".to_string()))
                        }
                    }
                    _ => Err(InterpreterError::TypeError("CHR requires numeric argument".to_string())),
                }
            }
            "ASC" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("ASC requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::String(s) => {
                        if let Some(ch) = s.chars().next() {
                            Ok(Value::Number(ch as u32 as f64))
                        } else {
                            Err(InterpreterError::RuntimeError("ASC requires non-empty string".to_string()))
                        }
                    }
                    _ => Err(InterpreterError::TypeError("ASC requires string argument".to_string())),
                }
            }
            "VAL" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("VAL requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::String(s) => {
                        match s.parse::<f64>() {
                            Ok(n) => Ok(Value::Number(n)),
                            Err(_) => Ok(Value::Number(0.0)),
                        }
                    }
                    Value::Number(n) => Ok(Value::Number(n)),
                }
            }
            "STR" => {
                if arguments.len() != 1 {
                    return Err(InterpreterError::RuntimeError("STR requires 1 argument".to_string()));
                }
                let arg = self.evaluate_expression(&arguments[0])?;
                match arg {
                    Value::Number(n) => Ok(Value::String(n.to_string())),
                    Value::String(s) => Ok(Value::String(s)),
                }
            }
            _ => Err(InterpreterError::RuntimeError(format!("Unknown function: {}", name))),
        }
    }

    pub fn provide_input(&mut self, input: String) {
        if let Some((var, _)) = self.pending_input.take() {
            // Try to parse as number first, then string
            if let Ok(num) = input.parse::<f64>() {
                self.variables.insert(var, Value::Number(num));
            } else {
                self.variables.insert(var, Value::String(input));
            }
        }
    }

    fn execute_line(&mut self, line: &str) -> Result<Option<String>, InterpreterError> {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.is_empty() {
            return Ok(None);
        }
        match parts[0].to_uppercase().as_str() {
            "LET" => {
                if parts.len() >= 4 && parts[2] == "=" {
                    let var = parts[1].to_string();
                    let value_str = parts[3..].join(" ").trim_matches('"').to_string();
                    // Try to parse as number first, then string
                    if let Ok(num) = value_str.parse::<f64>() {
                        self.variables.insert(var, Value::Number(num));
                    } else {
                        self.variables.insert(var, Value::String(value_str));
                    }
                }
            }
            "PRINT" => {
                let args_str = parts[1..].join(" ");
                let mut output = String::new();
                let parts: Vec<&str> = args_str.split(';').collect();
                for (i, part) in parts.iter().enumerate() {
                    let trimmed = part.trim();
                    if let Some(var) = trimmed.strip_suffix('$') {
                        if let Some(value) = self.variables.get(var) {
                            match value {
                                Value::String(s) => output.push_str(s),
                                Value::Number(n) => output.push_str(&n.to_string()),
                            }
                        } else {
                            output.push_str(trimmed);
                        }
                    } else if self.variables.contains_key(trimmed) {
                        if let Some(value) = self.variables.get(trimmed) {
                            match value {
                                Value::String(s) => output.push_str(s),
                                Value::Number(n) => output.push_str(&n.to_string()),
                            }
                        }
                    } else {
                        // Remove surrounding quotes if present
                        let cleaned = trimmed.trim_matches('"');
                        output.push_str(cleaned);
                    }
                    if i < parts.len() - 1 {
                        // No space for semicolon separation
                    }
                }
                return Ok(Some(output));
            }
            "T:" => {
                let prompt = parts[1..].join(" ");
                return Ok(Some(format!("{}?", prompt)));
            }
            "END" => {
                // End program execution
                return Ok(Some("Program ended.".to_string()));
            }
            "STOP" => {
                // Stop program execution
                return Ok(Some("Program stopped.".to_string()));
            }
            "INPUT" => {
                if parts.len() > 1 {
                    let prompt = if parts[1].starts_with('"') {
                        parts[1..].join(" ").trim_matches('"').to_string()
                    } else {
                        "Input:".to_string()
                    };
                    let var = if parts[1].starts_with('"') {
                        parts.last().unwrap().to_string()
                    } else {
                        parts[1].to_string()
                    };
                    self.pending_input = Some((var, prompt));
                }
            }
            "DIM" => {
                // Basic array support
                if parts.len() >= 2 {
                    let array_spec = parts[1];
                    if let Some(open_paren) = array_spec.find('(') {
                        let name = &array_spec[..open_paren];
                        if let Some(close_paren) = array_spec.find(')') {
                            let dims_str = &array_spec[open_paren+1..close_paren];
                            if let Ok(size) = dims_str.parse::<usize>() {
                                self.arrays.insert(name.to_string(), vec![Value::Number(0.0); size + 1]);
                            }
                        }
                    }
                }
            }
            "DATA" => {
                // Store data for READ
                let data_items = parts[1..].join(" ");
                self.data.extend(data_items.split(',').map(|s| s.trim().to_string()));
            }
            "READ" => {
                // Read from DATA
                for part in &parts[1..] {
                    if self.data_pointer < self.data.len() {
                        let data_value = &self.data[self.data_pointer];
                        self.data_pointer += 1;
                        if let Ok(num) = data_value.parse::<f64>() {
                            self.variables.insert(part.to_string(), Value::Number(num));
                        } else {
                            self.variables.insert(part.to_string(), Value::String(data_value.clone()));
                        }
                    }
                }
            }
            "RESTORE" => {
                // Reset data pointer
                self.data_pointer = 0;
            }
            "SIN" => {
                // SIN function
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        let result = arg.sin();
                        return Ok(Some(result.to_string()));
                    }
                }
            }
            "COS" => {
                // COS function
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        let result = arg.cos();
                        return Ok(Some(result.to_string()));
                    }
                }
            }
            "TAN" => {
                // TAN function
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        let result = arg.tan();
                        return Ok(Some(result.to_string()));
                    }
                }
            }
            "SQR" => {
                // SQR function (square root)
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        let result = arg.sqrt();
                        return Ok(Some(result.to_string()));
                    }
                }
            }
            "ABS" => {
                // ABS function
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        let result = arg.abs();
                        return Ok(Some(result.to_string()));
                    }
                }
            }
            "INT" => {
                // INT function (floor)
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        let result = arg.floor();
                        return Ok(Some(result.to_string()));
                    }
                }
            }
            "GOTO" => {
                // GOTO line number
                if parts.len() > 1 {
                    if let Ok(line_num) = parts[1].parse::<usize>() {
                        // For now, just indicate jump - execution logic will handle
                        return Ok(Some(format!("GOTO {}", line_num)));
                    }
                }
            }
            "GOSUB" => {
                // GOSUB line number (subroutine call)
                if parts.len() > 1 {
                    if let Ok(line_num) = parts[1].parse::<usize>() {
                        // Push current line to stack and jump
                        self.gosub_stack.push(self.current_line);
                        return Ok(Some(format!("GOTO {}", line_num)));
                    }
                }
            }
            "RETURN" => {
                // RETURN from subroutine
                if let Some(return_line) = self.gosub_stack.pop() {
                    return Ok(Some(format!("GOTO {}", return_line + 1)));
                }
            }
            "FOR" => {
                // FOR variable = start TO end [STEP step]
                if parts.len() >= 5 && parts[2] == "=" && parts[4].to_uppercase() == "TO" {
                    let var = parts[1].to_string();
                    if let Ok(start) = parts[3].parse::<f64>() {
                        if let Ok(end) = parts[5].parse::<f64>() {
                            let step = if parts.len() > 6 && parts[6].to_uppercase() == "STEP" && parts.len() > 7 {
                                parts[7].parse::<f64>().unwrap_or(1.0)
                            } else {
                                1.0
                            };
                            
                            // Set initial value
                            self.variables.insert(var.clone(), Value::Number(start));
                            
                            // Push loop to stack
                            self.for_loops.push(ForLoop {
                                variable: var,
                                start,
                                end,
                                step,
                                line: self.current_line,
                            });
                        }
                    }
                }
            }
            "NEXT" => {
                // NEXT variable
                if let Some(for_loop) = self.for_loops.last_mut() {
                    if let Some(Value::Number(ref mut current_val)) = self.variables.get_mut(&for_loop.variable) {
                        *current_val += for_loop.step;
                        
                        if (*current_val - for_loop.end).abs() < 0.0001 || 
                           (for_loop.step > 0.0 && *current_val <= for_loop.end) ||
                           (for_loop.step < 0.0 && *current_val >= for_loop.end) {
                            // Continue loop
                            self.current_line = for_loop.line;
                            return Ok(Some("CONTINUE_LOOP".to_string()));
                        } else {
                            // Exit loop
                            self.for_loops.pop();
                        }
                    }
                }
            }
            "LEN" => {
                // LEN(string) - returns string length
                if parts.len() > 1 {
                    let arg = parts[1..].join(" ").trim_matches('"').to_string();
                    return Ok(Some(arg.len().to_string()));
                }
            }
            "MID$" => {
                // MID$(string, start, length)
                if parts.len() >= 4 {
                    let string_arg = parts[1].trim_matches('"');
                    if let Ok(start) = parts[2].parse::<usize>() {
                        if let Ok(length) = parts[3].parse::<usize>() {
                            let start_idx = start.saturating_sub(1); // GW BASIC uses 1-based indexing
                            if start_idx < string_arg.len() {
                                let end_idx = (start_idx + length).min(string_arg.len());
                                let result = &string_arg[start_idx..end_idx];
                                return Ok(Some(format!("\"{}\"", result)));
                            }
                        }
                    }
                }
            }
            "LEFT$" => {
                // LEFT$(string, length)
                if parts.len() >= 3 {
                    let string_arg = parts[1].trim_matches('"');
                    if let Ok(length) = parts[2].parse::<usize>() {
                        let result = &string_arg[..length.min(string_arg.len())];
                        return Ok(Some(format!("\"{}\"", result)));
                    }
                }
            }
            "RIGHT$" => {
                // RIGHT$(string, length)
                if parts.len() >= 3 {
                    let string_arg = parts[1].trim_matches('"');
                    if let Ok(length) = parts[2].parse::<usize>() {
                        let start = string_arg.len().saturating_sub(length);
                        let result = &string_arg[start..];
                        return Ok(Some(format!("\"{}\"", result)));
                    }
                }
            }
            "CHR$" => {
                // CHR$(ascii) - character from ASCII code
                if parts.len() > 1 {
                    if let Ok(ascii) = parts[1].parse::<u8>() {
                        if let Some(ch) = char::from_u32(ascii as u32) {
                            return Ok(Some(format!("\"{}\"", ch)));
                        }
                    }
                }
            }
            "ASC" => {
                // ASC(string) - ASCII code of first character
                if parts.len() > 1 {
                    let string_arg = parts[1].trim_matches('"');
                    if let Some(first_char) = string_arg.chars().next() {
                        return Ok(Some((first_char as u32).to_string()));
                    }
                }
            }
            "VAL" => {
                // VAL(string) - convert string to number
                if parts.len() > 1 {
                    let string_arg = parts[1].trim_matches('"');
                    if let Ok(num) = string_arg.parse::<f64>() {
                        return Ok(Some(num.to_string()));
                    }
                }
            }
            "STR$" => {
                // STR$(number) - convert number to string
                if parts.len() > 1 {
                    if let Ok(num) = parts[1].parse::<f64>() {
                        return Ok(Some(format!("\"{}\"", num)));
                    }
                }
            }
            "LOG" => {
                // LOG(number) - natural logarithm
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        if arg > 0.0 {
                            return Ok(Some(arg.ln().to_string()));
                        }
                    }
                }
            }
            "EXP" => {
                // EXP(number) - e^x
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        return Ok(Some(arg.exp().to_string()));
                    }
                }
            }
            "ATN" => {
                // ATN(number) - arctangent
                if parts.len() > 1 {
                    if let Ok(arg) = parts[1].parse::<f64>() {
                        return Ok(Some(arg.atan().to_string()));
                    }
                }
            }
            "RND" => {
                // RND - random number between 0 and 1
                // Simple linear congruential generator
                self.random_seed = self.random_seed.wrapping_mul(1103515245).wrapping_add(12345);
                let random_val = (self.random_seed % 32768) as f64 / 32767.0;
                return Ok(Some(random_val.to_string()));
            }
            "RANDOMIZE" => {
                // RANDOMIZE seed - seed the random number generator
                if parts.len() > 1 {
                    if let Ok(seed) = parts[1].parse::<u64>() {
                        self.random_seed = seed;
                    }
                } else {
                    // Use current time if no seed provided
                    self.random_seed = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
                }
            }
            "OPEN" => {
                // OPEN "filename" FOR mode AS #filenum
                if parts.len() >= 6 && parts[2] == "FOR" && parts[4] == "AS" {
                    let filename = parts[1].trim_matches('"');
                    let mode = parts[3].to_uppercase();
                    let file_num_str = parts[5].trim_start_matches('#');
                    
                    if let Ok(file_num) = file_num_str.parse::<u8>() {
                        match mode.as_str() {
                            "INPUT" => {
                                if let Ok(file) = File::open(filename) {
                                    let reader = BufReader::new(file);
                                    let mut line_buffer = Vec::new();
                                    for line in reader.lines() {
                                        if let Ok(line) = line {
                                            line_buffer.push(line);
                                        }
                                    }
                                    self.files.insert(file_num, FileHandle {
                                        file: None, // File is consumed by BufReader
                                        mode,
                                        filename: filename.to_string(),
                                        line_buffer,
                                        current_line: 0,
                                    });
                                }
                            }
                            "OUTPUT" => {
                                if let Ok(file) = File::create(filename) {
                                    self.files.insert(file_num, FileHandle {
                                        file: Some(file),
                                        mode,
                                        filename: filename.to_string(),
                                        line_buffer: Vec::new(),
                                        current_line: 0,
                                    });
                                }
                            }
                            "APPEND" => {
                                if let Ok(file) = OpenOptions::new().append(true).create(true).open(filename) {
                                    self.files.insert(file_num, FileHandle {
                                        file: Some(file),
                                        mode,
                                        filename: filename.to_string(),
                                        line_buffer: Vec::new(),
                                        current_line: 0,
                                    });
                                }
                            }
                            _ => {}
                        }
                    }
                }
            }
            "CLOSE" => {
                // CLOSE #filenum
                if parts.len() > 1 {
                    let file_num_str = parts[1].trim_start_matches('#');
                    if let Ok(file_num) = file_num_str.parse::<u8>() {
                        self.files.remove(&file_num);
                    }
                }
            }
            "PRINT#" => {
                // PRINT #filenum, expression
                if parts.len() >= 3 {
                    let file_num_str = parts[1].trim_start_matches('#');
                    if let Ok(file_num) = file_num_str.parse::<u8>() {
                        if let Some(file_handle) = self.files.get_mut(&file_num) {
                            if file_handle.mode == "OUTPUT" || file_handle.mode == "APPEND" {
                                if let Some(ref mut file) = file_handle.file {
                                    let expression = parts[2..].join(" ");
                                    let _ = writeln!(file, "{}", expression);
                                }
                            }
                        }
                    }
                }
            }
            "INPUT#" => {
                // INPUT #filenum, variable
                if parts.len() >= 3 {
                    let file_num_str = parts[1].trim_start_matches('#');
                    if let Ok(file_num) = file_num_str.parse::<u8>() {
                        if let Some(file_handle) = self.files.get_mut(&file_num) {
                            if file_handle.mode == "INPUT" {
                                if file_handle.current_line < file_handle.line_buffer.len() {
                                    let line = &file_handle.line_buffer[file_handle.current_line];
                                    file_handle.current_line += 1;
                                    
                                    let var = parts[2];
                                    // Try to parse as number first, then string
                                    if let Ok(num) = line.parse::<f64>() {
                                        self.variables.insert(var.to_string(), Value::Number(num));
                                    } else {
                                        self.variables.insert(var.to_string(), Value::String(line.clone()));
                                    }
                                }
                            }
                        }
                    }
                }
            }
            "EOF" => {
                // EOF(filenum) - check end of file
                if parts.len() > 1 {
                    if let Ok(file_num) = parts[1].parse::<u8>() {
                        if let Some(file_handle) = self.files.get(&file_num) {
                            if file_handle.mode == "INPUT" {
                            let is_eof = file_handle.current_line >= file_handle.line_buffer.len();
                            return Ok(Some(if is_eof { "-1" } else { "0" }.to_string()));
                            }
                        }
                    }
                }
            }
            _ => {}
        }
        Ok(None)
    }
}