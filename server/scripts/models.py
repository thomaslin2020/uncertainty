from datetime import datetime

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://vkqaytdz:MZX9H4J6Y8c7L8Al5XAmcENBoR7QFL3k@raja.db.elephantsql.com:5432/vkqaytdz"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Calculation(db.Model):
    __tablename__ = 'calculation'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    equation = db.Column(db.Text)
    mode = db.Column(db.Text)
    show_graph = db.Column(db.Boolean)

    def __init__(self, date, equation, mode, show_graph):
        self.date = date
        self.equation = equation
        self.mode = mode
        self.show_graph = show_graph

    def __repr__(self):
        return f"<Equation {self.equation}>"


db.create_all()
temp = Calculation(date=datetime.utcnow(), equation="3", mode="simple", show_graph=True)
db.session.add(temp)
db.session.commit()
