"""Search view."""
import os
import pathlib
import flask
from flask import request, redirect, session, url_for, send_from_directory
import search
import requests


@search.app.route('/', methods=['GET'])
def result():
    content = {'results': [], 'ifempty': 1}
    if bool(request.args):
        query = request.args['q']
        weight = request.args['w']
        connection = search.search.model.get_db()
        res = requests.get('http://localhost:8001/api/v1/hits/?w=' + weight + '&q=' + query)
        print(res)
        res = res.json()
        index = 0
        print(res)
        for item in res['hits']:
            if index > 10:
                break
            cur = connection.execute(
                "SELECT * FROM Documents WHERE docid = ?", (item['docid'],)
            )
            content['results'].append(cur.fetchall()[0])
            index = index + 1
        if len(content['results']) != 0:
            content['ifempty'] = 0
    return flask.render_template("index.html", **content)
