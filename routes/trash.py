from flask import request, jsonify, abort, Blueprint
from app import db
from models import Trash


TrashRoutes = Blueprint('TrashRoutes', __name__)


@TrashRoutes.route('/trashAll/', methods=["GET"])
def get_all_trash():
    trash = Trash.query.all()
    return jsonify([t.serialize() for t in trash])


@TrashRoutes.route('/trash', methods=["POST"])
def create_trash():
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
            trash_type=trash_type,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(trash)
        db.session.commit()
        return jsonify(trash.serialize())
    except Exception as e:
        return str(e)


@TrashRoutes.route('/trash/<trash_id>', methods=["DELETE"])
def remove_trash(trash_id):
    try:
        trash = Trash.query.filter_by(id=trash_id).first()
        db.session.delete(trash)
        db.session.commit()
        return jsonify('Trash successfully deleted')
    except Exception as e:
        return str(e)


@TrashRoutes.route('/trashScan', methods=["POST"])
def scan_trash():
    # get image, longitude, latitude from request
    # get all instances of trash in the image
    # crop all instances of trash and classify what type of trash it is
    # add all the trash to the db
    return 'todo'
