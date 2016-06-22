# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import easytrader
from trade.util import *
from easytrader.MongoDB import *
import time
XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "strategy"

db = MongoDB(XUEQIU_DB_NAME)
logger = get_logger(COLLECTION)
xq = easytrader.use('xq')
xq.prepare('config/xq1.json')
email = Email()

info = {}
while(1):
    try:
        time.sleep(5)
        info_list = xq.get_xq_strategy("9")
        for info in info_list:
            if not db.get_doc(COLLECTION, info):
                for item in info:
                    print item + " @" + info[item]["price"] + " :" + info[item]["reason"]
                db.insert_doc(COLLECTION, info)
    except Exception, e:
        msg = "catch: " + e.message
        record_msg(logger=logger, msg=msg, email=email)

        time.sleep(60)
        xq.autologin()


