from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    # as_dict 实现对象序列化
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    id = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, unique=False, nullable=False)
    location = db.Column(db.String, unique=False, nullable=False)
    age = db.Column(db.String, unique=False, nullable=False)
    avatar_url = db.Column(db.String, unique=False, nullable=False)


class Book(db.Model):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, unique=False, nullable=False)
    author = db.Column(db.String, unique=False, nullable=False)
    year = db.Column(db.String, unique=False, nullable=False)
    publisher = db.Column(db.String, unique=False, nullable=False)
    img_url_s = db.Column(db.String, unique=False, nullable=False)
    img_url_m = db.Column(db.String, unique=False, nullable=False)
    img_url_l = db.Column(db.String, unique=False, nullable=False)


class Rating(db.Model):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=False, nullable=False)
    book_id = db.Column(db.String, unique=False, nullable=False)
    score = db.Column(db.String, unique=False, nullable=False)
