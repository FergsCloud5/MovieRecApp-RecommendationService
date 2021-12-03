import json
import logging

from application_services.recommendationResource import recommendationResource
from middleware.security import Security
from flask import Flask, request, Response, session, url_for, redirect
from flask_cors import CORS
from flask_login import (LoginManager, login_required)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

application  = Flask(__name__)
CORS(application)
sec = Security()

application.secret_key = "my secret"

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'google.login'

gb = sec.get_google_blueprint()
application.register_blueprint(gb, url_prefix="/login")

# zip -r -X Archive.zip *

@application.before_request
def before_request():
    print("before_request is running!")
    print("request.path:", request.path)

    # a_ok = sec.check_authentication(request.path)
    # print("a_ok:", a_ok)
    # if a_ok[0] != 200:
    #     session["next_url"] = request.base_url
    #     return redirect(url_for('google.login'))


@application.after_request
def after_request(response):
    return response


@application.route("/", methods=["GET"])
def home():
    next_url = session.get("next_url", None)
    if next_url:
        session.pop("next_url", None)
        return redirect(next_url)
    return "Hello, welcome to the recommendation service!"


@application.route("/similarity", methods=["GET"])
def similarity():

    movieID = request.args.get("movieID", None)
    movieTitle = request.args.get("movieTitle", None)

    try:
        if movieID is not None:
            recs = recommendationResource.recommend_by_id(movieID)
            return Response(json.dumps(recs), status=200, content_type='application/json')
        elif movieTitle is not None:
            recs = recommendationResource.recommend_by_title(movieTitle)
            return Response(json.dumps(recs), status=200, content_type='application/json')
        else:
            return Response("Please provide either movieID or movieTitle in query string.",
                            status=400,
                            content_type='text/plain')
    except LookupError as e:
        return Response("Lookup error", status=404, content_type='text/plain')
    except Exception as e:
        logger.error("Error on /similarity", str(e))
        return Response("Internal Server Error", status=500, content_type='text/plain')



@application.route("/recommendations", methods=["GET"])
def recommendations():
    try:
        data = recommendationResource.find_by_template(request.args)
        response = recommendationResource.construct_response(data,
                                                             request.args,
                                                             request.path,
                                                             request.full_path)
        return Response(json.dumps(response), status=200, content_type='application/json')
    except Exception as e:
        logger.error("Error on /recommendations: ", str(e))
        return Response("Internal Server Error", status=500, content_type='text/plain')


@application.route("/recommendations/<userID>", methods=["GET", "POST"])
def recommendations_userID(userID):
    try:
        if request.method == "GET":
            data = recommendationResource.get_by_id(userID)
            if len(data) == 0:
                return Response(status=404)

            # if we get here, we found a user
            response = {"data": data}
            return Response(json.dumps(response), status=200, content_type='application/json')

        # otherwise we want a post
        elif request.method == "POST":
            body = request.get_json()
            res = recommendationResource.add_recommendation(body)
            return Response(status=201, content_type='text/plain')
    except Exception as e:
        logger.error("Error on /recommendations/<userID>", str(e))
        return Response("Internal Server Error", status=500, content_type='text/plain')

@application.route("/recommendations/<userID>/<movieID>", methods=["GET", "PUT", "DELETE"])
def delete_recommendation(userID, movieID):
    try:
        if request.method == "GET":
            template = {"userID": userID, "movieID": movieID}
            data = recommendationResource.find_by_template(template)
            if len(data) == 0:
                return Response(status=404)

            # if we get here, we found a recommendation
            response = {"data": data}
            return Response(json.dumps(response), status=200, content_type="application/json")
        elif request.method == "PUT":
            updatedRec = request.get_json()
            template = {"userID": updatedRec["userID"], "movieID": updatedRec["movieID"]}
            res = recommendationResource.find_by_template(template)
            if len(res) == 0:
                return Response("Recommendation not found.", status=404, content_type="text/plain")
            else:
                res = recommendationResource.update_rec(updatedRec)
                location = "/recommendations/" + str(updatedRec["userID"]) + "/" + str(updatedRec["movieID"])
                response = {
                    "status": "200",
                    "location": location
                }
                return Response(json.dumps(response), status=200, content_type="application/json")
        elif request.method == "DELETE":
            res = recommendationResource.delete_rec(userID, movieID)
            if res == 0:
                return Response("Recommendation not found.", status=404, content_type="text/plain")
            else:
                return Response("Recommendation deleted.", status=204, content_type="text/plain")
    except Exception as e:
        logger.error("Error: ", str(e))
        return Response("Internal Server Error", status=500, content_type="text/plain")


@application.route("/recommendations/<userID>/swipedYes", methods=["GET"])
def recommendations_swiped(userID):
    try:
        check = recommendationResource.get_by_id(userID)
        if len(check) == 0:
            return Response(status=404, content_type="text/plain")

        # otherwise, user exists, get data we want
        data = recommendationResource.get_by_swiped(userID)
        response = recommendationResource.construct_response(data,
                                                             request.args,
                                                             request.path,
                                                             request.full_path)
        return Response(json.dumps(response), status=200, content_type='application/json')
    except Exception as e:
        logger.error("Error on /recommendations/<userID>/swipedYes", str(e))
        return Response("Internal Server Error", status=500, content_type="text/plain")



if __name__ == '__main__':
    application.run(host="0.0.0.0")
