# JAMES Application File Convention

## File Extension: .JTC

JAMES applications and programs (written using the JAMES IDE) use the `.JTC` extension to distinguish them from regular Python files and establish a unique identity for programs created in the JAMES environment.

### Benefits of .JTC Extension

1. **Unique Identity**: Clearly identifies applications written in JAMES
2. **IDE Integration**: Allows for specialized syntax highlighting and tooling for JAMES programs
3. **Educational Context**: Reinforces that these are educational programming applications
4. **Version Control**: Easy to identify JAMES applications in repositories

### File Types

- **JAMES.py** - The JAMES IDE itself (Python application)
- ***.JTC** - Applications and programs written in JAMES
- ***.pilot** - PILOT language program files (unchanged)

### Usage

#### Running the JAMES IDE
Run the JAMES IDE itself:
```bash
python3 JAMES.py
```

#### Creating JAMES Applications
When developing applications with JAMES IDE, save your programs with the .JTC extension:
```bash
# Example JAMES application
my_program.JTC
```

#### Executing JAMES Applications
Execute .JTC applications using the provided launcher:
```bash
python3 jtc_launcher.py my_program.JTC
```

### Migration

When creating applications in JAMES, save them with .JTC extension:
```bash
# Save your JAMES applications as:
my_game.JTC
my_calculator.JTC
my_drawing_app.JTC
```

The .JTC files contain JAMES/PILOT code and can be loaded into the JAMES IDE.

### Tools

- **jtc_launcher.py** - Command-line launcher for .JTC files
- Standard Python tools work with .JTC files since they contain Python code

This convention helps establish JAMES as a distinct educational programming environment while maintaining full compatibility with Python tooling.