import os
import json
from flask_dance.contrib.google import make_google_blueprint, google
from middleware.context import get_google_info


class Security:

    def __init__(self):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        wl_file = open(dir_path + "/white_list.json")
        self.white_list = json.load(wl_file)
        self.login_path = "/"

    def get_google_blueprint(self):
        google_id, google_secret = get_google_info()
        return make_google_blueprint(
            client_id=google_id,
            client_secret=google_secret,
            scope=['profile', 'email']
        )

    def check_whitelist(self, path):
        """
        Returns True is request.path is a white list path.
        Returns False if the request.path requires login.
        TODO: GENERALIZE THE PATH WITH <MOVIE_ID> ADD TO WHITE LIST
        TODO: WITH REGEX.
        """
        if path not in self.white_list.keys():
            return False
        return True

    def is_authorized(self):
        if not google.authorized:
            return False
        return True

    def check_authentication(self, path):

        if self.check_whitelist(path):
            print("whitelist")

            return 200, "", ""
        else:
            print("blacklist")
            if self.is_authorized():
                return 200, "", ""

            return 401, path, "UNAUTHORIZED"
