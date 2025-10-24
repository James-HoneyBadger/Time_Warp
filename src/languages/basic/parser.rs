use crate::languages::basic::ast::{
    BinaryOperator, CaseValue, Expression, FunctionDefinition, InterpreterError, PrintSeparator,
    Program, SelectCase, Statement, Token, UnaryOperator,
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

            // Check for line number at start of statement
            let line_number = if let Some(Token::Number(num)) = self.current_token() {
                if num.fract() == 0.0 && *num >= 0.0 && *num <= 65529.0 {
                    let line_num = *num as usize;
                    self.advance(); // consume the line number
                    Some(line_num)
                } else {
                    None
                }
            } else {
                None
            };

            let statement = self.parse_statement()?;
            let statement_index = statements.len();
            statements.push(statement);

            // Store line number mapping if present
            if let Some(line_num) = line_number {
                line_numbers.insert(line_num, statement_index);
            }

            // Expect statement separator (colon), end of line, or end of file
            if !self.match_token(&[Token::Colon])
                && !self.match_token(&[Token::Eol])
                && !self.is_at_end()
            {
                return Err(InterpreterError::ParseError(
                    "Expected ':' or end of line after statement".to_string(),
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
            Some(Token::Clear) => self.parse_clear_statement(),
            Some(Token::Writeln) => self.parse_writeln_statement(),
            Some(Token::Printx) => self.parse_printx_statement(),
            Some(Token::Defint) => self.parse_defint_statement(),
            Some(Token::Defsng) => self.parse_defsng_statement(),
            Some(Token::Defstr) => self.parse_defstr_statement(),
            Some(Token::Defdbl) => self.parse_defdbl_statement(),
            Some(Token::Select) => self.parse_select_statement(),
            Some(Token::Forward) => self.parse_forward_statement(),
            Some(Token::Back) => self.parse_back_statement(),
            Some(Token::TurnLeft) => self.parse_turn_left_statement(),
            Some(Token::TurnRight) => self.parse_turn_right_statement(),
            Some(Token::Penup) => self.parse_penup_statement(),
            Some(Token::Pendown) => self.parse_pendown_statement(),
            Some(Token::Home) => self.parse_home_statement(),
            Some(Token::Setxy) => self.parse_setxy_statement(),
            Some(Token::Turn) => self.parse_turn_statement(),
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
            Some(Token::Date) => {
                self.advance();
                Ok(Expression::FunctionCall {
                    name: "DATE".to_string(),
                    arguments: vec![],
                })
            }
            Some(Token::Timer) => {
                self.advance();
                Ok(Expression::FunctionCall {
                    name: "TIMER".to_string(),
                    arguments: vec![],
                })
            }
            Some(Token::Tab) => {
                self.advance();
                self.consume_token(Token::LParen)?;
                let arg = self.parse_expression()?;
                self.consume_token(Token::RParen)?;
                Ok(Expression::FunctionCall {
                    name: "TAB".to_string(),
                    arguments: vec![arg],
                })
            }
            Some(Token::Spc) => {
                self.advance();
                self.consume_token(Token::LParen)?;
                let arg = self.parse_expression()?;
                self.consume_token(Token::RParen)?;
                Ok(Expression::FunctionCall {
                    name: "SPC".to_string(),
                    arguments: vec![arg],
                })
            }
            Some(Token::Fn) => {
                self.advance();
                let func_name = self.parse_identifier()?;
                self.consume_token(Token::LParen)?;
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
                    name: format!("FN{}", func_name),
                    arguments,
                })
            }
            Some(Token::Int) => {
                self.advance();
                self.consume_token(Token::LParen)?;
                let arg = self.parse_expression()?;
                self.consume_token(Token::RParen)?;
                Ok(Expression::FunctionCall {
                    name: "INT".to_string(),
                    arguments: vec![arg],
                })
            }
            Some(Token::Rnd) => {
                self.advance();
                self.consume_token(Token::LParen)?;
                let arg = self.parse_expression()?;
                self.consume_token(Token::RParen)?;
                Ok(Expression::FunctionCall {
                    name: "RND".to_string(),
                    arguments: vec![arg],
                })
            }
            Some(Token::Environ) => {
                self.advance();
                // ENVIRON requires an argument
                self.consume_token(Token::LParen)?;
                let arg = self.parse_expression()?;
                self.consume_token(Token::RParen)?;
                Ok(Expression::FunctionCall {
                    name: "ENVIRON".to_string(),
                    arguments: vec![arg],
                })
            }
            Some(Token::Identifier(ident)) => {
                self.advance();

                // Check if this is a function call (with or without parentheses)
                let is_function = self.check(&[Token::LParen])
                    || ident.ends_with('$')
                    || matches!(
                        ident.to_uppercase().as_str(),
                        "TAB"
                            | "SPC"
                            | "SIN"
                            | "COS"
                            | "TAN"
                            | "SQR"
                            | "ABS"
                            | "INT"
                            | "RND"
                            | "LEN"
                            | "MID"
                            | "LEFT"
                            | "RIGHT"
                            | "CHR"
                            | "ASC"
                            | "VAL"
                            | "STR"
                    );

                if is_function {
                    let mut arguments = Vec::new();

                    if self.match_token(&[Token::LParen]) {
                        // Function call with parentheses
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
                    }
                    // For functions without parentheses, arguments is empty

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

    fn parse_clear_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Clear)?;
        Ok(Statement::Clear)
    }

    fn parse_writeln_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Writeln)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Writeln { expression })
    }

    fn parse_printx_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Printx)?;
        let expression = self.parse_expression()?;
        Ok(Statement::Printx { expression })
    }

    fn parse_defint_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Defint)?;
        let ranges = self.parse_range_list()?;
        Ok(Statement::DefInt { ranges })
    }

    fn parse_defsng_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Defsng)?;
        let ranges = self.parse_range_list()?;
        Ok(Statement::DefSng { ranges })
    }

    fn parse_defstr_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Defstr)?;
        let ranges = self.parse_range_list()?;
        Ok(Statement::DefStr { ranges })
    }

    fn parse_defdbl_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Defdbl)?;
        let ranges = self.parse_range_list()?;
        Ok(Statement::DefDbl { ranges })
    }

    fn parse_range_list(&mut self) -> Result<Vec<String>, InterpreterError> {
        let mut ranges = Vec::new();
        loop {
            // Parse the start of the range (should be a single letter identifier)
            let start = self.parse_identifier()?;

            // Check if this is a range (start-end)
            let range = if self.match_token(&[Token::Minus]) {
                let end = self.parse_identifier()?;
                format!("{}-{}", start, end)
            } else {
                start
            };

            ranges.push(range);
            if !self.match_token(&[Token::Comma]) {
                break;
            }
        }
        Ok(ranges)
    }

    fn parse_select_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Select)?;
        self.consume_token(Token::Case)?;
        let expression = self.parse_expression()?;
        self.consume_token(Token::Eol)?;

        let mut cases = Vec::new();
        while !self.check(&[Token::End]) {
            if self.match_token(&[Token::Case]) {
                let value = if self.check(&[Token::Else]) {
                    self.consume_token(Token::Else)?;
                    None
                } else {
                    // CASE value or CASE min TO max or CASE IS operator value
                    let expr1 = self.parse_expression()?;
                    if self.match_token(&[Token::To]) {
                        let expr2 = self.parse_expression()?;
                        Some(CaseValue::Range(expr1, expr2))
                    } else if self.match_token(&[Token::Is]) {
                        let operator = self.parse_comparison_operator()?;
                        let expr2 = self.parse_expression()?;
                        Some(CaseValue::Is(operator, expr2))
                    } else {
                        Some(CaseValue::Single(expr1))
                    }
                };

                let mut statements = Vec::new();
                while !self.check(&[Token::Case, Token::End, Token::Eol]) {
                    statements.push(self.parse_statement()?);
                    if !self.match_token(&[Token::Colon]) {
                        break;
                    }
                }

                cases.push(SelectCase { value, statements });
            } else {
                break;
            }
        }

        self.consume_token(Token::End)?;
        self.consume_token(Token::Select)?;

        Ok(Statement::Select { expression, cases })
    }

    fn parse_comparison_operator(&mut self) -> Result<BinaryOperator, InterpreterError> {
        match self.current_token() {
            Some(Token::Equal) => {
                self.advance();
                Ok(BinaryOperator::Equal)
            }
            Some(Token::NotEqual) => {
                self.advance();
                Ok(BinaryOperator::NotEqual)
            }
            Some(Token::Less) => {
                self.advance();
                Ok(BinaryOperator::Less)
            }
            Some(Token::LessEqual) => {
                self.advance();
                Ok(BinaryOperator::LessEqual)
            }
            Some(Token::Greater) => {
                self.advance();
                Ok(BinaryOperator::Greater)
            }
            Some(Token::GreaterEqual) => {
                self.advance();
                Ok(BinaryOperator::GreaterEqual)
            }
            _ => Err(InterpreterError::ParseError(
                "Expected comparison operator after IS".to_string(),
            )),
        }
    }

    fn parse_forward_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Forward)?;
        let distance = self.parse_expression()?;
        Ok(Statement::Forward { distance })
    }

    fn parse_back_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Back)?;
        let distance = self.parse_expression()?;
        Ok(Statement::Back { distance })
    }

    fn parse_turn_left_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::TurnLeft)?;
        let angle = self.parse_expression()?;
        Ok(Statement::TurnLeft { angle })
    }

    fn parse_turn_right_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::TurnRight)?;
        let angle = self.parse_expression()?;
        Ok(Statement::TurnRight { angle })
    }

    fn parse_penup_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Penup)?;
        Ok(Statement::Penup)
    }

    fn parse_pendown_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Pendown)?;
        Ok(Statement::Pendown)
    }

    fn parse_home_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Home)?;
        Ok(Statement::Home)
    }

    fn parse_setxy_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Setxy)?;
        let x = self.parse_expression()?;
        self.consume_token(Token::Comma)?;
        let y = self.parse_expression()?;
        Ok(Statement::Setxy { x, y })
    }

    fn parse_turn_statement(&mut self) -> Result<Statement, InterpreterError> {
        self.consume_token(Token::Turn)?;
        let angle = self.parse_expression()?;
        Ok(Statement::Turn { angle })
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
