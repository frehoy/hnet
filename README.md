# hnet

A simple flask app that queries the SR API for programs by name and gets audio links to the latest episodes of the matching programs.

## Getting started

### Local

Ensure you have python3 with pip on your path.
To install the package and requirements to a virtual environment in ./.venv run

    ./setup_local_development.sh

To run a local debug server on localhost:5000 run

    ./run_debug_local.sh

and to run the test suite run

    ./run_tools_local.sh

### Dockerised

To run a docker container of the "prod" image with gunicorn at localhost:5000 run

    ./run_prodish_docker.sh

and to run the test/lint suite in docker run

    ./run_tools_docker.sh
