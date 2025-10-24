use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// Core value types in BASIC
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Number(f64),
    String(String),
    Integer(i32),
}

/// Token types for lexical analysis
#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // Keywords
    Let,
    Print,
    Input,
    If,
    Then,
    Else,
    End,
    Stop,
    For,
    To,
    Step,
    Next,
    Goto,
    Gosub,
    Return,
    Rem,
    Dim,
    Def,
    Fn,

    // Operators
    Plus,
    Minus,
    Multiply,
    Divide,
    Modulo,
    Power,
    Equal,
    NotEqual,
    Less,
    LessEqual,
    Greater,
    GreaterEqual,
    And,
    Or,
    Not,

    // Functions
    Sin,
    Cos,
    Tan,
    Sqr,
    Abs,
    Int,
    Rnd,
    Len,
    Mid,
    Left,
    Right,
    Chr,
    Asc,
    Val,
    Str,

    // System functions
    Date,
    Time,
    Timer,
    Environ,

    // Literals
    Number(f64),
    String(String),
    Identifier(String),

    // Punctuation
    LParen,
    RParen,
    Comma,
    Semicolon,
    Colon,

    // Special
    Eol,
    Eof,
}

/// Abstract Syntax Tree node types
#[derive(Debug, Clone, PartialEq)]
pub enum Expression {
    Number(f64),
    String(String),
    Variable(String),
    BinaryOp {
        left: Box<Expression>,
        operator: BinaryOperator,
        right: Box<Expression>,
    },
    UnaryOp {
        operator: UnaryOperator,
        operand: Box<Expression>,
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

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BinaryOperator {
    Add,
    Subtract,
    Multiply,
    Divide,
    Modulo,
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

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum UnaryOperator {
    Negate,
    Not,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Statement {
    Let {
        variable: String,
        expression: Expression,
    },
    Print {
        expressions: Vec<Expression>,
        separators: Vec<PrintSeparator>,
    },
    Input {
        prompt: Option<String>,
        variable: String,
    },
    If {
        condition: Expression,
        then_branch: Vec<Statement>,
        else_branch: Option<Vec<Statement>>,
    },
    For {
        variable: String,
        start: Expression,
        end: Expression,
        step: Option<Expression>,
        body: Vec<Statement>,
    },
    Next {
        variable: Option<String>,
    },
    Goto {
        line: Expression,
    },
    Gosub {
        line: Expression,
    },
    Return,
    End,
    Stop,
    Rem(String),
    Dim {
        arrays: Vec<(String, Vec<Expression>)>,
    },
    Def {
        name: String,
        parameters: Vec<String>,
        body: Expression,
    },
}

#[derive(Debug, Clone, PartialEq)]
pub enum PrintSeparator {
    Comma,
    Semicolon,
    None,
}

/// Complete BASIC program AST
#[derive(Debug, Clone, PartialEq)]
pub struct Program {
    pub statements: Vec<Statement>,
    pub line_numbers: HashMap<usize, usize>, // line_number -> statement_index
}

/// User-defined function definition
#[derive(Debug, Clone)]
pub struct FunctionDefinition {
    pub parameters: Vec<String>,
    pub body: Expression,
}

/// Execution context and state
#[derive(Debug, Clone)]
pub struct ExecutionContext {
    pub variables: HashMap<String, Value>,
    pub arrays: HashMap<String, Vec<Value>>,
    pub functions: HashMap<String, FunctionDefinition>,
    pub for_loops: Vec<ForLoop>,
    pub gosub_stack: Vec<usize>,
    pub data: Vec<Value>,
    pub data_pointer: usize,
    pub random_seed: u64,
    pub array_base: usize,
    pub input_variable: Option<String>,
}

#[derive(Debug, Clone)]
pub struct ForLoop {
    pub variable: String,
    pub end_value: f64,
    pub step_value: f64,
    pub line_index: usize,
    pub body_start: usize,
}

/// Execution results
#[derive(Debug, Clone)]
pub enum ExecutionResult {
    Complete {
        output: String,
        graphics_commands: Vec<GraphicsCommand>,
    },
    NeedInput {
        variable: String,
        prompt: String,
        partial_output: String,
        partial_graphics: Vec<GraphicsCommand>,
    },
    Error(String),
}

#[derive(Debug, Clone)]
pub struct GraphicsCommand {
    pub command: String,
    pub value: f32,
}

/// Error types
#[derive(Debug, Clone)]
pub enum InterpreterError {
    ParseError(String),
    RuntimeError(String),
    TypeError(String),
    UndefinedVariable(String),
    UndefinedFunction(String),
    DivisionByZero,
    IndexOutOfBounds,
}
