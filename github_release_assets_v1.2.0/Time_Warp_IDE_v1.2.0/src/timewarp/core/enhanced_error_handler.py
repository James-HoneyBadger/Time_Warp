#!/usr/bin/env python3
"""
Enhanced Error Handler for Time_Warp IDE
Educational error messages with suggestions and location highlighting
"""

import tkinter as tk
import re
from typing import Dict, Optional, Callable
from dataclasses import dataclass


@dataclass
class ErrorInfo:
    """Error information structure"""
    line_number: int
    column: int
    error_type: str
    message: str
    suggestion: str
    code_snippet: str


class EnhancedErrorHandler:
    """Enhanced error handler with educational features"""
    
    def __init__(self, output_callback: Optional[Callable[[str], None]] = None):
        self.output_callback = output_callback
        self.error_patterns = self.initialize_error_patterns()
        
    def initialize_error_patterns(self) -> Dict[str, Dict]:
        """Initialize language-specific error patterns and suggestions"""
        return {
            'python': {
                'SyntaxError': {
                    'patterns': [
                        (r"invalid syntax.*line (\d+)", "Check for missing punctuation or incorrect indentation"),
                        (r"unexpected EOF", "Missing closing bracket, parenthesis, or quote"),
                        (r"invalid character", "Check for unusual characters or encoding issues")
                    ],
                    'suggestions': "Common Python syntax errors:\n• Missing colons after if/for/while/def\n• Incorrect indentation\n• Unmatched brackets or quotes"
                },
                'NameError': {
                    'patterns': [
                        (r"name '(.+?)' is not defined", "Variable '{}' hasn't been created yet. Define it first!")
                    ],
                    'suggestions': "Variable not found:\n• Check spelling\n• Make sure variable is defined before use\n• Check indentation levels"
                },
                'TypeError': {
                    'patterns': [
                        (r"unsupported operand type", "Cannot perform this operation on these data types"),
                        (r"takes (\d+) positional arguments", "Function called with wrong number of arguments")
                    ],
                    'suggestions': "Type mismatch:\n• Check data types in operations\n• Verify function arguments\n• Use str(), int(), float() to convert types"
                }
            },
            'basic': {
                'syntax_error': {
                    'patterns': [
                        (r"line (\d+)", "Check BASIC syntax on line {}"),
                        (r"missing line number", "BASIC programs need line numbers (10, 20, 30, etc.)"),
                        (r"invalid command", "Unknown BASIC command - check spelling")
                    ],
                    'suggestions': "BASIC syntax tips:\n• Start lines with numbers (10, 20, 30)\n• Use PRINT for output\n• Use LET for variables\n• End with END"
                },
                'variable_error': {
                    'patterns': [
                        (r"undefined variable (.+)", "Variable '{}' not defined. Use LET first!")
                    ],
                    'suggestions': "Variable issues:\n• Use LET VARNAME = VALUE\n• Variable names: letters and numbers\n• Arrays need DIM statement"
                }
            },
            'logo': {
                'command_error': {
                    'patterns': [
                        (r"unknown command (.+)", "Logo command '{}' not recognized"),
                        (r"wrong number of inputs", "Command needs different number of parameters")
                    ],
                    'suggestions': "Logo command help:\n• FORWARD, BACK need distance\n• LEFT, RIGHT need angle\n• Check procedure definitions"
                },
                'procedure_error': {
                    'patterns': [
                        (r"procedure (.+) not defined", "Procedure '{}' doesn't exist")
                    ],
                    'suggestions': "Logo procedures:\n• Define with TO NAME ... END\n• Call by name with parameters\n• Check spelling and parameters"
                }
            },
            'pilot': {
                'command_error': {
                    'patterns': [
                        (r"invalid command prefix", "PILOT commands start with letter and colon (T:, A:, etc.)"),
                        (r"missing colon", "PILOT commands need colon after letter")
                    ],
                    'suggestions': "PILOT command format:\n• T: for text output\n• A: for input\n• J: for jumps\n• M: for matching"
                },
                'label_error': {
                    'patterns': [
                        (r"label (.+) not found", "Jump label '{}' doesn't exist"),
                        (r"invalid label", "Labels start with * and contain letters/numbers")
                    ],
                    'suggestions': "PILOT labels:\n• Define with *LABEL\n• Jump with J:*LABEL\n• Use letters and numbers only"
                }
            }
        }
        
    def process_error(self, error_text: str, language: str, code: str = "") -> ErrorInfo:
        """Process error and create enhanced error information"""
        # Extract basic error info
        line_number = self.extract_line_number(error_text)
        error_type = self.extract_error_type(error_text, language)
        
        # Get language patterns
        patterns = self.error_patterns.get(language, {})
        
        # Find matching pattern and suggestion
        suggestion = self.find_suggestion(error_text, error_type, patterns)
        
        # Extract relevant code snippet
        code_snippet = self.extract_code_snippet(code, line_number)
        
        # Clean up error message
        clean_message = self.clean_error_message(error_text)
        
        return ErrorInfo(
            line_number=line_number,
            column=0,  # Column extraction not implemented yet
            error_type=error_type,
            message=clean_message,
            suggestion=suggestion,
            code_snippet=code_snippet
        )
        
    def extract_line_number(self, error_text: str) -> int:
        """Extract line number from error text"""
        patterns = [
            r"line (\d+)",
            r"Line (\d+)",
            r"at line (\d+)",
            r"on line (\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_text)
            if match:
                return int(match.group(1))
                
        return 0
        
    def extract_error_type(self, error_text: str, language: str) -> str:
        """Extract error type from error text"""
        if language == 'python':
            python_errors = ['SyntaxError', 'NameError', 'TypeError', 'ValueError', 'IndexError', 'KeyError']
            for error_type in python_errors:
                if error_type in error_text:
                    return error_type
                    
        elif language == 'basic':
            if 'syntax' in error_text.lower():
                return 'syntax_error'
            elif 'variable' in error_text.lower():
                return 'variable_error'
                
        elif language == 'logo':
            if 'command' in error_text.lower():
                return 'command_error'
            elif 'procedure' in error_text.lower():
                return 'procedure_error'
                
        elif language == 'pilot':
            if 'command' in error_text.lower():
                return 'command_error'
            elif 'label' in error_text.lower():
                return 'label_error'
                
        return 'unknown_error'
        
    def find_suggestion(self, error_text: str, error_type: str, patterns: Dict) -> str:
        """Find appropriate suggestion for error"""
        if error_type in patterns:
            error_info = patterns[error_type]
            
            # Check specific patterns first
            for pattern, suggestion in error_info.get('patterns', []):
                match = re.search(pattern, error_text, re.IGNORECASE)
                if match:
                    # Format suggestion with matched groups
                    try:
                        return suggestion.format(*match.groups())
                    except (IndexError, ValueError):
                        return suggestion
                        
            # Return general suggestions
            return error_info.get('suggestions', 'Check your code for common errors.')
            
        return self.get_general_suggestion(error_type)
        
    def get_general_suggestion(self, error_type: str) -> str:
        """Get general suggestion for error type"""
        general_suggestions = {
            'syntax_error': "Check your syntax:\n• Missing punctuation\n• Incorrect spacing\n• Typos in commands",
            'variable_error': "Variable issues:\n• Check spelling\n• Make sure it's defined\n• Check scope",
            'command_error': "Command problems:\n• Check spelling\n• Verify parameters\n• Check documentation",
            'unknown_error': "General debugging:\n• Read error message carefully\n• Check recent changes\n• Test smaller parts"
        }
        return general_suggestions.get(error_type, "Check your code for errors.")
        
    def extract_code_snippet(self, code: str, line_number: int) -> str:
        """Extract relevant code snippet around error line"""
        if not code or line_number <= 0:
            return ""
            
        lines = code.split('\n')
        if line_number > len(lines):
            return ""
            
        # Get lines around error (with context)
        start_line = max(0, line_number - 3)
        end_line = min(len(lines), line_number + 2)
        
        snippet_lines = []
        for i in range(start_line, end_line):
            line_num = i + 1
            prefix = ">>> " if line_num == line_number else "    "
            snippet_lines.append(f"{prefix}{line_num:3d}: {lines[i]}")
            
        return '\n'.join(snippet_lines)
        
    def clean_error_message(self, error_text: str) -> str:
        """Clean up error message for better readability"""
        # Remove file paths and technical jargon
        cleaned = re.sub(r'File "[^"]*", ', '', error_text)
        cleaned = re.sub(r'Traceback \(most recent call last\):', '', cleaned)
        cleaned = re.sub(r'^\s*', '', cleaned, flags=re.MULTILINE)
        
        # Remove empty lines
        lines = [line for line in cleaned.split('\n') if line.strip()]
        
        return '\n'.join(lines)
        
    def format_error_display(self, error_info: ErrorInfo, language: str) -> str:
        """Format error for display in IDE"""
        language_emoji = {
            'python': '🐍',
            'basic': '🔢', 
            'logo': '🐢',
            'pilot': '✈️',
            'javascript': '📜',
            'perl': '🔷'
        }
        
        emoji = language_emoji.get(language, '❌')
        
        display_text = f"{emoji} {language.upper()} ERROR\n"
        display_text += "=" * 50 + "\n\n"
        
        if error_info.line_number > 0:
            display_text += f"📍 Line {error_info.line_number}\n"
            
        display_text += f"🔥 {error_info.error_type}: {error_info.message}\n\n"
        
        if error_info.code_snippet:
            display_text += "📝 Code:\n"
            display_text += error_info.code_snippet + "\n\n"
            
        display_text += "💡 Suggestion:\n"
        display_text += error_info.suggestion + "\n\n"
        
        display_text += "🔗 Quick Help:\n"
        display_text += self.get_quick_help(language) + "\n"
        
        return display_text
        
    def get_quick_help(self, language: str) -> str:
        """Get quick help for language"""
        help_text = {
            'python': "• Use print() for output\n• Check indentation (4 spaces)\n• Variables don't need declaration",
            'basic': "• Start lines with numbers\n• Use PRINT for output\n• Variables need LET statement",
            'logo': "• FORWARD/BACK move turtle\n• LEFT/RIGHT turn turtle\n• Define procedures with TO...END",
            'pilot': "• Commands start with letter:\n• T: text, A: input, J: jump\n• Labels start with *",
            'javascript': "• Use console.log() for output\n• Variables: let, const, var\n• Check semicolons and brackets",
            'perl': "• Variables start with $, @, %\n• Use print for output\n• End statements with semicolon"
        }
        return help_text.get(language, "Check language documentation")
        
    def display_error(self, error_text: str, language: str, code: str = ""):
        """Display enhanced error in IDE"""
        error_info = self.process_error(error_text, language, code)
        formatted_error = self.format_error_display(error_info, language)
        
        if self.output_callback:
            self.output_callback(formatted_error)
        else:
            print(formatted_error)
            
        return error_info


class ErrorHighlighter:
    """Highlight errors in code editor"""
    
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self.configure_tags()
        
    def configure_tags(self):
        """Configure text tags for error highlighting"""
        self.text_widget.tag_configure('error_line', background='#ffebee', foreground='#c62828')
        self.text_widget.tag_configure('error_text', background='#ffcdd2', foreground='#d32f2f', underline=True)
        self.text_widget.tag_configure('warning_line', background='#fff3e0', foreground='#ef6c00')
        
    def highlight_error(self, line_number: int, column: int = 0, length: int = 0):
        """Highlight error at specific location"""
        if line_number <= 0:
            return
            
        # Clear previous error highlights
        self.clear_highlights()
        
        # Highlight entire line
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        self.text_widget.tag_add('error_line', line_start, line_end)
        
        # Highlight specific text if column specified
        if column > 0 and length > 0:
            error_start = f"{line_number}.{column}"
            error_end = f"{line_number}.{column + length}"
            self.text_widget.tag_add('error_text', error_start, error_end)
            
        # Scroll to error line
        self.text_widget.see(line_start)
        
    def clear_highlights(self):
        """Clear all error highlights"""
        for tag in ['error_line', 'error_text', 'warning_line']:
            self.text_widget.tag_remove(tag, '1.0', tk.END)
            
    def highlight_warning(self, line_number: int):
        """Highlight warning at specific line"""
        if line_number <= 0:
            return
            
        line_start = f"{line_number}.0"
        line_end = f"{line_number}.end"
        self.text_widget.tag_add('warning_line', line_start, line_end)