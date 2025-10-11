#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Time_Warp IDE tests
"""

import sys
import os

# Add src to path for all tests (same as main entry point)
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
