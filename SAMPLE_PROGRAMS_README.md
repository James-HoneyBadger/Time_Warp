# TW BASIC, TW Pascal, and TW Prolog Sample Programs

This directory contains sample programs demonstrating the features of the Time Warp IDE's three supported languages.

## TW BASIC Samples

### `tw_basic_sample.twb`
A comprehensive demonstration of TW BASIC's unified features:
- **GW BASIC**: Variables, arithmetic, PRINT statements
- **PILOT**: Interactive questions (T:) and answers (A:)
- **Logo**: Turtle graphics commands (FORWARD, RIGHT, etc.)

**Features demonstrated:**
- Variable assignment with LET
- Text output with PRINT
- Interactive input with A: (PILOT style)
- Turtle graphics with FORWARD, RIGHT, etc.
- Logo's REPEAT loop structure

### `tw_basic_game.twb`
A traditional line-numbered BASIC program implementing a number guessing game.

**Features demonstrated:**
- Line-numbered program structure
- Variables and arithmetic
- INPUT for user interaction
- IF...THEN conditional logic
- GOTO for program flow control
- REM comments

## TW Pascal Samples

### `tw_pascal_sample.twp`
An introductory Pascal program showing basic language features.

**Features demonstrated:**
- Program structure with begin/end
- Variable declarations (var)
- Input/output with readln/writeln
- Control structures (if, for, case)
- String handling

### `tw_pascal_advanced.twp`
An advanced Pascal program demonstrating procedures and functions.

**Features demonstrated:**
- Function definitions and calls (factorial)
- Procedure definitions (find_max, calculate_sum)
- Array handling
- Parameter passing (var parameters)
- Complex expressions and calculations

## TW Prolog Samples

### `tw_prolog_sample.tpr`
A basic Prolog program with facts, rules, and queries.

**Features demonstrated:**
- Domain declarations
- Predicate declarations
- Facts (person/2, likes/2)
- Rules (adult/1, child/1, favorite_color/2)
- Query execution in the goal section

### `tw_prolog_advanced.tpr`
An advanced Prolog program showing recursion and arithmetic.

**Features demonstrated:**
- Recursive predicates (fibonacci, factorial)
- List processing (sum_list, length_list, average_list)
- Arithmetic operations
- Complex rules with mathematical calculations
- Built-in predicates (mod, etc.)

## How to Use These Samples

1. **Load a sample program:**
   - Use File → Open File... to load any of the .twb, .twp, or .tpr files
   - Or copy/paste the code into the code editor

2. **Select the appropriate language:**
   - For .twb files: Select "TW BASIC" from the language dropdown
   - For .twp files: Select "TW Pascal" from the language dropdown
   - For .tpr files: Select "TW Prolog" from the language dropdown

3. **Run the program:**
   - Click the "Run ▶" button in the toolbar
   - Or use Run → Run Program from the menu
   - The output will appear in the Output & Graphics tab

4. **Interact with the program:**
   - For programs that require input, click in the text area of the Output & Graphics tab
   - Type your response and press Enter
   - Some programs also generate turtle graphics in the graphics area

## Language-Specific Notes

### TW BASIC
- Combines GW BASIC, PILOT, and Logo syntax
- Supports both modern free-form and traditional line-numbered styles
- Use `INPUT` or `A:` for user input
- Logo turtle commands work in any TW BASIC program

### TW Pascal
- Turbo Pascal-style syntax
- Supports procedures, functions, and complex data types
- Use `readln()` for input and `writeln()` for output
- Programs end with a period (.)

### TW Prolog
- Turbo Prolog-style syntax
- Programs consist of domains, predicates, and clauses sections
- The goal section contains queries to execute
- Use `write()` and `nl` for output, `readln()` for input

## File Extensions
- `.twb` - TW BASIC programs
- `.twp` - TW Pascal programs
- `.tpr` - TW Prolog programs

These samples showcase the full capabilities of each language as implemented in the Time Warp IDE. Feel free to modify them or use them as templates for your own programs!