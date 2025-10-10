#!/usr/bin/env python3
"""
Time_Warp IDE Standardization Script
Replaces all occurrences of 'Time_Warp' and 'time_warp' with 'Time_Warp'
"""

import os
import re
import glob
from pathlib import Path

def update_file_content(filepath, replacements):
    """Update file content with the given replacements"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for old_pattern, new_text in replacements:
            if isinstance(old_pattern, str):
                content = content.replace(old_pattern, new_text)
            else:  # regex pattern
                content = old_pattern.sub(new_text, content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False
    
    return False

def main():
    """Main standardization function"""
    print("🔄 Starting Time_Warp IDE standardization...")
    
    # Define replacement patterns
    replacements = [
        # Class and function names
        ('Time_WarpInterpreter', 'Time_WarpInterpreter'),
        ('Time_WarpIDE', 'Time_WarpIDE'),
        ('Time_WarpTestCase', 'Time_WarpTestCase'),
        
        # General references - most specific first
        ('Time_Warp IDE', 'Time_Warp IDE'),
        ('Time_Warp.py', 'Time_Warp.py'),  # File references
        ('Time_Warp/', 'Time_Warp/'),      # Directory references
        ('cd Time_Warp', 'cd Time_Warp'),  # Command references
        
        # URLs and repository references 
        ('Time_WarpIDE/Time_Warp', 'Time_WarpIDE/Time_Warp'),
        ('github.com/Time_WarpIDE/Time_Warp', 'github.com/Time_WarpIDE/Time_Warp'),
        
        # Package and module references
        ('time_warp-ide', 'time_warp-ide'),
        ('time_warp-compiler', 'time_warp-compiler'),
        ('time_warp_env', 'time_warp_env'),
        ('/.time_warp/', '/.time_warp/'),
        
        # Generic Time_Warp -> Time_Warp (after more specific ones)
        (re.compile(r'\bTimeWarp\b'), 'Time_Warp'),
        (re.compile(r'\btimewarp\b'), 'time_warp'),
        
        # File extensions and special cases
        ('.time_warp', '.time_warp'),
    ]
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Files to update (exclude binary files, git files, etc.)
    file_patterns = [
        '**/*.py',
        '**/*.md',
        '**/*.txt', 
        '**/*.sh',
        '**/*.bat',
        '**/*.yml',
        '**/*.yaml',
        '**/*.json',
        '**/*.pilot',
        '**/*.bas',
        '**/*.logo',
        '**/*.js',
        '**/*.pl'
    ]
    
    # Directories to exclude
    exclude_dirs = {'.git', '__pycache__', '.vscode', 'node_modules', '.Time_Warp'}
    
    updated_files = []
    
    for pattern in file_patterns:
        for filepath in project_root.glob(pattern):
            # Skip if in excluded directory
            if any(excluded in filepath.parts for excluded in exclude_dirs):
                continue
                
            # Skip binary files
            if filepath.suffix in {'.pyc', '.pyo', '.exe', '.so', '.dll'}:
                continue
                
            if filepath.is_file():
                if update_file_content(filepath, replacements):
                    updated_files.append(str(filepath.relative_to(project_root)))
                    print(f"✅ Updated: {filepath.relative_to(project_root)}")
    
    print(f"\n🎉 Standardization complete!")
    print(f"📊 Updated {len(updated_files)} files")
    
    if updated_files:
        print("\n📝 Updated files:")
        for file in sorted(updated_files):
            print(f"   • {file}")

if __name__ == "__main__":
    main()