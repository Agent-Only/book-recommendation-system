import itemcf
import usercf
import json
from flask import Flask
from flask_cors import *

app = Flask(__name__)

CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/itemcf/recoms/<user_id>')
def user_recoms(user_id):
    respones = {}
    data = itemcf.get_user_recom_result(user_id)
    if(data != {}):
      respones["status"] = "success"
      respones["data"] = data
    else:
      respones["status"] = "fail"
      respones["data"] = {}

    return json.dumps(respones)


@app.route('/itemcf/sims/<item_id>')
def item_sims(item_id):
    return itemcf.get_item_sim_info(item_id)


if __name__ == '__main__':
    app.run()
