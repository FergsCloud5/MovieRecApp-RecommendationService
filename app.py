import database_services.RDBService as d_service
import json
import os
import pandas as pd

from application_services.imdb_artists_resource import IMDBArtistResource
from application_services.recommendation_service import recommendationResource
from middleware.context import get_db_info
from flask import Flask, render_template, request, Response
from flask_cors import CORS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def create_similarity():
    here = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(here, "main_data.csv")
    data = pd.read_csv(data_file)
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix)
    return data,similarity

def rcmd(m):
    m = m.lower()
    try:
        data.head()
        similarity.shape
    except:
        data, similarity = create_similarity()
    if m not in data['movie_title'].unique():
        return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    else:
        i = data.loc[data['movie_title']==m].index[0]
        lst = list(enumerate(similarity[i]))
        lst = sorted(lst, key=lambda x:x[1], reverse=True)
        lst = lst[1:11] # excluding first item since it is the requested movie itself
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        return l

# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

def get_suggestions():
    here = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(here, "main_data.csv")
    data = pd.read_csv(data_file)
    return list(data['movie_title'].str.capitalize())

app = Flask(__name__)
CORS(app)

@app.route("/similarity", methods=["GET"])
def similarity():
    movie = request.form['name']
    rc = rcmd(movie)
    if type(rc)==type('string'):
        return rc
    else:
        m_str="---".join(rc)
        return m_str

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
            rsp = Response("Created!", status=201, content_type='application/json')
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
