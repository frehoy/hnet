# Source this file to Set local development environment
# Activate our venv
source .venv/bin/activate
# Set the flask app so "flask run" works
export FLASK_APP=hnet/app.py
# Set mode to development to run in debug mode
export FLASK_ENV=development
