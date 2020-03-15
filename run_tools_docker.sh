#!/usr/bin/env sh


# Run the CI suite on docker

clear

# Stop on error
set -e

# Build the "prod" Dockerfile with just the app
echo "Building Dockerfile"
docker build --file=Dockerfile --tag=hnet --tag=latest .
# Build another image on top of that with all the dev-specific tools
# This keeps all the dev specific stuff from the prod image and keeps it smaller.
echo "Building Dockerfile_dev"
docker build --file=Dockerfile_dev --tag=hnet-dev --tag=latest .

# Run black on the package and tests
echo "Running black"
docker run hnet-dev:latest black -l 79 hnet --check
docker run hnet-dev:latest black -l 79 tests --check
# Run mypy on package and tests
echo "Running mypy"
docker run hnet-dev:latest mypy hnet
docker run hnet-dev:latest mypy tests

# Run test coverage
echo "Running tests"
# Coverage run and coverage report need to be run in a single command
docker run hnet-dev:latest /bin/bash -c "coverage run --source hnet -m pytest tests/ ; coverage report --show-missing"

# Basic linting
echo "Running flake8"
docker run hnet-dev:latest flake8 hnet
docker run hnet-dev:latest flake8 tests

# Run pylint last as it is the pickiest
echo "Running pylint"
docker run hnet-dev:latest pylint --rcfile=.pylintrc hnet
docker run hnet-dev:latest pylint --rcfile=.pylintrc tests

git status

# If all the tests and lints are OK:
echo "Great success"