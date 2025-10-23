use crate::languages::basic::{BasicInterpreter, ExecutionResult, InterpreterError};

pub struct Interpreter {
    pub basic_interpreter: BasicInterpreter,
}

impl Interpreter {
    pub fn new() -> Self {
        Self {
            basic_interpreter: BasicInterpreter::new(),
        }
    }

    pub fn execute_tw_basic(&mut self, code: &str) -> Result<ExecutionResult, InterpreterError> {
        self.basic_interpreter.execute(code)
    }

    pub fn provide_input(&mut self, input: String) {
        self.basic_interpreter.provide_input(input);
    }
}