use std::collections::HashMap;

#[derive(Clone, Debug)]
pub enum PascalValue {
    Integer(i64),
    Real(f64),
    Char(char),
    String(String),
    Boolean(bool),
}

#[derive(Clone, Debug)]
pub struct PascalVariable {
    pub value: PascalValue,
    pub var_type: String,
}

#[derive(Clone, Debug)]
pub struct PascalProcedure {
    pub name: String,
    pub parameters: Vec<String>,
    pub body: String,
}

#[derive(Clone, Debug)]
pub enum CommandResult {
    Output(String),
    Input(String, String), // (variable_name, prompt)
    Continue,
    End,
}

pub struct PascalInterpreter {
    variables: HashMap<String, PascalVariable>,
    procedures: HashMap<String, PascalProcedure>,
    program_lines: Vec<String>,
    current_line: usize,
}

impl PascalInterpreter {
    pub fn new() -> Self {
        Self {
            variables: HashMap::new(),
            procedures: HashMap::new(),
            program_lines: Vec::new(),
            current_line: 0,
        }
    }

    pub fn execute(&mut self, code: &str) -> String {
        // Parse program into lines
        self.program_lines.clear();
        for line in code.lines() {
            let trimmed = line.trim();
            if !trimmed.is_empty() {
                self.program_lines.push(trimmed.to_string());
            }
        }

        // Execute the program
        self.current_line = 0;
        let mut output = String::new();
        let mut variables = std::collections::HashMap::new();

        while self.current_line < self.program_lines.len() {
            let line = self.program_lines[self.current_line].clone();
            let result = self.execute_statement_with_vars(&line, &mut variables);

            match result {
                CommandResult::Output(text) => {
                    output.push_str(&text);
                    output.push('\n');
                }
                CommandResult::Input(_var_name, prompt) => {
                    // For now, return the prompt to indicate input is needed
                    // The main app will handle the actual input
                    output.push_str(&prompt);
                    // Don't continue execution until input is provided
                    break;
                }
                CommandResult::Continue => {}
                CommandResult::End => break,
            }

            self.current_line += 1;
        }

        if output.is_empty() {
            "Pascal program executed successfully".to_string()
        } else {
            output
        }
    }

    pub fn execute_statement_with_vars(
        &mut self,
        statement: &str,
        variables: &mut std::collections::HashMap<String, String>,
    ) -> CommandResult {
        let stmt = statement.trim_end_matches(';');

        if stmt.to_lowercase().starts_with("program ") {
            // Program header - ignore for now
            return CommandResult::Continue;
        }

        if stmt.to_lowercase().starts_with("var ") {
            // Variable declarations
            self.handle_var_declaration(stmt);
            return CommandResult::Continue;
        }

        if stmt.to_lowercase().starts_with("procedure ") {
            // Procedure declarations
            self.handle_procedure_declaration(stmt);
            return CommandResult::Continue;
        }

        if stmt.to_lowercase().starts_with("function ") {
            // Function declarations
            self.handle_function_declaration(stmt);
            return CommandResult::Continue;
        }

        if stmt.to_lowercase().starts_with("begin") {
            // Begin block
            return CommandResult::Continue;
        }

        if stmt.to_lowercase() == "end" {
            // End block
            return CommandResult::End;
        }

        if stmt.to_lowercase().starts_with("writeln(") {
            return self.handle_writeln_with_vars(stmt, variables);
        }

        if stmt.to_lowercase().starts_with("write(") {
            return self.handle_write_with_vars(stmt, variables);
        }

        if stmt.to_lowercase().starts_with("readln(") {
            return self.handle_readln(stmt);
        }

        if stmt.contains(":=") {
            self.handle_assignment_with_vars(stmt, variables);
            return CommandResult::Continue;
        }

        if stmt.to_lowercase().starts_with("if ") {
            return self.handle_if_statement(stmt);
        }

        if stmt.to_lowercase().starts_with("while ") {
            return self.handle_while_loop(stmt);
        }

        if stmt.to_lowercase().starts_with("for ") {
            return self.handle_for_loop(stmt);
        }

        if stmt.to_lowercase().starts_with("repeat") {
            return self.handle_repeat_loop(stmt);
        }

        if stmt.to_lowercase().starts_with("case ") {
            return self.handle_case_statement(stmt);
        }

        CommandResult::Output(format!("Unknown statement: {}", stmt))
    }

    fn handle_var_declaration(&mut self, stmt: &str) -> CommandResult {
        // Simple variable declaration parsing
        // var x, y: integer; z: real;
        let var_part = &stmt[4..]; // Remove "var "
        let declarations: Vec<&str> = var_part.split(';').collect();

        for decl in declarations {
            let decl = decl.trim();
            if decl.is_empty() {
                continue;
            }

            if let Some(colon_pos) = decl.find(':') {
                let var_names = &decl[..colon_pos];
                let var_type = decl[colon_pos + 1..].trim();

                let names: Vec<&str> = var_names.split(',').map(|s| s.trim()).collect();
                for name in names {
                    match var_type.to_lowercase().as_str() {
                        "integer" => {
                            self.variables.insert(
                                name.to_string(),
                                PascalVariable {
                                    value: PascalValue::Integer(0),
                                    var_type: "integer".to_string(),
                                },
                            );
                        }
                        "real" => {
                            self.variables.insert(
                                name.to_string(),
                                PascalVariable {
                                    value: PascalValue::Real(0.0),
                                    var_type: "real".to_string(),
                                },
                            );
                        }
                        "char" => {
                            self.variables.insert(
                                name.to_string(),
                                PascalVariable {
                                    value: PascalValue::Char('\0'),
                                    var_type: "char".to_string(),
                                },
                            );
                        }
                        "string" => {
                            self.variables.insert(
                                name.to_string(),
                                PascalVariable {
                                    value: PascalValue::String(String::new()),
                                    var_type: "string".to_string(),
                                },
                            );
                        }
                        "boolean" => {
                            self.variables.insert(
                                name.to_string(),
                                PascalVariable {
                                    value: PascalValue::Boolean(false),
                                    var_type: "boolean".to_string(),
                                },
                            );
                        }
                        _ => {}
                    }
                }
            }
        }
        CommandResult::Continue
    }

    fn handle_procedure_declaration(&mut self, stmt: &str) -> CommandResult {
        // procedure name(params);
        if let Some(open_paren) = stmt.find('(') {
            let name = stmt[10..open_paren].trim(); // Remove "procedure "
            let params_str = &stmt[open_paren + 1..];
            if let Some(close_paren) = params_str.find(')') {
                let params: Vec<String> = params_str[..close_paren]
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .collect();

                self.procedures.insert(
                    name.to_string(),
                    PascalProcedure {
                        name: name.to_string(),
                        parameters: params,
                        body: String::new(), // Would need to parse the body
                    },
                );
            }
        }
        CommandResult::Continue
    }

    fn handle_function_declaration(&mut self, stmt: &str) -> CommandResult {
        // Similar to procedure but returns a value
        self.handle_procedure_declaration(stmt)
    }

    fn handle_writeln(&mut self, stmt: &str) -> CommandResult {
        if let Some(open_paren) = stmt.find('(') {
            if let Some(close_paren) = stmt.find(')') {
                let args = &stmt[open_paren + 1..close_paren];
                if args.trim().is_empty() {
                    return CommandResult::Output(String::new()); // Just a newline
                }

                let expressions: Vec<&str> = args
                    .split(',')
                    .map(|s| s.trim().trim_matches('\''))
                    .collect();
                let mut output = String::new();

                for (i, expr) in expressions.iter().enumerate() {
                    if let Some(var) = self.variables.get(*expr) {
                        match &var.value {
                            PascalValue::Integer(n) => output.push_str(&n.to_string()),
                            PascalValue::Real(n) => output.push_str(&n.to_string()),
                            PascalValue::Char(c) => output.push(*c),
                            PascalValue::String(s) => output.push_str(s),
                            PascalValue::Boolean(b) => {
                                output.push_str(if *b { "TRUE" } else { "FALSE" })
                            }
                        }
                    } else {
                        // Try to parse as literal
                        if let Ok(n) = expr.parse::<i64>() {
                            output.push_str(&n.to_string());
                        } else if let Ok(n) = expr.parse::<f64>() {
                            output.push_str(&n.to_string());
                        } else if expr.starts_with('\'') && expr.ends_with('\'') && expr.len() == 3
                        {
                            output.push(expr.chars().nth(1).unwrap());
                        } else {
                            output.push_str(expr);
                        }
                    }

                    if i < expressions.len() - 1 {
                        output.push(' ');
                    }
                }

                return CommandResult::Output(output);
            }
        }
        CommandResult::Continue
    }

    fn handle_write(&mut self, stmt: &str) -> CommandResult {
        self.handle_writeln(stmt) // Same as writeln but without newline
    }

    fn handle_writeln_with_vars(
        &mut self,
        stmt: &str,
        variables: &std::collections::HashMap<String, String>,
    ) -> CommandResult {
        if let Some(open_paren) = stmt.find('(') {
            if let Some(close_paren) = stmt.find(')') {
                let args = &stmt[open_paren + 1..close_paren];
                if args.trim().is_empty() {
                    return CommandResult::Output(String::new()); // Just a newline
                }

                let expressions: Vec<&str> = args
                    .split(',')
                    .map(|s| s.trim().trim_matches('\''))
                    .collect();
                let mut output = String::new();

                for (i, expr) in expressions.iter().enumerate() {
                    if let Some(var_value) = variables.get(*expr) {
                        output.push_str(var_value);
                    } else {
                        // Try to parse as literal
                        if let Ok(n) = expr.parse::<i64>() {
                            output.push_str(&n.to_string());
                        } else if let Ok(n) = expr.parse::<f64>() {
                            output.push_str(&n.to_string());
                        } else if expr.starts_with('\'') && expr.ends_with('\'') && expr.len() == 3
                        {
                            output.push(expr.chars().nth(1).unwrap());
                        } else {
                            output.push_str(expr);
                        }
                    }

                    if i < expressions.len() - 1 {
                        output.push(' ');
                    }
                }

                return CommandResult::Output(output);
            }
        }
        CommandResult::Continue
    }

    fn handle_write_with_vars(
        &mut self,
        stmt: &str,
        variables: &std::collections::HashMap<String, String>,
    ) -> CommandResult {
        self.handle_writeln_with_vars(stmt, variables) // Same as writeln but without newline
    }

    fn handle_assignment_with_vars(
        &mut self,
        stmt: &str,
        variables: &mut std::collections::HashMap<String, String>,
    ) {
        if let Some(assign_pos) = stmt.find(":=") {
            let var_name = stmt[..assign_pos].trim();
            let expr = stmt[assign_pos + 2..].trim();

            // Simple expression evaluation - store in the shared variables
            let value = if expr.starts_with('\'') && expr.ends_with('\'') {
                expr[1..expr.len() - 1].to_string()
            } else if let Ok(n) = expr.parse::<i64>() {
                n.to_string()
            } else if let Ok(n) = expr.parse::<f64>() {
                n.to_string()
            } else {
                // Check if it's a variable reference
                variables.get(expr).unwrap_or(&expr.to_string()).clone()
            };

            variables.insert(var_name.to_string(), value);
        }
    }

    fn handle_readln(&mut self, stmt: &str) -> CommandResult {
        if let Some(open_paren) = stmt.find('(') {
            if let Some(close_paren) = stmt.find(')') {
                let var_name = &stmt[open_paren + 1..close_paren].trim();
                return CommandResult::Input(var_name.to_string(), format!("? "));
            }
        }
        CommandResult::Continue
    }

    fn handle_assignment(&mut self, stmt: &str) -> CommandResult {
        if let Some(assign_pos) = stmt.find(":=") {
            let var_name = stmt[..assign_pos].trim();
            let expr = stmt[assign_pos + 2..].trim();

            // First check if expr is a variable reference
            let expr_value = if let Some(other_var) = self.variables.get(expr) {
                Some(other_var.value.clone())
            } else {
                None
            };

            if let Some(var) = self.variables.get_mut(var_name) {
                // Simple expression evaluation
                if let Ok(n) = expr.parse::<i64>() {
                    var.value = PascalValue::Integer(n);
                } else if let Ok(n) = expr.parse::<f64>() {
                    var.value = PascalValue::Real(n);
                } else if expr.starts_with('\'') && expr.ends_with('\'') && expr.len() == 3 {
                    var.value = PascalValue::Char(expr.chars().nth(1).unwrap());
                } else if expr.to_lowercase() == "true" {
                    var.value = PascalValue::Boolean(true);
                } else if expr.to_lowercase() == "false" {
                    var.value = PascalValue::Boolean(false);
                } else if expr.starts_with('\'') && expr.ends_with('\'') {
                    var.value = PascalValue::String(expr[1..expr.len() - 1].to_string());
                } else if let Some(value) = expr_value {
                    var.value = value;
                }
            }
        }
        CommandResult::Continue
    }

    fn handle_if_statement(&mut self, stmt: &str) -> CommandResult {
        // Basic if-then parsing - simplified for now
        if let Some(then_pos) = stmt.to_lowercase().find(" then ") {
            let condition = &stmt[3..then_pos];
            let then_part = &stmt[then_pos + 6..];

            // Very simple condition evaluation
            let condition_result = if condition.contains("=") {
                let parts: Vec<&str> = condition.split('=').collect();
                if parts.len() == 2 {
                    let left = parts[0].trim();
                    let right = parts[1].trim();

                    if let (Some(left_var), Some(right_var)) =
                        (self.variables.get(left), self.variables.get(right))
                    {
                        match (&left_var.value, &right_var.value) {
                            (PascalValue::Integer(l), PascalValue::Integer(r)) => l == r,
                            (PascalValue::Real(l), PascalValue::Real(r)) => (l - r).abs() < 0.0001,
                            (PascalValue::Boolean(l), PascalValue::Boolean(r)) => l == r,
                            _ => false,
                        }
                    } else {
                        false
                    }
                } else {
                    false
                }
            } else {
                false
            };

            if condition_result {
                // For now, just handle simple assignments in then clause
                let then_stmt = then_part.trim_end_matches(" end").trim();
                if then_stmt.contains(":=") {
                    self.handle_assignment(then_stmt);
                }
            }
        }
        CommandResult::Continue
    }

    fn handle_while_loop(&mut self, _stmt: &str) -> CommandResult {
        CommandResult::Output("While loops not fully implemented".to_string())
    }

    fn handle_for_loop(&mut self, _stmt: &str) -> CommandResult {
        CommandResult::Output("For loops not fully implemented".to_string())
    }

    fn handle_repeat_loop(&mut self, _stmt: &str) -> CommandResult {
        CommandResult::Output("Repeat loops not fully implemented".to_string())
    }

    fn handle_case_statement(&mut self, _stmt: &str) -> CommandResult {
        CommandResult::Output("Case statements not implemented".to_string())
    }
}
