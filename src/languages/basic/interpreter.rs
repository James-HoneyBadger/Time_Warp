use crate::languages::basic::ast::{
    BinaryOperator, ExecutionContext, ExecutionResult, Expression, ForLoop, FunctionDefinition,
    GraphicsCommand, InterpreterError, PrintSeparator, Program, Statement, UnaryOperator, Value,
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
            context: ExecutionContext {
                variables: HashMap::new(),
                arrays: HashMap::new(),
                functions: HashMap::new(),
                for_loops: Vec::new(),
                gosub_stack: Vec::new(),
                data: Vec::new(),
                data_pointer: 0,
                random_seed: 12345, // Fixed seed for reproducibility
                array_base: 0,
                input_variable: None,
            },
            program: None,
            current_line: 0,
            instruction_count: 0,
            max_instructions: 100000,
        }
    }

    pub fn execute(&mut self, code: &str) -> Result<ExecutionResult, InterpreterError> {
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
            let result = self.execute_statement(statement, &mut graphics_commands)?;

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
        graphics_commands: &mut Vec<GraphicsCommand>,
    ) -> Result<Option<String>, InterpreterError> {
        match statement {
            Statement::Let {
                variable,
                expression,
            } => {
                let value = self.evaluate_expression(expression)?;
                self.context.variables.insert(variable.clone(), value);
                Ok(None)
            }
            Statement::Print {
                expressions,
                separators,
            } => {
                let mut output = String::new();
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
                // If no expressions or last separator was not None, add newline
                if expressions.is_empty()
                    || (!separators.is_empty() && separators.last() != Some(&PrintSeparator::None))
                {
                    output.push('\n');
                }
                Ok(Some(format!("PRINT {}", output)))
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
                    self.execute_statement_block(then_branch, graphics_commands)?;
                } else if let Some(else_branch) = else_branch {
                    self.execute_statement_block(else_branch, graphics_commands)?;
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
                self.context
                    .variables
                    .insert(variable.clone(), Value::Number(start_num));

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
                    name.clone(),
                    FunctionDefinition {
                        parameters: parameters.clone(),
                        body: body.clone(),
                    },
                );
                Ok(None)
            }
        }
    }

    fn execute_statement_block(
        &mut self,
        statements: &[Statement],
        graphics_commands: &mut Vec<GraphicsCommand>,
    ) -> Result<(), InterpreterError> {
        for statement in statements {
            self.execute_statement(statement, graphics_commands)?;
        }
        Ok(())
    }

    fn handle_next_statement(
        &mut self,
        variable: &Option<String>,
    ) -> Result<Option<String>, InterpreterError> {
        if let Some(for_loop) = self.context.for_loops.last() {
            // Check if variable matches (if specified)
            if let Some(var_name) = variable {
                if *var_name != for_loop.variable {
                    return Err(InterpreterError::RuntimeError(format!(
                        "NEXT {} does not match FOR {}",
                        var_name, for_loop.variable
                    )));
                }
            }

            // Get current value
            let current_value = self
                .context
                .variables
                .get(&for_loop.variable)
                .ok_or_else(|| InterpreterError::UndefinedVariable(for_loop.variable.clone()))?;
            let current_num = self.value_to_number(current_value)?;

            // Now borrow mutably to modify
            if let Some(for_loop_mut) = self.context.for_loops.last_mut() {
                // Increment
                let new_value = current_num + for_loop_mut.step_value;
                self.context
                    .variables
                    .insert(for_loop_mut.variable.clone(), Value::Number(new_value));

                // Check if loop should continue
                let should_continue = if for_loop_mut.step_value >= 0.0 {
                    new_value <= for_loop_mut.end_value
                } else {
                    new_value >= for_loop_mut.end_value
                };

                if should_continue {
                    // Continue loop
                    self.current_line = for_loop_mut.body_start - 1; // Will be incremented after return
                    Ok(Some("CONTINUE_LOOP".to_string()))
                } else {
                    // Exit loop
                    self.context.for_loops.pop();
                    Ok(None)
                }
            } else {
                Err(InterpreterError::RuntimeError(
                    "FOR loop state corrupted".to_string(),
                ))
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
            Expression::Variable(name) => self
                .context
                .variables
                .get(name)
                .cloned()
                .ok_or_else(|| InterpreterError::UndefinedVariable(name.clone())),
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
            if let Some(value) = self.context.variables.get(param) {
                saved_vars.insert(param.clone(), value.clone());
            }
        }

        // Set parameter values
        for (param, arg) in func_def.parameters.iter().zip(arguments) {
            self.context.variables.insert(param.clone(), arg.clone());
        }

        // Evaluate function body
        let result = self.evaluate_expression(&func_def.body);

        // Restore saved variables
        for (param, value) in saved_vars {
            self.context.variables.insert(param, value);
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

    // Helper methods for type conversion
    fn value_to_number(&self, value: &Value) -> Result<f64, InterpreterError> {
        match value {
            Value::Number(n) => Ok(*n),
            Value::Integer(i) => Ok(*i as f64),
            Value::String(s) => s.parse::<f64>().map_err(|_| {
                InterpreterError::TypeError(format!("Cannot convert '{}' to number", s))
            }),
        }
    }

    fn value_to_string(&self, value: &Value) -> String {
        match value {
            Value::Number(n) => n.to_string(),
            Value::Integer(i) => i.to_string(),
            Value::String(s) => s.clone(),
        }
    }

    fn value_to_bool(&self, value: &Value) -> Result<bool, InterpreterError> {
        match value {
            Value::Number(n) => Ok(*n != 0.0),
            Value::Integer(i) => Ok(*i != 0),
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
            (Value::String(l), Value::String(r)) => Ok(l.cmp(r) as i32),
            _ => Err(InterpreterError::TypeError(
                "Cannot compare different types".to_string(),
            )),
        }
    }

    pub fn provide_input(&mut self, input: &str) -> Result<ExecutionResult, InterpreterError> {
        // Parse the input value
        let value = if let Ok(num) = input.trim().parse::<f64>() {
            Value::Number(num)
        } else {
            Value::String(input.trim().to_string())
        };

        // Set the input variable if one is expected
        if let Some(ref var_name) = self.context.input_variable {
            self.context.variables.insert(var_name.clone(), value);
            self.context.input_variable = None;
        }

        // Continue execution
        self.execute_program()
    }
}
