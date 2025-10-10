#!/usr/bin/env python3
"""
Multi-Tab Code Editor for Time_Warp IDE
Enhanced editor with tabbed interface and file management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable
import re


class TabEditor:
    """Individual tab editor instance"""
    
    def __init__(self, parent_notebook: ttk.Notebook, file_path: Optional[str] = None, language_callback=None):
        self.notebook = parent_notebook
        self.file_path = file_path
        self.is_modified = False
        self.language = "text"
        self.language_callback = language_callback
        
        # Create tab frame
        self.frame = ttk.Frame(parent_notebook)
        self.setup_editor()
        
        # Add to notebook
        tab_name = self.get_tab_name()
        parent_notebook.add(self.frame, text=tab_name)
        
        # Load content if file provided
        if file_path and os.path.exists(file_path):
            self.load_file_content()
            
    def setup_editor(self):
        """Setup the text editor with enhanced features"""
        # Create editor with line numbers
        editor_frame = ttk.Frame(self.frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers frame
        line_frame = tk.Frame(editor_frame, width=50, bg='#2d2d2d')
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.line_numbers = tk.Text(
            line_frame,
            width=4,
            height=1,
            bg='#2d2d2d',
            fg='#6272a4',
            state=tk.DISABLED,
            font=('Consolas', 10),
            wrap=tk.NONE,
            border=0,
            highlightthickness=0,
            selectbackground='#44475a'
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor
        self.text_editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=('Consolas', 12),
            bg='#282a36',
            fg='#f8f8f2',
            insertbackground='#f8f8f2',
            selectbackground='#44475a',
            selectforeground='#f8f8f2',
            undo=True,
            maxundo=50
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        h_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.text_editor.xview)
        
        self.text_editor.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and editor
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.text_editor.bind('<KeyPress>', self.on_key_press)
        self.text_editor.bind('<Button-1>', self.on_click)
        self.text_editor.bind('<MouseWheel>', self.on_mousewheel)
        self.text_editor.bind('<<Modified>>', self.on_text_modified)
        
        # Sync line numbers with scrolling
        self.text_editor.bind('<Configure>', self.update_line_numbers)
        
        # Initialize line numbers
        self.update_line_numbers()
        
    def get_tab_name(self) -> str:
        """Get display name for tab"""
        if self.file_path:
            name = os.path.basename(self.file_path)
            return f"{'*' if self.is_modified else ''}{name}"
        else:
            return f"{'*' if self.is_modified else ''}Untitled"
            
    def load_file_content(self):
        """Load file content into editor"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_editor.delete('1.0', tk.END)
                self.text_editor.insert('1.0', content)
                self.is_modified = False
                self.detect_language()
                self.apply_syntax_highlighting()
                self.update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {str(e)}")
            
    def detect_language(self):
        """Detect programming language from file extension"""
        if not self.file_path:
            return
            
        ext = Path(self.file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.pilot': 'pilot',
            '.bas': 'basic',
            '.logo': 'logo',
            '.pl': 'perl',
            '.txt': 'text'
        }
        self.language = language_map.get(ext, 'text')
        
    def detect_and_set_language(self):
        """Detect language from filename and content, then update language"""
        # First try extension
        if self.file_path:
            ext = Path(self.file_path).suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.pilot': 'pilot',
                '.bas': 'basic',
                '.basic': 'basic',
                '.logo': 'logo',
                '.pl': 'perl',
                # Removed .jtc mapping - was TempleCode remnant
                '.time_warp': 'time_warp'
            }
            detected = language_map.get(ext, None)
            if detected:
                self.language = detected
                return
        
        # Then try content analysis
        content = self.text_editor.get('1.0', tk.END).strip()
        if not content:
            self.language = 'text'
            return
            
        content_lower = content.lower()
        lines = content.split('\n')
        
        # Check for line numbers (BASIC)
        has_line_numbers = any(line.strip() and line.strip()[0].isdigit() for line in lines[:5])
        if has_line_numbers and any(word in content_lower for word in ['print', 'let', 'goto', 'if']):
            self.language = 'basic'
            return
        
        # Check for PILOT commands
        pilot_commands = ['t:', 'a:', 'j:', 'y:', 'n:', 'c:', 'e:', 'm:']
        if any(cmd in content_lower for cmd in pilot_commands):
            self.language = 'pilot'
            return
        
        # Check for Logo commands
        logo_commands = ['forward', 'back', 'left', 'right', 'penup', 'pendown', 'repeat']
        if any(cmd in content_lower for cmd in logo_commands):
            self.language = 'logo'
            return
        
        # Check for Python
        python_keywords = ['def ', 'import ', 'from ', 'class ', 'if __name__']
        if any(keyword in content_lower for keyword in python_keywords):
            self.language = 'python'
            return
        
        # Check for JavaScript
        js_keywords = ['function', 'var ', 'let ', 'const ', 'document.', 'window.']
        if any(keyword in content_lower for keyword in js_keywords):
            self.language = 'javascript'
            return
        
        # Default to text
        self.language = 'text'
        
    def apply_syntax_highlighting(self):
        """Apply basic syntax highlighting based on language"""
        content = self.text_editor.get('1.0', tk.END)
        
        # Clear existing tags
        for tag in self.text_editor.tag_names():
            if tag.startswith('highlight_'):
                self.text_editor.tag_delete(tag)
        
        # Define color schemes
        colors = {
            'keyword': '#ff79c6',
            'string': '#f1fa8c', 
            'comment': '#6272a4',
            'number': '#bd93f9',
            'function': '#50fa7b'
        }
        
        # Configure tags
        for tag, color in colors.items():
            self.text_editor.tag_configure(f'highlight_{tag}', foreground=color)
            
        # Apply highlighting based on language
        if self.language == 'python':
            self.highlight_python()
        elif self.language == 'basic':
            self.highlight_basic()
        elif self.language == 'logo':
            self.highlight_logo()
        elif self.language == 'pilot':
            self.highlight_pilot()
            
    def highlight_python(self):
        """Python syntax highlighting"""
        keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'import', 'from', 'return', 'print']
        self.highlight_keywords(keywords)
        self.highlight_strings()
        self.highlight_comments('#')
        
    def highlight_basic(self):
        """BASIC syntax highlighting"""  
        keywords = ['PRINT', 'LET', 'IF', 'THEN', 'ELSE', 'FOR', 'NEXT', 'GOTO', 'GOSUB', 'RETURN', 'END', 'DIM', 'INPUT']
        self.highlight_keywords(keywords)
        self.highlight_strings()
        self.highlight_line_numbers()
        
    def highlight_logo(self):
        """Logo syntax highlighting"""
        keywords = ['FORWARD', 'BACK', 'LEFT', 'RIGHT', 'PENUP', 'PENDOWN', 'TO', 'END', 'REPEAT', 'IF', 'IFELSE']
        self.highlight_keywords(keywords)
        self.highlight_comments(';')
        
    def highlight_pilot(self):
        """PILOT syntax highlighting"""
        # Highlight command prefixes
        commands = [r'T:', r'A:', r'M:', r'J:', r'C:', r'U:', r'E:', r'R:']
        for cmd in commands:
            self.highlight_pattern(cmd, 'highlight_keyword')
        self.highlight_variables()
        
    def highlight_keywords(self, keywords: List[str]):
        """Highlight programming keywords"""
        content = self.text_editor.get('1.0', tk.END)
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_editor.tag_add('highlight_keyword', start, end)
                
    def highlight_strings(self):
        """Highlight string literals"""
        content = self.text_editor.get('1.0', tk.END)
        # Single and double quotes
        for pattern in [r'"[^"]*"', r"'[^']*'"]:
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_editor.tag_add('highlight_string', start, end)
                
    def highlight_comments(self, comment_char: str):
        """Highlight comments"""
        content = self.text_editor.get('1.0', tk.END)
        pattern = re.escape(comment_char) + r'.*'
        for match in re.finditer(pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add('highlight_comment', start, end)
            
    def highlight_line_numbers(self):
        """Highlight BASIC line numbers"""
        content = self.text_editor.get('1.0', tk.END)
        pattern = r'^\d+'
        for match in re.finditer(pattern, content, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add('highlight_number', start, end)
            
    def highlight_variables(self):
        """Highlight PILOT variables (#NAME)"""
        content = self.text_editor.get('1.0', tk.END)
        pattern = r'#[A-Za-z_][A-Za-z0-9_]*'
        for match in re.finditer(pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add('highlight_function', start, end)
            
    def highlight_pattern(self, pattern: str, tag: str):
        """Generic pattern highlighting"""
        content = self.text_editor.get('1.0', tk.END)
        for match in re.finditer(pattern, content, re.IGNORECASE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add(tag, start, end)
            
    def update_line_numbers(self, event=None):
        """Update line numbers display"""
        content = self.text_editor.get('1.0', tk.END)
        lines = content.count('\n')
        
        line_text = '\n'.join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_text)
        self.line_numbers.config(state=tk.DISABLED)
        
    def on_key_press(self, event):
        """Handle key press events"""
        # Auto-indentation
        if event.keysym == 'Return':
            self.auto_indent()
        # Tab completion
        elif event.keysym == 'Tab':
            return self.handle_tab()
        # Trigger syntax highlighting on certain keys
        elif event.char in [' ', ':', '(', ')', '"', "'"]:
            self.text_editor.after_idle(self.apply_syntax_highlighting)
            
    def auto_indent(self):
        """Handle automatic indentation"""
        current_line = self.text_editor.index(tk.INSERT).split('.')[0]
        line_content = self.text_editor.get(f"{current_line}.0", f"{current_line}.end")
        
        # Count leading whitespace
        indent = 0
        for char in line_content:
            if char in [' ', '\t']:
                indent += 1
            else:
                break
                
        # Add extra indent for certain patterns
        if any(keyword in line_content.upper() for keyword in ['FOR', 'IF', 'WHILE', 'DEF', 'CLASS', 'TO']):
            indent += 4
            
        # Insert indentation
        self.text_editor.insert(tk.INSERT, ' ' * indent)
        
    def handle_tab(self):
        """Handle tab key for indentation"""
        self.text_editor.insert(tk.INSERT, '    ')  # 4 spaces
        return 'break'  # Prevent default tab behavior
        
    def on_click(self, event):
        """Handle mouse clicks"""
        self.update_line_numbers()
        
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def on_text_modified(self, event=None):
        """Handle text modifications"""
        if not self.is_modified:
            self.is_modified = True
            self.update_tab_title()
        # Detect language from content
        self.text_editor.after_idle(self.detect_and_set_language)
        # Schedule syntax highlighting update
        self.text_editor.after_idle(self.apply_syntax_highlighting)
        self.text_editor.after_idle(self.update_line_numbers)
        # Update language indicator
        if self.language_callback:
            try:
                self.text_editor.after_idle(lambda: self.language_callback() if self.language_callback else None)
            except Exception:
                pass
        
    def update_tab_title(self):
        """Update tab title to reflect modification status"""
        tab_name = self.get_tab_name()
        tab_index = self.notebook.index(self.frame)
        self.notebook.tab(tab_index, text=tab_name)
        
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save file content"""
        if file_path:
            self.file_path = file_path
            
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Python files", "*.py"),
                    ("BASIC files", "*.bas"),
                    ("Logo files", "*.logo"),
                    ("PILOT files", "*.pilot"),
                    ("JavaScript files", "*.js"),
                    ("Perl files", "*.pl"),
                    ("All files", "*.*")
                ]
            )
            if not self.file_path:
                return False
                
        try:
            content = self.text_editor.get('1.0', tk.END + '-1c')
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.is_modified = False
            self.detect_language()
            self.update_tab_title()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            return False
            
    def get_content(self) -> str:
        """Get editor content"""
        return self.text_editor.get('1.0', tk.END + '-1c')
        
    def set_content(self, content: str):
        """Set editor content"""
        self.text_editor.delete('1.0', tk.END)
        self.text_editor.insert('1.0', content)
        self.apply_syntax_highlighting()
        self.update_line_numbers()


class MultiTabEditor:
    """Multi-tab code editor manager"""
    
    def __init__(self, parent_widget, language_callback=None):
        self.parent = parent_widget
        self.tabs: Dict[str, TabEditor] = {}
        self.active_tab: Optional[TabEditor] = None
        self.language_callback = language_callback
        
        # Create notebook widget
        self.notebook = ttk.Notebook(parent_widget)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab selection event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Create initial untitled tab
        self.new_tab()
        
    def new_tab(self, file_path: Optional[str] = None) -> TabEditor:
        """Create new tab"""
        tab_editor = TabEditor(self.notebook, file_path, self.language_callback)
        
        # Generate unique key
        key = file_path if file_path else f"untitled_{len(self.tabs) + 1}"
        self.tabs[key] = tab_editor
        
        # Set as active tab
        self.notebook.select(tab_editor.frame)
        self.active_tab = tab_editor

        # Update language indicator
        if self.language_callback:
            try:
                self.language_callback()
            except Exception:
                pass

        return tab_editor
        
    def open_file(self, file_path: str) -> TabEditor:
        """Open file in new tab"""
        # Check if file already open
        for key, tab in self.tabs.items():
            if tab.file_path == file_path:
                self.notebook.select(tab.frame)
                self.active_tab = tab
                # Update language indicator
                if self.language_callback:
                    try:
                        self.language_callback()
                    except Exception:
                        pass
                return tab
                
        # Create new tab
        return self.new_tab(file_path)
        
    def close_tab(self, tab_key: Optional[str] = None) -> bool:
        """Close specified tab or active tab"""
        if not tab_key:
            if not self.active_tab:
                return False
            # Find key for active tab
            tab_key = None
            for key, tab in self.tabs.items():
                if tab == self.active_tab:
                    tab_key = key
                    break
                    
        if tab_key not in self.tabs:
            return False
            
        tab = self.tabs[tab_key]
        
        # Check for unsaved changes
        if tab.is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Save changes to {tab.get_tab_name().replace('*', '')}?"
            )
            if result is None:  # Cancel
                return False
            elif result:  # Yes, save
                if not tab.save_file():
                    return False
                    
        # Remove tab
        self.notebook.forget(tab.frame)
        del self.tabs[tab_key]
        
        # Update active tab
        if self.notebook.tabs():
            current_tab_id = self.notebook.select()
            for tab in self.tabs.values():
                if str(tab.frame) == current_tab_id:
                    self.active_tab = tab
                    break
        else:
            self.active_tab = None
            # Create new untitled tab if no tabs left
            self.new_tab()
            
        return True
        
    def save_active_tab(self) -> bool:
        """Save active tab"""
        if self.active_tab:
            return self.active_tab.save_file()
        return False
        
    def save_active_tab_as(self) -> bool:
        """Save active tab with new name"""
        if self.active_tab:
            return self.active_tab.save_file(None)
        return False
        
    def get_active_content(self) -> str:
        """Get content from active tab"""
        if self.active_tab:
            return self.active_tab.get_content()
        return ""
        
    def set_active_content(self, content: str):
        """Set content in active tab"""
        if self.active_tab:
            self.active_tab.set_content(content)
            
    def on_tab_changed(self, event):
        """Handle tab selection change"""
        selected_tab_id = self.notebook.select()
        for tab in self.tabs.values():
            if str(tab.frame) == selected_tab_id:
                self.active_tab = tab
                break
        
        # Update language indicator if callback is available
        if self.language_callback:
            try:
                self.language_callback()
            except Exception:
                pass  # Ignore callback errors
    
    def apply_theme(self, colors):
        """Apply theme colors comprehensively to all editor components"""
        try:
            # Apply theme to notebook with enhanced styling
            self.notebook.configure(style="Modern.TNotebook")
            
            # Apply theme to all tab editors with comprehensive styling
            for tab in self.tabs.values():
                if hasattr(tab, 'text_editor'):
                    # Apply theme to main text widget
                    tab.text_editor.configure(
                        bg=colors["bg_primary"],
                        fg=colors["text_primary"],
                        insertbackground=colors["accent"],
                        selectbackground=colors["selection"],
                        selectforeground=colors["text_primary"],
                        relief="flat",
                        borderwidth=0,
                        highlightthickness=1,
                        highlightcolor=colors["accent"],
                        highlightbackground=colors["border"],
                        font=("Consolas", 11),
                        wrap="none",
                        undo=True,
                        maxundo=50
                    )
                    
                    # Apply theme to line numbers if they exist
                    if hasattr(tab, 'line_numbers'):
                        tab.line_numbers.configure(
                            bg=colors["bg_secondary"],
                            fg=colors["text_secondary"],
                            relief="flat",
                            borderwidth=0,
                            highlightthickness=0,
                            font=("Consolas", 11),
                            width=4,
                            state="disabled"
                        )
                    
                    # Configure syntax highlighting tags with theme colors
                    tab.text_editor.tag_configure("keyword", foreground=colors.get("keyword", colors["accent"]))
                    tab.text_editor.tag_configure("string", foreground=colors.get("string", "#6A994E"))
                    tab.text_editor.tag_configure("comment", foreground=colors.get("comment", colors["text_secondary"]))
                    tab.text_editor.tag_configure("number", foreground=colors.get("number", "#F77F00"))
                    tab.text_editor.tag_configure("operator", foreground=colors.get("operator", colors["text_primary"]))
                    tab.text_editor.tag_configure("variable", foreground=colors.get("variable", "#BC6C25"))
                    
                    # Re-apply syntax highlighting after theme change
                    tab.apply_syntax_highlighting()
                
                # Apply theme to tab frame
                if hasattr(tab, 'frame'):
                    tab.frame.configure(style="Themed.TFrame")
        
        except Exception as e:
            print(f"⚠️ MultiTabEditor theme error: {e}")