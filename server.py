import os
import hashlib
import hmac
import json

from flask import request, jsonify, abort, session, redirect, url_for
from functools import wraps
from six.moves.urllib.parse import urlencode
from authlib.integrations.flask_client import OAuth
from app import create_app, db
from models import User, Trash, Event, EventUsers
from flask_cors import CORS

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env')

app = create_app()
cors = CORS(app, resources={r"*": {"origins": "*"}})
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='fteAxw9OIZy1xz7pUpfMu1Pp9HU9MfbF',
    client_secret=os.environ.get('AUTH0'),
    api_base_url='https://dev-ca6857k2.auth0.com',
    access_token_url='https://dev-ca6857k2.auth0.com/oauth/token',
    authorize_url='https://dev-ca6857k2.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    }
)


@app.route('/')
def home():
    return 'hi'


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://127.0.0.1:5000/callback')


@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': 'fteAxw9OIZy1xz7pUpfMu1Pp9HU9MfbF'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/callback')
def callback():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    if not request.json or 'ref' not in request.json:
        return jsonify({'success': False})
    if request.json['ref'] != 'refs/heads/master':
        return jsonify({'success': False})

    key = bytes(os.environ.get('SHUTDOWN_SECRET'), 'UTF-8')
    message = bytes(json.dumps(request.json, separators=(',', ':')), 'UTF-8')

    digest = hmac.new(key, message, hashlib.sha1)
    signature = digest.hexdigest()

    if signature != request.headers.get('x-hub-signature')[5:]:
        return jsonify({'success': False})

    shut_down = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        raise RuntimeError('Shutting down...')
    else:
        shut_down()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated


#########################
### USERS ###############
#########################
@app.route('/users/', methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users])


@app.route('/user/<user_id>/', methods=["GET"])
def get_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        return jsonify(user.serialize())
    except Exception:
        return "User not found"


@app.route('/user/', methods=["POST"])
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


@app.route('/user/<point_id>/addPoints/', methods=["POST"])
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


#########################
### EVENTS ##############
#########################
@app.route('/events/', methods=["GET"])
def get_events():
    events = Event.query.all()
    return jsonify([e.serialize() for e in events])


@app.route('/event', methods=["POST"])
def create_event():
    if not request.json:
        return abort(400)

    params = ['latitude', 'longitude', 'date', 'leader_id']

    for p in params:
        if p not in request.json:
            return abort(400)

    latitude = request.json['latitude']
    longitude = request.json['longitude']
    date = request.json['date']
    leader_id = request.json['leader_id']

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


@app.route('/event/<id>/', methods=["GET"])
def get_event(id):
    try:
        event = Event.query.filter_by(id=id).first()
        return jsonify(event.serialize())
    except Exception:
        return 'Event not found'


@app.route('/event/<event_id>', methods=["DELETE"])
def delete_event(event_id):
    try:
        event = Event.query.filter_by(id=event_id).first()
        db.session.delete(event)
        db.session.commit()
        return jsonify('Event successfully deleted')
    except Exception as e:
        return str(e)


@app.route('/event/<event_id>', methods=["POST"])
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
        return (str(e))

    return jsonify('User added successfully')


#########################
### TRASH ###############
#########################
@app.route('/trashAll/', methods=["GET"])
def get_all_trash():
    trash = Trash.query.all()
    return jsonify([t.serialize() for t in trash])


@app.route('/trash', methods=["POST"])
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


@app.route('/trash/<trash_id>', methods=["DELETE"])
def remove_trash(trash_id):
    try:
        trash = Trash.query.filter_by(id=trash_id).first()
        db.session.delete(trash)
        db.session.commit()
        return jsonify('Trash successfully deleted')
    except Exception as e:
        return str(e)


@app.route('/trashScan', methods=["POST"])
def scan_trash():
    # get image, longitude, latitude from request
    # get all instances of trash in the image
    # crop all instances of trash and classify what type of trash it is
    # add all the trash to the db
    return 'todo'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
