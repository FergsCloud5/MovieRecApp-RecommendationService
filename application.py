import json
import logging

from application_services.recommendationResource import recommendationResource
from flask import Flask, request, Response
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

application  = Flask(__name__)
CORS(application)


@application.before_request
def before_request():
    print("This is the request path:", request.path)
    return

@application.route("/", methods=["GET"])
def home():
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
        return Response(str(e), status=404, content_type='text/plain')
    except Exception as e:
        logger.error("Error on /similarity", str(e))
        return Response(str(e), status=500, content_type='text/plain')



@application.route("/recommendations", methods=["GET"])
def recommendations():
    try:
        #res = recommendationResource.get_all()
        res = recommendationResource.find_by_template(request.args)
        return Response(json.dumps(res), status=200, content_type='application/json')
    except Exception as e:
        logger.error("Error on /recommendations: ", str(e))
        return Response(str(e), status=500, content_type='text/plain')


@application.route("/recommendations/<userID>", methods=["GET", "POST"])
def recommendations_userID(userID):
    try:
        if request.method == "GET":
            res = recommendationResource.get_by_id(userID)
            if len(res) == 0:
                return Response("User not found", status=404, content_type='text/plain')

            # if we get here, we found a user
            return Response(json.dumps(res), status=200, content_type='application/json')

        # otherwise we want a post
        elif request.method == "POST":
            body = request.get_json()
            res = recommendationResource.add_recommendation(body)
            return Response("Created!", status=201, content_type='text/plain')
    except Exception as e:
        logger.error("Error on /recommendations/<userID>", str(e))
        return Response(str(e), status=400, content_type='text/plain')


@application.route("/recommendations/<userID>/swipedYes", methods=["GET"])
def recommendations_swiped(userID):
    try:
        check = recommendationResource.get_by_id(userID)
        if len(check) == 0:
            return Response("User not found.", status=404, content_type="text/plain")

        # otherwise, user exists, get data we want
        res = recommendationResource.get_by_swiped(userID)
        return Response(json.dumps(res), status=200, content_type='application/json')
    except Exception as e:
        logger.error("Error on /recommendations/<userID>/swipedYes", str(e))
        return Response(str(e), status=500, content_type="text/plain")



if __name__ == '__main__':
    application.run(host="0.0.0.0")
