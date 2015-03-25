from os import abort
from fuzzywuzzy import fuzz
from AccidentManager import app
from flask import Flask, jsonify
from flask import request
from Models import *


@app.route('/api/v1.0/groups', methods=['GET'])
def groups():
    from datetime import datetime,timedelta
    skip = request.args.get("skip", 0, type=int)
    take = request.args.get("take", 10, type=int)
    delta = request.args.get("timedelta", 10, type=int)
    grps = Group.objects(modified_at__gte=datetime.now() - timedelta(minutes = delta))
    cnt = grps.count()
    result = []
    for grp in grps.skip(skip).limit(take):
        data = {'id': str(grp.id),
                'caption': grp.caption,
                'stacktrace': grp.stacktrace,
                'source': grp.source,
                'created_at':grp.created_at,
                'modified_at':grp.modified_at,
                "accidents": Accident.objects(group=grp).count()}
        result.append(data)
    return jsonify({'count': cnt, 'result': result})


@app.route('/api/v1.0/accidents', methods=['GET'])
def accidents():
    skip = request.args.get("skip", 0, type=int)
    take = request.args.get("take", 10, type=int)
    accident = Accident.objects.skip(skip).limit(take)
    cnt = Accident.objects.count()
    result = []
    for item in accident:
        data = {'id': str(item.id),
                'description': item.description,
                'server': item.server,
                'source': item.source}
        result.append(data)
    return jsonify({'count': cnt, 'result': result})


@app.route('/api/v1.0/errors', methods=['POST'])
def errors():
    if not request.json or not 'caption' in request.json:
        abort()
    accident = Accident(
        caption=request.json.get('caption', ""),
        stacktrace=request.json.get('stacktrace', ""),
        host=request.json.get('host', request.host),
        address=request.json.get('address', request.remote_addr),
        source=request.get_data()
    )
    accident.save()
    return jsonify(request.json)

@app.route('/api/v1.0/emails', methods=['POST'])
def emails():
    if not request.json or not 'subject' in request.json:
        abort()
    accident = Accident(
        caption=request.json.get('subject', ""),
        stacktrace=request.json.get('body', ""),
        address=request.json.get('sender', ""),
        source=request.get_data()
    )
    accident.save()
    return jsonify(request.json)

def group():
    import re
    for accident in Accident.objects(group=None).all():
        accidentTrace = re.sub('\b\d+\b', '\\\\', accident.stacktrace)
        for grp in Group.objects.all():
            grpTrace=re.sub('\b\d+\b', '\\\\', grp.stacktrace)
            d1 = fuzz.ratio(grpTrace, accidentTrace)
            d2 = fuzz.ratio(grp.caption, accident.caption)
            if d1 > 80 and d2 > 95:
                accident.group = grp
                accident.save()
                grp.modified_at = datetime.now
                grp.save()
                break
        if accident.group is None:
            print('create group')
            newgroup = Group(
                caption=accident.caption,
                stacktrace=accident.stacktrace,
                source=accident.source
            )
            newgroup.save()
            accident.group = newgroup
            accident.save()

#group()
from Scheduler import *
scheduler.add_job(group, 'interval', seconds=30)

