from flask import request, jsonify, abort, Blueprint
from app import db
from models import User


UserRoutes = Blueprint('UserRoutes', __name__)


@UserRoutes.route('/users/', methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users])


@UserRoutes.route('/user/<user_id>/', methods=["GET"])
def get_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        return jsonify(user.serialize())
    except Exception:
        return "User not found"


@UserRoutes.route('/user/', methods=["POST"])
def make_user():
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
            email=email,
            name=name,
            password=password,
            points=0
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize())
    except Exception as e:
        return str(e)


@UserRoutes.route('/user/<point_id>/addPoints/', methods=["POST"])
def add_points(point_id):
    if not request.json:
        return abort(400)

    if 'points' not in request.json:
        return abort(400)

    points_to_add = request.json['points']

    try:
        user = User.query.filter_by(id=point_id).first()
        user.points += points_to_add
        db.session.commit()
        return jsonify(user.serialize())
    except Exception as e:
        return str(e)
