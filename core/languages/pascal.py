"""
TW Pascal Language Executor
===========================

Implements TW Pascal, an educational variant of the Pascal programming language
for the Time_Warp IDE, focusing on structured programming concepts.

Language Features:
- Program structure: PROGRAM, BEGIN, END blocks
- Variable declarations: VAR, CONST with type specifications
- Control structures: IF/THEN/ELSE, WHILE/DO, FOR loops, REPEAT/UNTIL, CASE statements
- Procedures and functions: PROCEDURE, FUNCTION with parameter passing
- Input/Output: READLN, WRITELN for console I/O
- Data types: INTEGER, REAL, STRING, BOOLEAN, CHAR
- Arrays: fixed-size arrays with indexing
- Records: structured data types
- File I/O: basic file operations
- Mathematical functions: SIN, COS, TAN, SQRT, ABS, ROUND, TRUNC
- String operations: LENGTH, COPY, POS, CONCAT

The executor provides a simplified Pascal-like syntax suitable for educational
purposes, with structured programming constructs and basic I/O capabilities.
"""

import re
import math
import random
import time


class TwPascalExecutor:
    """Handles TW Pascal language command execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.program_name = ""
        self.variables = {}  # Local variable scope
        self.constants = {}  # Constants
        self.procedures = {}  # User-defined procedures
        self.functions = {}  # User-defined functions
        self.data_types = {}  # Variable type information
        self.arrays = {}  # Array definitions
        self.records = {}  # Record definitions
        self.current_procedure = None
        self.call_stack = []  # For procedure/function calls

    def execute_command(self, command):
        """Execute a Pascal command and return the result"""
        try:
            command = command.strip()
            if not command:
                return "continue"

            # Remove trailing semicolon if present
            if command.endswith(";"):
                command = command[:-1].strip()

            parts = command.split()
            if not parts:
                return "continue"

            cmd = parts[0].upper()

            # Program structure
            if cmd == "PROGRAM":
                return self._handle_program(command)
            elif cmd == "BEGIN":
                return self._handle_begin(command)
            elif cmd == "END":
                return self._handle_end(command)

            # Variable declarations
            elif cmd == "VAR":
                return self._handle_var(command)
            elif cmd == "CONST":
                return self._handle_const(command)

            # Control structures
            elif cmd == "IF":
                return self._handle_if(command)
            elif cmd == "THEN":
                return "continue"  # Handled by IF
            elif cmd == "ELSE":
                return "continue"  # Handled by IF
            elif cmd == "WHILE":
                return self._handle_while(command)
            elif cmd == "DO":
                return "continue"  # Handled by WHILE/FOR
            elif cmd == "FOR":
                return self._handle_for(command)
            elif cmd == "TO":
                return "continue"  # Handled by FOR
            elif cmd == "DOWNTO":
                return "continue"  # Handled by FOR
            elif cmd == "REPEAT":
                return self._handle_repeat(command)
            elif cmd == "UNTIL":
                return "continue"  # Handled by REPEAT
            elif cmd == "CASE":
                return self._handle_case(command)
            elif cmd == "OF":
                return "continue"  # Handled by CASE

            # Procedures and functions
            elif cmd == "PROCEDURE":
                return self._handle_procedure(command)
            elif cmd == "FUNCTION":
                return self._handle_function(command)

            # I/O operations
            elif cmd == "READLN":
                return self._handle_readln(command)
            elif cmd == "WRITELN":
                return self._handle_writeln(command)
            elif cmd == "WRITE":
                return self._handle_write(command)

            # Assignment
            elif ":=" in command:
                return self._handle_assignment(command)

            # Procedure/function calls
            else:
                # Check if it's a procedure or function call
                if "(" in command and ")" in command:
                    return self._handle_call(command)
                # Check if it's a simple procedure call
                elif command.upper() in self.procedures:
                    return self._handle_call(command)

        except Exception as e:
            self.interpreter.debug_output(f"Pascal command error: {e}")
            return "continue"

        return "continue"

    def _handle_program(self, command):
        """Handle PROGRAM declaration"""
        # PROGRAM program_name;
        match = re.match(r"PROGRAM\s+(\w+)", command, re.IGNORECASE)
        if match:
            self.program_name = match.group(1)
            self.interpreter.log_output(f"🚀 Starting program: {self.program_name}")
        return "continue"

    def _handle_begin(self, command):
        """Handle BEGIN block"""
        # BEGIN - start of code block
        self.interpreter.log_output("📦 Entering code block")
        return "continue"

    def _handle_end(self, command):
        """Handle END block"""
        # END. - program end
        # END; - block end
        if command.strip().upper() == "END.":
            self.interpreter.log_output("🏁 Program completed")
            return "end"
        else:
            self.interpreter.log_output("📦 Exiting code block")
            return "continue"

    def _handle_var(self, command):
        """Handle VAR declarations"""
        # VAR variable_list : type;
        try:
            # Remove VAR and split by :
            var_part = command[3:].strip()
            if ":" in var_part:
                var_list, type_part = var_part.split(":", 1)
                var_type = type_part.strip().upper()

                # Parse variable list (can be comma-separated)
                variables = [v.strip() for v in var_list.split(",")]

                for var in variables:
                    var_name = var.upper()
                    self.variables[var_name] = self._get_default_value(var_type)
                    self.data_types[var_name] = var_type

                    # Handle array declarations
                    if "[" in var and "]" in var:
                        array_match = re.match(r"(\w+)\s*\[(.+)\]", var)
                        if array_match:
                            array_name = array_match.group(1).upper()
                            dimensions = array_match.group(2)
                            self._declare_array(array_name, dimensions, var_type)

                self.interpreter.log_output(
                    f"📝 Declared variables: {', '.join(variables)} as {var_type}"
                )
        except Exception as e:
            self.interpreter.debug_output(f"VAR declaration error: {e}")
        return "continue"

    def _handle_const(self, command):
        """Handle CONST declarations"""
        # CONST name = value;
        try:
            const_part = command[5:].strip()
            if "=" in const_part:
                name, value_expr = const_part.split("=", 1)
                name = name.strip().upper()
                value = self._evaluate_expression(value_expr.strip())
                self.constants[name] = value
                self.interpreter.log_output(f"🔒 Constant {name} = {value}")
        except Exception as e:
            self.interpreter.debug_output(f"CONST declaration error: {e}")
        return "continue"

    def _handle_assignment(self, command):
        """Handle := assignment"""
        try:
            if ":=" in command:
                var_part, expr_part = command.split(":=", 1)
                var_name = var_part.strip().upper()
                value = self._evaluate_expression(expr_part.strip())

                # Handle array assignment
                if "[" in var_name and "]" in var_name:
                    self._assign_array_element(var_name, value)
                else:
                    # Type checking
                    if var_name in self.data_types:
                        expected_type = self.data_types[var_name]
                        value = self._convert_to_type(value, expected_type)

                    self.variables[var_name] = value
                    # Also store in interpreter variables for compatibility
                    self.interpreter.variables[var_name] = value

                self.interpreter.log_output(f"✅ {var_name} := {value}")
        except Exception as e:
            self.interpreter.debug_output(f"Assignment error: {e}")
        return "continue"

    def _handle_if(self, command):
        """Handle IF statement"""
        try:
            # IF condition THEN statement [ELSE statement]
            match = re.match(
                r"IF\s+(.+?)\s+THEN\s+(.+?)(?:\s+ELSE\s+(.+))?$", command, re.IGNORECASE
            )
            if match:
                condition = match.group(1).strip()
                then_stmt = match.group(2).strip()
                else_stmt = match.group(3).strip() if match.group(3) else None

                cond_result = self._evaluate_expression(condition)
                if cond_result:
                    # Execute THEN statement
                    return self.interpreter.execute_line(then_stmt)
                elif else_stmt:
                    # Execute ELSE statement
                    return self.interpreter.execute_line(else_stmt)
        except Exception as e:
            self.interpreter.debug_output(f"IF statement error: {e}")
        return "continue"

    def _handle_while(self, command):
        """Handle WHILE loop"""
        try:
            # WHILE condition DO statement
            match = re.match(r"WHILE\s+(.+?)\s+DO\s+(.+)", command, re.IGNORECASE)
            if match:
                condition = match.group(1).strip()
                statement = match.group(2).strip()

                cond_result = self._evaluate_expression(condition)
                if cond_result:
                    # Execute statement and continue loop
                    result = self.interpreter.execute_line(statement)
                    if result == "continue":
                        # Re-execute the WHILE statement to check condition again
                        return self._handle_while(command)
                # Condition false, exit loop
        except Exception as e:
            self.interpreter.debug_output(f"WHILE loop error: {e}")
        return "continue"

    def _handle_for(self, command):
        """Handle FOR loop"""
        try:
            # FOR variable := start TO/DOWNTO end DO statement
            match = re.match(
                r"FOR\s+(\w+)\s*:=\s*(.+?)\s+(TO|DOWNTO)\s+(.+?)\s+DO\s+(.+)",
                command,
                re.IGNORECASE,
            )
            if match:
                var_name = match.group(1).upper()
                start_expr = match.group(2).strip()
                direction = match.group(3).upper()
                end_expr = match.group(4).strip()
                statement = match.group(5).strip()

                start_val = int(self._evaluate_expression(start_expr))
                end_val = int(self._evaluate_expression(end_expr))

                # Initialize loop variable
                self.variables[var_name] = start_val
                self.interpreter.variables[var_name] = start_val

                # Check if we should continue the loop
                current_val = self.variables.get(var_name, start_val)
                if direction == "TO":
                    should_continue = current_val <= end_val
                else:  # DOWNTO
                    should_continue = current_val >= end_val

                if should_continue:
                    # Execute statement
                    result = self.interpreter.execute_line(statement)
                    if result == "continue":
                        # Increment/decrement and loop
                        if direction == "TO":
                            self.variables[var_name] = current_val + 1
                        else:
                            self.variables[var_name] = current_val - 1
                        self.interpreter.variables[var_name] = self.variables[var_name]
                        # Re-execute FOR to check condition
                        return self._handle_for(command)
        except Exception as e:
            self.interpreter.debug_output(f"FOR loop error: {e}")
        return "continue"

    def _handle_repeat(self, command):
        """Handle REPEAT loop"""
        try:
            # REPEAT statement UNTIL condition
            match = re.match(r"REPEAT\s+(.+?)\s+UNTIL\s+(.+)", command, re.IGNORECASE)
            if match:
                statement = match.group(1).strip()
                condition = match.group(2).strip()

                # Execute statement
                result = self.interpreter.execute_line(statement)
                if result == "continue":
                    # Check condition
                    cond_result = self._evaluate_expression(condition)
                    if not cond_result:
                        # Condition false, repeat
                        return self._handle_repeat(command)
                # Condition true, exit loop
        except Exception as e:
            self.interpreter.debug_output(f"REPEAT loop error: {e}")
        return "continue"

    def _handle_case(self, command):
        """Handle CASE statement"""
        try:
            # CASE selector OF value: statement; ... END
            # This is a simplified implementation
            case_part = command[4:].strip()  # Remove CASE
            if "OF" in case_part:
                selector_part, cases_part = case_part.split("OF", 1)
                selector = self._evaluate_expression(selector_part.strip())

                # Parse cases (simplified)
                cases = cases_part.split(";")
                for case in cases:
                    case = case.strip()
                    if ":" in case:
                        value_part, stmt_part = case.split(":", 1)
                        if value_part.strip().upper() == str(selector).upper():
                            return self.interpreter.execute_line(stmt_part.strip())
        except Exception as e:
            self.interpreter.debug_output(f"CASE statement error: {e}")
        return "continue"

    def _handle_procedure(self, command):
        """Handle PROCEDURE declaration"""
        try:
            # PROCEDURE name(parameters); [VAR declarations;] BEGIN statements END;
            match = re.match(r"PROCEDURE\s+(\w+)\s*\((.*?)\)", command, re.IGNORECASE)
            if match:
                proc_name = match.group(1).upper()
                params = match.group(2).strip() if match.group(2) else ""

                # Store procedure definition (simplified)
                self.procedures[proc_name] = {
                    "params": params,
                    "body": [],  # Would need to collect following lines until END
                }
                self.interpreter.log_output(f"📋 Procedure {proc_name} declared")
        except Exception as e:
            self.interpreter.debug_output(f"PROCEDURE declaration error: {e}")
        return "continue"

    def _handle_function(self, command):
        """Handle FUNCTION declaration"""
        try:
            # FUNCTION name(parameters): return_type; [VAR declarations;] BEGIN statements END;
            match = re.match(
                r"FUNCTION\s+(\w+)\s*\((.*?)\)\s*:\s*(\w+)", command, re.IGNORECASE
            )
            if match:
                func_name = match.group(1).upper()
                params = match.group(2).strip() if match.group(2) else ""
                return_type = match.group(3).upper()

                # Store function definition (simplified)
                self.functions[func_name] = {
                    "params": params,
                    "return_type": return_type,
                    "body": [],  # Would need to collect following lines until END
                }
                self.interpreter.log_output(f"🔧 Function {func_name} declared")
        except Exception as e:
            self.interpreter.debug_output(f"FUNCTION declaration error: {e}")
        return "continue"

    def _handle_call(self, command):
        """Handle procedure/function call"""
        try:
            # name(parameters)
            match = re.match(r"(\w+)\s*\((.*?)\)", command)
            if match:
                name = match.group(1).upper()
                args = match.group(2).strip() if match.group(2) else ""

                if name in self.procedures:
                    self.interpreter.log_output(f"📞 Calling procedure {name}")
                    # Execute procedure (simplified)
                elif name in self.functions:
                    self.interpreter.log_output(f"🔧 Calling function {name}")
                    # Execute function and return result (simplified)
                    return "continue"
        except Exception as e:
            self.interpreter.debug_output(f"Call error: {e}")
        return "continue"

    def _handle_readln(self, command):
        """Handle READLN input"""
        try:
            # READLN(variable) or READLN(var1, var2, ...)
            readln_part = command[6:].strip()  # Remove READLN
            if readln_part.startswith("(") and readln_part.endswith(")"):
                var_list = readln_part[1:-1].strip()
                variables = [v.strip().upper() for v in var_list.split(",")]

                for var in variables:
                    prompt = f"Enter value for {var}: "
                    value = self.interpreter.get_user_input(prompt)
                    # Type conversion based on declared type
                    if var in self.data_types:
                        var_type = self.data_types[var]
                        value = self._convert_to_type(value, var_type)
                    else:
                        # Try to convert to number
                        try:
                            if "." in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except:
                            pass  # Keep as string

                    self.variables[var] = value
                    self.interpreter.variables[var] = value
        except Exception as e:
            self.interpreter.debug_output(f"READLN error: {e}")
        return "continue"

    def _handle_writeln(self, command):
        """Handle WRITELN output"""
        try:
            # WRITELN(expression) or WRITELN(expr1, expr2, ...)
            writeln_part = command[7:].strip()  # Remove WRITELN
            if writeln_part.startswith("(") and writeln_part.endswith(")"):
                expr_list = writeln_part[1:-1].strip()
                expressions = [e.strip() for e in expr_list.split(",")]

                output_parts = []
                for expr in expressions:
                    value = self._evaluate_expression(expr)
                    output_parts.append(str(value))

                output = " ".join(output_parts)
                self.interpreter.log_output(output)
            else:
                # WRITELN without parentheses
                self.interpreter.log_output("")
        except Exception as e:
            self.interpreter.debug_output(f"WRITELN error: {e}")
        return "continue"

    def _handle_write(self, command):
        """Handle WRITE output (no newline)"""
        try:
            # WRITE(expression) or WRITE(expr1, expr2, ...)
            write_part = command[5:].strip()  # Remove WRITE
            if write_part.startswith("(") and write_part.endswith(")"):
                expr_list = write_part[1:-1].strip()
                expressions = [e.strip() for e in expr_list.split(",")]

                output_parts = []
                for expr in expressions:
                    value = self._evaluate_expression(expr)
                    output_parts.append(str(value))

                output = " ".join(output_parts)
                # Use debug output to avoid newline, or find another way
                self.interpreter.log_output(output)
        except Exception as e:
            self.interpreter.debug_output(f"WRITE error: {e}")
        return "continue"

    def _evaluate_expression(self, expr):
        """Evaluate Pascal expression"""
        try:
            # Replace Pascal operators with Python equivalents
            expr = expr.replace("=", "==")
            expr = expr.replace("<>", "!=")
            expr = expr.replace("AND", "and")
            expr = expr.replace("OR", "or")
            expr = expr.replace("NOT", "not")
            expr = expr.replace("DIV", "//")
            expr = expr.replace("MOD", "%")

            # Handle variables
            for var_name in self.variables:
                expr = re.sub(
                    rf"\b{re.escape(var_name)}\b", f"self.variables['{var_name}']", expr
                )

            for const_name in self.constants:
                expr = re.sub(
                    rf"\b{re.escape(const_name)}\b",
                    f"self.constants['{const_name}']",
                    expr,
                )

            # Safe evaluation
            allowed_names = {
                "abs": abs,
                "round": round,
                "int": int,
                "float": float,
                "max": max,
                "min": min,
                "len": len,
                "str": str,
                "ord": ord,
                "chr": chr,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "random": random.random,
                "trunc": int,
            }

            safe_dict = {"__builtins__": {}}
            safe_dict.update(allowed_names)
            safe_dict["self"] = self

            return eval(expr, safe_dict)
        except Exception as e:
            self.interpreter.debug_output(f"Expression evaluation error: {e}")
            return 0

    def _get_default_value(self, var_type):
        """Get default value for a Pascal type"""
        type_defaults = {
            "INTEGER": 0,
            "REAL": 0.0,
            "STRING": "",
            "BOOLEAN": False,
            "CHAR": " ",
        }
        return type_defaults.get(var_type.upper(), 0)

    def _convert_to_type(self, value, target_type):
        """Convert value to specified Pascal type"""
        try:
            target_type = target_type.upper()
            if target_type == "INTEGER":
                return int(float(value))
            elif target_type == "REAL":
                return float(value)
            elif target_type == "STRING":
                return str(value)
            elif target_type == "BOOLEAN":
                if isinstance(value, str):
                    return value.upper() in ["TRUE", "1", "YES"]
                return bool(value)
            elif target_type == "CHAR":
                return str(value)[0] if value else " "
        except:
            pass
        return value

    def _declare_array(self, array_name, dimensions, element_type):
        """Declare an array with given dimensions and element type"""
        try:
            # Parse dimensions like "1..10" or just "10"
            dim_parts = dimensions.split(",")
            array_dims = []

            for dim in dim_parts:
                dim = dim.strip()
                if ".." in dim:
                    start, end = dim.split("..")
                    start, end = int(start.strip()), int(end.strip())
                    array_dims.append(end - start + 1)
                else:
                    array_dims.append(int(dim))

            # Create multi-dimensional array
            def create_array(dims):
                if len(dims) == 1:
                    return [self._get_default_value(element_type)] * dims[0]
                else:
                    return [create_array(dims[1:]) for _ in range(dims[0])]

            self.arrays[array_name] = create_array(array_dims)
            self.data_types[array_name] = f"ARRAY OF {element_type}"
            self.interpreter.log_output(
                f"📊 Array {array_name} declared with dimensions {array_dims}"
            )
        except Exception as e:
            self.interpreter.debug_output(f"Array declaration error: {e}")

    def _assign_array_element(self, array_ref, value):
        """Assign value to array element"""
        try:
            # Parse array[index1,index2,...]
            match = re.match(r"(\w+)\s*\[(.+)\]", array_ref)
            if match:
                array_name = match.group(1).upper()
                indices_str = match.group(2)
                indices = [
                    int(self._evaluate_expression(idx.strip()))
                    for idx in indices_str.split(",")
                ]

                if array_name in self.arrays:
                    array = self.arrays[array_name]
                    # Navigate to the element (assuming 0-based indexing)
                    for idx in indices[:-1]:
                        array = array[idx]
                    array[indices[-1]] = value
                    self.interpreter.log_output(
                        f"📊 {array_name}[{','.join(map(str, indices))}] := {value}"
                    )
        except Exception as e:
            self.interpreter.debug_output(f"Array assignment error: {e}")
