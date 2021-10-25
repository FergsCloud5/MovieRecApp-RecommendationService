import os

class Security():

    def __init__(self):
        self.whiteList = os.environ.get("RECOMMENDATION_")

    def checkWhiteList(self):