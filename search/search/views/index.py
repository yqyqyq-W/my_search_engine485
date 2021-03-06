"""Search view."""
import flask
from flask import request
import requests
import search


@search.app.route('/', methods=['GET'])
def result():
    """Search result."""
    content = {'results': [], 'ifempty': 1}
    if bool(request.args):
        query = request.args['q']
        weight = request.args['w']
        connection = search.search.model.get_db()
        url = search.app.config["INDEX_API_URL"]
        res = requests.get(url + '?w='
                           + weight + '&q=' + query)
        print(res)
        res = res.json()
        index = 0
        print(res)
        for item in res['hits']:
            if index > 9:
                break
            cur = connection.execute(
                "SELECT * FROM Documents WHERE docid = ?", (item['docid'],)
            )
            content['results'].append(cur.fetchall()[0])
            index = index + 1
        if len(content['results']) != 0:
            content['ifempty'] = 0
    return flask.render_template("index.html", **content)
