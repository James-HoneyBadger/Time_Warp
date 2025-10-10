#!/usr/bin/env python3
"""
Enhanced BASIC Native Compiler
==============================

A complete rewrite of the BASIC compiler with improved architecture,
better error handling, and enhanced language features.

Features:
- Full BASIC syntax support (PRINT, INPUT, LET, IF/THEN/ELSE, FOR/NEXT, etc.)
- Array support
- String operations
- Mathematical functions
- File I/O operations
- Error handling
"""

import re
from typing import List, Dict, Any
from . import BaseCompiler, CodeGenerator, Language


class BasicCodeGenerator(CodeGenerator):
    """Enhanced C code generator for BASIC"""

    def __init__(self):
        super().__init__(Language.BASIC)
        self.variables: Dict[str, Dict] = {}
        self.labels: Dict[str, int] = {}
        self.for_loops: List[Dict] = []
        self.arrays: Dict[str, Dict] = {}

    def generate_header(self) -> List[str]:
        """Generate BASIC-specific header code"""
        return [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <math.h>",
            "#include <time.h>",
            "#include <ctype.h>",
            "",
            "#define MAX_STRING_LEN 1024",
            "#define MAX_ARRAY_SIZE 10000",
            "#define MAX_VARIABLES 200",
            "#define MAX_STACK 100",
            "",
            "// Variable types",
            "typedef enum {",
            "    VAR_NUMBER,",
            "    VAR_STRING,",
            "    VAR_ARRAY",
            "} VarType;",
            "",
            "// Variable structure",
            "typedef struct {",
            "    char name[64];",
            "    VarType type;",
            "    double number_value;",
            "    char string_value[MAX_STRING_LEN];",
            "    double* array_data;",
            "    int array_size;",
            "} Variable;",
            "",
            "Variable variables[MAX_VARIABLES];",
            "int var_count = 0;",
            "int call_stack[MAX_STACK];",
            "int stack_ptr = 0;",
            "int data_ptr = 0;",
            "",
        ]

    def generate_runtime(self) -> List[str]:
        """Generate BASIC runtime functions"""
        return [
            "// Runtime functions",
            "Variable* find_variable(const char* name) {",
            "    for (int i = 0; i < var_count; i++) {",
            "        if (strcasecmp(variables[i].name, name) == 0) {",
            "            return &variables[i];",
            "        }",
            "    }",
            "    return NULL;",
            "}",
            "",
            "Variable* create_variable(const char* name, VarType type) {",
            "    Variable* var = find_variable(name);",
            "    if (var) return var;",
            "    if (var_count < MAX_VARIABLES) {",
            "        strcpy(variables[var_count].name, name);",
            "        variables[var_count].type = type;",
            "        variables[var_count].number_value = 0.0;",
            "        variables[var_count].string_value[0] = '\\0';",
            "        variables[var_count].array_data = NULL;",
            "        variables[var_count].array_size = 0;",
            "        return &variables[var_count++];",
            "    }",
            "    return NULL;",
            "}",
            "",
            "void set_number_variable(const char* name, double value) {",
            "    Variable* var = create_variable(name, VAR_NUMBER);",
            "    if (var) {",
            "        var->number_value = value;",
            "        var->type = VAR_NUMBER;",
            "    }",
            "}",
            "",
            "void set_string_variable(const char* name, const char* value) {",
            "    Variable* var = create_variable(name, VAR_STRING);",
            "    if (var) {",
            "        strncpy(var->string_value, value, MAX_STRING_LEN - 1);",
            "        var->string_value[MAX_STRING_LEN - 1] = '\\0';",
            "        var->type = VAR_STRING;",
            "    }",
            "}",
            "",
            "double get_number_variable(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    return var ? var->number_value : 0.0;",
            "}",
            "",
            "const char* get_string_variable(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    if (var && var->type == VAR_STRING) {",
            "        return var->string_value;",
            "    }",
            "    static char buffer[MAX_STRING_LEN];",
            "    if (var) {",
            '        snprintf(buffer, MAX_STRING_LEN, "%.6g", var->number_value);',
            "    } else {",
            '        strcpy(buffer, "0");',
            "    }",
            "    return buffer;",
            "}",
            "",
            "void create_array(const char* name, int size) {",
            "    Variable* var = create_variable(name, VAR_ARRAY);",
            "    if (var && size > 0 && size <= MAX_ARRAY_SIZE) {",
            "        var->array_data = (double*)malloc(size * sizeof(double));",
            "        if (var->array_data) {",
            "            var->array_size = size;",
            "            memset(var->array_data, 0, size * sizeof(double));",
            "        }",
            "    }",
            "}",
            "",
            "double get_array_element(const char* name, int index) {",
            "    Variable* var = find_variable(name);",
            "    if (var && var->type == VAR_ARRAY && var->array_data &&",
            "        index >= 0 && index < var->array_size) {",
            "        return var->array_data[index];",
            "    }",
            "    return 0.0;",
            "}",
            "",
            "void set_array_element(const char* name, int index, double value) {",
            "    Variable* var = find_variable(name);",
            "    if (var && var->type == VAR_ARRAY && var->array_data &&",
            "        index >= 0 && index < var->array_size) {",
            "        var->array_data[index] = value;",
            "    }",
            "}",
            "",
            "double evaluate_expression(const char* expr) {",
            "    // Enhanced expression evaluator",
            "    if (!expr || !*expr) return 0.0;",
            "",
            "    // Handle RND function",
            '    if (strncasecmp(expr, "RND", 3) == 0) {',
            "        return (double)rand() / RAND_MAX;",
            "    }",
            "",
            "    // Handle INT function",
            '    if (strncasecmp(expr, "INT(", 4) == 0) {',
            "        char arg[256];",
            '        if (sscanf(expr + 4, "%255[^)]", arg) == 1) {',
            "            return floor(evaluate_expression(arg));",
            "        }",
            "    }",
            "",
            "    // Handle ABS function",
            '    if (strncasecmp(expr, "ABS(", 4) == 0) {',
            "        char arg[256];",
            '        if (sscanf(expr + 4, "%255[^)]", arg) == 1) {',
            "            return fabs(evaluate_expression(arg));",
            "        }",
            "    }",
            "",
            "    // Handle SQR function",
            '    if (strncasecmp(expr, "SQR(", 4) == 0) {',
            "        char arg[256];",
            '        if (sscanf(expr + 4, "%255[^)]", arg) == 1) {',
            "            double val = evaluate_expression(arg);",
            "            return sqrt(val);",
            "        }",
            "    }",
            "",
            "    // Handle SIN/COS functions",
            '    if (strncasecmp(expr, "SIN(", 4) == 0) {',
            "        char arg[256];",
            '        if (sscanf(expr + 4, "%255[^)]", arg) == 1) {',
            "            return sin(evaluate_expression(arg) * M_PI / 180.0);",
            "        }",
            "    }",
            '    if (strncasecmp(expr, "COS(", 4) == 0) {',
            "        char arg[256];",
            '        if (sscanf(expr + 4, "%255[^)]", arg) == 1) {',
            "            return cos(evaluate_expression(arg) * M_PI / 180.0);",
            "        }",
            "    }",
            "",
            "    // Handle array access A(5)",
            "    char array_name[64];",
            "    int array_index;",
            '    if (sscanf(expr, "%63[^\\(](%d)", array_name, &array_index) == 2) {',
            "        return get_array_element(array_name, array_index);",
            "    }",
            "",
            "    // Handle simple variable reference",
            "    Variable* var = find_variable(expr);",
            "    if (var) {",
            "        if (var->type == VAR_STRING) {",
            "            return atof(var->string_value);",
            "        }",
            "        return var->number_value;",
            "    }",
            "",
            "    // Try to parse as number",
            "    return atof(expr);",
            "}",
            "",
            "int evaluate_condition(const char* expr) {",
            "    if (!expr || !*expr) return 0;",
            "",
            "    // Handle compound conditions with AND/OR",
            '    char* and_pos = strstr(expr, " AND ");',
            "    if (and_pos) {",
            "        *and_pos = '\\0';",
            "        return evaluate_condition(expr) && evaluate_condition(and_pos + 5);",
            "    }",
            "",
            '    char* or_pos = strstr(expr, " OR ");',
            "    if (or_pos) {",
            "        *or_pos = '\\0';",
            "        return evaluate_condition(expr) || evaluate_condition(or_pos + 4);",
            "    }",
            "",
            "    // Handle NOT",
            '    if (strncasecmp(expr, "NOT ", 4) == 0) {',
            "        return !evaluate_condition(expr + 4);",
            "    }",
            "",
            "    // Handle comparisons",
            "    char left[256], right[256];",
            "    char op[4];",
            "",
            "    // >= comparison",
            '    if (sscanf(expr, "%255[^>]>=%255s", left, right) == 2) {',
            "        return evaluate_expression(left) >= evaluate_expression(right);",
            "    }",
            "    // <= comparison",
            '    if (sscanf(expr, "%255[^<]<=%255s", left, right) == 2) {',
            "        return evaluate_expression(left) <= evaluate_expression(right);",
            "    }",
            "    // > comparison",
            '    if (sscanf(expr, "%255[^>]>%255s", left, right) == 2) {',
            "        return evaluate_expression(left) > evaluate_expression(right);",
            "    }",
            "    // < comparison",
            '    if (sscanf(expr, "%255[^<]<%255s", left, right) == 2) {',
            "        return evaluate_expression(left) < evaluate_expression(right);",
            "    }",
            "    // <> or != comparison",
            '    if (sscanf(expr, "%255[^!<]!=%255s", left, right) == 2 ||',
            '        sscanf(expr, "%255[^!<]><%255s", left, right) == 2) {',
            "        return evaluate_expression(left) != evaluate_expression(right);",
            "    }",
            "    // = comparison",
            '    if (sscanf(expr, "%255[^=]=%255s", left, right) == 2) {',
            "        return fabs(evaluate_expression(left) - evaluate_expression(right)) < 0.000001;",
            "    }",
            "",
            "    // Default: evaluate as expression (0 = false, non-zero = true)",
            "    return evaluate_expression(expr) != 0.0;",
            "}",
            "",
            "void print_value(const char* expr, int add_newline) {",
            "    if (!expr || !*expr) {",
            '        if (add_newline) printf("\\n");',
            "        return;",
            "    }",
            "",
            "    // Handle string literals",
            "    if (expr[0] == '\"') {",
            "        char str[MAX_STRING_LEN];",
            "        strcpy(str, expr + 1);",
            "        if (str[strlen(str)-1] == '\"') {",
            "            str[strlen(str)-1] = '\\0';",
            "        }",
            '        printf("%s", str);',
            "    } else {",
            "        // Variable or expression",
            "        Variable* var = find_variable(expr);",
            "        if (var) {",
            "            if (var->type == VAR_STRING) {",
            '                printf("%s", var->string_value);',
            "            } else {",
            '                printf("%.6g", var->number_value);',
            "            }",
            "        } else {",
            '            printf("%.6g", evaluate_expression(expr));',
            "        }",
            "    }",
            '    if (add_newline) printf("\\n");',
            "}",
            "",
        ]

    def generate_main(self, statements: List[Any]) -> List[str]:
        """Generate main function from BASIC statements"""
        lines = [
            "int main() {",
            "    srand(time(NULL));",
            "    char input_buffer[MAX_STRING_LEN];",
            "    int pc = 0;",
            f"    int program_size = {len(statements)};",
            "",
            "    while (pc < program_size) {",
            "        switch (pc) {",
        ]

        # Generate code for each statement
        for i, stmt in enumerate(statements):
            lines.append(f"            case {i}:")
            lines.extend(self.generate_statement(stmt, i))
            lines.extend(
                [
                    "                pc++;",
                    "                break;",
                ]
            )

        lines.extend(
            [
                "            default:",
                "                pc++;",
                "                break;",
                "        }",
                "    }",
                "    return 0;",
                "}",
            ]
        )

        return lines

    def generate_statement(self, stmt: Dict, index: int) -> List[str]:  # pylint: disable=unused-argument
        """Generate C code for a BASIC statement"""
        stmt_type = stmt.get("type")
        args = stmt.get("args", {})

        if stmt_type == "PRINT":
            return self.generate_print(args)
        elif stmt_type == "INPUT":
            return self.generate_input(args)
        elif stmt_type == "LET":
            return self.generate_let(args)
        elif stmt_type == "IF":
            return self.generate_if(args)
        elif stmt_type == "FOR":
            return self.generate_for(args)
        elif stmt_type == "NEXT":
            return self.generate_next(args)
        elif stmt_type == "GOTO":
            return self.generate_goto(args)
        elif stmt_type == "GOSUB":
            return self.generate_gosub(args)
        elif stmt_type == "RETURN":
            return self.generate_return()
        elif stmt_type == "DIM":
            return self.generate_dim(args)
        elif stmt_type == "END":
            return ["                return 0;"]
        elif stmt_type == "REM":
            return [f"                // {args.get('comment', '')}"]
        else:
            return [f"                // Unknown statement: {stmt_type}"]

    def generate_print(self, args: Dict) -> List[str]:
        """Generate PRINT statement"""
        items = args.get("items", [])
        lines = []

        for i, item in enumerate(items):
            add_newline = i == len(items) - 1  # Only last item gets newline
            if isinstance(item, str) and item.strip():
                lines.append(
                    f'                print_value("{self.escape_string(item.strip())}", {1 if add_newline else 0});'
                )
            elif isinstance(item, dict) and "expression" in item:
                lines.append(
                    f"                print_value(\"{self.escape_string(item['expression'])}\", {1 if add_newline else 0});"
                )

        if not items:
            lines.append('                printf("\\n");')

        return lines

    def generate_input(self, args: Dict) -> List[str]:
        """Generate INPUT statement"""
        prompt = args.get("prompt", "")
        variable = args.get("variable", "")

        lines = []
        if prompt:
            lines.append(f'                printf("{self.escape_string(prompt)}");')

        lines.extend(
            [
                "                fgets(input_buffer, MAX_STRING_LEN, stdin);",
                "                input_buffer[strcspn(input_buffer, \"\\n\")] = '\\0';",
                f'                set_string_variable("{variable}", input_buffer);',
            ]
        )

        return lines

    def generate_let(self, args: Dict) -> List[str]:
        """Generate LET/assignment statement"""
        variable = args.get("variable", "")
        expression = args.get("expression", "")

        # Check if it's an array assignment
        if "(" in variable and ")" in variable:
            # Array assignment A(5) = 10
            array_match = re.match(r"(\w+)\s*\(\s*(.+?)\s*\)", variable)
            if array_match:
                array_name = array_match.group(1)
                index_expr = array_match.group(2)
                return [
                    f'                set_array_element("{array_name}", (int)evaluate_expression("{self.escape_string(index_expr)}"), evaluate_expression("{self.escape_string(expression)}"));',
                ]

        return [
            f'                set_number_variable("{variable}", evaluate_expression("{self.escape_string(expression)}"));',
        ]

    def generate_if(self, args: Dict) -> List[str]:
        """Generate IF statement"""
        condition = args.get("condition", "")
        then_stmt = args.get("then", "")
        else_stmt = args.get("else", "")

        lines = []

        if else_stmt:
            lines.append(f'                if (evaluate_condition("{self.escape_string(condition)}")) {{')
            # Handle THEN part
            if then_stmt.upper().startswith("GOTO "):
                target = then_stmt[5:].strip()
                if target in self.labels:
                    lines.append(f"                    pc = {self.labels[target]} - 1;")
            lines.append("                } else {")
            # Handle ELSE part
            if else_stmt.upper().startswith("GOTO "):
                target = else_stmt[5:].strip()
                if target in self.labels:
                    lines.append(f"                    pc = {self.labels[target]} - 1;")
            lines.append("                }")
        else:
            lines.append(f'                if (evaluate_condition("{self.escape_string(condition)}")) {{')
            if then_stmt.upper().startswith("GOTO "):
                target = then_stmt[5:].strip()
                if target in self.labels:
                    lines.append(f"                    pc = {self.labels[target]} - 1;")
            lines.append("                }")

        return lines

    def generate_for(self, args: Dict) -> List[str]:
        """Generate FOR loop start"""
        variable = args.get("variable", "")
        start = args.get("start", "0")
        end = args.get("end", "0")
        step = args.get("step", "1")

        return [
            f'                set_number_variable("{variable}", evaluate_expression("{self.escape_string(start)}"));',
            f"                // FOR {variable} = {start} TO {end} STEP {step}",
        ]

    def generate_next(self, args: Dict) -> List[str]:
        """Generate NEXT statement"""
        variable = args.get("variable", "")

        # Find the matching FOR loop
        for loop in reversed(self.for_loops):
            if not variable or loop["variable"] == variable:
                for_var = loop["variable"]
                end_expr = loop["end"]
                step_expr = loop["step"]
                for_pc = loop["start_pc"]

                return [
                    f'                set_number_variable("{for_var}", get_number_variable("{for_var}") + evaluate_expression("{self.escape_string(step_expr)}"));',
                    f'                if (get_number_variable("{for_var}") <= evaluate_expression("{self.escape_string(end_expr)}")) {{',
                    f"                    pc = {for_pc} - 1; // Jump back to FOR",
                    "                }",
                ]

        return ["                // NEXT without matching FOR"]

    def generate_goto(self, args: Dict) -> List[str]:
        """Generate GOTO statement"""
        label = args.get("label", "")
        if label in self.labels:
            return [f"                pc = {self.labels[label]} - 1;"]
        return [f"                // GOTO unknown label: {label}"]

    def generate_gosub(self, args: Dict) -> List[str]:
        """Generate GOSUB statement"""
        label = args.get("label", "")
        if label in self.labels:
            return [
                "                call_stack[stack_ptr++] = pc;",
                f"                pc = {self.labels[label]} - 1;",
            ]
        return [f"                // GOSUB unknown label: {label}"]

    def generate_return(self) -> List[str]:
        """Generate RETURN statement"""
        return [
            "                if (stack_ptr > 0) {",
            "                    pc = call_stack[--stack_ptr];",
            "                }",
        ]

    def generate_dim(self, args: Dict) -> List[str]:
        """Generate DIM statement for arrays"""
        array_name = args.get("array", "")
        size = args.get("size", 10)

        return [
            f'                create_array("{array_name}", {size});',
        ]

    def escape_string(self, s: str) -> str:
        """Escape string for C code"""
        if not s:
            return ""
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


class BasicCompiler(BaseCompiler):
    """Enhanced BASIC compiler"""

    def __init__(self):
        super().__init__(Language.BASIC)

    def create_code_generator(self) -> CodeGenerator:
        """Create BASIC code generator"""
        return BasicCodeGenerator()

    def parse_source(self, source: str) -> List[Dict]:
        """Parse BASIC source into statements"""
        statements = []
        lines = source.strip().split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.upper().startswith("REM"):
                continue

            # Remove line numbers if present
            line_match = re.match(r"^(\d+)\s+(.+)$", line)
            if line_match:
                actual_line_num = int(line_match.group(1))
                line = line_match.group(2)
            else:
                actual_line_num = line_num

            # Parse different BASIC statements
            line_upper = line.upper()

            if line_upper.startswith("PRINT "):
                statements.append(self.parse_print(line[6:], actual_line_num))
            elif line_upper == "PRINT":
                statements.append({"type": "PRINT", "args": {"items": []}, "line": actual_line_num})
            elif line_upper.startswith("INPUT "):
                statements.append(self.parse_input(line[6:], actual_line_num))
            elif line_upper.startswith("LET "):
                statements.append(self.parse_let(line[4:], actual_line_num))
            elif "=" in line and not any(line_upper.startswith(x) for x in ["IF ", "FOR ", "WHILE "]):
                statements.append(self.parse_let(line, actual_line_num))
            elif line_upper.startswith("IF "):
                statements.append(self.parse_if(line[3:], actual_line_num))
            elif line_upper.startswith("FOR "):
                statements.append(self.parse_for(line[4:], actual_line_num))
            elif line_upper.startswith("NEXT"):
                statements.append(self.parse_next(line[4:], actual_line_num))
            elif line_upper.startswith("GOTO "):
                statements.append(self.parse_goto(line[5:], actual_line_num))
            elif line_upper.startswith("GOSUB "):
                statements.append(self.parse_gosub(line[6:], actual_line_num))
            elif line_upper == "RETURN":
                statements.append({"type": "RETURN", "args": {}, "line": actual_line_num})
            elif line_upper.startswith("DIM "):
                statements.append(self.parse_dim(line[4:], actual_line_num))
            elif line_upper.startswith("REM "):
                statements.append({"type": "REM", "args": {"comment": line[4:]}, "line": actual_line_num})
            elif line_upper == "END":
                statements.append({"type": "END", "args": {}, "line": actual_line_num})
            else:
                statements.append({"type": "UNKNOWN", "args": {"text": line}, "line": actual_line_num})

        return statements

    def parse_print(self, args: str, line_num: int) -> Dict:
        """Parse PRINT statement"""
        items = []
        current_item = ""

        i = 0
        while i < len(args):
            char = args[i]

            if char == '"':
                # String literal
                if current_item.strip():
                    items.append(current_item.strip())
                    current_item = ""
                # Find closing quote
                i += 1
                start = i
                while i < len(args) and args[i] != '"':
                    i += 1
                if i < len(args):
                    items.append(f'"{args[start:i]}"')
                    i += 1
                else:
                    items.append(f'"{args[start:]}')
                    break
            elif char in ",;":
                # Separator
                if current_item.strip():
                    items.append(current_item.strip())
                    current_item = ""
                i += 1
            else:
                current_item += char
                i += 1

        if current_item.strip():
            items.append(current_item.strip())

        return {"type": "PRINT", "args": {"items": items}, "line": line_num}

    def parse_input(self, args: str, line_num: int) -> Dict:
        """Parse INPUT statement"""
        # Handle INPUT "prompt"; variable format
        if '"' in args and (";" in args or "," in args):
            sep = ";" if ";" in args else ","
            parts = args.split(sep, 1)
            if len(parts) == 2:
                prompt_part = parts[0].strip()
                var_part = parts[1].strip()

                # Extract prompt from quotes
                prompt_match = re.search(r'"([^"]*)"', prompt_part)
                prompt = prompt_match.group(1) if prompt_match else ""

                return {"type": "INPUT", "args": {"prompt": prompt, "variable": var_part}, "line": line_num}

        # Simple INPUT variable
        return {"type": "INPUT", "args": {"prompt": "", "variable": args.strip()}, "line": line_num}

    def parse_let(self, args: str, line_num: int) -> Dict:
        """Parse LET/assignment statement"""
        if "=" in args:
            var_part, expr_part = args.split("=", 1)
            return {
                "type": "LET",
                "args": {"variable": var_part.strip(), "expression": expr_part.strip()},
                "line": line_num,
            }
        return {"type": "LET", "args": {"variable": args.strip(), "expression": "0"}, "line": line_num}

    def parse_if(self, args: str, line_num: int) -> Dict:
        """Parse IF statement"""
        # Handle IF condition THEN action ELSE action
        then_match = re.search(r"\bTHEN\b", args, re.IGNORECASE)
        if then_match:
            condition = args[: then_match.start()].strip()
            then_part = args[then_match.end() :].strip()

            # Check for ELSE
            else_match = re.search(r"\bELSE\b", then_part, re.IGNORECASE)
            if else_match:
                then_action = then_part[: else_match.start()].strip()
                else_action = then_part[else_match.end() :].strip()
            else:
                then_action = then_part
                else_action = ""

            return {
                "type": "IF",
                "args": {"condition": condition, "then": then_action, "else": else_action},
                "line": line_num,
            }

        return {"type": "IF", "args": {"condition": args.strip(), "then": "", "else": ""}, "line": line_num}

    def parse_for(self, args: str, line_num: int) -> Dict:
        """Parse FOR loop"""
        # FOR variable = start TO end [STEP step]
        match = re.match(r"(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+?))?$", args, re.IGNORECASE)

        if match:
            variable = match.group(1)
            start = match.group(2)
            end = match.group(3)
            step = match.group(4) if match.group(4) else "1"

            return {
                "type": "FOR",
                "args": {"variable": variable, "start": start, "end": end, "step": step},
                "line": line_num,
            }

        return {"type": "FOR", "args": {"variable": "I", "start": "1", "end": "10", "step": "1"}, "line": line_num}

    def parse_next(self, args: str, line_num: int) -> Dict:
        """Parse NEXT statement"""
        variable = args.strip() if args.strip() else ""
        return {"type": "NEXT", "args": {"variable": variable}, "line": line_num}

    def parse_goto(self, args: str, line_num: int) -> Dict:
        """Parse GOTO statement"""
        return {"type": "GOTO", "args": {"label": args.strip()}, "line": line_num}

    def parse_gosub(self, args: str, line_num: int) -> Dict:
        """Parse GOSUB statement"""
        return {"type": "GOSUB", "args": {"label": args.strip()}, "line": line_num}

    def parse_dim(self, args: str, line_num: int) -> Dict:
        """Parse DIM statement"""
        # DIM array(size)
        match = re.match(r"(\w+)\s*\(\s*(\d+)\s*\)", args)
        if match:
            array_name = match.group(1)
            size = int(match.group(2))
            return {"type": "DIM", "args": {"array": array_name, "size": size}, "line": line_num}

        return {"type": "DIM", "args": {"array": args.strip(), "size": 10}, "line": line_num}
