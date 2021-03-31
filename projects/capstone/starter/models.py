from flask_sqlalchemy import SQLAlchemy
from datetime import date
from config import database_setup

import json
import os

# -----------------------------------------
# DATABASE SETUP
# -----------------------------------------

db = SQLAlchemy()

database_path = os.environ["DATABASE_URL"]


def setup_db(app, database_path=database_path):
    """connect the Flask application to the SQLAlchemy service"""
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_refresh():
    """drops all tables and create new database"""
    db.drop_all()
    db.create_all()


# -----------------------------------------
# MODEL SETUP
# -----------------------------------------


class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime)
    # actors = db.relationship("Actor", secondary="actor", backref="movie", lazy=True)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {"id": self.id, "title": self.title, "release_date": self.release_date}


class Actor(db.Model):
    __tablename__ = "actor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    gender = db.Column(db.String(120))
    age = db.Column(db.Integer)

    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
        }