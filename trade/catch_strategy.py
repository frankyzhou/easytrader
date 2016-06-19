# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import easytrader
from trade.util import *
from easytrader.MongoDB import *

XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "strategy"

db = MongoDB(XUEQIU_DB_NAME)
logger = get_logger(COLLECTION)
user = easytrader.use('xq')
user.prepare('config/xq1.json')

info = {}
while(1):
    try:
        time.sleep(8)
        info_list = user.get_xq_strategy("9")
        for info in info_list:
            if not db.get_doc(COLLECTION, info):
                for item in info:
                    print item + " @" + info[item]["price"] + " :" + info[item]["reason"]
                db.insert_doc(COLLECTION, info)
    except Exception, e:
        print e


