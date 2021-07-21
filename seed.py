from app import app
from models import db, User, Comment


db.drop_all()
db.create_all()
