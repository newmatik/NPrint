"""Flask APP configuration."""
from os import environ, path
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

# General Config
ENVIRONMENT = environ.get("ENVIRONMENT")
FLASK_APP = environ.get("FLASK_APP")
FLASK_DEBUG = environ.get("FLASK_DEBUG")
FLASK_RUN_HOST=environ.get("FLASK_RUN_HOST")
FLASK_RUN_PORT=environ.get("FLASK_RUN_PORT")
SECRET_KEY = environ.get("SECRET_KEY")
API_KEY = environ.get("API_KEY")
