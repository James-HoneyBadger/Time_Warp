use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

/// Variable type declarations
#[derive(Debug, Clone, PartialEq)]
pub enum VariableType {
    Integer, // %
    Single,  // ! or default
    Double,  // #
    String,  // $
}

/// Runtime value types
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Integer(i32),
    Single(f32),
    Double(f64),
    String(String),
    Number(f64), // Legacy support
}

/// Variable information with type tracking
#[derive(Debug, Clone, PartialEq)]
pub struct VariableInfo {
    pub value: Value,
    pub declared_type: VariableType,
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
    Clear,
    Cls,
    Writeln,
    Printx,
    Defint,
    Defsng,
    Defstr,
    Defdbl,
    Select,
    Case,
    Is,

    // Turtle graphics
    Forward,
    Back,
    TurnLeft,
    TurnRight,
    Penup,
    Pendown,
    Home,
    Setxy,
    Turn,

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
    Tab,
    Spc,

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
    Clear,
    Cls,
    Writeln {
        expression: Expression,
    },
    Printx {
        expression: Expression,
    },
    Select {
        expression: Expression,
        cases: Vec<SelectCase>,
    },
    Forward {
        distance: Expression,
    },
    Back {
        distance: Expression,
    },
    TurnLeft {
        angle: Expression,
    },
    TurnRight {
        angle: Expression,
    },
    Penup,
    Pendown,
    Home,
    Setxy {
        x: Expression,
        y: Expression,
    },
    Turn {
        angle: Expression,
    },
    DefInt {
        ranges: Vec<String>, // e.g., "A-C", "X"
    },
    DefSng {
        ranges: Vec<String>,
    },
    DefDbl {
        ranges: Vec<String>,
    },
    DefStr {
        ranges: Vec<String>,
    },
}

#[derive(Debug, Clone, PartialEq)]
pub enum CaseValue {
    Single(Expression),
    Range(Expression, Expression),  // min TO max
    Is(BinaryOperator, Expression), // IS operator value
}

#[derive(Debug, Clone, PartialEq)]
pub struct SelectCase {
    pub value: Option<CaseValue>, // None for CASE ELSE
    pub statements: Vec<Statement>,
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
    pub variables: HashMap<String, VariableInfo>,
    pub arrays: HashMap<String, Vec<Value>>,
    pub functions: HashMap<String, FunctionDefinition>,
    pub for_loops: Vec<ForLoop>,
    pub gosub_stack: Vec<usize>,
    pub data: Vec<Value>,
    pub data_pointer: usize,
    pub random_seed: u64,
    pub array_base: usize,
    pub input_variable: Option<String>,
    pub type_declarations: HashMap<String, VariableType>, // Range -> Type mappings
}

impl ExecutionContext {
    pub fn new() -> Self {
        Self {
            variables: HashMap::new(),
            arrays: HashMap::new(),
            functions: HashMap::new(),
            for_loops: Vec::new(),
            gosub_stack: Vec::new(),
            data: Vec::new(),
            data_pointer: 0,
            random_seed: 12345,
            array_base: 0,
            input_variable: None,
            type_declarations: HashMap::new(),
        }
    }

    /// Extract base name and type from variable name with declaration character
    pub fn parse_variable_name(name: &str) -> (String, Option<VariableType>) {
        let name = name.to_uppercase();
        if let Some(stripped) = name.strip_suffix('%') {
            (stripped.to_string(), Some(VariableType::Integer))
        } else if let Some(stripped) = name.strip_suffix('!') {
            (stripped.to_string(), Some(VariableType::Single))
        } else if let Some(stripped) = name.strip_suffix('#') {
            (stripped.to_string(), Some(VariableType::Double))
        } else if let Some(stripped) = name.strip_suffix('$') {
            (stripped.to_string(), Some(VariableType::String))
        } else {
            (name, None)
        }
    }

    /// Get the declared type for a variable, considering both declaration characters and DEF statements
    pub fn get_variable_type(&self, name: &str) -> VariableType {
        let (base_name, explicit_type) = Self::parse_variable_name(name);

        // Explicit type declaration character takes precedence
        if let Some(var_type) = explicit_type {
            return var_type;
        }

        // Check DEF statements for the first character
        if let Some(first_char) = base_name.chars().next() {
            let range_key = first_char.to_string();
            if let Some(def_type) = self.type_declarations.get(&range_key) {
                return def_type.clone();
            }
        }

        // Default to Single (GW-BASIC default for undeclared variables)
        VariableType::Single
    }

    /// Get or create a variable with proper typing
    pub fn get_variable(&mut self, name: &str) -> &mut VariableInfo {
        let var_type = self.get_variable_type(name);
        let (base_name, _) = Self::parse_variable_name(name);

        self.variables
            .entry(base_name)
            .or_insert_with(|| VariableInfo {
                value: match var_type {
                    VariableType::Integer => Value::Integer(0),
                    VariableType::Single => Value::Single(0.0),
                    VariableType::Double => Value::Double(0.0),
                    VariableType::String => Value::String(String::new()),
                },
                declared_type: var_type,
            })
    }
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
