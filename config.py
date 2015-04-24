from pymongo import read_preferences
MONGODB_SETTINGS = {'db': "accident",'read_preference': read_preferences.ReadPreference.PRIMARY}
