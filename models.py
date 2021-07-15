from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):

    __tablename__ = 'users'

    username = db.Column(db.Text, primary_key=True, unique=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.Text, nullable=False)

    first_name = db.Column(db.Text, nullable=False)

    last_name = db.Column(db.Text, nullable=False)

    comment = db.relationship(
        'Comment', backref="user", cascade='all,delete')

    @classmethod
    def signup(cls, username, password, first_name, last_name, email):

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, first_name=first_name, last_name=last_name, email=email)

    @classmethod
    def authenticate(cls, email, password):

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # return user instance
            return user
        else:
            return False


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)

    comment = db.Column(db.Text, nullable=False)

    user_name = db.Column(db.Text, db.ForeignKey('users.username'))
