"""WSGI entry point for PythonAnywhere deployment."""
import sys
import os

# Add the backend directory to the path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Import the FastAPI app
from app.main import app as fastapi_app

# Convert ASGI to WSGI using a2wsgi
from a2wsgi import ASGIMiddleware

# Create WSGI application
application = ASGIMiddleware(fastapi_app)
