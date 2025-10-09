#!/usr/bin/env python3
"""
JAMES Application Launcher
Executes JAMES applications with .JTC extension
Usage: python3 jtc_launcher.py <application.JTC>
"""

import sys
import os

def run_jtc_file(filename):
    """Execute a .JTC file"""
    if not filename.endswith('.JTC'):
        print(f"Error: {filename} is not a .JTC file")
        return False
        
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found")
        return False
        
    try:
        # Read and execute the .JTC file
        with open(filename, 'r') as f:
            content = f.read()
            
        # Execute the content
        exec(content)
        return True
        
    except Exception as e:
        print(f"Error executing {filename}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 jtc_launcher.py <filename.JTC>")
        sys.exit(1)
        
    filename = sys.argv[1]
    success = run_jtc_file(filename)
    sys.exit(0 if success else 1)