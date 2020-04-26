from flask import request, jsonify, abort, Blueprint
from app import db
from models import User, Event, EventUsers
from datetime import datetime
from flask_login import current_user

from auth import requires_auth

EventRoutes = Blueprint('EventRoutes', __name__)


@EventRoutes.route('/events/', methods=["GET"])
def get_events():
    events = Event.query.filter(Event.date >= datetime.now())
    return jsonify([e.serialize() for e in events])


@EventRoutes.route('/event', methods=["POST"])
@requires_auth
def create_event():
    if not request.json:
        return abort(400)

    params = ['latitude', 'longitude', 'date']

    for p in params:
        if p not in request.json:
            return abort(400)

    latitude = request.json['latitude']
    longitude = request.json['longitude']
    date = request.json['date']
    leader_id = current_user.id

    try:
        leader = User.query.filter_by(id=leader_id).first()
    except Exception:
        return 'Leader not found'

    try:
        event = Event(
            latitude=latitude,
            longitude=longitude,
            date=datetime.strptime(date, '%Y-%m-%d %H:%M'),
            leader_id=leader_id
        )

        db.session.add(event)
        db.session.commit()

        eventuser = EventUsers(
            user_id=leader_id,
            event_id=event.id
        )
        db.session.add(eventuser)
        db.session.commit()

        return jsonify(event.serialize())
    except Exception as e:
        return str(e)


@EventRoutes.route('/event/<event_id>/', methods=["GET"])
def get_event(event_id):
    try:
        event = Event.query.filter_by(id=event_id).first()
        return jsonify(event.serialize())
    except Exception:
        return 'Event not found'


@EventRoutes.route('/event/<event_id>', methods=["DELETE"])
@requires_auth
def delete_event(event_id):
    try:
        event = Event.query.filter_by(id=event_id).first()
        db.session.delete(event)
        db.session.commit()
        return jsonify('Event successfully deleted')
    except Exception as e:
        return str(e)


@EventRoutes.route('/event/<event_id>', methods=["POST"])
@requires_auth
def join_event(event_id):
    if not request.json:
        return abort(400)

    if 'user_id' not in request.json:
        return abort(400)

    user_id = request.json['user_id']

    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception:
        return 'User not found'

    try:
        eventuser = EventUsers(
            user_id=user_id,
            event_id=event_id
        )

        db.session.add(eventuser)
        db.session.commit()
    except Exception as e:
        return str(e)

    return jsonify('User added successfully')



