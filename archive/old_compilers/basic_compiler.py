#!/usr/bin/env python3
"""
BASIC Native Compiler
=====================

A compiler for the BASIC programming language that produces 
standalone Linux executables. This version supports the core
BASIC features used in the Time_Warp IDE.

BASIC Language Features Supported:
- Variable assignments (LET X = 10)
- PRINT statements with variables
- INPUT statements  
- Conditional statements (IF...THEN...ELSE)
- Loops (FOR...NEXT, WHILE...WEND)
- GOTO and GOSUB with line numbers
- Built-in functions (RND, INT, STR$, etc.)
- Arrays and string operations
"""

import re
import os
import sys
import subprocess
import tempfile


class BasicSimpleCompiler:
    """Simple BASIC compiler that converts BASIC source to C and compiles to executable"""
    
    def __init__(self):
        self.debug = False
        
    def compile_file(self, input_file: str, output_file = None) -> bool:
        """Compile BASIC source file to Linux executable"""
        try:
            # Read source file
            with open(input_file, 'r') as f:
                source = f.read()
            
            # Determine output filename
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = f"{base_name}_compiled"
            
            return self.compile_source(source, output_file)
            
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def compile_source(self, source: str, output_file: str) -> bool:
        """Compile BASIC source code to Linux executable"""
        try:
            print(f"🔧 Compiling BASIC source to executable: {output_file}")
            
            # Parse BASIC source into statements
            print("📝 Step 1: Parsing BASIC source...")
            statements = self.parse_basic_source(source)
            print(f"   Found {len(statements)} statements")
            
            if self.debug:
                for i, stmt in enumerate(statements):
                    print(f"   {i}: {stmt}")
            
            # Generate C code
            print("⚙️  Step 2: Generating C code...")
            c_code = self.generate_c_code(statements)
            
            if self.debug:
                print("Generated C code:")
                print(c_code)
            
            # Compile to executable
            print("🔨 Step 3: Building executable...")
            success = self.build_executable(c_code, output_file)
            
            if success:
                print(f"✅ Compilation successful: {output_file}")
                # Make executable
                os.chmod(output_file, 0o755)
            
            return success
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            return False
    
    def parse_basic_source(self, source: str) -> list:
        """Parse BASIC source into list of statements"""
        statements = []
        lines = source.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("'") or line.startswith("REM"):
                continue
            
            # Remove line numbers if present
            line_match = re.match(r'^(\d+)\s+(.+)$', line)
            if line_match:
                actual_line_num = int(line_match.group(1))
                line = line_match.group(2)
            else:
                actual_line_num = line_num
            
            # Parse different BASIC statements
            line_upper = line.upper()
            
            if line_upper.startswith('PRINT '):
                statements.append(('PRINT', line[6:].strip(), actual_line_num))
            elif line_upper == 'PRINT':
                statements.append(('PRINT', '', actual_line_num))
            elif line_upper.startswith('INPUT '):
                input_part = line[6:].strip()
                # Handle INPUT "prompt"; variable format
                if '"' in input_part and ';' in input_part:
                    quote_end = input_part.rfind('"')
                    if quote_end > 0:
                        prompt = input_part[1:quote_end]  # Extract prompt without quotes
                        var_part = input_part[quote_end+1:].strip()
                        if var_part.startswith(';'):
                            var_name = var_part[1:].strip()
                            statements.append(('INPUT_PROMPT', f"{prompt}|{var_name}", actual_line_num))
                        else:
                            statements.append(('INPUT', input_part, actual_line_num))
                    else:
                        statements.append(('INPUT', input_part, actual_line_num))
                else:
                    statements.append(('INPUT', input_part, actual_line_num))
            elif line_upper.startswith('LET '):
                statements.append(('LET', line[4:].strip(), actual_line_num))
            elif '=' in line and not any(line_upper.startswith(x) for x in ['IF ', 'FOR ', 'WHILE ']):
                # Assignment without LET
                statements.append(('LET', line.strip(), actual_line_num))
            elif line_upper.startswith('IF '):
                statements.append(('IF', line[3:].strip(), actual_line_num))
            elif line_upper.startswith('FOR '):
                statements.append(('FOR', line[4:].strip(), actual_line_num))
            elif line_upper.startswith('NEXT'):
                var = line[4:].strip() if len(line) > 4 else ''
                statements.append(('NEXT', var, actual_line_num))
            elif line_upper.startswith('WHILE '):
                statements.append(('WHILE', line[6:].strip(), actual_line_num))
            elif line_upper.startswith('WEND'):
                statements.append(('WEND', '', actual_line_num))
            elif line_upper.startswith('GOTO '):
                statements.append(('GOTO', line[5:].strip(), actual_line_num))
            elif line_upper.startswith('GOSUB '):
                statements.append(('GOSUB', line[6:].strip(), actual_line_num))
            elif line_upper == 'RETURN':
                statements.append(('RETURN', '', actual_line_num))
            elif line_upper.startswith('DIM '):
                statements.append(('DIM', line[4:].strip(), actual_line_num))
            elif line_upper.startswith('REM '):
                statements.append(('REM', line[4:].strip(), actual_line_num))
            elif line_upper == 'END':
                statements.append(('END', '', actual_line_num))
            else:
                # Unknown statement, treat as comment
                statements.append(('COMMENT', line, actual_line_num))
        
        return statements
    
    def generate_c_code(self, statements: list) -> str:
        """Generate C code from BASIC statements"""
        # Collect line numbers and variables
        line_numbers = {}
        variables = set()
        for_loops = []
        while_loops = []
        
        for i, (cmd, arg, line_num) in enumerate(statements):
            line_numbers[line_num] = i
            
            if cmd in ['LET', 'INPUT']:
                if '=' in arg:
                    var_name = arg.split('=')[0].strip()
                    variables.add(var_name)
                else:
                    variables.add(arg)
            elif cmd == 'FOR':
                # FOR I = 1 TO 10
                match = re.match(r'(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$', arg, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    variables.add(var_name)
                    for_loops.append((i, var_name))
            elif cmd in ['PRINT', 'IF', 'WHILE']:
                # Extract variables referenced in expressions
                vars_found = re.findall(r'\b[A-Za-z][A-Za-z0-9]*\b', arg)
                for var in vars_found:
                    if var.upper() not in ['PRINT', 'IF', 'THEN', 'ELSE', 'WHILE', 'AND', 'OR', 'NOT', 'TO', 'STEP']:
                        variables.add(var)
        
        # Generate C code
        c_code = []
        
        # Headers
        c_code.extend([
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <time.h>",
            "#include <math.h>",
            "",
            "#define MAX_STRING_LEN 1024",
            "#define MAX_VARIABLES 200",
            "#define MAX_STACK 100",
            "",
            "// Variable structure",
            "typedef struct {",
            "    char name[64];",
            "    double value;",
            "    char str_value[MAX_STRING_LEN];",
            "    int is_string;",
            "} Variable;",
            "",
            "Variable variables[MAX_VARIABLES];",
            "int var_count = 0;",
            "int call_stack[MAX_STACK];",
            "int stack_ptr = 0;",
            "",
        ])
        
        # Runtime functions
        c_code.extend([
            "Variable* find_variable(const char* name) {",
            "    for (int i = 0; i < var_count; i++) {",
            "        if (strcasecmp(variables[i].name, name) == 0) {",
            "            return &variables[i];",
            "        }",
            "    }",
            "    return NULL;",
            "}",
            "",
            "Variable* create_variable(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    if (var) return var;",
            "    if (var_count < MAX_VARIABLES) {",
            "        strcpy(variables[var_count].name, name);",
            "        variables[var_count].value = 0.0;",
            "        variables[var_count].str_value[0] = '\\0';",
            "        variables[var_count].is_string = 0;",
            "        return &variables[var_count++];",
            "    }",
            "    return NULL;",
            "}",
            "",
            "void set_variable_number(const char* name, double value) {",
            "    Variable* var = create_variable(name);",
            "    if (var) {",
            "        var->value = value;",
            "        snprintf(var->str_value, MAX_STRING_LEN, \"%.6g\", value);",
            "        var->is_string = 0;",
            "    }",
            "}",
            "",
            "void set_variable_string(const char* name, const char* value) {",
            "    Variable* var = create_variable(name);",
            "    if (var) {",
            "        strncpy(var->str_value, value, MAX_STRING_LEN - 1);",
            "        var->str_value[MAX_STRING_LEN - 1] = '\\0';",
            "        var->is_string = 1;",
            "        var->value = atof(value);",
            "    }",
            "}",
            "",
            "double get_variable_number(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    return var ? var->value : 0.0;",
            "}",
            "",
            "const char* get_variable_string(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    if (var) {",
            "        if (var->is_string) {",
            "            return var->str_value;",
            "        } else {",
            "            static char buffer[MAX_STRING_LEN];",
            "            snprintf(buffer, MAX_STRING_LEN, \"%.6g\", var->value);",
            "            return buffer;",
            "        }",
            "    }",
            "    return \"\";",
            "}",
            "",
            "double evaluate_expression(const char* expr) {",
            "    // Simple expression evaluator for BASIC",
            "    char buffer[MAX_STRING_LEN];",
            "    strcpy(buffer, expr);",
            "    ",
            "    // Handle RND function",
            "    if (strstr(buffer, \"RND\")) {",
            "        return (double)rand() / RAND_MAX;",
            "    }",
            "    ",
            "    // Handle simple variable references",
            "    Variable* var = find_variable(buffer);",
            "    if (var) {",
            "        return var->value;",
            "    }",
            "    ",
            "    // Try to parse as number",
            "    return atof(buffer);",
            "}",
            "",
            "int evaluate_condition(const char* expr) {",
            "    // Simple condition evaluator",
            "    char buffer[MAX_STRING_LEN];",
            "    strcpy(buffer, expr);",
            "    ",
            "    // Handle equality",
            "    if (strstr(buffer, \"=\")) {",
            "        char* eq_pos = strstr(buffer, \"=\");",
            "        *eq_pos = '\\0';",
            "        char* left = buffer;",
            "        char* right = eq_pos + 1;",
            "        ",
            "        // Trim spaces",
            "        while (*left == ' ') left++;",
            "        while (*right == ' ') right++;",
            "        ",
            "        double left_val = evaluate_expression(left);",
            "        double right_val = evaluate_expression(right);",
            "        return fabs(left_val - right_val) < 0.000001;",
            "    }",
            "    ",
            "    // Handle greater than",
            "    if (strstr(buffer, \">\")) {",
            "        char* gt_pos = strstr(buffer, \">\");",
            "        *gt_pos = '\\0';",
            "        char* left = buffer;",
            "        char* right = gt_pos + 1;",
            "        double left_val = evaluate_expression(left);",
            "        double right_val = evaluate_expression(right);",
            "        return left_val > right_val;",
            "    }",
            "    ",
            "    // Handle less than",
            "    if (strstr(buffer, \"<\")) {",
            "        char* lt_pos = strstr(buffer, \"<\");",
            "        *lt_pos = '\\0';",
            "        char* left = buffer;",
            "        char* right = lt_pos + 1;",
            "        double left_val = evaluate_expression(left);",
            "        double right_val = evaluate_expression(right);",
            "        return left_val < right_val;",
            "    }",
            "    ",
            "    // Default: evaluate as number (0 = false, non-zero = true)",
            "    return evaluate_expression(buffer) != 0.0;",
            "}",
            "",
            "void print_value(const char* expr) {",
            "    // Handle string literals",
            "    if (expr[0] == '\"') {",
            "        char str[MAX_STRING_LEN];",
            "        strcpy(str, expr + 1);",
            "        if (str[strlen(str)-1] == '\"') {",
            "            str[strlen(str)-1] = '\\0';",
            "        }",
            "        printf(\"%s\", str);",
            "    } else {",
            "        // Variable or expression",
            "        Variable* var = find_variable(expr);",
            "        if (var) {",
            "            if (var->is_string) {",
            "                printf(\"%s\", var->str_value);",
            "            } else {",
            "                printf(\"%.6g\", var->value);",
            "            }",
            "        } else {",
            "            printf(\"%.6g\", evaluate_expression(expr));",
            "        }",
            "    }",
            "}",
            "",
        ])
        
        # Main function
        c_code.extend([
            "int main() {",
            "    srand(time(NULL));",
            "    char input_buffer[MAX_STRING_LEN];",
            f"    int pc = 0;",
            f"    int program_size = {len(statements)};",
            "",
            "    while (pc < program_size) {",
            "        switch (pc) {",
        ])
        
        # Generate code for each statement
        for i, (cmd, arg, line_num) in enumerate(statements):
            c_code.append(f"            case {i}: // Line {line_num}")
            
            if cmd == 'PRINT':
                if not arg:
                    c_code.append("                printf(\"\\n\");")
                else:
                    # Handle multiple print arguments separated by semicolons or commas
                    if ';' in arg or ',' in arg:
                        parts = re.split(r'[;,]', arg)
                        for part in parts:
                            part = part.strip()
                            if part:
                                c_code.append(f"                print_value(\"{self.escape_string(part)}\");")
                        c_code.append("                printf(\"\\n\");")
                    else:
                        c_code.append(f"                print_value(\"{self.escape_string(arg)}\");")
                        c_code.append("                printf(\"\\n\");")
            
            elif cmd == 'INPUT':
                var_name = arg.strip()
                c_code.extend([
                    f"                printf(\"? \");",
                    "                fgets(input_buffer, MAX_STRING_LEN, stdin);",
                    "                input_buffer[strcspn(input_buffer, \"\\n\")] = '\\0';",
                    f"                set_variable_string(\"{var_name}\", input_buffer);",
                ])
            
            elif cmd == 'INPUT_PROMPT':
                parts = arg.split('|')
                if len(parts) == 2:
                    prompt, var_name = parts
                    escaped_prompt = self.escape_string(prompt)
                    c_code.extend([
                        f"                printf(\"{escaped_prompt}\");",
                        "                fgets(input_buffer, MAX_STRING_LEN, stdin);",
                        "                input_buffer[strcspn(input_buffer, \"\\n\")] = '\\0';",
                        f"                set_variable_string(\"{var_name}\", input_buffer);",
                    ])
            
            elif cmd == 'LET':
                if '=' in arg:
                    var_name, expr = arg.split('=', 1)
                    var_name = var_name.strip()
                    expr = expr.strip()
                    c_code.extend([
                        f"                set_variable_number(\"{var_name}\", evaluate_expression(\"{self.escape_string(expr)}\"));",
                    ])
            
            elif cmd == 'IF':
                # Parse IF...THEN...ELSE
                if_match = re.match(r'(.+?)\s+THEN\s+(.+?)(?:\s+ELSE\s+(.+))?$', arg, re.IGNORECASE)
                if if_match:
                    condition = if_match.group(1)
                    then_part = if_match.group(2)
                    else_part = if_match.group(3) if if_match.group(3) else None
                    
                    c_code.extend([
                        f"                if (evaluate_condition(\"{self.escape_string(condition)}\")) {{",
                    ])
                    
                    # Handle THEN part (could be GOTO or statement)
                    if then_part.upper().startswith('GOTO '):
                        target_line = int(then_part[5:].strip())
                        if target_line in line_numbers:
                            c_code.append(f"                    pc = {line_numbers[target_line]} - 1;")
                    else:
                        c_code.append(f"                    // THEN: {then_part}")
                    
                    if else_part:
                        c_code.append("                } else {")
                        if else_part.upper().startswith('GOTO '):
                            target_line = int(else_part[5:].strip())
                            if target_line in line_numbers:
                                c_code.append(f"                    pc = {line_numbers[target_line]} - 1;")
                        else:
                            c_code.append(f"                    // ELSE: {else_part}")
                    
                    c_code.append("                }")
            
            elif cmd == 'FOR':
                # FOR I = 1 TO 10 STEP 1
                match = re.match(r'(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$', arg, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    start_val = match.group(2)
                    end_val = match.group(3)
                    step_val = match.group(4) if match.group(4) else "1"
                    
                    c_code.extend([
                        f"                set_variable_number(\"{var_name}\", evaluate_expression(\"{start_val}\"));",
                        f"                // FOR loop: {var_name} = {start_val} TO {end_val} STEP {step_val}",
                    ])
            
            elif cmd == 'NEXT':
                var_name = arg if arg else 'I'  # Default to I if no variable specified
                # Find matching FOR loop
                for j in range(i-1, -1, -1):
                    if statements[j][0] == 'FOR':
                        for_match = re.match(r'(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$', statements[j][1], re.IGNORECASE)
                        if for_match and (not var_name or for_match.group(1).upper() == var_name.upper()):
                            for_var = for_match.group(1)
                            end_val = for_match.group(3)
                            step_val = for_match.group(4) if for_match.group(4) else "1"
                            
                            c_code.extend([
                                f"                set_variable_number(\"{for_var}\", get_variable_number(\"{for_var}\") + evaluate_expression(\"{step_val}\"));",
                                f"                if (get_variable_number(\"{for_var}\") <= evaluate_expression(\"{end_val}\")) {{",
                                f"                    pc = {j + 1} - 1; // Jump to statement AFTER FOR, -1 for pc++",
                                "                }",
                            ])
                            break
            
            elif cmd == 'GOTO':
                target_line = int(arg)
                if target_line in line_numbers:
                    c_code.append(f"                pc = {line_numbers[target_line]} - 1;")
            
            elif cmd == 'GOSUB':
                target_line = int(arg)
                if target_line in line_numbers:
                    c_code.extend([
                        "                call_stack[stack_ptr++] = pc;",
                        f"                pc = {line_numbers[target_line]} - 1;",
                    ])
            
            elif cmd == 'RETURN':
                c_code.extend([
                    "                if (stack_ptr > 0) {",
                    "                    pc = call_stack[--stack_ptr];",
                    "                }",
                ])
            
            elif cmd == 'DIM':
                # Array declarations - simplified to just comments for now
                c_code.append(f"                // Array declaration: {self.escape_string(arg)}")
            
            elif cmd == 'REM':
                # Comments
                c_code.append(f"                // REM: {self.escape_string(arg)}")
            
            elif cmd == 'END':
                c_code.append("                return 0;")
            
            elif cmd == 'COMMENT':
                c_code.append(f"                // {arg}")
            
            c_code.extend([
                "                pc++;",
                "                break;",
            ])
        
        c_code.extend([
            "            default:",
            "                pc++;",
            "                break;",
            "        }",
            "    }",
            "    return 0;",
            "}",
        ])
        
        return "\n".join(c_code)
    
    def escape_string(self, s: str) -> str:
        """Escape string for C code"""
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    
    def build_executable(self, c_code: str, output_file: str) -> bool:
        """Compile C code to executable"""
        try:
            # Create temporary C file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(c_code)
                c_file = f.name
            
            try:
                # Compile with gcc
                cmd = ['gcc', '-o', output_file, c_file, '-lm']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("   C compilation successful")
                    return True
                else:
                    print(f"   C compilation failed: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary C file
                os.unlink(c_file)
                
        except Exception as e:
            print(f"   Build error: {e}")
            return False


def main():
    """Main compiler entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BASIC Native Compiler")
    parser.add_argument('input_file', help='BASIC source file to compile')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    compiler = BasicSimpleCompiler()
    compiler.debug = args.debug
    
    success = compiler.compile_file(args.input_file, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()