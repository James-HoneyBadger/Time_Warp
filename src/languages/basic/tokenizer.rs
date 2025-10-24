use crate::languages::basic::ast::{InterpreterError, Token};

/// Lexical analyzer for BASIC code
pub struct Tokenizer {
    input: Vec<char>,
    position: usize,
    line: usize,
    column: usize,
}

impl Tokenizer {
    pub fn new(input: &str) -> Self {
        Self {
            input: input.chars().collect(),
            position: 0,
            line: 1,
            column: 1,
        }
    }

    pub fn tokenize(&mut self) -> Result<Vec<Token>, InterpreterError> {
        let mut tokens = Vec::new();

        while let Some(token) = self.next_token()? {
            tokens.push(token);
        }

        tokens.push(Token::Eof);
        Ok(tokens)
    }

    fn next_token(&mut self) -> Result<Option<Token>, InterpreterError> {
        self.skip_whitespace();

        if self.position >= self.input.len() {
            return Ok(None);
        }

        let ch = self.input[self.position];

        match ch {
            // Single character tokens
            '(' => {
                self.advance();
                Ok(Some(Token::LParen))
            }
            ')' => {
                self.advance();
                Ok(Some(Token::RParen))
            }
            ',' => {
                self.advance();
                Ok(Some(Token::Comma))
            }
            ';' => {
                self.advance();
                Ok(Some(Token::Semicolon))
            }
            ':' => {
                self.advance();
                Ok(Some(Token::Colon))
            }

            // Operators
            '+' => {
                self.advance();
                Ok(Some(Token::Plus))
            }
            '-' => {
                self.advance();
                Ok(Some(Token::Minus))
            }
            '*' => {
                self.advance();
                if self.peek() == Some('^') {
                    self.advance();
                    Ok(Some(Token::Power))
                } else {
                    Ok(Some(Token::Multiply))
                }
            }
            '/' => {
                self.advance();
                Ok(Some(Token::Divide))
            }
            '%' => {
                self.advance();
                Ok(Some(Token::Modulo))
            }
            '=' => {
                self.advance();
                Ok(Some(Token::Equal))
            }
            '<' => {
                self.advance();
                if self.peek() == Some('=') {
                    self.advance();
                    Ok(Some(Token::LessEqual))
                } else if self.peek() == Some('>') {
                    self.advance();
                    Ok(Some(Token::NotEqual))
                } else {
                    Ok(Some(Token::Less))
                }
            }
            '>' => {
                self.advance();
                if self.peek() == Some('=') {
                    self.advance();
                    Ok(Some(Token::GreaterEqual))
                } else {
                    Ok(Some(Token::Greater))
                }
            }

            // Numbers
            '0'..='9' => self.tokenize_number(),

            // Strings
            '"' => self.tokenize_string(),

            // Identifiers and keywords
            'A'..='Z' | 'a'..='z' | '_' => self.tokenize_identifier(),

            // End of line
            '\n' => {
                self.advance();
                self.line += 1;
                self.column = 1;
                Ok(Some(Token::Eol))
            }

            // Unexpected character
            _ => Err(InterpreterError::ParseError(format!(
                "Unexpected character '{}' at line {}, column {}",
                ch, self.line, self.column
            ))),
        }
    }

    fn tokenize_number(&mut self) -> Result<Option<Token>, InterpreterError> {
        let start = self.position;

        while self.position < self.input.len() && self.input[self.position].is_ascii_digit() {
            self.advance();
        }

        if self.peek() == Some('.') {
            self.advance(); // consume '.'
            while self.position < self.input.len() && self.input[self.position].is_ascii_digit() {
                self.advance();
            }
        }

        let number_str: String = self.input[start..self.position].iter().collect();
        match number_str.parse::<f64>() {
            Ok(num) => Ok(Some(Token::Number(num))),
            Err(_) => Err(InterpreterError::ParseError(format!(
                "Invalid number: {}",
                number_str
            ))),
        }
    }

    fn tokenize_string(&mut self) -> Result<Option<Token>, InterpreterError> {
        self.advance(); // consume opening quote
        let start = self.position;

        while self.position < self.input.len() && self.input[self.position] != '"' {
            self.advance();
        }

        if self.position >= self.input.len() {
            return Err(InterpreterError::ParseError(
                "Unterminated string literal".to_string(),
            ));
        }

        let string: String = self.input[start..self.position].iter().collect();
        self.advance(); // consume closing quote

        Ok(Some(Token::String(string)))
    }

    fn tokenize_identifier(&mut self) -> Result<Option<Token>, InterpreterError> {
        let start = self.position;

        while self.position < self.input.len()
            && (self.input[self.position].is_ascii_alphanumeric()
                || self.input[self.position] == '_'
                || self.input[self.position] == '$')
        {
            self.advance();
        }

        let identifier: String = self.input[start..self.position].iter().collect();
        let upper_identifier = identifier.to_uppercase();

        // Check for keywords
        let token = match upper_identifier.as_str() {
            "LET" => Token::Let,
            "PRINT" => Token::Print,
            "INPUT" => Token::Input,
            "IF" => Token::If,
            "THEN" => Token::Then,
            "ELSE" => Token::Else,
            "END" => Token::End,
            "STOP" => Token::Stop,
            "FOR" => Token::For,
            "TO" => Token::To,
            "STEP" => Token::Step,
            "NEXT" => Token::Next,
            "GOTO" => Token::Goto,
            "GOSUB" => Token::Gosub,
            "RETURN" => Token::Return,
            "REM" => Token::Rem,
            "DIM" => Token::Dim,
            "DEF" => Token::Def,
            "FN" => Token::Fn,
            "CLEAR" => Token::Clear,
            "WRITELN" => Token::Writeln,
            "PRINTX" => Token::Printx,
            "DEFINT" => Token::Defint,
            "DEFSNG" => Token::Defsng,
            "DEFSTR" => Token::Defstr,
            "DEFDBL" => Token::Defdbl,
            "SELECT" => Token::Select,
            "CASE" => Token::Case,
            "IS" => Token::Is,
            "FORWARD" => Token::Forward,
            "BACK" => Token::Back,
            "LEFT" => Token::TurnLeft,
            "RIGHT" => Token::TurnRight,
            "PENUP" => Token::Penup,
            "PENDOWN" => Token::Pendown,
            "HOME" => Token::Home,
            "SETXY" => Token::Setxy,
            "TURN" => Token::Turn,
            "TAB" => Token::Tab,
            "SPC" => Token::Spc,
            "AND" => Token::And,
            "OR" => Token::Or,
            "NOT" => Token::Not,
            "SIN" => Token::Sin,
            "COS" => Token::Cos,
            "TAN" => Token::Tan,
            "SQR" => Token::Sqr,
            "ABS" => Token::Abs,
            "INT" => Token::Int,
            "RND" => Token::Rnd,
            "LEN" => Token::Len,
            "MID" => Token::Mid,
            "CHR" => Token::Chr,
            "ASC" => Token::Asc,
            "VAL" => Token::Val,
            "STR" => Token::Str,
            "DATE" => Token::Date,
            "TIME" => Token::Time,
            "TIMER" => Token::Timer,
            "ENVIRON" => Token::Environ,
            _ => Token::Identifier(identifier),
        };

        Ok(Some(token))
    }

    fn skip_whitespace(&mut self) {
        while self.position < self.input.len() {
            let ch = self.input[self.position];
            if ch.is_whitespace() && ch != '\n' {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn advance(&mut self) {
        if self.position < self.input.len() {
            self.position += 1;
            self.column += 1;
        }
    }

    fn peek(&self) -> Option<char> {
        if self.position < self.input.len() {
            Some(self.input[self.position])
        } else {
            None
        }
    }
}
