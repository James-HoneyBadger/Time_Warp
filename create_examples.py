#!/usr/bin/env python3
"""
Hello World examples for all Time_Warp compilation languages.
These programs demonstrate the compilation feature.
"""

# PILOT Hello World
pilot_hello = '''T: Hello World Program
A: This program demonstrates PILOT compilation
J: END'''

# BASIC Hello World
basic_hello = '''10 REM Hello World in BASIC
20 PRINT "Hello, BASIC World!"
30 PRINT "This program was compiled to executable!"
40 END'''

# Logo Hello World (simple graphics)
logo_hello = '''; Logo Hello World - Simple Square
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90
FORWARD 100
RIGHT 90'''

# Pascal Hello World
pascal_hello = '''program HelloWorld;
begin
  writeln('Hello, Pascal World!');
  writeln('This program was compiled to executable!');
end.'''

# Prolog Hello World (simple facts)
prolog_hello = '''% Prolog Hello World
parent(john, mary).
parent(mary, susan).

grandparent(X, Y) :- parent(X, Z), parent(Z, Y).

% Query: grandparent(john, susan).'''

# Forth Hello World
forth_hello = ''': HELLO   CR ." Hello, Forth World!" CR ;
: GREETING   CR ." This program was compiled to executable!" CR ;
HELLO GREETING'''

# Save examples to files
examples = [
    ('examples/hello_pilot.pilot', pilot_hello),
    ('examples/hello_basic.bas', basic_hello),
    ('examples/hello_logo.logo', logo_hello),
    ('examples/hello_pascal.pas', pascal_hello),
    ('examples/hello_prolog.plg', prolog_hello),
    ('examples/hello_forth.fs', forth_hello),
]

for filename, content in examples:
    with open(filename, 'w') as f:
        f.write(content)

print("✅ Created hello world examples for all compilation languages!")
print("\n📁 Files created:")
for filename, _ in examples:
    print(f"  • {filename}")
print("\n🚀 You can now compile these programs using:")
print("   Tools → Compile to Executable... (Ctrl+Shift+E)")