#!/usr/bin/env python3
"""
Simple wrapper to run Pyramid server without auto-reload for Python 3.14 compatibility.
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

# Now we need to import the application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from pyramid.config import Configurator
    from waitress import serve
    import backend.models
    print("Imports successful")
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("  pip install -r backend/requirements.txt")
    sys.exit(1)

def main():
    # Create configuration
    config = Configurator()
    
    # Setup database
    from sqlalchemy import engine_from_config
    from backend.models import Base
    
    # Read configuration
    config_file = os.path.join('backend', 'development.ini')
    
    # For simplicity, let's use a basic configuration
    settings = {
        'sqlalchemy.url': 'sqlite:///../database/contacts.db',
        'pyramid.reload_templates': True,
        'pyramid.debug_authorization': False,
        'pyramid.debug_notfound': False,
        'pyramid.debug_routematch': False,
        'pyramid.default_locale_name': 'en',
    }
    
    config = Configurator(settings=settings)
    
    # Include Pyramid extensions
    config.include('pyramid_debugtoolbar')
    
    # Setup routes
    config.add_route('home', '/')
    config.add_route('api_v1_contacts', '/api/v1.0/contacts')
    config.add_route('api_v1_contact', '/api/v1.0/contacts/{id}')
    config.add_route('api_v1_meetings', '/api/v1.0/meetings')
    config.add_route('api_v1_meeting', '/api/v1.0/meetings/{id}')
    config.add_route('api_v1_notes', '/api/v1.0/notes')
    config.add_route('api_v1_note', '/api/v1.0/notes/{id}')
    config.add_route('api_v1_reports_upcoming', '/api/v1.0/reports/upcoming')
    config.add_route('api_v1_reports_history', '/api/v1.0/reports/history')
    
    # Scan for views
    config.scan('backend.views.api.v1')
    
    # Create app
    app = config.make_wsgi_app()
    
    print("Starting Pyramid server on http://localhost:6543")
    print("No auto-reload (simple mode for Python 3.14 compatibility)")
    print("Press Ctrl+C to stop")
    print("")
    
    # Serve application
    serve(app, host='0.0.0.0', port=6543)

if __name__ == '__main__':
    main()