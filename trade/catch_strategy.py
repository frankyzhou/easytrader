# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import easytrader
from trade.util import *
from easytrader.MongoDB import *
import time
XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "strategy"
TEST_STATE = False

info = {}
class catch_strategy:
    def __init__(self):
        self.db = MongoDB(XUEQIU_DB_NAME)
        self.logger = get_logger(COLLECTION)
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq1.json')
        self.email = Email()
        self.trade_time = get_date_now("CN")

    def main(self):

        while(1):
            if is_trade_time(test=TEST_STATE, trade_time=self.trade_time):
                try:
                    time.sleep(5)
                    info_list = self.xq.get_xq_strategy("9")
                    for info in info_list:
                        if not self.db.get_doc(COLLECTION, info):
                            for item in info:
                                print item + " @" + info[item]["price"] + " :" + info[item]["reason"]
                            self.db.insert_doc(COLLECTION, info)

                except Exception, e:
                    msg = "catch: " + e.message
                    record_msg(logger=self.logger, msg=msg, email=self.email)

                    time.sleep(60)
                    self.xq.autologin()

if __name__ == "__main__":
    e = catch_strategy()
    e.main()

