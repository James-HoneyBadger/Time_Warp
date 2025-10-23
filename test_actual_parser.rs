// Extract just the tokenizer and parser parts from basic.rs
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // Keywords
    Let,
    Print,
    If,
    Then,
    Else,
    End,
    Stop,
    Cls,
    Color,
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
    Left,
    StringRight,
    Chr,
    Asc,
    Val,
    Str,
    Open,
    Close,
    FileEof,

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
    FunctionCall {
        name: String,
        arguments: Vec<Expression>,
    },
}

#[derive(Debug, Clone)]
pub enum BinaryOperator {
    Plus, Minus, Multiply, Divide, Mod, Power,
    Equal, NotEqual, Less, LessEqual, Greater, GreaterEqual,
    And, Or,
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
        else_statements: Vec<Statement>,
    },
    For {
        variable: String,
        start: Expression,
        end: Expression,
        step: Option<Expression>,
        statements: Vec<Statement>,
    },
    Next {
        variable: String,
    },
    Goto {
        line: Expression,
    },
    Gosub {
        line: Expression,
    },
    Return,
    On {
        expression: Expression,
        is_gosub: bool,
        targets: Vec<Expression>,
    },
    Input {
        prompt: Option<String>,
        variables: Vec<String>,
    },
    Dim {
        arrays: Vec<(String, Vec<Expression>)>,
    },
    Data {
        values: Vec<Expression>,
    },
    Read {
        variables: Vec<String>,
    },
    Restore {
        line: Option<Expression>,
    },
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
    Comma, Semicolon, None,
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

    pub fn tokenize(&mut self) -> Result<Vec<Token>, String> {
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
                    while self.position < self.input.len() && self.input.as_bytes()[self.position].is_ascii_digit() {
                        self.position += 1;
                    }
                    if self.position < self.input.len() && self.input.as_bytes()[self.position] == b'.' {
                        self.position += 1;
                        while self.position < self.input.len() && self.input.as_bytes()[self.position].is_ascii_digit() {
                            self.position += 1;
                        }
                    }
                    let num_str = &self.input[start..self.position];
                    if let Ok(num) = num_str.parse::<f64>() {
                        tokens.push(Token::Number(num));
                    } else {
                        return Err(format!("Invalid number: {}", num_str));
                    }
                }
                '"' => {
                    self.position += 1;
                    let start = self.position;
                    while self.position < self.input.len() && self.input.as_bytes()[self.position] as char != '"' {
                        self.position += 1;
                    }
                    if self.position >= self.input.len() {
                        return Err("Unterminated string".to_string());
                    }
                    let str_val = self.input[start..self.position].to_string();
                    self.position += 1;
                    tokens.push(Token::String(str_val));
                }
                'A'..='Z' | 'a'..='z' | '_' => {
                    let start = self.position;
                    while self.position < self.input.len() && (self.input.as_bytes()[self.position].is_ascii_alphanumeric() || self.input.as_bytes()[self.position] == b'_') {
                        self.position += 1;
                    }
                    let ident = self.input[start..self.position].to_uppercase();
                    let token = match ident.as_str() {
                        "LET" => Token::Let,
                        "PRINT" => Token::Print,
                        "IF" => Token::If,
                        "THEN" => Token::Then,
                        "ELSE" => Token::Else,
                        "END" => Token::End,
                        "STOP" => Token::Stop,
                        "CLS" => Token::Cls,
                        "COLOR" => Token::Color,
                        "FORWARD" => Token::GraphicsForward,
                        "RIGHT" => Token::GraphicsRight,
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
                    if self.position + 1 < self.input.len() && self.input.as_bytes()[self.position + 1] == b'*' {
                        tokens.push(Token::Power);
                        self.position += 2;
                    } else {
                        tokens.push(Token::Multiply);
                        self.position += 1;
                    }
                }
                '/' => {
                    tokens.push(Token::Divide);
                    self.position += 1;
                }
                '%' => {
                    tokens.push(Token::Mod);
                    self.position += 1;
                }
                '=' => {
                    tokens.push(Token::Equal);
                    self.position += 1;
                }
                '<' => {
                    if self.position + 1 < self.input.len() {
                        match self.input.as_bytes()[self.position + 1] as char {
                            '=' => {
                                tokens.push(Token::LessEqual);
                                self.position += 2;
                            }
                            '>' => {
                                tokens.push(Token::NotEqual);
                                self.position += 2;
                            }
                            _ => {
                                tokens.push(Token::Less);
                                self.position += 1;
                            }
                        }
                    } else {
                        tokens.push(Token::Less);
                        self.position += 1;
                    }
                }
                '>' => {
                    if self.position + 1 < self.input.len() && self.input.as_bytes()[self.position + 1] == b'=' {
                        tokens.push(Token::GreaterEqual);
                        self.position += 2;
                    } else {
                        tokens.push(Token::Greater);
                        self.position += 1;
                    }
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
                ':' => {
                    tokens.push(Token::Colon);
                    self.position += 1;
                }
                '$' => {
                    tokens.push(Token::Dollar);
                    self.position += 1;
                }
                _ => {
                    return Err(format!("Unexpected character: {}", ch));
                }
            }
        }
        tokens.push(Token::EndOfFile);
        Ok(tokens)
    }
}

#[derive(Debug)]
pub struct Parser {
    tokens: Vec<Token>,
    position: usize,
    current_token: Option<Token>,
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

    pub fn parse_program(&mut self) -> Result<Vec<Statement>, String> {
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

        Ok(statements)
    }

    fn parse_statement(&mut self) -> Result<Statement, String> {
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
            Some(Token::GraphicsRight) => self.parse_right_statement(),
            Some(Token::Rem) => self.parse_rem_statement(),
            Some(Token::Identifier(ref id)) if id.to_uppercase() == "RIGHT" => {
                self.parse_right_statement()
            }
            _ => Err(format!(
                "Unexpected token in statement: {:?}",
                self.current_token
            )),
        }
    }

    fn parse_let_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume LET
        let var_name = self.parse_identifier()?;
        self.expect(&Token::Equal)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Let {
            variable: var_name,
            expression,
        })
    }

    fn parse_print_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume PRINT
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

        Ok(Statement::Print {
            expressions,
            separator,
        })
    }

    fn parse_if_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume IF
        let condition = self.parse_expression()?;
        self.expect(&Token::Then)?;
        
        let mut then_statements = Vec::new();
        let mut else_statements = Vec::new();
        
        // Parse then statements until ELSE or end
        while let Some(ref token) = self.current_token {
            if let Token::Else = token {
                self.advance(); // consume ELSE
                // Parse else statements
                while let Some(ref token) = self.current_token {
                    if let Token::Colon | Token::EndOfFile = token {
                        break;
                    }
                    let stmt = self.parse_statement()?;
                    else_statements.push(stmt);
                    if let Some(Token::Colon) = self.current_token {
                        self.advance();
                    }
                }
                break;
            } else if let Token::Colon | Token::EndOfFile = token {
                break;
            } else {
                let stmt = self.parse_statement()?;
                then_statements.push(stmt);
                if let Some(Token::Colon) = self.current_token {
                    self.advance();
                }
            }
        }

        Ok(Statement::If {
            condition,
            then_statements,
            else_statements,
        })
    }

    fn parse_goto_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume GOTO
        let line = self.parse_expression()?;
        Ok(Statement::Goto { line })
    }

    fn parse_input_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume INPUT
        let mut prompt = None;
        let mut variables = Vec::new();

        // Check for optional prompt
        if let Some(Token::String(s)) = &self.current_token {
            prompt = Some(s.clone());
            self.advance();
            if let Some(Token::Semicolon) = self.current_token {
                self.advance();
            }
        }

        // Parse variable list
        loop {
            let var_name = self.parse_identifier()?;
            variables.push(var_name);
            
            if let Some(Token::Comma) = self.current_token {
                self.advance();
            } else {
                break;
            }
        }

        Ok(Statement::Input { prompt, variables })
    }

    fn parse_rem_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume REM
        let mut comment = String::new();
        
        // Collect everything until end of line or colon
        while let Some(ref token) = self.current_token {
            match token {
                Token::Colon | Token::EndOfFile => break,
                Token::String(s) => {
                    comment.push_str(&s);
                    self.advance();
                }
                _ => {
                    // For other tokens, just advance (comments can contain anything)
                    self.advance();
                }
            }
        }
        
        Ok(Statement::Rem { comment })
    }

    fn parse_end_statement(&mut self) -> Result<Statement, String> {
        self.advance(); // consume END
        Ok(Statement::End)
    }

    // Stub implementations for other statements
    fn parse_for_statement(&mut self) -> Result<Statement, String> {
        Err("FOR loops not implemented in test".to_string())
    }
    fn parse_next_statement(&mut self) -> Result<Statement, String> {
        Err("NEXT not implemented in test".to_string())
    }
    fn parse_gosub_statement(&mut self) -> Result<Statement, String> {
        Err("GOSUB not implemented in test".to_string())
    }
    fn parse_return_statement(&mut self) -> Result<Statement, String> {
        Err("RETURN not implemented in test".to_string())
    }
    fn parse_on_statement(&mut self) -> Result<Statement, String> {
        Err("ON not implemented in test".to_string())
    }
    fn parse_dim_statement(&mut self) -> Result<Statement, String> {
        Err("DIM not implemented in test".to_string())
    }
    fn parse_data_statement(&mut self) -> Result<Statement, String> {
        Err("DATA not implemented in test".to_string())
    }
    fn parse_read_statement(&mut self) -> Result<Statement, String> {
        Err("READ not implemented in test".to_string())
    }
    fn parse_restore_statement(&mut self) -> Result<Statement, String> {
        Err("RESTORE not implemented in test".to_string())
    }
    fn parse_stop_statement(&mut self) -> Result<Statement, String> {
        Err("STOP not implemented in test".to_string())
    }
    fn parse_cls_statement(&mut self) -> Result<Statement, String> {
        Err("CLS not implemented in test".to_string())
    }
    fn parse_color_statement(&mut self) -> Result<Statement, String> {
        Err("COLOR not implemented in test".to_string())
    }
    fn parse_forward_statement(&mut self) -> Result<Statement, String> {
        Err("FORWARD not implemented in test".to_string())
    }
    fn parse_right_statement(&mut self) -> Result<Statement, String> {
        Err("RIGHT not implemented in test".to_string())
    }

    fn parse_expression(&mut self) -> Result<Expression, String> {
        self.parse_or()
    }

    fn parse_or(&mut self) -> Result<Expression, String> {
        let mut left = self.parse_and()?;

        while let Some(Token::Or) = self.current_token {
            self.advance();
            let right = self.parse_and()?;
            left = Expression::BinaryOp {
                left: Box::new(left),
                operator: BinaryOperator::Or,
                right: Box::new(right),
            };
        }

        Ok(left)
    }

    fn parse_and(&mut self) -> Result<Expression, String> {
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

    fn parse_comparison(&mut self) -> Result<Expression, String> {
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

    fn parse_additive(&mut self) -> Result<Expression, String> {
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

    fn parse_multiplicative(&mut self) -> Result<Expression, String> {
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

    fn parse_unary(&mut self) -> Result<Expression, String> {
        if let Some(Token::Minus) = self.current_token {
            self.advance();
            let expr = self.parse_unary()?;
            Ok(Expression::BinaryOp {
                left: Box::new(Expression::Number(0.0)),
                operator: BinaryOperator::Minus,
                right: Box::new(expr),
            })
        } else if let Some(Token::Not) = self.current_token {
            self.advance();
            let expr = self.parse_unary()?;
            Ok(Expression::BinaryOp {
                left: Box::new(Expression::Number(0.0)),
                operator: BinaryOperator::Minus,
                right: Box::new(expr),
            })
        } else {
            self.parse_power()
        }
    }

    fn parse_power(&mut self) -> Result<Expression, String> {
        let mut left = self.parse_primary()?;

        if let Some(Token::Power) = self.current_token {
            self.advance();
            let right = self.parse_unary()?;
            left = Expression::BinaryOp {
                left: Box::new(left),
                operator: BinaryOperator::Power,
                right: Box::new(right),
            };
        }

        Ok(left)
    }

    fn parse_primary(&mut self) -> Result<Expression, String> {
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
                
                // Check if this is a function call
                if let Some(Token::LParen) = self.current_token {
                    self.advance(); // consume '('
                    let mut arguments = Vec::new();
                    
                    if let Some(Token::RParen) = self.current_token {
                        self.advance(); // consume ')'
                    } else {
                        loop {
                            let arg = self.parse_expression()?;
                            arguments.push(arg);
                            
                            if let Some(Token::Comma) = self.current_token {
                                self.advance();
                            } else {
                                break;
                            }
                        }
                        self.expect(&Token::RParen)?;
                    }
                    
                    Ok(Expression::FunctionCall {
                        name: ident,
                        arguments,
                    })
                } else {
                    Ok(Expression::Variable(ident))
                }
            }
            Some(Token::LParen) => {
                self.advance(); // consume '('
                let expr = self.parse_expression()?;
                self.expect(&Token::RParen)?;
                Ok(expr)
            }
            _ => Err("Expected expression".to_string()),
        }
    }

    fn parse_identifier(&mut self) -> Result<String, String> {
        if let Some(Token::Identifier(id)) = self.current_token.clone() {
            self.advance();
            Ok(id)
        } else {
            Err("Expected identifier".to_string())
        }
    }

    fn expect(&mut self, expected: &Token) -> Result<(), String> {
        if let Some(ref token) = self.current_token {
            if token == expected {
                self.advance();
                Ok(())
            } else {
                Err(format!("Expected {:?}, found {:?}", expected, token))
            }
        } else {
            Err(format!("Expected {:?}, found end of input", expected))
        }
    }
}

fn main() {
    // Test the actual BASIC code from the game
    let program_code = r#"REM Number Guessing Game : PRINT "I'm thinking of a number between 1 and 100" : LET SECRET = 42 : PRINT "Guess the number:" : INPUT GUESS : IF GUESS = SECRET THEN GOTO 100 : IF GUESS < SECRET THEN PRINT "Too low!" : IF GUESS > SECRET THEN PRINT "Too high!" : GOTO 40 : PRINT "Correct! You win!""#;
    
    println!("Testing processed BASIC code:");
    println!("{}", program_code);
    println!("\n--- Tokenizing ---");
    
    let mut tokenizer = Tokenizer::new(program_code);
    match tokenizer.tokenize() {
        Ok(tokens) => {
            println!("Tokens: {:?}", tokens);
            println!("\n--- Parsing ---");
            
            let mut parser = Parser::new(tokens);
            match parser.parse_program() {
                Ok(statements) => {
                    println!("Successfully parsed {} statements:", statements.len());
                    for (i, stmt) in statements.iter().enumerate() {
                        println!("  {}: {:?}", i + 1, stmt);
                    }
                }
                Err(e) => {
                    println!("Parse error: {}", e);
                }
            }
        }
        Err(e) => {
            println!("Tokenize error: {}", e);
        }
    }
}
