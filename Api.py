from os import abort
from AccidentManager import app
from flask import Flask, jsonify
from datetime import datetime
from flask import request
from Models import *

@app.route('/api/v1.0/accidents', methods=['GET'])
def get_list():
    skip = request.args.get("skip", 0, type=int)
    take = request.args.get("take", 10, type=int)
    accident = Accident.objects.skip(skip).limit(take)
    cnt = Accident.objects.count()
    result = []
    for item in accident:
        data = {'description': item.description,
                'server': item.server,
                'source': item.source}
        result.append(data)
    return jsonify({'count': cnt, 'result': result})


@app.route('/api/v1.0/accidents', methods=['POST'])
def create():
    if not request.json or not 'description' in request.json:
        abort(400)
    accident = Accident(
        description=request.json.get('description', ""),
        source=request.json.get('source', ""),
        server=request.json.get('server', ""),
    )
    accident.save()
    return jsonify(request.json)
