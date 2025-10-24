use std::env;use std::collections::HashMap;

use time_warp_ide::languages::basic::Interpreter;use std::time::{SystemTime, UNIX_EPOCH};



fn main() {#[derive(Debug, Clone, PartialEq)]

    let args: Vec<String> = env::args().collect();pub enum Token {

    if args.len() < 2 {    Let,

        eprintln!("Usage: {} <basic_program>", args[0]);    Print,

        return;    End,

    }    Identifier(String),

    Number(f64),

    let program = &args[1];    String(String),

    let mut interpreter = Interpreter::new();    Plus,

    Equal,

    match interpreter.execute(program) {    Comma,

        Ok(result) => {    Semicolon,

            match result {    Colon,

                time_warp_ide::languages::basic::ExecutionResult::Complete { output, graphics_commands } => {    EndOfFile,

                    println!("Program executed successfully!");}

                    println!("Output: {}", output);

                    println!("Graphics commands: {}", graphics_commands.len());#[derive(Debug, Clone)]

                }pub enum Expression {

                time_warp_ide::languages::basic::ExecutionResult::NeedInput { variable, prompt, partial_output, partial_graphics } => {    Number(f64),

                    println!("Program needs input for variable: {}", variable);    String(String),

                    println!("Prompt: {}", prompt);    Variable(String),

                }    BinaryOp {

                time_warp_ide::languages::basic::ExecutionResult::Error(msg) => {        left: Box<Expression>,

                    println!("Execution error: {}", msg);        operator: BinaryOperator,

                }        right: Box<Expression>,

            }    },

        }}

        Err(e) => {

            println!("Parse/execution error: {:?}", e);#[derive(Debug, Clone)]

        }pub enum BinaryOperator {

    }    Plus,

}    Equal,
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
    End,
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
                    while self.position < self.input.len()
                        && self.input.as_bytes()[self.position].is_ascii_digit()
                    {
                        self.position += 1;
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
                    while self.position < self.input.len()
                        && self.input.as_bytes()[self.position] as char != '"'
                    {
                        self.position += 1;
                    }
                    if self.position >= self.input.len() {
                        return Err("Unterminated string".to_string());
                    }
                    let str_val = self.input[start..self.position].to_string();
                    self.position += 1;
                    tokens.push(Token::String(str_val));
                }
                'A'..='Z' | 'a'..='z' => {
                    let start = self.position;
                    while self.position < self.input.len()
                        && (self.input.as_bytes()[self.position].is_ascii_alphanumeric()
                            || self.input.as_bytes()[self.position] == b'_')
                    {
                        self.position += 1;
                    }
                    let ident = self.input[start..self.position].to_uppercase();
                    let token = match ident.as_str() {
                        "LET" => Token::Let,
                        "PRINT" => Token::Print,
                        "END" => Token::End,
                        _ => Token::Identifier(ident),
                    };
                    tokens.push(token);
                }
                '+' => {
                    tokens.push(Token::Plus);
                    self.position += 1;
                }
                '=' => {
                    tokens.push(Token::Equal);
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

    pub fn parse_program(&mut self) -> Result<Program, String> {
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

    fn parse_statement(&mut self) -> Result<Statement, String> {
        match self.current_token {
            Some(Token::Let) => self.parse_let_statement(),
            Some(Token::Print) => self.parse_print_statement(),
            Some(Token::End) => {
                self.advance();
                Ok(Statement::End)
            }
            _ => Err("Unknown statement".to_string()),
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

    fn parse_expression(&mut self) -> Result<Expression, String> {
        self.parse_additive()
    }

    fn parse_additive(&mut self) -> Result<Expression, String> {
        let mut left = self.parse_primary()?;

        while let Some(ref token) = self.current_token {
            let operator = match token {
                Token::Plus => Some(BinaryOperator::Plus),
                _ => None,
            };

            if let Some(op) = operator {
                self.advance();
                let right = self.parse_primary()?;
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
                Ok(Expression::Variable(ident))
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
    // Test the parser with a simple BASIC program
    let code = r#"LET A = 5 : PRINT "Hello" : END"#;
    println!("Testing code: {}", code);

    let mut tokenizer = Tokenizer::new(code);
    match tokenizer.tokenize() {
        Ok(tokens) => {
            println!("Tokens: {:?}", tokens);

            let mut parser = Parser::new(tokens);
            match parser.parse_program() {
                Ok(program) => {
                    println!("Parsed program: {:?}", program);
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
