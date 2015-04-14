from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = MongoEngine(app)

@app.route('/', methods=['GET'])
def index():
    return "Test"

@app.errorhandler(500)
def handle_invalid_usage(error):
    return error.args[0]

from Api import *
from Scheduler import *

if __name__ == '__main__':
    app.debug = True
    app.run()

