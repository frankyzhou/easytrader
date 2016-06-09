# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import datetime
import logging
import logging.handlers
import pymongo
import easytrader
import time

from easytrader.MongoDB import *

XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "strategy"

TIME = datetime.datetime.now().strftime("%Y-%m-%d")
LOG_FILE = 'logs/' + TIME + COLLECTION +'.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler
fmt = '%(asctime)s -  %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter

logger = logging.getLogger('tst')    # 获取名为tst的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.DEBUG)

user = easytrader.use('xq')
user.prepare('xq.json')

user.setattr("portfolio_code", "ZH776826")

portfolio_list =[
    'ZH776826',
    'ZH743053',
    'ZH796463'
]
info = {}

##dbclient = DB.getDB()
db = MongoDB(XUEQIU_DB_NAME)

while(1):
    try:
        time.sleep(8)
        info_list = user.get_xq_strategy("9")
        for info in info_list:
            if not db.get_doc(COLLECTION, info):
                logger.info("-"*50)
                logger.info("update new message!")
                for item in info:
                    print item + " @" + info[item]["price"] + " :" + info[item]["reason"]
                db.insert_doc(COLLECTION, info)
    except Exception, e:
        print e


