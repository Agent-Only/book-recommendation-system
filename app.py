import json

from flask import Flask
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy

import itemcf
import top
import usercf

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/book'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

CORS(app, supports_credentials=True)


class User(db.Model):
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    id = db.Column(db.String, primary_key=True)
    location = db.Column(db.String, unique=False, nullable=False)
    age = db.Column(db.String, unique=False, nullable=False)
    avatar_url = db.Column(db.String, unique=False, nullable=False)


@app.route('/')
def hello_world():
    users = User.query.all()
    response = {}
    user_list = []
    for user in users[:100]:
        user_list.append(User.as_dict(user))

    print(user_list)
    response['status'] = 'success'
    response['data'] = user_list

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


@app.route('/item/detail/<item_id>')
def show_item_by_id(item_id):
    response = {}
    data = itemcf.get_item_by_id(item_id)
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
    data = itemcf.get_user_recom_result(user_id)
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
    data = usercf.get_user_recom_result(user_id)
    if data != {}:
        response['status'] = "success"
        response['data'] = data
    else:
        response['status'] = 'fail'
        response['data'] = {}

    return json.dumps(response)


# 基于 itemcf 生成物品间的相似度
@app.route('/itemcf/sims/<item_id>')
def item_sims(item_id):
    return itemcf.get_item_sim_info(item_id)


if __name__ == '__main__':
    app.run()
