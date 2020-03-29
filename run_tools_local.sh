#!/usr/bin/env bash

set -e # Fail on error
clear
echo "Setting env"
source local_dev_env.sh
echo "Running black"
black -l 79 hnet
black -l 79 tests
echo "Running pytest with coverage"
coverage run --source hnet -m pytest tests/
coverage report --show-missing
echo "Running mypy type checker"
mypy hnet
mypy tests
echo "pylint"
pylint --rcfile=.pylintrc hnet
pylint --rcfile=.pylintrc tests
echo "flake8"
flake8 ogdata
flake8 tests
echo "git status"
git status
echo "Great success"
