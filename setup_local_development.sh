#!/usr/bin/env bash

# Setup a local development environment with:
# * An up-to-date pip
# * A virtual env with our deps and development-specific deps installed
# * The hnet package installed in editable mode

# Stop on error
set -e
# Clear .venv if an old one exists
echo "Removing existing .venv if it exists"
rm -rf .venv
# Create our venv
echo "Createing new .venv"
python3 -m venv .venv
# Activate the venv
echo "Activating .venv"
source .venv/bin/activate
#use latest and greatest pip
echo "Updating pip"
pip install --upgrade pip
# Install package requirements
echo "Installing requirements"
pip install -r requirements.txt
# Install dev requirements
echo "Installing dev requirements"
pip install -r requirements_dev.txt
# Install the package locally in develop mode
echo "Installing ogdata package with pip --editable"
pip install --editable .
echo "Local dev setup completed."
