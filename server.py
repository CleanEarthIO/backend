from flask import Flask, request, jsonify, abort

from app import create_app, db
from models import User, Trash

import os

app = create_app()

@app.route('/')
def home():
    return 'hi'

@app.route('/users/', methods=["GET"])
def getUsers():
    users = User.query.all()
    return jsonify([u.serialize() for u in users])

@app.route('/user/<id>/', methods=["GET"])
def getUser(id):
    try:
        user = User.query.filter_by(id = id).first()
        return jsonify(user.serialize())
    except Exception:
        return("User not found")

@app.route('/user/', methods=["POST"])
def makeUser():
    if not request.json:
        return abort(400)

    params = ['email', 'name', 'password']

    for p in params:
        if p not in request.json:
            return abort(400)

    email = request.json['email']
    name = request.json['name']
    password = request.json['password']

    try:
        user = User(
            email = email,
            name = name,
            password = password,
            points = 0
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize())
    except Exception as e:
        return(str(e))

@app.route('/user/<id>/addPoints/', methods=["POST"])
def addPoints(id):
    if not request.json:
        return abort(400)

    if 'points' not in request.json:
        return abort(400)

    pointsToAdd = request.json['points']

    try:
        user = User.query.filter_by(id = id).first()
        user.points += pointsToAdd
        db.session.commit()
        return jsonify(user.serialize())
    except Exception as e:
        return(str(e))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
