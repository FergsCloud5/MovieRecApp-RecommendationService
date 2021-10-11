from application_services.BaseApplicationResource import BaseApplicationResource
from database_services.RDBService import RDBService


class recommendationResource(BaseApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_all(cls):
        return RDBService.get_full_resource("recommendation_service", "recommendations")

    @classmethod
    def get_by_id(cls, id):
        return RDBService.find_by_template("recommendation_service", "recommendations",
                                           {"userID": id})

    @classmethod
    def get_by_swiped(cls, id):
        return RDBService.find_by_template("recommendation_service", "recommendations",
                                           {"userID": id, "swipedYes": 1})

    @classmethod
    def add_recomendation(cls, recommendation):
        return RDBService.create("recommendation_service", "recommendations",
                                 recommendation)
