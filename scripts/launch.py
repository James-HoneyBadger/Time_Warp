#!/usr/bin/env python3
"""
Time_Warp IDE Python Launcher
Alternative launcher that can be run directly with Python
"""

import os
import sys
import subprocess

def main():
    """Launch Time_Warp IDE"""
    print("🚀 Time_Warp IDE 1.1 Python Launcher")
    print("=" * 50)
    
    # Get the directory where this launcher is located
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main Time_Warp application
    timewarp_path = os.path.join(launcher_dir, "Time_Warp.py")
    
    if not os.path.exists(timewarp_path):
        print(f"❌ Time_Warp.py not found at: {timewarp_path}")
        print("Please make sure you're running this from the Time_Warp directory")
        return 1
    
    print(f"📁 Time_Warp directory: {launcher_dir}")
    print(f"🐍 Python version: {sys.version}")
    print(f"▶️ Launching: {timewarp_path}")
    print()
    
    try:
        # Launch Time_Warp IDE
        result = subprocess.run([sys.executable, timewarp_path], cwd=launcher_dir, check=False)
        print("\n👋 Time_Warp IDE session ended.")
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