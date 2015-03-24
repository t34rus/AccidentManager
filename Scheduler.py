from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

jobstores = {'mongo': MongoDBJobStore()}
executors = {'default': ThreadPoolExecutor(50)}
job_defaults = {'coalesce': False,'max_instances': 1}
scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc)
print(scheduler)
scheduler.start()