from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    points = db.Column(db.Integer)

    def __init__(self, email, name, points=0):
        self.email = email
        self.name = name
        self.points = points

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'points': self.points
        }


class Trash(db.Model):
    __tablename__ = 'trash'

    id = db.Column(db.Integer, primary_key=True)
    trash_type = db.Column(db.String(), nullable=True)
    image = db.Column(db.String())
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    country = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    road = db.Column(db.String(64))
    postcode = db.Column(db.String(10))
    state_code = db.Column(db.String(10))
    country_code = db.Column(db.String(10))

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'trash_type': self.trash_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image': self.image,
            'country': self.country,
            'city': self.city,
            'state': self.state,
            'road': self.road,
            'postcode': self.postcode,
            'state_code': self.state_code,
            'country_code': self.country_code
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    country = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    road = db.Column(db.String(64))
    postcode = db.Column(db.String(10))
    state_code = db.Column(db.String(10))
    country_code = db.Column(db.String(10))
    date = db.Column(db.DateTime)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    members = db.relationship("User", secondary='eventusers')
    leader = db.relationship("User")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date': str(self.date),
            'members': [u.serialize() for u in self.members],
            'leader': self.leader.serialize(),
            'country': self.country,
            'city': self.city,
            'state': self.state,
            'road': self.road,
            'postcode': self.postcode,
            'state_code': self.state_code,
            'country_code': self.country_code
        }


class EventUsers(db.Model):
    __tablename__ = 'eventusers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_id': self.event_id,
        }
