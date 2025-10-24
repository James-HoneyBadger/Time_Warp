use crate::languages::basic::ast::{
    BinaryOperator, CaseValue, ExecutionContext, ExecutionResult, Expression, ForLoop,
    FunctionDefinition, GraphicsCommand, InterpreterError, PrintSeparator, Program, Statement,
    UnaryOperator, Value, VariableType,
};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// BASIC interpreter engine
pub struct Interpreter {
    context: ExecutionContext,
    program: Option<Program>,
    current_line: usize,
    instruction_count: usize,
    pub max_instructions: usize,
}

impl Interpreter {
    pub fn new() -> Self {
        Self {
            context: ExecutionContext::new(),
            program: None,
            current_line: 0,
            instruction_count: 0,
            max_instructions: 100000,
        }
    }

    pub fn execute(&mut self, code: &str) -> Result<ExecutionResult, InterpreterError> {
        if code.is_empty() && self.program.is_some() {
            // Continue execution without resetting
            self.execute_program()
        } else {
            // Reset state
            self.reset();

            // Tokenize and parse
            let mut tokenizer = crate::languages::basic::tokenizer::Tokenizer::new(code);
            let tokens = tokenizer.tokenize()?;

            let mut parser = crate::languages::basic::parser::Parser::new(tokens);
            let program = parser.parse_program()?;

            self.program = Some(program);
            self.execute_program()
        }
    }

    fn reset(&mut self) {
        self.context.variables.clear();
        self.context.arrays.clear();
        self.context.functions.clear();
        self.context.for_loops.clear();
        self.context.gosub_stack.clear();
        self.context.data.clear();
        self.context.data_pointer = 0;
        self.context.input_variable = None;
        self.program = None;
        self.current_line = 0;
        self.instruction_count = 0;
    }

    fn execute_program(&mut self) -> Result<ExecutionResult, InterpreterError> {
        let mut output = String::new();
        let mut graphics_commands = Vec::new();

        // Extract statements to avoid borrowing conflicts
        let statements = if let Some(ref program) = self.program {
            program.statements.clone()
        } else {
            return Err(InterpreterError::RuntimeError(
                "No program loaded".to_string(),
            ));
        };

        while self.current_line < statements.len() {
            self.instruction_count += 1;
            if self.instruction_count > self.max_instructions {
                return Err(InterpreterError::RuntimeError(format!(
                    "Execution timeout: exceeded {} instructions",
                    self.max_instructions
                )));
            }

            let statement = &statements[self.current_line];
            let result = self.execute_statement(statement, &mut output, &mut graphics_commands)?;

            match result {
                Some(special_result) => {
                    if special_result == "END" {
                        break;
                    } else if special_result == "STOP" {
                        break;
                    } else if special_result.starts_with("GOTO ") {
                        if let Ok(line_num) = special_result[5..].parse::<usize>() {
                            if line_num < statements.len() {
                                self.current_line = line_num;
                                continue;
                            }
                        }
                    } else if special_result == "CONTINUE_LOOP" {
                        // NEXT statement handled the line adjustment
                        continue;
                    } else if special_result.starts_with("INPUT ") {
                        let prompt = special_result[6..].to_string();
                        return Ok(ExecutionResult::NeedInput {
                            variable: self
                                .context
                                .input_variable
                                .clone()
                                .unwrap_or("".to_string()),
                            prompt,
                            partial_output: output,
                            partial_graphics: graphics_commands,
                        });
                    }
                }
                None => {}
            }

            self.current_line += 1;
        }

        Ok(ExecutionResult::Complete {
            output,
            graphics_commands,
        })
    }

    fn execute_statement(
        &mut self,
        statement: &Statement,
        output: &mut String,
        graphics_commands: &mut Vec<GraphicsCommand>,
    ) -> Result<Option<String>, InterpreterError> {
        match statement {
            Statement::Let {
                variable,
                expression,
            } => {
                let value = self.evaluate_expression(expression)?;
                let var_type = self.context.get_variable_type(variable);
                let converted_value = self.convert_value_to_variable_type(&value, variable)?;
                let var_info = self.context.get_variable(variable);
                var_info.value = converted_value;
                var_info.declared_type = var_type;
                Ok(None)
            }
            Statement::Print {
                expressions,
                separators,
            } => {
                for (i, expr) in expressions.iter().enumerate() {
                    let value = self.evaluate_expression(expr)?;
                    let value_str = self.value_to_string(&value);
                    output.push_str(&value_str);

                    // Add separator if not the last expression
                    if i < separators.len() {
                        match separators[i] {
                            PrintSeparator::Comma => output.push('\t'),
                            PrintSeparator::Semicolon => {} // No separator
                            PrintSeparator::None => output.push('\n'),
                        }
                    }
                }
                // Add newline if there are fewer separators than expressions
                if separators.len() < expressions.len() {
                    output.push('\n');
                }
                Ok(None)
            }
            Statement::Input { prompt, variable } => {
                self.context.input_variable = Some(variable.clone());
                let prompt_text = prompt.as_ref().unwrap_or(&"? ".to_string()).clone();
                Ok(Some(format!("INPUT {}", prompt_text)))
            }
            Statement::If {
                condition,
                then_branch,
                else_branch,
            } => {
                let condition_value = self.evaluate_expression(condition)?;
                let condition_bool = self.value_to_bool(&condition_value)?;

                if condition_bool {
                    self.execute_statement_block(then_branch, output, graphics_commands)?;
                } else if let Some(else_branch) = else_branch {
                    self.execute_statement_block(else_branch, output, graphics_commands)?;
                }
                Ok(None)
            }
            Statement::For {
                variable,
                start,
                end,
                step,
                body,
            } => {
                let start_value = self.evaluate_expression(start)?;
                let end_value = self.evaluate_expression(end)?;
                let step_value = step
                    .as_ref()
                    .map(|s| self.evaluate_expression(s))
                    .unwrap_or(Ok(Value::Number(1.0)))?;

                let start_num = self.value_to_number(&start_value)?;
                let end_num = self.value_to_number(&end_value)?;
                let step_num = self.value_to_number(&step_value)?;

                // Initialize loop variable
                let var_type = self.context.get_variable_type(variable);
                let converted_start = self
                    .convert_value_to_variable_type(&Value::Single(start_num as f32), variable)?;
                let var_info = self.context.get_variable(variable);
                var_info.value = converted_start;
                var_info.declared_type = var_type;

                // Push loop context
                self.context.for_loops.push(ForLoop {
                    variable: variable.clone(),
                    end_value: end_num,
                    step_value: step_num,
                    line_index: self.current_line,
                    body_start: self.current_line + 1,
                });

                Ok(None)
            }
            Statement::Next { variable } => self.handle_next_statement(variable),
            Statement::Goto { line } => {
                let line_value = self.evaluate_expression(line)?;
                let line_num = self.value_to_number(&line_value)? as usize;
                Ok(Some(format!("GOTO {}", line_num)))
            }
            Statement::Gosub { line } => {
                let line_value = self.evaluate_expression(line)?;
                let line_num = self.value_to_number(&line_value)? as usize;
                self.context.gosub_stack.push(self.current_line);
                Ok(Some(format!("GOTO {}", line_num)))
            }
            Statement::Return => {
                if let Some(return_line) = self.context.gosub_stack.pop() {
                    Ok(Some(format!("GOTO {}", return_line + 1)))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "RETURN without GOSUB".to_string(),
                    ))
                }
            }
            Statement::End => Ok(Some("END".to_string())),
            Statement::Stop => Ok(Some("STOP".to_string())),
            Statement::Rem(_) => Ok(None), // Comments do nothing
            Statement::Dim { arrays } => {
                for (name, dimensions) in arrays {
                    self.create_array(name, dimensions)?;
                }
                Ok(None)
            }
            Statement::Def {
                name,
                parameters,
                body,
            } => {
                self.context.functions.insert(
                    format!("FN{}", name),
                    FunctionDefinition {
                        parameters: parameters.clone(),
                        body: body.clone(),
                    },
                );
                Ok(None)
            }
            Statement::Clear => {
                self.context.variables.clear();
                self.context.type_declarations.clear();
                output.push_str("Variables cleared\n");
                Ok(None)
            }
            Statement::Cls => {
                // Clear screen - in text mode, this might just be a visual command
                // For now, just output a message
                output.push_str("Screen cleared\n");
                Ok(None)
            }
            Statement::Writeln { expression } => {
                let value = self.evaluate_expression(expression)?;
                let value_str = self.value_to_string(&value);
                output.push_str(&value_str);
                output.push('\n');
                Ok(None)
            }
            Statement::Printx { expression } => {
                let value = self.evaluate_expression(expression)?;
                let value_str = self.value_to_string(&value);
                output.push_str(&value_str);
                Ok(None)
            }
            Statement::DefInt { ranges } => {
                for range in ranges {
                    self.set_type_declaration(range, VariableType::Integer)?;
                }
                Ok(None)
            }
            Statement::DefSng { ranges } => {
                for range in ranges {
                    self.set_type_declaration(range, VariableType::Single)?;
                }
                Ok(None)
            }
            Statement::DefStr { ranges } => {
                for range in ranges {
                    self.set_type_declaration(range, VariableType::String)?;
                }
                Ok(None)
            }
            Statement::DefDbl { ranges } => {
                for range in ranges {
                    self.set_type_declaration(range, VariableType::Double)?;
                }
                Ok(None)
            }
            Statement::Select { expression, cases } => {
                let select_value = self.evaluate_expression(expression)?;

                for case in cases {
                    let matches = match &case.value {
                        Some(CaseValue::Single(expr)) => {
                            let case_value = self.evaluate_expression(expr)?;
                            self.values_equal(&select_value, &case_value)?
                        }
                        Some(CaseValue::Range(min_expr, max_expr)) => {
                            let case_min = self.evaluate_expression(min_expr)?;
                            let case_max = self.evaluate_expression(max_expr)?;
                            let min_cmp = self.compare_values(&select_value, &case_min)?;
                            let max_cmp = self.compare_values(&select_value, &case_max)?;
                            min_cmp >= 0 && max_cmp <= 0 // value >= min && value <= max
                        }
                        Some(CaseValue::Is(_, _)) => {
                            // CASE IS not implemented yet
                            false
                        }
                        None => {
                            // CASE ELSE always matches
                            true
                        }
                    };

                    if matches {
                        self.execute_statement_block(&case.statements, output, graphics_commands)?;
                        break;
                    }
                }
                Ok(None)
            }
            Statement::Forward { distance } => {
                let dist = self.evaluate_expression(distance)?;
                let dist_num = self.value_to_number(&dist)?;
                graphics_commands.push(GraphicsCommand {
                    command: "FORWARD".to_string(),
                    value: dist_num as f32,
                });
                output.push_str(&format!("Moved forward {}\n", dist_num));
                Ok(None)
            }
            Statement::Back { distance } => {
                let dist = self.evaluate_expression(distance)?;
                let dist_num = self.value_to_number(&dist)?;
                graphics_commands.push(GraphicsCommand {
                    command: "BACK".to_string(),
                    value: dist_num as f32,
                });
                output.push_str(&format!("Moved back {}\n", dist_num));
                Ok(None)
            }
            Statement::TurnLeft { angle } => {
                let ang = self.evaluate_expression(angle)?;
                let ang_num = self.value_to_number(&ang)?;
                graphics_commands.push(GraphicsCommand {
                    command: "LEFT".to_string(),
                    value: ang_num as f32,
                });
                output.push_str(&format!("Turned left by {} degrees\n", ang_num));
                Ok(None)
            }
            Statement::TurnRight { angle } => {
                let ang = self.evaluate_expression(angle)?;
                let ang_num = self.value_to_number(&ang)?;
                graphics_commands.push(GraphicsCommand {
                    command: "RIGHT".to_string(),
                    value: ang_num as f32,
                });
                output.push_str(&format!("Turned right {}\n", ang_num));
                Ok(None)
            }
            Statement::Penup => {
                graphics_commands.push(GraphicsCommand {
                    command: "PENUP".to_string(),
                    value: 0.0,
                });
                output.push_str("Pen up\n");
                Ok(None)
            }
            Statement::Pendown => {
                graphics_commands.push(GraphicsCommand {
                    command: "PENDOWN".to_string(),
                    value: 0.0,
                });
                output.push_str("Pen down\n");
                Ok(None)
            }
            Statement::Home => {
                graphics_commands.push(GraphicsCommand {
                    command: "HOME".to_string(),
                    value: 0.0,
                });
                output.push_str("Moved to home position\n");
                Ok(None)
            }
            Statement::Setxy { x, y } => {
                let x_val = self.evaluate_expression(x)?;
                let y_val = self.evaluate_expression(y)?;
                let x_num = self.value_to_number(&x_val)?;
                let y_num = self.value_to_number(&y_val)?;
                // For SETXY, we might need to store both values somehow
                // For now, just store x and handle y separately if needed
                graphics_commands.push(GraphicsCommand {
                    command: "SETXY".to_string(),
                    value: x_num as f32,
                });
                output.push_str(&format!("Moved to ({}, {})\n", x_num, y_num));
                Ok(None)
            }
            Statement::Turn { angle } => {
                let ang = self.evaluate_expression(angle)?;
                let ang_num = self.value_to_number(&ang)?;
                graphics_commands.push(GraphicsCommand {
                    command: "TURN".to_string(),
                    value: ang_num as f32,
                });
                output.push_str(&format!("Turned by {} degrees\n", ang_num));
                Ok(None)
            }
        }
    }

    fn execute_statement_block(
        &mut self,
        statements: &[Statement],
        output: &mut String,
        graphics_commands: &mut Vec<GraphicsCommand>,
    ) -> Result<(), InterpreterError> {
        for statement in statements {
            self.execute_statement(statement, output, graphics_commands)?;
        }
        Ok(())
    }

    fn handle_next_statement(
        &mut self,
        variable: &Option<String>,
    ) -> Result<Option<String>, InterpreterError> {
        if let Some(for_loop) = self.context.for_loops.last() {
            let loop_var = for_loop.variable.clone();
            let loop_end = for_loop.end_value;
            let loop_step = for_loop.step_value;

            // Check if variable matches (if specified)
            if let Some(var_name) = variable {
                if *var_name != loop_var {
                    return Err(InterpreterError::RuntimeError(format!(
                        "NEXT {} does not match FOR {}",
                        var_name, loop_var
                    )));
                }
            }

            // Get current value
            let var_info = self.context.get_variable(&loop_var);
            let current_value = var_info.value.clone();
            let current_num = self.value_to_number(&current_value)?;

            // Increment
            let new_value = current_num + loop_step;
            let var_type = self.context.get_variable_type(&loop_var);
            let converted_value =
                self.convert_value_to_variable_type(&Value::Single(new_value as f32), &loop_var)?;
            let var_info_mut = self.context.get_variable(&loop_var);
            var_info_mut.value = converted_value;
            var_info_mut.declared_type = var_type;

            // Check if loop should continue
            let should_continue = if loop_step >= 0.0 {
                new_value <= loop_end
            } else {
                new_value >= loop_end
            };

            if should_continue {
                // Continue loop - jump to the body start
                if let Some(for_loop) = self.context.for_loops.last() {
                    self.current_line = for_loop.body_start;
                    Ok(Some("CONTINUE_LOOP".to_string()))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "FOR loop state corrupted".to_string(),
                    ))
                }
            } else {
                // Exit loop
                self.context.for_loops.pop();
                Ok(None)
            }
        } else {
            Err(InterpreterError::RuntimeError(
                "NEXT without FOR".to_string(),
            ))
        }
    }

    fn evaluate_expression(&mut self, expression: &Expression) -> Result<Value, InterpreterError> {
        match expression {
            Expression::Number(n) => Ok(Value::Number(*n)),
            Expression::String(s) => Ok(Value::String(s.clone())),
            Expression::Variable(name) => {
                let var_info = self.context.get_variable(name);
                Ok(var_info.value.clone())
            }
            Expression::BinaryOp {
                left,
                operator,
                right,
            } => {
                let left_val = self.evaluate_expression(left)?;
                let right_val = self.evaluate_expression(right)?;
                self.evaluate_binary_op(*operator, &left_val, &right_val)
            }
            Expression::UnaryOp { operator, operand } => {
                let operand_val = self.evaluate_expression(operand)?;
                self.evaluate_unary_op(*operator, &operand_val)
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
                let index_num = self.value_to_number(&index_val)? as usize;
                self.get_array_element(name, index_num)
            }
        }
    }

    fn evaluate_binary_op(
        &self,
        operator: BinaryOperator,
        left: &Value,
        right: &Value,
    ) -> Result<Value, InterpreterError> {
        match operator {
            BinaryOperator::Add => match (left, right) {
                (Value::Number(l), Value::Number(r)) => Ok(Value::Number(l + r)),
                (Value::String(l), Value::String(r)) => Ok(Value::String(format!("{}{}", l, r))),
                _ => Err(InterpreterError::TypeError(
                    "Invalid types for addition".to_string(),
                )),
            },
            BinaryOperator::Subtract => {
                let l = self.value_to_number(left)?;
                let r = self.value_to_number(right)?;
                Ok(Value::Number(l - r))
            }
            BinaryOperator::Multiply => {
                let l = self.value_to_number(left)?;
                let r = self.value_to_number(right)?;
                Ok(Value::Number(l * r))
            }
            BinaryOperator::Divide => {
                let l = self.value_to_number(left)?;
                let r = self.value_to_number(right)?;
                if r == 0.0 {
                    return Err(InterpreterError::DivisionByZero);
                }
                Ok(Value::Number(l / r))
            }
            BinaryOperator::Modulo => {
                let l = self.value_to_number(left)?;
                let r = self.value_to_number(right)?;
                Ok(Value::Number(l % r))
            }
            BinaryOperator::Power => {
                let l = self.value_to_number(left)?;
                let r = self.value_to_number(right)?;
                Ok(Value::Number(l.powf(r)))
            }
            BinaryOperator::Equal => {
                let result = self.compare_values(left, right)?;
                Ok(Value::Number(if result == 0 { -1.0 } else { 0.0 }))
            }
            BinaryOperator::NotEqual => {
                let result = self.compare_values(left, right)?;
                Ok(Value::Number(if result != 0 { -1.0 } else { 0.0 }))
            }
            BinaryOperator::Less => {
                let result = self.compare_values(left, right)?;
                Ok(Value::Number(if result < 0 { -1.0 } else { 0.0 }))
            }
            BinaryOperator::LessEqual => {
                let result = self.compare_values(left, right)?;
                Ok(Value::Number(if result <= 0 { -1.0 } else { 0.0 }))
            }
            BinaryOperator::Greater => {
                let result = self.compare_values(left, right)?;
                Ok(Value::Number(if result > 0 { -1.0 } else { 0.0 }))
            }
            BinaryOperator::GreaterEqual => {
                let result = self.compare_values(left, right)?;
                Ok(Value::Number(if result >= 0 { -1.0 } else { 0.0 }))
            }
            BinaryOperator::And => {
                let l = self.value_to_bool(left)?;
                let r = self.value_to_bool(right)?;
                Ok(Value::Number(if l && r { -1.0 } else { 0.0 }))
            }
            BinaryOperator::Or => {
                let l = self.value_to_bool(left)?;
                let r = self.value_to_bool(right)?;
                Ok(Value::Number(if l || r { -1.0 } else { 0.0 }))
            }
        }
    }

    fn evaluate_unary_op(
        &self,
        operator: UnaryOperator,
        operand: &Value,
    ) -> Result<Value, InterpreterError> {
        match operator {
            UnaryOperator::Negate => {
                let num = self.value_to_number(operand)?;
                Ok(Value::Number(-num))
            }
            UnaryOperator::Not => {
                let bool_val = self.value_to_bool(operand)?;
                Ok(Value::Number(if bool_val { 0.0 } else { -1.0 }))
            }
        }
    }

    fn evaluate_function(
        &mut self,
        name: &str,
        arguments: &[Value],
    ) -> Result<Value, InterpreterError> {
        match name.to_uppercase().as_str() {
            "SIN" => self.math_function(arguments, |x| x.sin()),
            "COS" => self.math_function(arguments, |x| x.cos()),
            "TAN" => self.math_function(arguments, |x| x.tan()),
            "SQR" => self.math_function(arguments, |x| x.sqrt()),
            "ABS" => self.math_function(arguments, |x| x.abs()),
            "INT" => self.math_function(arguments, |x| x.floor()),
            "RND" => {
                if arguments.is_empty() || arguments.len() == 1 {
                    // Generate random number
                    let random_val =
                        (self.context.random_seed as f64 * 9301.0 + 49297.0) % 233280.0 / 233280.0;
                    self.context.random_seed = (self.context.random_seed * 9301 + 49297) % 233280;
                    Ok(Value::Number(random_val))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "RND takes 0 or 1 arguments".to_string(),
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
            "DATE$" => {
                if arguments.is_empty() {
                    let now = SystemTime::now();
                    let datetime: chrono::DateTime<chrono::Utc> = now.into();
                    let date_str = datetime.format("%m-%d-%Y").to_string();
                    Ok(Value::String(date_str))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "DATE$ takes no arguments".to_string(),
                    ))
                }
            }
            "TIME$" => {
                if arguments.is_empty() {
                    let now = SystemTime::now();
                    let datetime: chrono::DateTime<chrono::Utc> = now.into();
                    let time_str = datetime.format("%H:%M:%S").to_string();
                    Ok(Value::String(time_str))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "TIME$ takes no arguments".to_string(),
                    ))
                }
            }
            "TIMER" => {
                if arguments.is_empty() {
                    let now = SystemTime::now();
                    let duration = now.duration_since(UNIX_EPOCH).unwrap();
                    let seconds = duration.as_secs() % 86400; // Seconds since midnight
                    Ok(Value::Number(seconds as f64))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "TIMER takes no arguments".to_string(),
                    ))
                }
            }
            "TAB" => {
                if arguments.len() == 1 {
                    let col = self.value_to_number(&arguments[0])? as usize;
                    // TAB(n) moves to column n, padding with spaces if necessary
                    // For simplicity, we'll just return a string with spaces
                    let spaces = if col > 0 {
                        " ".repeat(col)
                    } else {
                        String::new()
                    };
                    Ok(Value::String(spaces))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "TAB requires 1 argument".to_string(),
                    ))
                }
            }
            "SPC" => {
                if arguments.len() == 1 {
                    let count = self.value_to_number(&arguments[0])? as usize;
                    let spaces = " ".repeat(count);
                    Ok(Value::String(spaces))
                } else {
                    Err(InterpreterError::RuntimeError(
                        "SPC requires 1 argument".to_string(),
                    ))
                }
            }
            "ENVIRON$" => {
                if arguments.len() == 1 {
                    match &arguments[0] {
                        Value::String(var_name) => {
                            // Get environment variable by name
                            match std::env::var(var_name) {
                                Ok(value) => Ok(Value::String(value)),
                                Err(_) => Ok(Value::String(String::new())), // Empty string if not found
                            }
                        }
                        Value::Number(index) => {
                            // Get environment variable by index (1-based)
                            let index = *index as usize;
                            if index > 0 {
                                let env_vars: Vec<_> = std::env::vars().collect();
                                if index <= env_vars.len() {
                                    let (key, value) = &env_vars[index - 1];
                                    Ok(Value::String(format!("{}={}", key, value)))
                                } else {
                                    Ok(Value::String(String::new()))
                                }
                            } else {
                                Ok(Value::String(String::new()))
                            }
                        }
                        _ => Err(InterpreterError::TypeError(
                            "ENVIRON$ argument must be string or number".to_string(),
                        )),
                    }
                } else {
                    Err(InterpreterError::RuntimeError(
                        "ENVIRON$ requires 1 argument".to_string(),
                    ))
                }
            }
            _ => {
                // Check for user-defined functions
                if let Some(func_def) = self.context.functions.get(name).cloned() {
                    self.call_user_function(&func_def, arguments)
                } else {
                    Err(InterpreterError::UndefinedFunction(name.to_string()))
                }
            }
        }
    }

    fn math_function<F>(&self, arguments: &[Value], func: F) -> Result<Value, InterpreterError>
    where
        F: Fn(f64) -> f64,
    {
        if arguments.len() == 1 {
            let num = self.value_to_number(&arguments[0])?;
            Ok(Value::Number(func(num)))
        } else {
            Err(InterpreterError::RuntimeError(
                "Math function requires 1 argument".to_string(),
            ))
        }
    }

    fn call_user_function(
        &mut self,
        func_def: &FunctionDefinition,
        arguments: &[Value],
    ) -> Result<Value, InterpreterError> {
        if arguments.len() != func_def.parameters.len() {
            return Err(InterpreterError::RuntimeError(format!(
                "Function expects {} arguments, got {}",
                func_def.parameters.len(),
                arguments.len()
            )));
        }

        // Save current variable values
        let mut saved_vars = HashMap::new();
        for param in &func_def.parameters {
            if let Some(var_info) = self.context.variables.get(param) {
                saved_vars.insert(param.clone(), var_info.clone());
            }
        }

        // Set parameter values (parameters are treated as Single by default in GW-BASIC)
        for (param, arg) in func_def.parameters.iter().zip(arguments) {
            let var_type = self.context.get_variable_type(param);
            let converted_arg = self.convert_value_to_variable_type(&arg, param)?;
            let var_info = self.context.get_variable(param);
            var_info.value = converted_arg;
            var_info.declared_type = var_type;
        }

        // Evaluate function body
        let result = self.evaluate_expression(&func_def.body);

        // Restore saved variables
        for (param, var_info) in saved_vars {
            self.context.variables.insert(param, var_info);
        }

        result
    }

    fn create_array(
        &mut self,
        name: &str,
        dimensions: &[Expression],
    ) -> Result<(), InterpreterError> {
        if dimensions.len() != 1 {
            return Err(InterpreterError::RuntimeError(
                "Multi-dimensional arrays not yet supported".to_string(),
            ));
        }

        let size_expr = &dimensions[0];
        let size_value = self.evaluate_expression(size_expr)?;
        let size = self.value_to_number(&size_value)? as usize;

        let mut array = Vec::with_capacity(size + 1); // +1 for 0-based indexing
        for _ in 0..=size {
            array.push(Value::Number(0.0));
        }

        self.context.arrays.insert(name.to_string(), array);
        Ok(())
    }

    fn get_array_element(&self, name: &str, index: usize) -> Result<Value, InterpreterError> {
        if let Some(array) = self.context.arrays.get(name) {
            if index < array.len() {
                Ok(array[index].clone())
            } else {
                Err(InterpreterError::IndexOutOfBounds)
            }
        } else {
            Err(InterpreterError::UndefinedVariable(format!(
                "Array {}",
                name
            )))
        }
    }

    fn values_equal(&self, left: &Value, right: &Value) -> Result<bool, InterpreterError> {
        match (left, right) {
            (Value::Number(l), Value::Number(r)) => Ok((l - r).abs() < f64::EPSILON),
            (Value::String(l), Value::String(r)) => Ok(l == r),
            (Value::Integer(l), Value::Integer(r)) => Ok(l == r),
            (Value::Number(l), Value::Integer(r)) => Ok((l - *r as f64).abs() < f64::EPSILON),
            (Value::Integer(l), Value::Number(r)) => Ok((*l as f64 - r).abs() < f64::EPSILON),
            _ => Ok(false), // Different types are not equal
        }
    }

    // Helper methods for type conversion
    fn value_to_number(&self, value: &Value) -> Result<f64, InterpreterError> {
        match value {
            Value::Number(n) => Ok(*n),
            Value::Integer(i) => Ok(*i as f64),
            Value::Single(s) => Ok(*s as f64),
            Value::Double(d) => Ok(*d),
            Value::String(s) => s.parse::<f64>().map_err(|_| {
                InterpreterError::TypeError(format!("Cannot convert '{}' to number", s))
            }),
        }
    }

    fn value_to_string(&self, value: &Value) -> String {
        match value {
            Value::Number(n) => n.to_string(),
            Value::Integer(i) => i.to_string(),
            Value::Single(s) => s.to_string(),
            Value::Double(d) => d.to_string(),
            Value::String(s) => s.clone(),
        }
    }

    fn value_to_bool(&self, value: &Value) -> Result<bool, InterpreterError> {
        match value {
            Value::Number(n) => Ok(*n != 0.0),
            Value::Integer(i) => Ok(*i != 0),
            Value::Single(s) => Ok(*s != 0.0),
            Value::Double(d) => Ok(*d != 0.0),
            Value::String(s) => Ok(!s.is_empty()),
        }
    }

    fn compare_values(&self, left: &Value, right: &Value) -> Result<i32, InterpreterError> {
        match (left, right) {
            (Value::Number(l), Value::Number(r)) => Ok(if l < r {
                -1
            } else if l > r {
                1
            } else {
                0
            }),
            (Value::Integer(l), Value::Integer(r)) => Ok(l.cmp(r) as i32),
            (Value::Single(l), Value::Single(r)) => Ok(if l < r {
                -1
            } else if l > r {
                1
            } else {
                0
            }),
            (Value::Double(l), Value::Double(r)) => Ok(if l < r {
                -1
            } else if l > r {
                1
            } else {
                0
            }),
            (Value::String(l), Value::String(r)) => Ok(l.cmp(r) as i32),
            // Cross-type comparisons
            (Value::Number(l), Value::Integer(r)) => {
                let cmp = if l < &(*r as f64) {
                    -1
                } else if l > &(*r as f64) {
                    1
                } else {
                    0
                };
                Ok(cmp)
            }
            (Value::Integer(l), Value::Number(r)) => {
                let cmp = if (*l as f64) < *r {
                    -1
                } else if (*l as f64) > *r {
                    1
                } else {
                    0
                };
                Ok(cmp)
            }
            (Value::Number(l), Value::Single(r)) => {
                let cmp = if l < &(*r as f64) {
                    -1
                } else if l > &(*r as f64) {
                    1
                } else {
                    0
                };
                Ok(cmp)
            }
            (Value::Single(l), Value::Number(r)) => {
                let cmp = if (*l as f64) < *r {
                    -1
                } else if (*l as f64) > *r {
                    1
                } else {
                    0
                };
                Ok(cmp)
            }
            (Value::Integer(l), Value::Single(r)) => {
                let cmp = if (*l as f32) < *r {
                    -1
                } else if (*l as f32) > *r {
                    1
                } else {
                    0
                };
                Ok(cmp)
            }
            (Value::Single(l), Value::Integer(r)) => {
                let cmp = if l < &(*r as f32) {
                    -1
                } else if l > &(*r as f32) {
                    1
                } else {
                    0
                };
                Ok(cmp)
            }
            _ => Err(InterpreterError::TypeError(
                "Cannot compare different types".to_string(),
            )),
        }
    }

    pub fn provide_input(&mut self, input: &str) -> Result<ExecutionResult, InterpreterError> {
        // Parse the input value - default to Single type for numeric input
        let parsed_value = if let Ok(num) = input.trim().parse::<f64>() {
            Value::Single(num as f32) // GW-BASIC default for input
        } else {
            Value::String(input.trim().to_string())
        };

        // Set the input variable if one is expected
        if let Some(ref var_name) = self.context.input_variable.clone() {
            let var_type = self.context.get_variable_type(&var_name);
            let converted_value = self.convert_value_to_variable_type(&parsed_value, &var_name)?;
            let var_info = self.context.get_variable(&var_name);
            var_info.value = converted_value;
            var_info.declared_type = var_type;
            self.context.input_variable = None;
        }

        // Continue execution
        self.execute_program()
    }

    /// Set type declaration for a range of variable names
    fn set_type_declaration(
        &mut self,
        range: &str,
        var_type: VariableType,
    ) -> Result<(), InterpreterError> {
        if range.len() == 1 {
            // Single character range like "A"
            let first_char = range.chars().next().unwrap().to_ascii_uppercase();
            self.context
                .type_declarations
                .insert(first_char.to_string(), var_type);
        } else if range.len() == 3 && range.chars().nth(1) == Some('-') {
            // Range like "A-C"
            let start = range.chars().next().unwrap().to_ascii_uppercase();
            let end = range.chars().nth(2).unwrap().to_ascii_uppercase();
            if start <= end {
                for ch in start..=end {
                    self.context
                        .type_declarations
                        .insert(ch.to_string(), var_type.clone());
                }
            } else {
                return Err(InterpreterError::RuntimeError(format!(
                    "Invalid range specification: {}",
                    range
                )));
            }
        } else {
            return Err(InterpreterError::RuntimeError(format!(
                "Invalid range specification: {}",
                range
            )));
        }
        Ok(())
    }

    /// Convert a value to the appropriate type for a variable
    fn convert_value_to_variable_type(
        &self,
        value: &Value,
        variable_name: &str,
    ) -> Result<Value, InterpreterError> {
        let target_type = self.context.get_variable_type(variable_name);

        match (value, target_type) {
            // Legacy Number type support
            (Value::Number(n), VariableType::Integer) => Ok(Value::Integer(*n as i32)),
            (Value::Number(n), VariableType::Single) => Ok(Value::Single(*n as f32)),
            (Value::Number(n), VariableType::Double) => Ok(Value::Double(*n)),
            (Value::Number(n), VariableType::String) => Ok(Value::String(n.to_string())),

            // No conversion needed if types match
            (Value::Integer(i), VariableType::Integer) => Ok(Value::Integer(*i)),
            (Value::Single(s), VariableType::Single) => Ok(Value::Single(*s)),
            (Value::Double(d), VariableType::Double) => Ok(Value::Double(*d)),
            (Value::String(s), VariableType::String) => Ok(Value::String(s.clone())),

            // Convert to Integer
            (Value::Single(s), VariableType::Integer) => Ok(Value::Integer(*s as i32)),
            (Value::Double(d), VariableType::Integer) => Ok(Value::Integer(*d as i32)),

            // Convert to Single
            (Value::Integer(i), VariableType::Single) => Ok(Value::Single(*i as f32)),
            (Value::Double(d), VariableType::Single) => Ok(Value::Single(*d as f32)),

            // Convert to Double
            (Value::Integer(i), VariableType::Double) => Ok(Value::Double(*i as f64)),
            (Value::Single(s), VariableType::Double) => Ok(Value::Double(*s as f64)),

            // String conversions - GW-BASIC allows some numeric conversions
            (Value::String(s), VariableType::Integer) => {
                if let Ok(num) = s.parse::<i32>() {
                    Ok(Value::Integer(num))
                } else {
                    Err(InterpreterError::TypeError(format!(
                        "Cannot convert string '{}' to integer",
                        s
                    )))
                }
            }
            (Value::String(s), VariableType::Single) => {
                if let Ok(num) = s.parse::<f32>() {
                    Ok(Value::Single(num))
                } else {
                    Err(InterpreterError::TypeError(format!(
                        "Cannot convert string '{}' to single",
                        s
                    )))
                }
            }
            (Value::String(s), VariableType::Double) => {
                if let Ok(num) = s.parse::<f64>() {
                    Ok(Value::Double(num))
                } else {
                    Err(InterpreterError::TypeError(format!(
                        "Cannot convert string '{}' to double",
                        s
                    )))
                }
            }

            // Numeric to string conversion
            (Value::Integer(i), VariableType::String) => Ok(Value::String(i.to_string())),
            (Value::Single(s), VariableType::String) => Ok(Value::String(s.to_string())),
            (Value::Double(d), VariableType::String) => Ok(Value::String(d.to_string())),
        }
    }
}
