from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "accident"}
db = MongoEngine(app)

@app.route('/', methods=['GET'])
def index():
    return "Test"

from Api import *

if __name__ == '__main__':
    app.run()
