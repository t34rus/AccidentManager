from flask import Flask
from flask.ext.mongoengine import MongoEngine
from Celery import *

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "accident"}
app.config.update(
    CELERY_BROKER_URL='mongodb://localhost:27017/accident',
)
db = MongoEngine(app)
celery = make_celery(app)

@app.route('/', methods=['GET'])
def index():
    return "Test"

from Api import *

@celery.task()
def add_together(a, b):
    return a + b

if __name__ == '__main__':
    app.run()

