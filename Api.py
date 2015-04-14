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
    take = request.args.get("take", 100, type=int)
    delta = request.args.get("timedelta", 10, type=int)
    grps = Group.objects(modified_at__gte=datetime.now() - timedelta(minutes = delta))
    cnt = grps.count()
    result = []
    for grp in grps.skip(skip).limit(take):
        first = Accident.objects(group=grp).first()
        data = {'id': str(grp.id),
                'caption': grp.caption,
                'stacktrace': grp.stacktrace,
                'source': first.source,
                'environment': '',
                'instances': '',
                'version': '',
                'project': grp.project,
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
                'caption': item.caption,
                'stacktrace': item.stacktrace,
                'address': item.address,
                'project': item.project}
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
        source=request.json.get('source', ""),
        project=request.json.get('project', ""),
        version=request.json.get('version', ""),
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
        project=request.json.get('project', ""),
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
            if d1 > 80 and d2 > 95 and grp.project == accident.project:
                accident.group = grp
                accident.save()
                grp.modified_at = datetime.now
                grp.save()
                break
        if accident.group is None:
            newgroup = Group(
                caption=accident.caption,
                stacktrace=accident.stacktrace,
                project=accident.project
            )
            newgroup.save()
            accident.group = newgroup
            accident.save()

#group()
from Scheduler import *
scheduler.add_job(group, 'interval', seconds=30)

