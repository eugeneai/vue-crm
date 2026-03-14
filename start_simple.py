#!/usr/bin/env python3
"""
Start Pyramid server without hupper auto-reload for Python 3.14 compatibility.
"""

import sys
import os

# Add current directory to Python path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Apply the monkey patch FIRST
import pkgutil

if not hasattr(pkgutil, 'ImpImporter'):
    # Create a dummy ImpImporter class for compatibility
    class ImpImporter:
        def find_module(self, fullname, path=None):
            return None
    pkgutil.ImpImporter = ImpImporter
    print("Applied pkgutil.ImpImporter compatibility patch for Python 3.12+")

# Now we can safely import Pyramid
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, scoped_session

def main():
    # Database configuration - use absolute path
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'contacts.db')
    database_url = f'sqlite:///{db_path}'
    
    # Create engine and session
    engine = engine_from_config({'sqlalchemy.url': database_url})
    Session = scoped_session(sessionmaker(bind=engine))
    
    # Create configuration with settings
    settings = {
        'sqlalchemy.url': database_url,
        'pyramid.reload_templates': False,
        'pyramid.debug_authorization': False,
        'pyramid.debug_notfound': False,
        'pyramid.debug_routematch': False,
        'pyramid.default_locale_name': 'en',
        'pyramid.includes': 'pyramid_debugtoolbar',
    }
    
    # Use the main function from backend package
    from backend import main as backend_main
    app = backend_main({}, **settings)
    
    # Monkey patch to add database session to request
    # This is needed because backend_main doesn't set up dbsession in the way we need
    original_request_factory = app.request_factory
    
    def patched_request_factory(environ):
        request = original_request_factory(environ)
        request.dbsession = Session()
        return request
    
    app.request_factory = patched_request_factory
    
    # Cleanup session after request
    def cleanup_session(request):
        if hasattr(request, 'dbsession'):
            Session.remove()
    
    # We'll handle cleanup in the views
    
    print("Using backend.main() for proper Pyramid app configuration")
    
    print("Starting Pyramid server on http://localhost:6543")
    print("Simple mode (no auto-reload) for Python 3.14 compatibility")
    print("Press Ctrl+C to stop")
    print("")
    print("Available endpoints:")
    print("  GET  /                                         - Home page")
    print("  GET  /graphql                                  - GraphQL API (GET for info, POST for queries)")
    print("")
    print("  === REST API ===")
    print("  GET    /api/v1.0/contacts                     - List all contacts")
    print("  POST   /api/v1.0/contacts                     - Create new contact")
    print("  GET    /api/v1.0/contacts/{id}                - Get contact by ID")
    print("  PUT    /api/v1.0/contacts/{id}                - Update contact")
    print("  DELETE /api/v1.0/contacts/{id}                - Delete contact")
    print("")
    print("  === GraphQL API ===")
    print("  query { hello }                               - Test query")
    print("  query { version }                             - API version")
    print("  query { contact(id: \"1\") { id full_name } } - Get contact")
    print("  query { contacts { data { id full_name } } }  - List contacts")
    print("  mutation { create_contact(input: {full_name: \"John\"}) { id } } - Create contact")
    print("")
    print("For detailed API documentation, see STRUCTURES.md")
    
    # Serve the application
    serve(app, host='0.0.0.0', port=6543)

if __name__ == '__main__':
    main()