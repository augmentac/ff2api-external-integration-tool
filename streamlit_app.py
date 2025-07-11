#!/usr/bin/env python3
"""
Streamlit Cloud Entry Point
Redirects to the FF2API application
"""

import streamlit as st
import sys
import os

# Add src to path to enable imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the FF2API application
from src.frontend.app import main

if __name__ == "__main__":
    main()