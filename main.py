#!/usr/bin/env python3
"""
SoPDF - A Simple PDF Organizer

This is the main entry point for the SoPDF application (backwards compatibility).
The actual application code has been refactored into a modular structure in the src/ directory.

To run the application, you can use either:
- python main.py (this file)
- python run.py (dedicated entry point)
"""

import sys
import os

# Add the project root to the Python path so we can import from src
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main application from the new modular structure
from src.app import main

if __name__ == "__main__":
    print("🚀 Starting SoPDF with new modular architecture...")
    main() 