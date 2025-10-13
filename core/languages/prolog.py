"""
TW Prolog Language Executor
===========================

Implements TW Prolog, an educational variant of the Prolog logic programming
language for the Time_Warp IDE, focusing on declarative programming concepts.

Language Features:
- Facts: Define relationships and properties (e.g., parent(john, mary).)
- Rules: Define logical implications with conditions
- Queries: Ask questions about defined facts and rules
- Unification: Pattern matching and variable binding
- Backtracking: Automatic search through possible solutions
- Lists: [head|tail] syntax and list operations
- Arithmetic: Basic mathematical operations and comparisons
- Control: Cut (!) operator to control backtracking
- I/O: Basic input/output predicates for console interaction

The executor provides a simplified Prolog-like syntax for learning logic
programming, with support for facts, rules, queries, and basic backtracking.
"""

import re


class TwPrologExecutor:
    """Handles TW Prolog language command execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.database = {}  # Facts and rules database
        self.variables = {}  # Query variables
        self.current_query = None
        self.backtrack_stack = []  # For backtracking
        self.cut_flag = False  # Cut operator

    def execute_command(self, command):
        """Execute a Prolog command and return the result"""
        try:
            command = command.strip()
            if not command:
                return "continue"

            # Remove trailing period if present
            if command.endswith("."):
                command = command[:-1].strip()

            parts = command.split()
            if not parts:
                return "continue"

            cmd = parts[0].upper()

            # Fact/rule definition
            if ":-" in command:
                return self._handle_rule(command)
            elif command.startswith("?-"):
                return self._handle_query(command)
            elif "(" in command and ")" in command:
                # Likely a fact
                return self._handle_fact(command)
            elif cmd in ["LISTING", "LISTING."]:
                return self._handle_listing()
            elif cmd in ["TRACE", "TRACE."]:
                return self._handle_trace()
            elif cmd in ["NOTRACE", "NOTRACE."]:
                return self._handle_notrace()

        except Exception as e:
            self.interpreter.debug_output(f"Prolog command error: {e}")
            return "continue"

        return "continue"

    def _handle_fact(self, command):
        """Handle fact definition"""
        try:
            # fact(arg1, arg2, ...).
            match = re.match(r"(\w+)\s*\((.*?)\)", command)
            if match:
                predicate = match.group(1)
                args_str = match.group(2)

                # Parse arguments
                args = self._parse_arguments(args_str)

                # Store fact
                if predicate not in self.database:
                    self.database[predicate] = []

                self.database[predicate].append({"type": "fact", "args": args})

                self.interpreter.log_output(
                    f"📚 Fact added: {predicate}({', '.join(map(str, args))})"
                )
        except Exception as e:
            self.interpreter.debug_output(f"Fact definition error: {e}")
        return "continue"

    def _handle_rule(self, command):
        """Handle rule definition"""
        try:
            # head :- body.
            if ":-" in command:
                head_part, body_part = command.split(":-", 1)
                head_part = head_part.strip()
                body_part = body_part.strip()

                # Parse head
                head_match = re.match(r"(\w+)\s*\((.*?)\)", head_part)
                if head_match:
                    predicate = head_match.group(1)
                    head_args = self._parse_arguments(head_match.group(2))

                    # Parse body (can be multiple goals separated by commas)
                    goals = [goal.strip() for goal in body_part.split(",")]

                    # Store rule
                    if predicate not in self.database:
                        self.database[predicate] = []

                    self.database[predicate].append(
                        {"type": "rule", "head_args": head_args, "body": goals}
                    )

                    self.interpreter.log_output(
                        f"📋 Rule added: {predicate}({', '.join(map(str, head_args))}) "
                        f":- {', '.join(goals)}"
                    )
        except Exception as e:
            self.interpreter.debug_output(f"Rule definition error: {e}")
        return "continue"

    def _handle_query(self, command):
        """Handle query execution"""
        try:
            # ?- goal1, goal2, ...
            if command.startswith("?-"):
                query_part = command[2:].strip()

                # Parse goals
                goals = [goal.strip() for goal in query_part.split(",")]

                # Execute query
                results = self._execute_query(goals)

                if results:
                    self.interpreter.log_output("✅ Query succeeded")
                    for result in results[:5]:  # Limit output
                        if result:
                            var_bindings = [f"{k} = {v}" for k, v in result.items()]
                            self.interpreter.log_output(f"   {', '.join(var_bindings)}")
                    if len(results) > 5:
                        self.interpreter.log_output(
                            f"   ... and {len(results) - 5} more solutions"
                        )
                else:
                    self.interpreter.log_output("❌ Query failed - no solutions found")
        except Exception as e:
            self.interpreter.debug_output(f"Query execution error: {e}")
        return "continue"

    def _handle_listing(self):
        """Handle LISTING command - show database contents"""
        try:
            self.interpreter.log_output("📚 Prolog Database Contents:")
            for predicate, clauses in self.database.items():
                self.interpreter.log_output(f"\n{predicate}:")
                for clause in clauses:
                    if clause["type"] == "fact":
                        args_str = ", ".join(map(str, clause["args"]))
                        self.interpreter.log_output(f"  {predicate}({args_str}).")
                    elif clause["type"] == "rule":
                        head_args_str = ", ".join(map(str, clause["head_args"]))
                        body_str = ", ".join(clause["body"])
                        self.interpreter.log_output(
                            f"  {predicate}({head_args_str}) :- {body_str}."
                        )
        except Exception as e:
            self.interpreter.debug_output(f"Listing error: {e}")
        return "continue"

    def _handle_trace(self):
        """Handle TRACE command"""
        self.interpreter.log_output("🔍 Tracing enabled")
        return "continue"

    def _handle_notrace(self):
        """Handle NOTRACE command"""
        self.interpreter.log_output("🔍 Tracing disabled")
        return "continue"

    def _parse_arguments(self, args_str):
        """Parse argument list from string"""
        args = []
        current_arg = ""
        in_brackets = 0
        in_quotes = False

        i = 0
        while i < len(args_str):
            char = args_str[i]

            if char == '"' and (i == 0 or args_str[i - 1] != "\\"):
                in_quotes = not in_quotes
                current_arg += char
            elif char == "[" and not in_quotes:
                in_brackets += 1
                current_arg += char
            elif char == "]" and not in_quotes:
                in_brackets -= 1
                current_arg += char
            elif char == "," and not in_quotes and in_brackets == 0:
                if current_arg.strip():
                    args.append(self._parse_term(current_arg.strip()))
                    current_arg = ""
            else:
                current_arg += char

            i += 1

        if current_arg.strip():
            args.append(self._parse_term(current_arg.strip()))

        return args

    def _parse_term(self, term_str):
        """Parse a single term"""
        term_str = term_str.strip()

        # Variable (starts with uppercase or _)
        if re.match(r"^[A-Z_]\w*$", term_str):
            return {"type": "variable", "name": term_str}

        # List [a,b,c]
        elif term_str.startswith("[") and term_str.endswith("]"):
            list_content = term_str[1:-1]
            if not list_content.strip():
                return {"type": "list", "elements": []}
            elements = self._parse_arguments(list_content)
            return {"type": "list", "elements": elements}

        # String "text"
        elif term_str.startswith('"') and term_str.endswith('"'):
            return {"type": "string", "value": term_str[1:-1]}

        # Number
        elif re.match(r"^-?\d+(\.\d+)?$", term_str):
            if "." in term_str:
                return {"type": "number", "value": float(term_str)}
            else:
                return {"type": "number", "value": int(term_str)}

        # Atom (starts with lowercase)
        else:
            return {"type": "atom", "name": term_str}

    def _execute_query(self, goals):
        """Execute a query with backtracking"""
        self.variables = {}
        self.backtrack_stack = []
        self.cut_flag = False

        return self._prove_goals(goals, 0, {})

    def _prove_goals(self, goals, goal_index, bindings):
        """Prove a list of goals using backtracking"""
        if goal_index >= len(goals):
            # All goals proved
            return [bindings.copy()]

        goal = goals[goal_index]
        solutions = []

        # Try to prove current goal
        goal_solutions = self._prove_goal(goal, bindings)

        for solution_bindings in goal_solutions:
            # Merge bindings
            new_bindings = bindings.copy()
            new_bindings.update(solution_bindings)

            # Recursively prove remaining goals
            remaining_solutions = self._prove_goals(goals, goal_index + 1, new_bindings)
            solutions.extend(remaining_solutions)

            if self.cut_flag:
                break

        return solutions

    def _prove_goal(self, goal, bindings):
        """Prove a single goal"""
        # Parse goal
        match = re.match(r"(\w+)\s*\((.*?)\)", goal)
        if not match:
            # Built-in predicates
            return self._prove_builtin(goal, bindings)

        predicate = match.group(1)
        args_str = match.group(2)
        args = self._parse_arguments(args_str)

        solutions = []

        # Apply current bindings to args
        bound_args = self._apply_bindings(args, bindings)

        # Look up predicate in database
        if predicate in self.database:
            for clause in self.database[predicate]:
                if clause["type"] == "fact":
                    # Try to unify with fact
                    fact_args = clause["args"]
                    unification = self._unify(bound_args, fact_args, bindings.copy())
                    if unification is not None:
                        solutions.append(unification)

                elif clause["type"] == "rule":
                    # Try to prove rule body
                    rule_bindings = self._unify(
                        bound_args, clause["head_args"], bindings.copy()
                    )
                    if rule_bindings is not None:
                        # Prove rule body
                        body_solutions = self._prove_goals(
                            clause["body"], 0, rule_bindings
                        )
                        solutions.extend(body_solutions)

        return solutions

    def _prove_builtin(self, goal, bindings):
        """Prove built-in predicates"""
        goal = goal.strip()

        # write/1 - output
        if goal.startswith("write(") and goal.endswith(")"):
            arg_str = goal[6:-1].strip()
            arg = self._parse_term(arg_str)
            bound_arg = self._apply_bindings_to_term(arg, bindings)
            if bound_arg["type"] == "string":
                self.interpreter.log_output(bound_arg["value"])
            else:
                self.interpreter.log_output(str(bound_arg))
            return [bindings]

        # nl/0 - newline
        elif goal == "nl":
            self.interpreter.log_output("")
            return [bindings]

        # Arithmetic comparisons
        elif " =:= " in goal or r" =\= " in goal or " < " in goal or " > " in goal:
            return self._prove_arithmetic(goal, bindings)

        # List operations
        elif goal.startswith("member(") and goal.endswith(")"):
            return self._prove_member(goal, bindings)

        # Fail predicate
        elif goal == "fail":
            return []

        # True predicate
        elif goal == "true":
            return [bindings]

        return []

    def _prove_arithmetic(self, goal, bindings):
        """Prove arithmetic comparisons"""
        try:
            # Simple arithmetic evaluation
            expr = goal.replace("=\\=", "!=").replace("=:", "==")
            bound_expr = self._apply_bindings_to_expression(expr, bindings)

            # Safe evaluation
            allowed_names = {
                "abs": abs,
                "round": round,
                "int": int,
                "float": float,
                "max": max,
                "min": min,
                "sin": __import__("math").sin,
                "cos": __import__("math").cos,
                "sqrt": __import__("math").sqrt,
            }

            safe_dict = {"__builtins__": {}}
            safe_dict.update(allowed_names)

            result = eval(bound_expr, safe_dict)
            if result:
                return [bindings]
        except:
            pass
        return []

    def _prove_member(self, goal, bindings):
        """Prove member/2 predicate"""
        try:
            args_str = goal[7:-1]  # Remove member(
            args = self._parse_arguments(args_str)
            if len(args) == 2:
                element = self._apply_bindings_to_term(args[0], bindings)
                list_term = self._apply_bindings_to_term(args[1], bindings)

                if list_term["type"] == "list":
                    for item in list_term["elements"]:
                        unification = self._unify_terms(element, item, bindings.copy())
                        if unification is not None:
                            return [unification]
        except:
            pass
        return []

    def _unify(self, args1, args2, bindings):
        """Unify two argument lists"""
        if len(args1) != len(args2):
            return None

        result_bindings = bindings.copy()

        for arg1, arg2 in zip(args1, args2):
            unified = self._unify_terms(arg1, arg2, result_bindings)
            if unified is None:
                return None
            result_bindings = unified

        return result_bindings

    def _unify_terms(self, term1, term2, bindings):
        """Unify two terms"""
        # Apply existing bindings
        term1 = self._apply_bindings_to_term(term1, bindings)
        term2 = self._apply_bindings_to_term(term2, bindings)

        # Both variables
        if term1["type"] == "variable" and term2["type"] == "variable":
            if term1["name"] == term2["name"]:
                return bindings
            # Create binding
            new_bindings = bindings.copy()
            new_bindings[term1["name"]] = term2
            return new_bindings

        # First is variable
        elif term1["type"] == "variable":
            if self._occurs_check(term1["name"], term2, bindings):
                return None  # Occurs check failed
            new_bindings = bindings.copy()
            new_bindings[term1["name"]] = term2
            return new_bindings

        # Second is variable
        elif term2["type"] == "variable":
            if self._occurs_check(term2["name"], term1, bindings):
                return None  # Occurs check failed
            new_bindings = bindings.copy()
            new_bindings[term2["name"]] = term1
            return new_bindings

        # Both constants - check equality
        else:
            if term1 == term2:
                return bindings

        return None

    def _occurs_check(self, var_name, term, bindings):
        """Check if variable occurs in term (prevent circular bindings)"""
        if term["type"] == "variable":
            if term["name"] == var_name:
                return True
            if term["name"] in bindings:
                return self._occurs_check(var_name, bindings[term["name"]], bindings)
        elif term["type"] == "list":
            for element in term["elements"]:
                if self._occurs_check(var_name, element, bindings):
                    return True
        return False

    def _apply_bindings(self, args, bindings):
        """Apply bindings to argument list"""
        return [self._apply_bindings_to_term(arg, bindings) for arg in args]

    def _apply_bindings_to_term(self, term, bindings):
        """Apply bindings to a single term"""
        if term["type"] == "variable" and term["name"] in bindings:
            return self._apply_bindings_to_term(bindings[term["name"]], bindings)
        elif term["type"] == "list":
            return {
                "type": "list",
                "elements": [
                    self._apply_bindings_to_term(elem, bindings)
                    for elem in term["elements"]
                ],
            }
        else:
            return term

    def _apply_bindings_to_expression(self, expr, bindings):
        """Apply bindings to arithmetic expression"""
        for var_name, var_term in bindings.items():
            if var_term["type"] in ["number"]:
                expr = expr.replace(var_name, str(var_term["value"]))
        return expr
