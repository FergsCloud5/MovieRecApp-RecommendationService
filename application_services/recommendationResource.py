import os
import pandas as pd

from application_services.BaseApplicationResource import BaseApplicationResource
from database_services.RDBService import RDBService
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# defining global constants SQL access
REC_SCHEMA = "recommendation_service"
REC_TABLE  = "recommendations"

def create_similarity():
    here = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(here, "../main_data.csv")
    data = pd.read_csv(data_file)
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix)
    return data, similarity


class recommendationResource(BaseApplicationResource):
    data, similarity = create_similarity()

    def __init__(self):
        super().__init__()

    @classmethod
    def recommend_by_title(cls, movieTitle):
        movieTitle = movieTitle.lower()
        if movieTitle not in cls.data['movie_title'].unique():
            raise LookupError("Cannot find a movie matching this title, try again.")
        else:
            i = cls.data.loc[cls.data['movie_title'] == movieTitle].index[0]
            lst = list(enumerate(cls.similarity[i]))
            lst = sorted(lst, key=lambda x: x[1], reverse=True)
            orig_index = lst[0][0]
            lst = lst[1:11]  # excluding first item since it is the requested movie itself
            l = []
            for i in range(len(lst)):
                a = lst[i][0]
                l.append({'movieTitle': cls.data['movie_title'][a],
                          'movieID': cls.data['movie_id'][a]})

            return {'movie': movieTitle,
                    'movieID': cls.data['movie_id'][orig_index],
                    'recommendations': l}

    @classmethod
    def recommend_by_id(cls, movieID):
        if movieID not in cls.data['movie_id'].unique():
            raise LookupError("Cannot find a movie matching this id, try again.")
        else:
            i = cls.data.loc[cls.data['movie_id'] == movieID].index[0]
            lst = list(enumerate(cls.similarity[i]))
            lst = sorted(lst, key=lambda x: x[1], reverse=True)
            orig_index = lst[0][0]
            lst = lst[1:11]  # excluding first item since it is the requested movie itself
            l = []
            for i in range(len(lst)):
                a = lst[i][0]
                l.append({'movieTitle': cls.data['movie_title'][a],
                          'movieID': cls.data['movie_id'][a]})

            return {'movie': cls.data['movie_title'][orig_index],
                    'movieID': movieID,
                    'recommendations': l}

    @classmethod
    def get_all(cls):
        return RDBService.get_full_resource(REC_SCHEMA, REC_TABLE)

    @classmethod
    def get_by_id(cls, id):
        return RDBService.find_by_template(REC_SCHEMA, REC_TABLE,
                                           {"userID": id})

    @classmethod
    def get_by_swiped(cls, id):
        return RDBService.find_by_template(REC_SCHEMA, REC_TABLE,
                                           {"userID": id, "swipedYes": 1})

    @classmethod
    def add_recomendation(cls, recommendation):
        return RDBService.create(REC_SCHEMA, REC_TABLE,
                                 recommendation)

    @classmethod
    def find_by_template(cls, template):
        return RDBService.find_by_template(REC_SCHEMA, REC_TABLE, template)
