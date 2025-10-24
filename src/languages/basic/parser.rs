use crate::languages::basic::ast::{
    BinaryOperator, Expression, FunctionDefinition, InterpreterError, PrintSeparator, Program,
    Statement, Token, UnaryOperator,
};

/// Recursive descent parser for BASIC
pub struct Parser {
    tokens: Vec<Token>,
    position: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self {
            tokens,
            position: 0,
        }
    }

    pub fn parse_program(&mut self) -> Result<Program, InterpreterError> {
        let mut statements = Vec::new();
        let mut line_numbers = std::collections::HashMap::new();

        while !self.is_at_end() {
            // Skip empty lines
            while self.match_token(&[Token::Eol]) {}

            if self.is_at_end() {
                break;
            }

            let statement = self.parse_statement()?;
            statements.push(statement);

            // Expect end of line or end of file
            if !self.match_token(&[Token::Eol]) && !self.is_at_end() {
                return Err(InterpreterError::ParseError(
                    "Expected end of line".to_string(),
                ));
            }
        }

        Ok(Program {
            statements,
            line_numbers,
        })
    }

    fn parse_statement(&mut self) -> Result<Statement, InterpreterError> {
        match self.current_token() {
            Some(Token::Let) => self.parse_let_statement(),
            Some(Token::Print) => self.parse_print_statement(),
            Some(Token::Input) => self.parse_input_statement(),
            Some(Token::If) => self.parse_if_statement(),
            Some(Token::For) => self.parse_for_statement(),
            Some(Token::Next) => self.parse_next_statement(),
            Some(Token::Goto) => self.parse_goto_statement(),
            Some(Token::Gosub) => self.parse_gosub_statement(),
            Some(Token::Return) => self.parse_return_statement(),
            Some(Token::End) => self.parse_end_statement(),
            Some(Token::Stop) => self.parse_stop_statement(),
            Some(Token::Rem) => self.parse_rem_statement(),
            Some(Token::Dim) => self.parse_dim_statement(),
            Some(Token::Def) => self.parse_def_statement(),
            Some(Token::Identifier(_)) => self.parse_assignment_or_call(),
            _ => Err(InterpreterError::ParseError(format!(
                "Unexpected token in statement: {:?}",
                self.current_token()
            ))),
        }
    }

    fn parse_let_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Let)?;
        let variable = self.parse_identifier()?;
        self.consume_token(Token::Equal)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Let {
            variable,
            expression,
        })
    }

    fn parse_print_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Print)?;
        let mut expressions = Vec::new();
        let mut separators = Vec::new();

        while !self.check(&[Token::Eol, Token::Eof]) {
            expressions.push(self.parse_expression()?);

            if self.match_token(&[Token::Comma]) {
                separators.push(PrintSeparator::Comma);
            } else if self.match_token(&[Token::Semicolon]) {
                separators.push(PrintSeparator::Semicolon);
            } else {
                separators.push(PrintSeparator::None);
                break;
            }
        }

        Ok(Statement::Print {
            expressions,
            separators,
        })
    }

    fn parse_input_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Input)?;

        // Check for optional prompt string
        let prompt = if self.check(&[Token::String("".to_string())]) {
            let token = self.current_token().cloned();
            self.advance();
            if let Some(Token::String(s)) = token {
                Some(s)
            } else {
                None
            }
        } else {
            None
        };

        // Optional semicolon or comma separator
        if prompt.is_some() {
            self.match_token(&[Token::Comma, Token::Semicolon]);
        }

        // Parse variable name
        let variable = self.parse_identifier()?;

        Ok(Statement::Input { prompt, variable })
    }

    fn parse_if_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::If)?;
        let condition = self.parse_expression()?;
        self.consume_token(Token::Then)?;

        let then_branch = self.parse_statement_list()?;

        let else_branch = if self.match_token(&[Token::Else]) {
            Some(self.parse_statement_list()?)
        } else {
            None
        };

        Ok(Statement::If {
            condition,
            then_branch,
            else_branch,
        })
    }

    fn parse_for_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::For)?;
        let variable = self.parse_identifier()?;
        self.consume_token(Token::Equal)?;
        let start = self.parse_expression()?;
        self.consume_token(Token::To)?;
        let end = self.parse_expression()?;
        let step = if self.match_token(&[Token::Step]) {
            Some(self.parse_expression()?)
        } else {
            None
        };

        let body = self.parse_statement_list()?;

        Ok(Statement::For {
            variable,
            start,
            end,
            step,
            body,
        })
    }

    fn parse_next_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Next)?;
        let variable = if let Some(Token::Identifier(_)) = self.current_token() {
            Some(self.parse_identifier()?)
        } else {
            None
        };
        Ok(Statement::Next { variable })
    }

    fn parse_goto_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Goto)?;
        let line = self.parse_expression()?;
        Ok(Statement::Goto { line })
    }

    fn parse_gosub_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Gosub)?;
        let line = self.parse_expression()?;
        Ok(Statement::Gosub { line })
    }

    fn parse_return_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Return)?;
        Ok(Statement::Return)
    }

    fn parse_end_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::End)?;
        Ok(Statement::End)
    }

    fn parse_stop_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Stop)?;
        Ok(Statement::Stop)
    }

    fn parse_rem_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Rem)?;
        let comment = if let Some(Token::String(s)) = self.current_token().cloned() {
            self.advance();
            s.clone()
        } else {
            String::new()
        };
        Ok(Statement::Rem(comment))
    }

    fn parse_dim_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Dim)?;
        let mut arrays = Vec::new();

        loop {
            let name = self.parse_identifier()?;
            self.consume_token(Token::LParen)?;
            let mut dimensions = Vec::new();

            loop {
                dimensions.push(self.parse_expression()?);
                if !self.match_token(&[Token::Comma]) {
                    break;
                }
            }

            self.consume_token(Token::RParen)?;
            arrays.push((name, dimensions));

            if !self.match_token(&[Token::Comma]) {
                break;
            }
        }

        Ok(Statement::Dim { arrays })
    }

    fn parse_def_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Def)?;
        self.consume_token(Token::Fn)?;
        let name = self.parse_identifier()?;
        self.consume_token(Token::LParen)?;

        let mut parameters = Vec::new();
        if let Some(Token::Identifier(_)) = self.current_token() {
            loop {
                parameters.push(self.parse_identifier()?);
                if !self.match_token(&[Token::Comma]) {
                    break;
                }
            }
        }

        self.consume_token(Token::RParen)?;
        self.consume_token(Token::Equal)?;
        let body = self.parse_expression()?;

        Ok(Statement::Def {
            name,
            parameters,
            body,
        })
    }

    fn parse_assignment_or_call(&mut self) -> Result<Statement, InterpreterError> {
        let identifier = self.parse_identifier()?;

        if self.match_token(&[Token::Equal]) {
            let expression = self.parse_expression()?;
            Ok(Statement::Let {
                variable: identifier,
                expression,
            })
        } else if self.match_token(&[Token::LParen]) {
            // Function call as statement
            let mut arguments = Vec::new();

            if let Some(Token::RParen) = self.current_token() {
                self.advance();
            } else {
                loop {
                    arguments.push(self.parse_expression()?);
                    if !self.match_token(&[Token::Comma]) {
                        self.consume_token(Token::RParen)?;
                        break;
                    }
                }
            }

            // For now, treat function calls as statements that do nothing
            // In a real BASIC, this might be a subroutine call
            Ok(Statement::Rem(format!(
                "Function call: {}({:?})",
                identifier, arguments
            )))
        } else {
            Err(InterpreterError::ParseError(format!(
                "Expected '=' or '(' after identifier '{}'",
                identifier
            )))
        }
    }

    fn parse_statement_list(&mut self) -> Result<Vec<Statement>, InterpreterError> {
        let mut statements = Vec::new();

        while !self.check(&[Token::Else, Token::Next, Token::End, Token::Eol, Token::Eof]) {
            statements.push(self.parse_statement()?);

            if !self.match_token(&[Token::Colon]) {
                break;
            }
        }

        Ok(statements)
    }

    fn parse_expression(&mut self) -> Result<Expression, InterpreterError> {
        self.parse_logical_or()
    }

    fn parse_logical_or(&mut self) -> Result<Expression, InterpreterError> {
        let mut expr = self.parse_logical_and()?;

        while self.match_token(&[Token::Or]) {
            let operator = BinaryOperator::Or;
            let right = self.parse_logical_and()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_logical_and(&mut self) -> Result<Expression, InterpreterError> {
        let mut expr = self.parse_comparison()?;

        while self.match_token(&[Token::And]) {
            let operator = BinaryOperator::And;
            let right = self.parse_comparison()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_comparison(&mut self) -> Result<Expression, InterpreterError> {
        let mut expr = self.parse_term()?;

        while self.match_token(&[
            Token::Equal,
            Token::NotEqual,
            Token::Less,
            Token::LessEqual,
            Token::Greater,
            Token::GreaterEqual,
        ]) {
            let operator = match self.previous_token() {
                Some(Token::Equal) => BinaryOperator::Equal,
                Some(Token::NotEqual) => BinaryOperator::NotEqual,
                Some(Token::Less) => BinaryOperator::Less,
                Some(Token::LessEqual) => BinaryOperator::LessEqual,
                Some(Token::Greater) => BinaryOperator::Greater,
                Some(Token::GreaterEqual) => BinaryOperator::GreaterEqual,
                _ => unreachable!(),
            };
            let right = self.parse_term()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_term(&mut self) -> Result<Expression, InterpreterError> {
        let mut expr = self.parse_factor()?;

        while self.match_token(&[Token::Plus, Token::Minus]) {
            let operator = match self.previous_token() {
                Some(Token::Plus) => BinaryOperator::Add,
                Some(Token::Minus) => BinaryOperator::Subtract,
                _ => unreachable!(),
            };
            let right = self.parse_factor()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_factor(&mut self) -> Result<Expression, InterpreterError> {
        let mut expr = self.parse_power()?;

        while self.match_token(&[Token::Multiply, Token::Divide, Token::Modulo]) {
            let operator = match self.previous_token() {
                Some(Token::Multiply) => BinaryOperator::Multiply,
                Some(Token::Divide) => BinaryOperator::Divide,
                Some(Token::Modulo) => BinaryOperator::Modulo,
                _ => unreachable!(),
            };
            let right = self.parse_power()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                operator,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_power(&mut self) -> Result<Expression, InterpreterError> {
        let mut expr = self.parse_unary()?;

        if self.match_token(&[Token::Power]) {
            let right = self.parse_power()?;
            expr = Expression::BinaryOp {
                left: Box::new(expr),
                operator: BinaryOperator::Power,
                right: Box::new(right),
            };
        }

        Ok(expr)
    }

    fn parse_unary(&mut self) -> Result<Expression, InterpreterError> {
        if self.match_token(&[Token::Minus, Token::Not]) {
            let operator = match self.previous_token() {
                Some(Token::Minus) => UnaryOperator::Negate,
                Some(Token::Not) => UnaryOperator::Not,
                _ => unreachable!(),
            };
            let operand = self.parse_unary()?;
            Ok(Expression::UnaryOp {
                operator,
                operand: Box::new(operand),
            })
        } else {
            self.parse_primary()
        }
    }

    fn parse_primary(&mut self) -> Result<Expression, InterpreterError> {
        match self.current_token().cloned() {
            Some(Token::Number(n)) => {
                self.advance();
                Ok(Expression::Number(n))
            }
            Some(Token::String(s)) => {
                self.advance();
                Ok(Expression::String(s))
            }
            Some(Token::Identifier(ident)) => {
                self.advance();

                if self.match_token(&[Token::LParen]) {
                    // Function call or array access
                    let mut arguments = Vec::new();

                    if let Some(Token::RParen) = self.current_token() {
                        self.advance();
                    } else {
                        loop {
                            arguments.push(self.parse_expression()?);
                            if !self.match_token(&[Token::Comma]) {
                                self.consume_token(Token::RParen)?;
                                break;
                            }
                        }
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
                self.advance();
                let expr = self.parse_expression()?;
                self.consume_token(Token::RParen)?;
                Ok(expr)
            }
            _ => Err(InterpreterError::ParseError(format!(
                "Unexpected token in expression: {:?}",
                self.current_token()
            ))),
        }
    }

    fn parse_identifier(&mut self) -> Result<String, InterpreterError> {
        if let Some(Token::Identifier(id)) = self.current_token().cloned() {
            self.advance();
            Ok(id)
        } else {
            Err(InterpreterError::ParseError(
                "Expected identifier".to_string(),
            ))
        }
    }

    // Helper methods
    fn current_token(&self) -> Option<&Token> {
        if self.position < self.tokens.len() {
            Some(&self.tokens[self.position])
        } else {
            None
        }
    }

    fn previous_token(&self) -> Option<&Token> {
        if self.position > 0 {
            Some(&self.tokens[self.position - 1])
        } else {
            None
        }
    }

    fn advance(&mut self) {
        if self.position < self.tokens.len() {
            self.position += 1;
        }
    }

    fn match_token(&mut self, tokens: &[Token]) -> bool {
        for token in tokens {
            if self.check(&[token.clone()]) {
                self.advance();
                return true;
            }
        }
        false
    }

    fn check(&self, tokens: &[Token]) -> bool {
        if let Some(current) = self.current_token() {
            tokens.contains(current)
        } else {
            false
        }
    }

    fn consume_token(&mut self, expected: Token) -> Result<(), InterpreterError> {
        if self.check(&[expected.clone()]) {
            self.advance();
            Ok(())
        } else {
            Err(InterpreterError::ParseError(format!(
                "Expected {:?}, found {:?}",
                expected,
                self.current_token()
            )))
        }
    }

    fn is_at_end(&self) -> bool {
        matches!(self.current_token(), Some(Token::Eof) | None)
    }
}
