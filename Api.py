from os import abort
from fuzzywuzzy import fuzz
from AccidentManager import app
from flask import Flask, jsonify
from flask import request
from Models import *
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = '*'
            h['Access-Control-Allow-Methods'] = '*'
            h['Access-Control-Allow-Headers'] = '*'
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/1/groups', methods=['GET'])
@crossdomain(origin='*')
def groups():
    from datetime import datetime,timedelta
    skip = request.args.get("skip", 0, type=int)
    take = request.args.get("take", 100, type=int)
    delta = request.args.get("timedelta", 10, type=int)
    req_project = request.args.get("project", None, type=str)
    grps = Group.objects(modified_at__gte=datetime.now() - timedelta(minutes = delta))
    grps = grps(project=req_project)
    result = []
    for grp in grps.skip(skip).limit(take):
        last = Accident.objects(group=grp).order_by('-created_at').first()
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
    return jsonify({'count': grps.count(), 'result': result})


@app.route('/1/accidents', methods=['GET'])
@crossdomain(origin='*')
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


@app.route('/sentry/api/1/store/', methods=['POST','GET'])
@crossdomain(origin='*')
def sentry():
    import json
    import urllib.parse
    sentry_data = urllib.parse.unquote(request.values['sentry_data'])
    sentry_data_json = json.loads(sentry_data)
    exception = sentry_data_json['exception']
    stacktrace = json.dumps(sentry_data_json['stacktrace'])
    logger = sentry_data_json['logger']
    release = sentry_data_json['release']
    project = request.values['sentry_key']

    accident = Accident(
        caption=exception['value'].strip(),
        stacktrace=stacktrace,
        source=logger.strip(),
        version=release.strip(),
        project=project.strip(),
        request=request.get_data()
    )
    accident.save()
    return jsonify({'accident': accident})

@app.route('/1/errors', methods=['POST'])
@crossdomain(origin='*')
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
    return jsonify({'accident': accident})


@app.route('/1/emails', methods=['POST'])
@crossdomain(origin='*')
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
    return jsonify({'accident': accident})


@app.route('/newrelic/1/<project_key>', methods=['POST'])
@crossdomain(origin='*')
def newrelic(project_key):
    import json
    if not request.json or not 'short_description' in request.json:
        abort()
    accident = Accident(
        caption=request.json.get('short_description', "").strip(),
        stacktrace=json.dumps(request.json),
        address=request.json.get('alert_url', "").strip(),
        host=request.json.get('application_name', "").strip(),
        project=project_key.strip(),
        request=request.get_data()
    )
    accident.save()
    return jsonify({'accident': accident})


def group():
    import re
    for accident in Accident.objects(group=None):
        accident_caption = accident.caption
        accident_caption = re.sub('\d+', '', accident_caption)
        for grp in Group.objects(project=accident.project):
            if grp.host == accident.host and \
               grp.address == accident.address and \
               grp.source == accident.source and \
               grp.version == accident.version:
                grp_caption = grp.caption
                grp_caption = re.sub('\d+', '', grp_caption)
                ratio = fuzz.ratio(grp_caption, accident_caption)
                if ratio > 95:
                    accident.group = grp
                    accident.save()
                    grp.modified_at = datetime.now
                    grp.save()
                    break
        if accident.group is None:
            new_group = Group(
                caption=accident.caption,
                host=accident.host,
                address=accident.address,
                source=accident.source,
                project=accident.project,
                version=accident.version
            )
            new_group.save()
            accident.group = new_group
            accident.save()

def deleteOld():
    #remove ald accident
    for acdt in Accident.objects(created_at__lte=datetime.now() - timedelta(days = 21)):
        acdt.delete()
    #remove group without new accident
    for grp in Group.objects(modified_at__lte=datetime.now() - timedelta(days = 3)):
        for acdt in Accident.objects(group=grp):
            acdt.delete()
        grp.delete()

from Scheduler import *
scheduler.add_job(group, 'interval', seconds=15)
scheduler.add_job(deleteOld, 'interval', minutes=15)

