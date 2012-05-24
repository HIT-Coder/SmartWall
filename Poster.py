#-*- coding: utf-8 -*-

"""
Poster: 发布微博。
"""

import sys
sys.path.insert(0, "./lib")
sys.stderr = sys.stdout

import re
import pickle
import urllib2
from time import sleep

import config
from lib.weibopy.auth import OAuthHandler
from lib.weibopy.api import API
import Helper

log = Helper.log

USER_URL_FORMAT = "http://weibo.cn/%s/info?vt=4&wm=ig_0001_index&gsid=%s"

class Poster():

    def __init__(self):
        self.hdl = OAuthHandler(config.APP_KEY, config.APP_SECRET)
        self.api = None
        self.token = {}
        self.last_post_time = self.get_last_post_time()
        log("Last Post Time: %s" % self.last_post_time)
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
        try:
            with open(".gsid") as f:
                self.gsid = f.read().rstrip()
        except:
            raise Exception("Haven't Got GSID!")

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

    def post_status(self, status):
        try:
            self.api.update_status(status=status)
        except:
            #raise Exception("Post Status Failed!")
            log("Post Status:%s Failed!" % status)
            raise
        else:
            log("Post Status:%s Success!" % status)

    def run(self):
        """
        status = Helper.get_status(self.last_post_time)
        log("Total %d Status" % len(status))
        if len(status) == 0:
            log("Already Up to Date!")
        else:
            for item in status:
                gender,school,message = item[:-1]
                msg = "%s" % (message,)
                self.post_status(msg)
                sleep(5)
        """
        self.get_usercommand()

    def get_user_info(self, screen_name):
        try:
            user = {}
            ret = self.api.get_user(screen_name=screen_name)
            user_id = ret.id
            gender = ret.gender
            url = USER_URL_FORMAT % (user_id, self.gsid)
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0')
            html = urllib2.urlopen(request).read()
            if re.search(r'哈尔滨工业大学|哈工大（威海）|哈工大\(威海\)', html):
                school = '哈工大'
            elif re.search(r'山东大学|山大（威海）|山大\(威海\)', html):
                school = '山大'
            else:
                school = '未知'
            user.update(dict(id=user_id, name=screen_name, sex=gender, school=school))
            return user
        except:
            log("Exception Caught Here.User: %s" % screen_name)

    def get_usercommand(self):
        self.last_at_time = self.get_last_at_time()
        log("LAST_AT_TIME:%s" % self.last_at_time)
        self.last_at_time = Helper.str2date(self.last_at_time)
        try:
            list = self.api.mentions(5) #TODO: 5不靠谱.
            for listat in list:
                if listat.created_at>self.last_at_time:
                    if "zf@0904201".decode("utf-8") in listat.text:
                        log("ReceiveCommand %s From %s!" % \
                            (listat.user.name, "zf"))
                        Helper.add_command_log(listat.user.name, "zf", listat.text, str(listat.created_at))
                        try:
                            retid = listat.retweeted_status.id
                        except:
                            retid = listat.id
                        self.repost_message(retid)
                    else:
                        log("ReceiveUnknownCommand.Text:%s" % listat.text)
                else:
                    log("Break Loop at %s" % str(listat.created_at))
                    break
        except:
            log("Get User Command Except Exception!")
            raise
        Helper.refresh_at_time()
        
    def repost_message(self, repid):
        try:
            self.api.repost(id=repid)
        except:
            log("Repost Failed.REPOST_ID:%s" % repid)
        else:
            log("Repost Success.REPOST_ID:%s" % repid)

    def get_last_post_time(self):
        return Helper.get_app_value('post_time')

    def set_last_post_time(self, last_post_time):
        Helper.set_app_value('post_time', last_post_time)

    def get_last_at_time(self):
        return Helper.get_app_value('at_time')

    def set_last_at_time(self, last_at_time):
        Helper.set_app_value('at_time', last_at_time)

if __name__ == '__main__':
    poster = Poster()
    poster.run()
