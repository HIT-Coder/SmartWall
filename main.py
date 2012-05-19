#-*- coding: utf-8 -*-


"""
启动脚本
    start 启动 crontab
    stop  删除 crontab

"""

from Helper import log

# 获取启动参数
import sys, os
try:
    if sys.argv[1] == 'stop':
        os.system("crontab -r")
        log("rm all the crontab")
        exit(0)
except IndexError:
    pass
except SystemExit:
    raise

cnt_path = os.path.dirname(os.getcwd() + "/" + sys.argv[0])

SPIDER_FILE = "Spider.py"
POSTER_FILE = "Poster.py"
SPIDER_LOG  = "spider.log"
POSTER_LOG  = "poster.log"

SPIDER_CRON = "*/1 * * * * cd %s && python %s>>%s\n" % (cnt_path, SPIDER_FILE, SPIDER_LOG)
POSTER_CRON = "*/1 * * * * cd %s && python %s>>%s\n" % (cnt_path, POSTER_FILE, POSTER_LOG)

with open("cron_file", "w") as f:
    f.write(SPIDER_CRON)
    f.write(POSTER_CRON)
    log("cron file has been made!")

os.system("crontab cron_file")
