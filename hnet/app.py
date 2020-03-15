""" Main app for hnet """
import flask

app = flask.Flask(__name__)


@app.route("/")
def hello_world():
    """ Just say hello """
    return "Hello world!"


if __name__ == "__main__":
    app.run()
