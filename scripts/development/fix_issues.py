#!/usr/bin/env python3
"""
Fix Logo REPEAT parsing and theme issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_logo_repeat_parsing():
    """Fix the Logo REPEAT parsing to handle multi-line syntax"""
    
    # Read the current logo.py file
    logo_file = "core/languages/logo.py"
    with open(logo_file, 'r') as f:
        content = f.read()
    
    # Find the _handle_repeat method
    lines = content.split('\n')
    
    # Look for the line that causes the malformed error
    for i, line in enumerate(lines):
        if 'parsed = self._parse_repeat_nested(command.strip())' in line:
            print(f"Found problematic parsing at line {i+1}")
            
            # Add a preprocessing step before parsing
            new_code = '''    def _handle_repeat(self, command):
        """Handle REPEAT command with support for multi-line syntax"""
        # Preprocess multi-line REPEAT blocks by joining lines
        command_lines = command.strip().split('\\n')
        
        if len(command_lines) > 1:
            # Multi-line format - join into single line
            processed_command = ""
            bracket_depth = 0
            for line in command_lines:
                line = line.strip()
                if not line or line.startswith(';'):  # Skip empty lines and comments
                    continue
                    
                # Track bracket depth
                bracket_depth += line.count('[') - line.count(']')
                
                # Add line to processed command
                if processed_command:
                    processed_command += " " + line
                else:
                    processed_command = line
                    
                # If brackets are balanced, we have complete command
                if bracket_depth == 0 and '[' in processed_command:
                    break
                    
            command = processed_command
        
        parsed = self._parse_repeat_nested(command.strip())
        if not parsed:
            self.interpreter.log_output("Malformed REPEAT syntax or unmatched brackets")
            return "continue"
        
        count, commands = parsed
        
        # Expand and execute commands
        try:
            expanded = commands * count
            if len(expanded) > 10000:  # Prevent runaway
                self.interpreter.log_output("REPEAT aborted: expansion too large")
                return "continue"
            
            for cmd in expanded:
                if cmd.strip():
                    self.execute_command(cmd.strip())
            return "continue"
        except Exception as e:
            self.interpreter.log_output(f"Error in REPEAT execution: {e}")
            return "continue"'''
            
            # Find the start and end of the current _handle_repeat method
            method_start = i - 1  # Back up to the def line
            while method_start > 0 and not lines[method_start].strip().startswith('def _handle_repeat'):
                method_start -= 1
                
            if method_start > 0:
                # Find the end of the method (next def or end of class)
                method_end = method_start + 1
                while method_end < len(lines):
                    line = lines[method_end].strip()
                    if line.startswith('def ') and not line.startswith('def _handle_repeat'):
                        break
                    method_end += 1
                
                # Replace the method
                lines[method_start:method_end] = new_code.split('\\n')
                
                # Write back to file
                with open(logo_file, 'w') as f:
                    f.write('\\n'.join(lines))
                
                print(f"✅ Fixed Logo REPEAT parsing in {logo_file}")
                return True
    
    print("❌ Could not find REPEAT parsing code to fix")
    return False

def check_theme_consistency():
    """Check for theme inconsistency issues"""
    
    print("\\n🎨 Checking theme consistency...")
    
    # Check the theme manager
    from tools.theme import ThemeManager, load_config
    
    # Load current config
    config = load_config()
    print(f"Config current theme: {config.get('current_theme', 'not set')}")
    print(f"Config dark mode: {config.get('dark_mode', 'not set')}")
    
    # Check what theme the main application uses
    try:
        theme_manager = ThemeManager()
        print(f"ThemeManager current theme: {theme_manager.current_theme}")
        
        # Check if there are multiple theme loading points
        main_file = "Time_Warp.py"
        with open(main_file, 'r') as f:
            main_content = f.read()
            
        # Look for theme loading
        if 'load_theme' in main_content:
            print("✅ Main application loads themes")
        else:
            print("⚠️ No theme loading found in main application")
            
        # Look for multiple theme applications
        theme_count = main_content.count('apply_theme')
        if theme_count > 1:
            print(f"⚠️ Theme applied {theme_count} times - may cause inconsistency")
        elif theme_count == 1:
            print("✅ Theme applied once")
        else:
            print("❌ No theme application found")
            
    except Exception as e:
        print(f"❌ Error checking theme: {e}")

def main():
    print("🔧 Fixing Time_Warp IDE Issues...")
    print("=" * 50)
    
    # Fix Logo REPEAT parsing
    print("1. Fixing Logo REPEAT multi-line parsing...")
    if fix_logo_repeat_parsing():
        print("✅ Logo REPEAT parsing fixed")
    else:
        print("❌ Failed to fix Logo REPEAT parsing")
    
    # Check theme issues
    print("\\n2. Checking theme consistency...")
    check_theme_consistency()
    
    print("\\n🎯 Issue Analysis Complete!")
    print("\\nNext steps:")
    print("- Test the fixed Logo REPEAT parsing")
    print("- Verify theme consistency in the main application")
    print("- Update the distribution package if needed")

if __name__ == "__main__":
    main()