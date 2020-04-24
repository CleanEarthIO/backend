from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    password = db.Column(db.String(), nullable=False, unique=False)
    points = db.Column(db.Integer)

    def __init__(self, email, name, password, points):
        self.email = email
        self.name = name
        self.password = password
        self.points = points

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'points': self.points,
        }


class Trash(db.Model):
    __tablename__ = 'trash'

    id = db.Column(db.Integer, primary_key=True)
    trash_type = db.Column(db.String(), nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, trash_type, latitude, longitude):
        self.trash_type = trash_type
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'trash_type': self.trash_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    date = db.Column(db.Date)
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
            'date': self.date,
            'members': [u.serialize() for u in self.members],
            'leader': self.leader.serialize(),
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
