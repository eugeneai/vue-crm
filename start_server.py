#!/usr/bin/env python3
"""
Start Pyramid server with Python 3.14 compatibility.
This script applies the pkgutil.ImpImporter patch before importing Pyramid.
"""

import sys
import os

# Apply the monkey patch FIRST
import pkgutil

if not hasattr(pkgutil, 'ImpImporter'):
    # Create a dummy ImpImporter class for compatibility
    class ImpImporter:
        def find_module(self, fullname, path=None):
            return None
    pkgutil.ImpImporter = ImpImporter
    print("Applied pkgutil.ImpImporter compatibility patch for Python 3.12+")

# Now import Pyramid
from pyramid.scripts.pserve import main

if __name__ == '__main__':
    # Set up command line arguments for pserve
    config_file = os.path.join('backend', 'development.ini')
    sys.argv = ['pserve', config_file, '--reload']
    
    print(f"Starting Pyramid development server with {config_file}")
    print("Auto-reload enabled - server will restart on code changes")
    print("Press Ctrl+C to stop")
    print("")
    
    # Run pserve
    main()