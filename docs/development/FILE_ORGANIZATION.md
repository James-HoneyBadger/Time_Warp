# TimeWarp File System Organization

## Correct File Convention

### IDE vs Applications

- **TimeWarp.py** - The TimeWarp IDE itself (Python application that provides the development environment)
- **\*.JTC** - Applications and programs written using the TimeWarp IDE
- **\*.pilot** - PILOT language programs (can be loaded into TimeWarp)

### File Structure

```
TimeWarp/
├── TimeWarp.py                    # The TimeWarp IDE (Python application)
├── jtc_launcher.py            # Launcher for .JTC applications
├── calculator.JTC             # Example TimeWarp application
├── pilot_feature_test.pilot   # PILOT language test program
├── tools/                     # IDE support modules
│   ├── __init__.py
│   └── theme.py
└── docs/                      # Documentation files
    ├── ENHANCEMENT_SUMMARY.md
    ├── JTC_FILE_CONVENTION.md
    └── PILOT_EXTENDED_COMMANDS.md
```

### Usage Workflow

1. **Run the IDE**: `python3 TimeWarp.py`
2. **Create applications**: Save your programs as `my_app.JTC`
3. **Execute applications**: `python3 jtc_launcher.py my_app.JTC`

### Benefits

- **Clear Separation**: IDE (Python) vs Applications (JTC)
- **Educational Focus**: .JTC files are clearly identified as TimeWarp applications
- **Tooling Support**: Each file type can have specialized tools
- **Professional Structure**: Follows standard conventions for IDEs and their target applications

This structure mirrors real-world development environments where:
- The IDE is a separate application (like Visual Studio Code, written in TypeScript/JavaScript)
- Applications created in the IDE have their own file extensions (like .cs for C#, .java for Java)
- TimeWarp applications use .JTC to establish their identity in the educational programming space