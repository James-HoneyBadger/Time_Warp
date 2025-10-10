#!/usr/bin/env python3
"""
TimeWarp IDE v1.0.1 Python Launcher
Alternative launcher that can be run directly with Python
"""

import os
import sys
import subprocess

def main():
    """Launch TimeWarp IDE v1.0.1"""
    print("🚀 TimeWarp IDE v1.0.1 Python Launcher")
    print("=" * 50)
    
    # Get the directory where this launcher is located
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main TimeWarp application
    timewarp_path = os.path.join(launcher_dir, "TimeWarp_v101.py")
    
    if not os.path.exists(timewarp_path):
        print(f"❌ TimeWarp_v101.py not found at: {timewarp_path}")
        print("Please make sure you're running this from the TimeWarp directory")
        return 1
    
    print(f"📁 TimeWarp directory: {launcher_dir}")
    print(f"🐍 Python version: {sys.version}")
    print(f"▶️ Launching: {timewarp_path}")
    print()
    
    try:
        # Launch TimeWarp IDE
        result = subprocess.run([sys.executable, timewarp_path], cwd=launcher_dir, check=False)
        print("\n👋 TimeWarp IDE session ended.")
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚡ Launch interrupted by user")
        return 130
    except (OSError, subprocess.SubprocessError) as e:
        print(f"\n💥 Launch error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)