use std::fs;

mod languages {
    pub mod prolog;
}

fn main() {
    let code = r#"domains
  person = symbol
  color = symbol

predicates
  person(person)
  likes(person, color)
  adult(person)
  child(person)
  favorite_color(person, color)

clauses
  person(john).
  person(mary).
  person(susan).
  person(tom).

  likes(john, blue).
  likes(mary, red).
  likes(susan, green).
  likes(tom, blue).

  adult(Person) :- person(Person), Person <> tom.
  child(tom).

  favorite_color(Person, Color) :- likes(Person, Color).

goal
  write("People and their favorite colors:"), nl,
  favorite_color(Person, Color),
  write(Person, " likes ", Color), nl,
  fail.

goal
  write("Adults: "), nl,
  adult(Person),
  write(Person), nl,
  fail."#;

    let result = test_prolog(code);
    println!("Prolog execution result:");
    println!("{}", result);
}

fn test_prolog(code: &str) -> String {
    use crate::languages::prolog::PrologInterpreter;
    let mut interpreter = PrologInterpreter::new();
    interpreter.execute(code)
}
