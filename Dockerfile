FROM python:3.8

# Do all the work in /hnet/ of the image
WORKDIR /hnet
# Add requirements and install first so rebuilds can cache better
ADD requirements.txt /hnet/requirements.txt
RUN pip install -r requirements.txt
# Add the package diretory
ADD hnet/ /hnet/hnet/
# Add the setup file
ADD setup.py /hnet/
# README.md is sourced by setup.py so add that to
ADD README.md /hnet/
# Install as a package
RUN pip install .

#ENV FLASK_APP hnet/app.py
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0", "hnet.app:app"]