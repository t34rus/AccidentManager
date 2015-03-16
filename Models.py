from datetime import datetime
from AccidentManager import db

class Accident(db.Document):
    created_at = db.DateTimeField(default=datetime.now, required=True)
    description = db.StringField(required=True)
    source = db.StringField(required=True)
    server = db.StringField(required=True)
    is_processed = db.BooleanField(default=False,required=True)

meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'is_processed'],
        'ordering': ['-created_at']
    }