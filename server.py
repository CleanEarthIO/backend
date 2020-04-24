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

@app.route('/user/<id>/addPoints', methods=["POST"])
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

@app.route('/trashAll/', methods=["GET"])
def getAllTrash():
    trash = Trash.query.all()
    return jsonify([t.serialize() for t in trash])

@app.route('/trash', methods=["POST"])
def createTrash():
    if not request.json:
        return abort(400)

    params = ['trash_type', 'latitude', 'longitude']

    for p in params:
        if p not in request.json:
            return abort(400)

    trash_type = request.json['trash_type']
    latitude = request.json['latitude']
    longitude = request.json['longitude']

    try:
        trash = Trash(
            trash_type = trash_type,
            latitude = latitude,
            longitude = longitude
        )
        db.session.add(trash)
        db.session.commit()
        return jsonify(trash.serialize())
    except Exception as e:
        return(str(e))

@app.route('/trash/<id>', methods=["DELETE"])
def removeTrash(id):    
    try:
        trash = Trash.query.filter_by(id = id).first()
        db.session.delete(trash)
        db.session.commit()
        return jsonify(trash.serialize())
    except Exception as e:
        return(str(e))

@app.route('/trashScan', methods=["POST"])
def scanTrash():
    # get image, longitude, latitude from request
    # get all instances of trash in the image
    # crop all instances of trash and classify what type of trash it is
    # add all the trash to the db
    return 'todo'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
