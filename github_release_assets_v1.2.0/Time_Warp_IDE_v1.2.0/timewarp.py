#!/usr/bin/env python3
"""
Time_Warp IDE - Main Entry Point

Educational programming environment supporting multiple languages
with integrated turtle graphics and comprehensive learning tools.
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from timewarp.main import main

if __name__ == "__main__":
    main()