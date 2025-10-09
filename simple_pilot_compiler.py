#!/usr/bin/env python3
"""
Simple PILOT Native Compiler
=============================

A simplified compiler for the PILOT programming language that produces 
standalone Linux executables. This version focuses on functionality over 
type safety for rapid development.
"""

import re
import os
import sys
import subprocess
import tempfile


class PilotSimpleCompiler:
    """Simple PILOT compiler that converts PILOT source to C and compiles to executable"""
    
    def __init__(self):
        self.debug = False
        
    def compile_file(self, input_file: str, output_file: str = None) -> bool:
        """Compile PILOT source file to Linux executable"""
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
        """Compile PILOT source code to Linux executable"""
        try:
            print(f"🔧 Compiling PILOT source to executable: {output_file}")
            
            # Parse PILOT source into statements
            print("📝 Step 1: Parsing PILOT source...")
            statements = self.parse_pilot_source(source)
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
    
    def parse_pilot_source(self, source: str) -> list:
        """Parse PILOT source into list of statements"""
        statements = []
        lines = source.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse different command types
            if line.startswith('T:'):
                statements.append(('TEXT', line[2:].strip()))
            elif line.startswith('A:'):
                statements.append(('INPUT', line[2:].strip()))
            elif line.startswith('Y:'):
                statements.append(('YES_IF', line[2:].strip()))
            elif line.startswith('N:'):
                statements.append(('NO_IF', line[2:].strip()))
            elif line.startswith('J:'):
                statements.append(('JUMP', line[2:].strip()))
            elif line.startswith('L:'):
                statements.append(('LABEL', line[2:].strip()))
            elif line.startswith('U:'):
                statements.append(('UPDATE', line[2:].strip()))
            elif line.startswith('C:'):
                statements.append(('COMPUTE', line[2:].strip()))
            elif line.startswith('M:'):
                statements.append(('MATCH_JUMP', line[2:].strip()))
            elif line.startswith('MT:'):
                statements.append(('MATCH_TEXT', line[3:].strip()))
            elif line.startswith('R:'):
                statements.append(('RUNTIME', line[2:].strip()))
            elif line.startswith('E:'):
                statements.append(('ERROR', line[2:].strip()))
            elif line.startswith('TYPE:'):
                statements.append(('TYPE', line[5:].strip()))
            elif line.startswith('ACCEPT:'):
                statements.append(('ACCEPT', line[7:].strip()))
            elif line.startswith('MATCH:'):
                statements.append(('MATCH', line[6:].strip()))
            elif line.startswith('JUMP:'):
                statements.append(('JUMP_CMD', line[5:].strip()))
            elif line.startswith('COMPUTE:'):
                statements.append(('COMPUTE_CMD', line[8:].strip()))
            elif line.startswith('USE:'):
                statements.append(('USE', line[4:].strip()))
            elif line.startswith('REMARK:'):
                statements.append(('REMARK', line[7:].strip()))
            elif line.upper() == 'END':
                statements.append(('END', ''))
            elif line.startswith('J(') and '):' in line:
                # Handle J(condition):label format
                paren_end = line.find('):')
                if paren_end > 2:
                    condition = line[2:paren_end].strip()
                    label = line[paren_end+2:].strip()
                    statements.append(('COND_JUMP', f"{condition}|{label}"))
            else:
                # Unknown statement, treat as comment
                statements.append(('COMMENT', line))
        
        return statements
    
    def generate_c_code(self, statements: list) -> str:
        """Generate C code from PILOT statements"""
        # Collect labels and variables
        labels = {}
        variables = set()
        
        for i, (cmd, arg) in enumerate(statements):
            if cmd == 'LABEL':
                labels[arg] = i
            elif cmd in ['INPUT', 'UPDATE', 'COMPUTE']:
                if '=' in arg:
                    var_name = arg.split('=')[0].strip()
                    variables.add(var_name)
                else:
                    variables.add(arg)
            elif cmd in ['TEXT', 'YES_IF', 'NO_IF']:
                # Extract variables from *VAR* references
                vars_in_text = re.findall(r'\\*([A-Za-z_][A-Za-z0-9_]*)\\*', arg)
                variables.update(vars_in_text)
        
        # Generate C code
        c_code = []
        
        # Headers and includes
        c_code.extend([
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <time.h>",
            "#include <math.h>",
            "",
            "#define MAX_STRING_LEN 1024",
            "#define MAX_VARIABLES 100",
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
            "int match_flag = 0;",
            "",
        ])
        
        # Runtime functions
        c_code.extend([
            "Variable* find_variable(const char* name) {",
            "    for (int i = 0; i < var_count; i++) {",
            "        if (strcmp(variables[i].name, name) == 0) {",
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
            "void set_variable_number(const char* name, double value) {",
            "    Variable* var = create_variable(name);",
            "    if (var) {",
            "        var->value = value;",
            "        snprintf(var->str_value, MAX_STRING_LEN, \"%.2f\", value);",
            "        var->is_string = 0;",
            "    }",
            "}",
            "",
            "const char* get_variable_string(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    if (var) {",
            "        if (var->is_string) {",
            "            return var->str_value;",
            "        } else {",
            "            static char buffer[MAX_STRING_LEN];",
            "            snprintf(buffer, MAX_STRING_LEN, \"%.2f\", var->value);",
            "            return buffer;",
            "        }",
            "    }",
            "    return \"\";",
            "}",
            "",
            "double get_variable_number(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    return var ? var->value : 0.0;",
            "}",
            "",
            "void interpolate_string(const char* input, char* output) {",
            "    const char* p = input;",
            "    char* out = output;",
            "    while (*p) {",
            "        if (*p == '*') {",
            "            p++;",
            "            char var_name[64];",
            "            int i = 0;",
            "            while (*p && *p != '*' && i < 63) {",
            "                var_name[i++] = *p++;",
            "            }",
            "            var_name[i] = '\\0';",
            "            if (*p == '*') p++;",
            "            const char* var_value = get_variable_string(var_name);",
            "            strcpy(out, var_value);",
            "            out += strlen(var_value);",
            "        } else {",
            "            *out++ = *p++;",
            "        }",
            "    }",
            "    *out = '\\0';",
            "}",
            "",
            "int evaluate_condition(const char* expr) {",
            "    // Simple condition evaluator",
            "    char buffer[MAX_STRING_LEN];",
            "    strcpy(buffer, expr);",
            "    ",
            "    // Handle simple string equality like *NAME* == \"Alice\"",
            "    char* eq_pos = strstr(buffer, \"==\");",
            "    if (eq_pos) {",
            "        // Split at == manually",
            "        *eq_pos = '\\0';",
            "        char* left = buffer;",
            "        char* right = eq_pos + 2;",
            "        ",
            "        // Trim spaces from left",
            "        while (*left == ' ') left++;",
            "        char* left_end = left + strlen(left) - 1;",
            "        while (left_end > left && *left_end == ' ') *left_end-- = '\\0';",
            "        ",
            "        // Trim spaces from right",
            "        while (*right == ' ') right++;",
            "        char* right_end = right + strlen(right) - 1;",
            "        while (right_end > right && *right_end == ' ') *right_end-- = '\\0';",
            "        ",
            "        char left_val[MAX_STRING_LEN], right_val[MAX_STRING_LEN];",
            "        interpolate_string(left, left_val);",
            "        strcpy(right_val, right);",
            "        ",
            "        // Remove quotes from right side if present",
            "        if (right_val[0] == '\"' && right_val[strlen(right_val)-1] == '\"') {",
            "            right_val[strlen(right_val)-1] = '\\0';",
            "            memmove(right_val, right_val + 1, strlen(right_val));",
            "        }",
            "        ",
            "        return strcmp(left_val, right_val) == 0;",
            "    }",
            "    return 0;",
            "}",
            "",
        ])
        
        # Main function
        c_code.extend([
            "int main() {",
            "    srand(time(NULL));",
            "    char input_buffer[MAX_STRING_LEN];",
            "    char output_buffer[MAX_STRING_LEN];",
            f"    int pc = 0;",
            f"    int program_size = {len(statements)};",
            "",
            "    while (pc < program_size) {",
            "        switch (pc) {",
        ])
        
        # Generate code for each statement
        for i, (cmd, arg) in enumerate(statements):
            c_code.append(f"            case {i}:")
            
            if cmd == 'TEXT':
                escaped_arg = arg.replace('\\', '\\\\').replace('"', '\\"')
                c_code.extend([
                    f"                interpolate_string(\"{escaped_arg}\", output_buffer);",
                    "                printf(\"%s\\n\", output_buffer);",
                ])
            
            elif cmd == 'INPUT':
                c_code.extend([
                    f"                printf(\"Enter value for {arg}: \");",
                    "                fgets(input_buffer, MAX_STRING_LEN, stdin);",
                    "                input_buffer[strcspn(input_buffer, \"\\n\")] = '\\0';",
                    f"                set_variable_string(\"{arg}\", input_buffer);",
                ])
            
            elif cmd == 'YES_IF':
                escaped_arg = arg.replace('\\', '\\\\').replace('"', '\\"')
                c_code.extend([
                    f"                match_flag = evaluate_condition(\"{escaped_arg}\");",
                ])
            
            elif cmd == 'NO_IF':
                escaped_arg = arg.replace('\\', '\\\\').replace('"', '\\"')
                c_code.extend([
                    f"                match_flag = !evaluate_condition(\"{escaped_arg}\");",
                ])
            
            elif cmd == 'JUMP':
                target = labels.get(arg, -1)
                if target >= 0:
                    c_code.extend([
                        f"                pc = {target} - 1; // -1 because pc++ happens after",
                    ])
            
            elif cmd == 'COND_JUMP':
                parts = arg.split('|')
                if len(parts) == 2:
                    condition, label = parts
                    target = labels.get(label, -1)
                    if target >= 0:
                        escaped_condition = condition.replace('\\', '\\\\').replace('"', '\\"')
                        c_code.extend([
                            f"                if (evaluate_condition(\"{escaped_condition}\")) {{",
                            f"                    pc = {target} - 1; // -1 because pc++ happens after",
                            "                }",
                        ])
            
            elif cmd == 'LABEL':
                c_code.append(f"                // Label: {arg}")
            
            elif cmd == 'UPDATE' or cmd == 'COMPUTE':
                if '=' in arg:
                    var_name, expr = arg.split('=', 1)
                    var_name = var_name.strip()
                    expr = expr.strip()
                    # Simple numeric assignment
                    if expr.isdigit():
                        c_code.extend([
                            f"                set_variable_number(\"{var_name}\", {expr});",
                        ])
                    else:
                        c_code.extend([
                            f"                set_variable_string(\"{var_name}\", \"{expr}\");",
                        ])
            
            elif cmd == 'MATCH_JUMP':
                target = labels.get(arg, -1)
                if target >= 0:
                    c_code.extend([
                        "                if (match_flag) {",
                        f"                    pc = {target} - 1; // -1 because pc++ happens after",
                        "                }",
                    ])
            
            elif cmd == 'MATCH_TEXT':
                escaped_arg = arg.replace('\\', '\\\\').replace('"', '\\"')
                c_code.extend([
                    "                if (match_flag) {",
                    f"                    interpolate_string(\"{escaped_arg}\", output_buffer);",
                    "                    printf(\"%s\\n\", output_buffer);",
                    "                }",
                ])
            
            elif cmd == 'RUNTIME':
                # R: commands - runtime operations
                c_code.extend([
                    f"                printf(\"Runtime: {arg}\\n\");",
                ])
            
            elif cmd == 'ERROR':
                # E: commands - error handling
                c_code.extend([
                    f"                printf(\"Error: {arg}\\n\");",
                ])
            
            elif cmd == 'TYPE':
                # TYPE: commands - alternative to T:
                escaped_arg = arg.replace('\\', '\\\\').replace('"', '\\"')
                c_code.extend([
                    f"                interpolate_string(\"{escaped_arg}\", output_buffer);",
                    "                printf(\"%s\\n\", output_buffer);",
                ])
            
            elif cmd == 'ACCEPT':
                # ACCEPT: commands - alternative to A:
                c_code.extend([
                    f"                printf(\"Enter value for {arg}: \");",
                    "                fgets(input_buffer, MAX_STRING_LEN, stdin);",
                    "                input_buffer[strcspn(input_buffer, \"\\n\")] = '\\0';",
                    f"                set_variable_string(\"{arg}\", input_buffer);",
                ])
            
            elif cmd == 'MATCH':
                # MATCH: commands - alternative to M:
                escaped_arg = arg.replace('\\', '\\\\').replace('"', '\\"')
                c_code.extend([
                    f"                match_flag = evaluate_condition(\"{escaped_arg}\");",
                ])
            
            elif cmd == 'JUMP_CMD':
                # JUMP: commands - alternative to J:
                target = labels.get(arg, -1)
                if target >= 0:
                    c_code.extend([
                        f"                pc = {target} - 1; // -1 because pc++ happens after",
                    ])
            
            elif cmd == 'COMPUTE_CMD':
                # COMPUTE: commands - alternative to C:
                if '=' in arg:
                    var_name, expr = arg.split('=', 1)
                    var_name = var_name.strip()
                    expr = expr.strip()
                    if expr.isdigit():
                        c_code.extend([
                            f"                set_variable_number(\"{var_name}\", {expr});",
                        ])
                    else:
                        c_code.extend([
                            f"                set_variable_string(\"{var_name}\", \"{expr}\");",
                        ])
            
            elif cmd == 'USE':
                # USE: commands - subroutine calls
                c_code.extend([
                    f"                printf(\"Using subroutine: {arg}\\n\");",
                ])
            
            elif cmd == 'REMARK':
                # REMARK: comments
                c_code.extend([
                    f"                // Remark: {arg}",
                ])
            
            elif cmd == 'END':
                c_code.extend([
                    "                return 0;",
                ])
            
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
    
    parser = argparse.ArgumentParser(description="Simple PILOT Native Compiler")
    parser.add_argument('input_file', help='PILOT source file to compile')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    compiler = PilotSimpleCompiler()
    compiler.debug = args.debug
    
    success = compiler.compile_file(args.input_file, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()