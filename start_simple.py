#!/usr/bin/env python3
"""
Start Pyramid server without hupper auto-reload for Python 3.14 compatibility.
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

# Now we can safely import Pyramid
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve

def main():
    # Create a simple Pyramid app for testing
    config = Configurator()
    
    # Add a simple route
    config.add_route('home', '/')
    
    def home_view(request):
        return Response('CRM API Server is running!')
    
    config.add_view(home_view, route_name='home')
    
    # Add API routes
    config.add_route('api_v1_contacts', '/api/v1.0/contacts')
    config.add_route('api_v1_contact', '/api/v1.0/contacts/{id}')
    config.add_route('api_v1_meetings', '/api/v1.0/meetings')
    config.add_route('api_v1_meeting', '/api/v1.0/meetings/{id}')
    config.add_route('api_v1_notes', '/api/v1.0/notes')
    config.add_route('api_v1_note', '/api/v1.0/notes/{id}')
    config.add_route('api_v1_reports_upcoming', '/api/v1.0/reports/upcoming')
    config.add_route('api_v1_reports_history', '/api/v1.0/reports/history')
    
    # Create the app
    app = config.make_wsgi_app()
    
    print("Starting Pyramid server on http://localhost:6543")
    print("Simple mode (no auto-reload) for Python 3.14 compatibility")
    print("Press Ctrl+C to stop")
    print("")
    print("Available endpoints:")
    print("  GET  /                         - Server status")
    print("  GET  /api/v1.0/contacts        - List contacts")
    print("  POST /api/v1.0/contacts        - Create contact")
    print("  GET  /api/v1.0/contacts/{id}   - Get contact by ID")
    print("  PUT  /api/v1.0/contacts/{id}   - Update contact")
    print("  DELETE /api/v1.0/contacts/{id} - Delete contact")
    print("  ... and more (see STRUCTURES.md)")
    
    # Serve the application
    serve(app, host='0.0.0.0', port=6543)

if __name__ == '__main__':
    main()