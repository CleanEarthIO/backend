from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String(), nullable=False, unique=False)
    password = db.Column(db.String(), nullable=False, unique=False)
    points = db.Column(db.Integer, server_default=0)

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
            'password': self.password,
            'points': self.points,
		}

class Trash(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    trash_type = db.Column(db.String(), nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, trash_type, latitude, longitude):
        self.trash_type = email
        self.latitude = name
        self.longitude = password

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'trash_type': self.trash_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
		}

