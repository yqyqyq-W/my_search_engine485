"""Search view."""
import os
import pathlib
import flask
from flask import request, redirect, session, url_for, send_from_directory
import search
import requests


@search.app.route('/', methods=['GET'])
def result():
    query = request.form['q']
    weight = request.form['w']
    connection = search.search.model.get_db()
    res = requests.get('http://localhost:8000/api/v1/hits/?w=' + weight + '&q=' + query)
    index = 0
    content = {'results': [], 'ifempty': 0}
    for item in res:
        if index > 10:
            break
        cur = connection.execute(
            "SELECT * FROM Documents WHERE docid = ?", (item['docid'],)
        )
        content['results'].append(cur.fetchall()[0])
        index = index + 1
    if len(content['results']) == 0:
        content['ifempty'] = 1
    return flask.render_template("index.html", **content)
