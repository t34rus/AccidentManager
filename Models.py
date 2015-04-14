from datetime import datetime
from AccidentManager import db


class Accident(db.Document):
    created_at = db.DateTimeField(default=datetime.now, required=True)
    caption = db.StringField(required=True)
    stacktrace = db.StringField(required=False)
    host = db.StringField(required=False)
    address = db.StringField(required=False)
    source = db.StringField(required=False)
    project = db.StringField(required=False)
    version = db.StringField(required=False)
    group = db.ReferenceField("Group",required=False)

meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at'],
        'ordering': ['-created_at']
    }

class Group(db.Document):
    created_at = db.DateTimeField(default=datetime.now, required=True)
    modified_at = db.DateTimeField(default=datetime.now, required=True)
    caption = db.StringField(required=True)
    stacktrace = db.StringField(required=False)
    project = db.StringField(required=False)

meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at'],
        'ordering': ['-created_at']
    }