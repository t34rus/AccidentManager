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
    delta = request.args.get("timedelta", 10, type=int)
    grps = Group.objects(modified_at__gte=datetime.now() - timedelta(minutes = delta))
    cnt = grps.count()
    result = []
    for grp in grps.skip(skip).limit(take):
        last = Accident.objects(group=grp).last()
        last_stacktrace = ''
        if (last is not None):
            last_stacktrace = last.stacktrace
        data = {'id': str(grp.id),
                'caption': grp.caption,
                'stacktrace': last_stacktrace,
                'source': grp.source,
                'environment': {'hostname': grp.host,'address': grp.address},
                'version': grp.version,
                'project': grp.project,
                'created_at':grp.created_at,
                'modified_at':grp.modified_at,
                "instances": Accident.objects(group=grp).count()}
        result.append(data)
    return jsonify({'count': cnt, 'result': result})


@app.route('/api/v1.0/accidents', methods=['GET'])
def accidents():
    skip = request.args.get("skip", 0, type=int)
    take = request.args.get("take", 100, type=int)
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
    return jsonify({'count': cnt, 'result': accident})


@app.route('/api/v1.0/errors', methods=['POST'])
def errors():
    if not request.json or not 'caption' in request.json:
        abort()
    accident = Accident(
        caption=request.json.get('caption', '').strip(),
        stacktrace=request.json.get('stacktrace', '').strip(),
        host=request.json.get('host', request.host).strip(),
        address=request.json.get('address', request.remote_addr).strip(),
        source=request.json.get('source', '').strip(),
        project=request.json.get('project', '').strip(),
        version=request.json.get('version', '').strip(),
        request=request.get_data()
    )
    accident.save()
    return jsonify(request.json)

@app.route('/api/v1.0/emails', methods=['POST'])
def emails():
    if not request.json or not 'subject' in request.json:
        abort()
    accident = Accident(
        caption=request.json.get('subject', "").strip(),
        stacktrace=request.json.get('body', "").strip(),
        address=request.json.get('sender', "").strip(),
        project=request.json.get('project', "").strip(),
        request=request.get_data()
    )
    accident.save()
    return jsonify(request.json)

def group():
    import re
    for accident in Accident.objects(group=None).all():
        accident_caption = re.sub('\b\d+\b', '\\\\', accident.caption)
        for grp in Group.objects.all():
            if grp.host.lower() == accident.host.lower() and \
               grp.address.lower() == accident.address.lower() and \
               grp.source.lower() == accident.source.lower() and \
               grp.project.lower() == accident.project.lower() and \
               grp.version.lower() == accident.version.lower():
                grp_caption=re.sub('\b\d+\b', '\\\\', grp.caption)
                ratio = fuzz.ratio(grp_caption, accident_caption)
                if ratio > 95:
                    accident.group = grp
                    accident.save()
                    grp.modified_at = datetime.now
                    grp.save()
                break
        if accident.group is None:
            newgroup = Group(
                caption=accident.caption,
                host=accident.host,
                address=accident.address,
                source=accident.source,
                project=accident.project,
                version=accident.version
            )
            newgroup.save()
            accident.group = newgroup
            accident.save()

from Scheduler import *
scheduler.add_job(group, 'interval', seconds=30)

