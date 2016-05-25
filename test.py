# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import datetime
import logging
import logging.handlers
import pymongo
import easytrader
import time

from easytrader import MongoDB as DB

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

dbclient = DB.getDB()
db = dbclient[XUEQIU_DB_NAME]


while(1):
    time.sleep(10)
    info_list = user.get_xq_strategy("9")
    for info in info_list:
        if not DB.get_doc(db, COLLECTION, info):
            logger.info("-"*50)
            logger.info("update new message!")
            DB.insert_doc(db, COLLECTION, info)
    # for p in portfolio_list:
    #     user.setattr("portfolio_code", p)
    #     time.sleep(8)
    #     position = user.get_position()
    # for e in user.get_balance()[0]:
    #     print e + ": " +str(user.get_balance()[0][e])

    # print "-"*50
    # for e in user.get_entrust():
    #     for i in e:
    #         print i + ": " + str(e[i])
    #     print "*"*50

        # logger.info("-"*50)
        # for stock in position:
        #     logger.info(stock["stock_name"] + ": " + str(stock["percent"]))

