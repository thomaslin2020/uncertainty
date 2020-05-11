from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from server.scripts.operators import *

app = Flask(__name__)
# app.config[
#     'SQLALCHEMY_DATABASE_URI'] = "postgres://gslwpmqsclkhow:e168d5f8c4d218190ba52672c1435167a090d2d08acbcb79beea24a1f8cfb80e@ec2-54-81-37-115.compute-1.amazonaws.com:5432/dduagbh5uvjp1u"
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World'


@app.route('/api/calculate', methods=['POST'])
def calculate():
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
    app.run(port='5000', debug=True)
