#-*- coding: utf-8 -*-

"""
Poster: 发布微博。
"""

import sys
sys.path.insert(0, "./lib")

import pickle
import config
from lib.weibopy.auth import OAuthHandler
from lib.weibopy.api import API
from Helper import log

class Poster():

    def __init__(self):
        self.hdl = OAuthHandler(config.APP_KEY, config.APP_SECRET)
        self.api = None
        self.token = {}
        try:
            with open(config.TOKEN_FILE) as f:
                self.token = pickle.load(f)
            log("token init success!")
            log("Access Token is: " + str(self.token))
            self.hdl.setToken(
                self.token["key"],
                self.token["secret"]
            )
            self.api = API(self.hdl)
        except:
            log("Haven't Authorizationed!")
            print "Authorization URL: %s" % self.get_auth_url()
            pin = raw_input("PIN: ")
            self.auth(pin)

    def get_auth_url(self):
        return self.hdl.get_authorization_url()

    def auth(self, pin):
        try:
            token = self.hdl.get_access_token(pin)
            self.api = API(self.hdl)
        except:
            raise Exception("OAuth Failed!")
        self.token.update(dict(key=token.key, secret=token.secret))
        log("Access Token is: " + str(self.token))
        with open(config.TOKEN_FILE, "w") as f:
            pickle.dump(self.token, f)
        log("pickle saved success!")

    def post(self, status):
        try:
            self.api.update_status(status=status)
        except:
            raise Exception("Post Status Failed!")

if __name__ == '__main__':
    poster = Poster()
    poster.post("This is a Test!")
