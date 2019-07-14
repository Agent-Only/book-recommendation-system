import json

from flask import Flask, request
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

import itemcf
import top
import usercf
import util.db_reader as reader

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/book'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

CORS(app, supports_credentials=True)


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


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/login', methods=['POST'])
def login():
    response = {}
    user_id = request.form['userId']
    password = request.form['password']
    login_user = User.query.filter_by(id=user_id).first()

    if login_user is not None:
        if login_user.password == password:
            response['status'] = 'success'
            response['data'] = User.as_dict(login_user)
            return json.dumps(response)

        else:
            response['status'] = 'fail'
            response['errMsg'] = '密码不正确'
            return json.dumps(response)

    else:
        response['status'] = 'fail'
        response['errMsg'] = '用户名不存在'
        return json.dumps(response)


# 显示热门图书
@app.route('/top')
def show_top():
    response = {}
    data = top.get_top_book()
    if data != {}:
        response["status"] = "success"
        response["data"] = data
    else:
        response["status"] = "fail"
        response["data"] = {}

    return json.dumps(response)


# 基于 itemcf 生成用户推荐结果
@app.route('/itemcf/recoms/<user_id>')
def recoms_by_item(user_id):
    response = {}
    data = itemcf.get_user_recom_result(
        user_id, user_like=get_user_like(), user_rate=get_user_rate(), item_full_info=get_item_info())
    if data != {}:
        response["status"] = "success"
        response["data"] = data
    else:
        response["status"] = "fail"
        response["data"] = {}

    return json.dumps(response)


# 基于 usercf 生成用户推荐结果
@app.route('/usercf/recoms/<user_id>')
def recoms_by_user(user_id):
    response = {}

    data = usercf.get_user_recom_result(
        user_id, user_rate=get_user_rate(), item_full_info=get_item_info())
    if data != {}:
        response['status'] = "success"
        response['data'] = data
    else:
        response['status'] = 'fail'
        response['data'] = {}

    return json.dumps(response)


# 查询用户的评分列表
@app.route('/rating/me/<user_id>')
def show_specific_user_rate(user_id):
    ratings = Rating.query.filter_by(user_id=user_id)
    print(ratings)
    rating_list = []
    response = {}
    for row in ratings:
        tmp_dict = Rating.as_dict(row)
        # 过滤评分为 0 的图书
        if tmp_dict['score'] == '0':
            continue
        rating_list.append(tmp_dict)

    if ratings is not []:
        response['status'] = 'success'
        response['data'] = rating_list

    return json.dumps(response)


# 添加用户评分
@app.route('/rating/add', methods=['POST'])
def add_rate():
    user_id = request.form['userId']
    book_id = request.form['bookId']
    score = request.form['score']

    rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()

    if rating is not None:
        rating.score = score
    else:
        db.session.add(Rating(user_id=user_id, book_id=book_id, score=score))

    db.session.commit()

    response = {'status': 'success'}

    return json.dumps(response)


# 根据字段查询书籍
@app.route('/book/search/<content>')
def search_book(content):
    rows = Book.query.filter(
        or_(Book.id.like("%" + content + "%") if content is not None else "",
            Book.title.like("%" + content + "%") if content is not None else "",
            Book.author.like("%" + content + "%") if content is not None else "",
            Book.publisher.like("%" + content + "%") if content is not None else "",
            Book.year.like("%" + content + "%") if content is not None else "")
    ).limit(100)

    response = {}
    book_list = []
    for row in rows:
        book_list.append(Book.as_dict(row))

    if len(book_list) is not 0:
        response['status'] = 'success'
        response['data'] = book_list
    else:
        response['status'] = 'fail'
        response['data'] = {}

    return json.dumps(response)


# 查询用户对某本书的评分
@app.route('/rating/user/<user_id>/<book_id>')
def rating_user_book(user_id, book_id):
    row = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()

    response = {}
    if row is not None:
        rating = Rating.as_dict(row)
        response = {'status': 'success', 'data': rating}

    else:
        response = {'status': 'null', 'data': {}}

    return json.dumps(response)


@app.route('/test')
def test_user():
    rows = User.query.filter(
        User.location.like("%" + "new" + "%") if "new" is not None else ""
    ).all()
    response = {}
    user_list = []
    for row in rows:
        user_list.append(User.as_dict(row))

    response['data'] = user_list

    return json.dumps(response)


@app.route('/userlike')
def show_user_like():
    rows = Rating.query.all()
    rating_list = []
    for row in rows:
        rating_list.append(Rating.as_dict(row))
    user_like_dict = reader.get_user_like(rating_list)

    return json.dumps(user_like_dict)


@app.route('/userrate')
def show_user_rate():
    rows = Rating.query.all()
    rating_list = []
    for row in rows:
        rating_list.append(Rating.as_dict(row))
    user_rate_dict = reader.get_user_rate(rating_list)

    return json.dumps(user_rate_dict)


@app.route('/iteminfo')
def show_item_info():
    rows = Book.query.all()
    book_list = []
    for row in rows:
        book_list.append(Book.as_dict(row))
    item_info_dict = reader.get_item_full_info(book_list)

    return json.dumps(item_info_dict)


@app.route('/user')
def user_query_all():
    rows = User.query.all()
    response = {}
    user_list = []
    for row in rows[:100]:
        user_list.append(User.as_dict(row))

    response['status'] = 'success'
    response['data'] = user_list

    return json.dumps(response)


@app.route('/book')
def book_query_all():
    rows = Book.query.all()
    response = {}
    book_list = []
    for row in rows[:100]:
        book_list.append(Book.as_dict(row))

    response['status'] = 'success'
    response['data'] = book_list

    return json.dumps(response)


@app.route('/rating')
def rating_query_all():
    rows = Rating.query.all()
    response = {}
    rating_list = []
    for row in rows[:100]:
        rating_list.append(Rating.as_dict(row))

    response['status'] = 'success'
    response['data'] = rating_list

    return json.dumps(response)


def get_user_like():
    rows = Rating.query.all()
    rating_list = []
    for row in rows:
        rating_list.append(Rating.as_dict(row))
    user_like_dict = reader.get_user_like(rating_list)

    return user_like_dict


def get_user_rate():
    rows = Rating.query.all()
    rating_list = []
    for row in rows:
        rating_list.append(Rating.as_dict(row))
    user_rate_dict = reader.get_user_rate(rating_list)

    return user_rate_dict


def get_item_info():
    rows = Book.query.all()
    book_list = []
    for row in rows:
        book_list.append(Book.as_dict(row))
    item_info_dict = reader.get_item_full_info(book_list)

    return item_info_dict


if __name__ == '__main__':
    app.run()
