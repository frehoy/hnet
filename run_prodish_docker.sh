#!/usr/bin/env bash

# Run the "prod" docker image to make sure gunicorn works and the app looks sane
set -e # Stop on error
# Build the main dockerfile
docker build --file=Dockerfile --tag=hnet --tag frehoy/hnet .
# gunicorn runs on 8000 by default, expose it on 5000
docker run -p 5000:8000 hnet:latest
