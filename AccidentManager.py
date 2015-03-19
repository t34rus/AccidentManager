from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = MongoEngine(app)

@app.route('/', methods=['GET'])
def index():
    return "Test"

from Api import *
from Mail import *
#getmails()

if __name__ == '__main__':
    app.run()

