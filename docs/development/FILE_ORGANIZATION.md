# Time_Warp File System Organization

## Correct File Convention

### IDE vs Applications

- **Time_Warp.py** - The Time_Warp IDE itself (Python application that provides the development environment)
- **\*.pilot** - PILOT language programs (educational programming language)
- **\*.bas** - BASIC language programs (classic line-numbered programming)
- **\*.logo** - Logo language programs (turtle graphics programming)
- **\*.py** - Python programs (modern scripting language)
- **\*.js** - JavaScript programs (web and general scripting)
- **\*.pl** - Perl programs (text processing and scripting)

### File Structure

```
Time_Warp/
├── Time_Warp.py                    # The Time_Warp IDE (Python application)
├── calculator.py              # Example Python program
├── demo.pilot                 # Example PILOT program
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

1. **Run the IDE**: `python3 Time_Warp.py`
2. **Create programs**: Save your programs with appropriate extensions (`my_program.pilot`, `my_script.py`, etc.)
3. **Execute programs**: Use the Time_Warp IDE's Run button (F5) or run directly with language interpreters

### Benefits

- **Multi-Language Support**: Native support for PILOT, BASIC, Logo, Python, JavaScript, and Perl
- **Educational Focus**: Each language serves different learning objectives and programming paradigms
- **Standard Extensions**: Uses industry-standard file extensions for maximum compatibility
- **Professional Structure**: Follows established conventions for educational programming environments

This structure enables effective programming education by:
- Supporting multiple programming languages and paradigms
- Using familiar file extensions that work with standard development tools
- Providing a consistent development experience across all supported languages
- Encouraging exploration of different programming approaches and historical languages