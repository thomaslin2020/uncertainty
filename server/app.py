from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return 'Hello World'
    if request.method == 'POST':
        return 'Hello World'


if __name__ == '__main__':
    app.run(port='5001')
