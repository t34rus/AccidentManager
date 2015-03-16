from os import abort
from fuzzywuzzy import fuzz
from AccidentManager import app
from flask import Flask, jsonify
from datetime import datetime
from flask import request
from Models import *

@app.route('/api/v1.0/groups', methods=['GET'])
def groups():
    skip = request.args.get("skip", 0, type=int)
    take = request.args.get("take", 10, type=int)
    cnt = Group.objects.count()
    result = []
    for grp in Group.objects.skip(skip).limit(take):
        data = {'id': str(grp.id),
                'description': grp.description,
                'server': grp.server,
                'source': grp.source,
                "accidents": Accident.objects(group = grp).count()
                }
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

import re
@app.route('/api/v1.0/accidents', methods=['POST'])
def create():
    if not request.json or not 'description' in request.json:
        abort(400)
    if not request.json or not 'description' in request.json:
        abort(400)
    accident = Accident(
        description=request.json.get('description', ""),
        source=request.json.get('source', ""),
        server=request.json.get('server', ""),
    )
    desc = re.Sub('\b\d+\b', '', accident.description)
    for grp in Group.objects.all():
        if grp.server == accident.server:
            d1 = fuzz.ratio(re.Sub('\b\d+\b', '', grp.description), desc)
            d2 = fuzz.ratio(grp.source, accident.source)
            if d1 > 80 and d2 > 95:
                accident.group = grp
    if accident.group is None:
        newgroup = Group(
            description=accident.description,
            source=accident.source,
            server=accident.server,
        )
        newgroup.save()
        accident.group = newgroup
    accident.save()
    return jsonify(request.json)
