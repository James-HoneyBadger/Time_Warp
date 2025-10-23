use std::fs;

mod languages;

fn main() {
    let code = fs::read_to_string("test_prolog.tpr").expect("Failed to read file");
    let result = test_prolog(&code);
    println!("Prolog execution result:");
    println!("{}", result);
}

fn test_prolog(code: &str) -> String {
    use crate::languages::prolog::PrologInterpreter;
    let mut interpreter = PrologInterpreter::new();
    interpreter.execute(code)
}
