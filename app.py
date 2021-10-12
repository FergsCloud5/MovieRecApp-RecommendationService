import json

from application_services.recommendationResource import recommendationResource
from flask import Flask, request, Response
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/similarity", methods=["GET"])
def similarity():
    movieTitle = request.form['name']
    recs = recommendationResource.recommend_by_title(movieTitle)
    return recs


@app.route("/recommendations", methods=["GET"])
def recommendations():
    res = recommendationResource.get_all()
    rsp = Response(json.dumps(res), status=200, content_type='application/json')
    return rsp


@app.route("/recommendations/<userID>", methods=["GET", "POST"])
def recommendations_userID(userID):
    if request.method == "GET":
        res = recommendationResource.get_by_id(userID)
        if len(res) != 0:
            rsp = Response(json.dumps(res), status=200, content_type='application/json')
        else:
            rsp = Response("User not found", status=404, content_type='text/plain')
        return rsp
    else:
        try:
            body = request.get_json()
            res = recommendationResource.add_recomendation(body)
            rsp = Response("Created!", status=201, content_type='text/plain')
            return rsp
        except:
            rsp = Response("Error on POST", status=400, content_type='text/plain')
            return rsp


@app.route("/recommendations/<userID>/swipedYes", methods=["GET"])
def recommendations_swiped(userID):
    res = recommendationResource.get_by_swiped(userID)
    rsp = Response(json.dumps(res), status=200, content_type='application/json')
    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0")
