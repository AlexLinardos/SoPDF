#!/usr/bin/env python3
"""
SoPDF - A Simple PDF Organizer

Main entry point for the SoPDF application.
Run this file to start the application.
"""

import sys
import os

# Add the project root to the Python path so we can import from src
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main application
from src.app import main

if __name__ == "__main__":
    main() 