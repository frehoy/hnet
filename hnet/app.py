""" Main app for hnet """

# pylint: disable=no-member

from markupsafe import escape
import flask

from . import sr

app = flask.Flask(__name__)

app.logger.info(f"Starting.")
PROGRAMS = sr.get_all_programs_from_api()
app.logger.info(f"Ready.")


@app.route("/")
def main():
    """ Main endpoint """

    query = flask.request.args.get("query", "")
    if query:
        response = present_results(query)
    else:
        app.logger.info(f"No query, returning plain index.html")
        response = flask.render_template("index.html")
    return response


def present_results(query):
    """ Present the results from a query """
    app.logger.info(f"Presenting results for {query}")
    programs = sr.query_programs(name=escape(query), programs=PROGRAMS)
    for program in programs:
        program.refresh_episodes()

    return flask.render_template("index.html", query=query, programs=programs)
