from app import db, create_app
from models import User, Trash

app = create_app()

with app.app_context():
    db.create_all()