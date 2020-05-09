from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from server.scripts.operators import *
from server.scripts.constants import *
import math

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

CORS(app, resources={r'/*': {'origins': '*'}})


# noinspection PyBroadException
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return 'Hello World'
    if request.method == 'POST':
        U = None
        if request.form['method'] == 'simple':
            U = SimpleUncertainty
        else:
            U = StdUncertainty
        try:
            return str(eval(request.form['equation']))
        except:
            return 'Please fix your equation'


if __name__ == '__main__':
    app.run(port='5001')
