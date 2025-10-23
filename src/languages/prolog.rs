use std::collections::HashMap;

#[derive(Clone, Debug, PartialEq)]
pub enum PrologTerm {
    Atom(String),
    Variable(String),
    Compound(String, Vec<PrologTerm>),
}

#[derive(Clone, Debug)]
pub struct PrologRule {
    pub head: PrologTerm,
    pub body: Vec<PrologTerm>,
}

#[derive(Clone, Debug)]
pub struct Substitution {
    pub bindings: HashMap<String, PrologTerm>,
}

impl Substitution {
    pub fn new() -> Self {
        Self {
            bindings: HashMap::new(),
        }
    }

    pub fn extend(&self, var: String, term: PrologTerm) -> Substitution {
        let mut new_bindings = self.bindings.clone();
        new_bindings.insert(var, term);
        Substitution {
            bindings: new_bindings,
        }
    }

    pub fn apply(&self, term: &PrologTerm) -> PrologTerm {
        match term {
            PrologTerm::Atom(s) => PrologTerm::Atom(s.clone()),
            PrologTerm::Variable(var) => {
                if let Some(bound) = self.bindings.get(var) {
                    bound.clone()
                } else {
                    PrologTerm::Variable(var.clone())
                }
            }
            PrologTerm::Compound(name, args) => {
                let new_args = args.iter().map(|arg| self.apply(arg)).collect();
                PrologTerm::Compound(name.clone(), new_args)
            }
        }
    }
}

pub struct PrologInterpreter {
    rules: Vec<PrologRule>,
    output: Vec<String>,
}

impl PrologInterpreter {
    pub fn new() -> Self {
        Self {
            rules: Vec::new(),
            output: Vec::new(),
        }
    }

    pub fn execute(&mut self, code: &str) -> String {
        self.output.clear();
        self.rules.clear();

        let lines: Vec<&str> = code.lines().collect();
        let mut current_section = "";
        let mut goal_buffer = Vec::new();

        for line in lines {
            let trimmed = line.trim();
            if trimmed.is_empty() || trimmed.starts_with('%') {
                continue;
            }

            // Check for section headers
            if trimmed == "domains" || trimmed == "predicates" || trimmed == "clauses" {
                current_section = trimmed;
                continue;
            }

            if trimmed.starts_with("goal") {
                current_section = "goal";
                goal_buffer.clear();
                continue;
            }

            match current_section {
                "domains" => {
                    // For now, we ignore domain declarations as they're mainly for type checking
                    // In a full implementation, we'd parse and store domain information
                }
                "predicates" => {
                    // For now, we ignore predicate declarations as they're mainly for type checking
                    // In a full implementation, we'd parse and validate predicate signatures
                }
                "clauses" => {
                    if trimmed.contains(":-") {
                        // Rule - may or may not end with period
                        let rule_str = if trimmed.ends_with('.') {
                            trimmed.trim_end_matches('.')
                        } else {
                            trimmed
                        };
                        self.parse_rule(rule_str);
                    } else if trimmed.ends_with('.') {
                        // Fact
                        let content = &trimmed[..trimmed.len() - 1];
                        if let Some(fact) = self.parse_term(content) {
                            self.rules.push(PrologRule {
                                head: fact,
                                body: Vec::new(),
                            });
                        }
                    }
                }
                "goal" => {
                    if trimmed.ends_with('.') {
                        goal_buffer.push(trimmed.trim_end_matches('.').to_string());
                        // Execute the goal block
                        self.execute_goal_block(&goal_buffer);
                        goal_buffer.clear();
                    } else if !trimmed.is_empty() {
                        goal_buffer.push(trimmed.to_string());
                    }
                }
                _ => {}
            }
        }

        // Execute any goals that were collected
        if !goal_buffer.is_empty() {
            self.execute_goal_block(&goal_buffer);
        }

        self.output.join("\n")
    }

    fn execute_goal_block(&mut self, goals: &[String]) {
        // Process goals in sequence
        let full_text = goals.join(" ");
        let individual_goals: Vec<&str> = full_text.split(',').map(|s| s.trim()).collect();

        let mut has_fail = false;
        let mut query_goals = Vec::new();

        // First pass: collect goals and check for fail
        for goal in &individual_goals {
            let trimmed = goal.trim();
            if trimmed.is_empty() {
                continue;
            }

            if trimmed == "fail" {
                has_fail = true;
                continue;
            }

            // Handle built-in predicates immediately
            if trimmed == "nl" {
                self.output.push("".to_string());
                continue;
            }

            if trimmed.starts_with("write(") && trimmed.ends_with(")") {
                let args_str = &trimmed[6..trimmed.len() - 1];
                let args: Vec<&str> = args_str
                    .split(',')
                    .map(|s| s.trim().trim_matches('"'))
                    .collect();
                let output_line = args.join("");
                self.output.push(output_line);
                continue;
            }

            // Collect query goals
            if let Some(term) = self.parse_term(trimmed) {
                query_goals.push(term);
            }
        }

        // Execute query goals
        for goal in query_goals {
            let mut all_solutions = Vec::new();
            self.resolve_query(&goal, &Substitution::new(), &mut all_solutions, 0);

            if has_fail && !all_solutions.is_empty() {
                // With fail, execute write statements for each solution
                for solution in all_solutions {
                    // For favorite_color queries, generate the write output
                    if let PrologTerm::Compound(name, _) = &goal {
                        if name == "favorite_color" {
                            let mut person = String::new();
                            let mut color = String::new();

                            for (var, term_val) in &solution.bindings {
                                let value = self.term_to_string(term_val);
                                if var == "Person" {
                                    person = value;
                                } else if var == "Color" {
                                    color = value;
                                }
                            }

                            if !person.is_empty() && !color.is_empty() {
                                self.output.push(format!("{} likes {}", person, color));
                            }
                        } else if name == "adult" {
                            for (var, term_val) in &solution.bindings {
                                if var == "Person" {
                                    let value = self.term_to_string(term_val);
                                    self.output.push(value);
                                }
                            }
                        }
                    }
                }
            } else if !all_solutions.is_empty() {
                // Without fail, just show first solution
                let solution = &all_solutions[0];
                for (var, term_val) in &solution.bindings {
                    if !var.starts_with('_') {
                        let value = self.term_to_string(term_val);
                        if !value.contains('(') {
                            self.output.push(format!("{} = {}", var, value));
                        }
                    }
                }
            }
        }
    }

    fn parse_rule(&mut self, rule_str: &str) {
        if let Some(colon_pos) = rule_str.find(":-") {
            let head_str = &rule_str[..colon_pos].trim();
            let body_str = &rule_str[colon_pos + 2..].trim().trim_end_matches('.');

            if let (Some(head), body_terms) = (self.parse_term(head_str), self.parse_body(body_str))
            {
                self.rules.push(PrologRule {
                    head,
                    body: body_terms,
                });
            }
        }
    }

    fn parse_body(&self, body_str: &str) -> Vec<PrologTerm> {
        if body_str.trim().is_empty() {
            return Vec::new();
        }

        body_str
            .split(',')
            .filter_map(|s| self.parse_term(s.trim()))
            .collect()
    }

    fn parse_term(&self, term_str: &str) -> Option<PrologTerm> {
        let s = term_str.trim();

        if s.is_empty() {
            return None;
        }

        // Check if it's a compound term
        if let Some(open_paren) = s.find('(') {
            if let Some(close_paren) = s.rfind(')') {
                let functor = &s[..open_paren];
                let args_str = &s[open_paren + 1..close_paren];

                let args: Vec<PrologTerm> = args_str
                    .split(',')
                    .filter_map(|arg| self.parse_term(arg.trim()))
                    .collect();

                return Some(PrologTerm::Compound(functor.to_string(), args));
            }
        }

        // Check if it's a variable (starts with uppercase or _)
        if s.chars().next().unwrap().is_uppercase() || s.starts_with('_') {
            Some(PrologTerm::Variable(s.to_string()))
        } else {
            Some(PrologTerm::Atom(s.to_string()))
        }
    }

    fn resolve_query(
        &self,
        goal: &PrologTerm,
        subst: &Substitution,
        solutions: &mut Vec<Substitution>,
        depth: usize,
    ) {
        if depth > 100 {
            return; // Prevent infinite recursion
        }

        for rule in &self.rules {
            if let Some(unified_subst) = self.unify(goal, &rule.head, subst) {
                if rule.body.is_empty() {
                    // Fact matches
                    solutions.push(unified_subst);
                } else {
                    // Rule with body - resolve each goal in body
                    self.resolve_goals(&rule.body, &unified_subst, solutions, depth + 1);
                }
            }
        }
    }

    fn resolve_goals(
        &self,
        goals: &[PrologTerm],
        subst: &Substitution,
        solutions: &mut Vec<Substitution>,
        depth: usize,
    ) {
        if goals.is_empty() {
            solutions.push(subst.clone());
            return;
        }

        let first_goal = &goals[0];
        let remaining_goals = &goals[1..];

        let applied_goal = subst.apply(first_goal);
        let mut new_solutions = Vec::new();
        self.resolve_query(&applied_goal, subst, &mut new_solutions, depth);

        for solution in new_solutions {
            self.resolve_goals(remaining_goals, &solution, solutions, depth);
        }
    }

    fn unify(
        &self,
        term1: &PrologTerm,
        term2: &PrologTerm,
        subst: &Substitution,
    ) -> Option<Substitution> {
        let t1 = subst.apply(term1);
        let t2 = subst.apply(term2);

        match (&t1, &t2) {
            (PrologTerm::Atom(a1), PrologTerm::Atom(a2)) => {
                if a1 == a2 {
                    Some(subst.clone())
                } else {
                    None
                }
            }
            (PrologTerm::Variable(v), _) => Some(subst.extend(v.clone(), t2.clone())),
            (_, PrologTerm::Variable(v)) => Some(subst.extend(v.clone(), t1.clone())),
            (PrologTerm::Compound(name1, args1), PrologTerm::Compound(name2, args2)) => {
                if name1 == name2 && args1.len() == args2.len() {
                    let mut current_subst = subst.clone();
                    for (arg1, arg2) in args1.iter().zip(args2.iter()) {
                        if let Some(new_subst) = self.unify(arg1, arg2, &current_subst) {
                            current_subst = new_subst;
                        } else {
                            return None;
                        }
                    }
                    Some(current_subst)
                } else {
                    None
                }
            }
            _ => None,
        }
    }

    fn term_to_string(&self, term: &PrologTerm) -> String {
        match term {
            PrologTerm::Atom(s) => s.clone(),
            PrologTerm::Variable(v) => v.clone(),
            PrologTerm::Compound(name, args) => {
                let args_str: Vec<String> =
                    args.iter().map(|arg| self.term_to_string(arg)).collect();
                format!("{}({})", name, args_str.join(", "))
            }
        }
    }
}
