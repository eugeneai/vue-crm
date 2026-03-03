#!/usr/bin/env python3
"""
Wrapper script to run Pyramid server with Python 3.14 compatibility patch.
This fixes the pkgutil.ImpImporter issue in Python 3.12+.
"""

import sys
import os

# Apply monkey patch for Python 3.12+ compatibility
import pkgutil

if not hasattr(pkgutil, 'ImpImporter'):
    # Create a dummy ImpImporter class for compatibility
    class ImpImporter:
        def find_module(self, fullname, path=None):
            return None
    pkgutil.ImpImporter = ImpImporter
    print("Applied pkgutil.ImpImporter compatibility patch for Python 3.12+")

# Now import and run pserve
from pyramid.scripts.pserve import main

if __name__ == '__main__':
    # Add --reload flag for development
    sys.argv.append('--reload')
    
    # Run pserve with the development configuration
    config_file = os.path.join('backend', 'development.ini')
    sys.argv.insert(1, config_file)
    
    print(f"Starting Pyramid development server with {config_file}")
    print("Auto-reload enabled - server will restart on code changes")
    print("Press Ctrl+C to stop")
    print("")
    
    main()