#!/usr/bin/env python3
"""
TimeWarp IDE - Main Entry Point
A multi-language educational programming environment
"""

import sys
import os

# Add the current directory to path for direct execution
sys.path.insert(0, os.path.dirname(__file__))


def main():
    """Main entry point for TimeWarp IDE"""
    try:
        # Import and run the main application
        from TimeWarp import main as timewarp_main

        timewarp_main()
    except ImportError as e:
        print(f"Error: Could not import TimeWarp IDE: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTimeWarp IDE closed.")
        sys.exit(0)
    except Exception as e:
        print(f"Error running TimeWarp IDE: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
