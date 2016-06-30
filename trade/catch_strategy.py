# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import easytrader
from trade.util import *
from easytrader.MongoDB import *
import time
import types

XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "strategy"
TEST_STATE = False
TEST_NUM = 50
PAGE_DICT = {
    "1": "大股东增持",
    "2": "高送转预期",
    "3": "三一公司价值投资选股",
    "4": "格雷厄姆成长股",
    "5": "低价绩优跌破定增股",
    "6": "MACD金叉股",
    "7": "均线金叉股",
    "8": "跌停板大单买入",
    "9": "日内超跌放量股",
    "10": "涨停板敢死队",
    "11": "组合龙虎榜",
    "12": "情绪宝",
    "18": "一线游资进场",
    "19": "主力盘中连续抢筹",
    "20": "主力洗筹完毕待拉升",
    "21": "前期整理平台放量突破",
    "22": "缩量涨停板",
    "24": "多头趋势回撤点",
}
info = {}
class catch_strategy:
    def __init__(self):
        self.db = MongoDB(XUEQIU_DB_NAME)
        self.logger = get_logger(COLLECTION)
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq1.json')
        self.email = Email()
        self.trade_time = get_date_now("CN")

    def update_name(self):
        for i in range(1, TEST_NUM, 1):
            key = str(i)
            try:
                info_list = self.xq.get_xq_strategy(key)
                print info_list[0]
                time.sleep(5)
            except Exception, e:
                print e

    def main(self):
        while(1):
            if is_trade_time(test=TEST_STATE, trade_time=self.trade_time):
                # try:
                    time.sleep(5)
                    info_list = self.xq.get_xq_strategy("9")
                    for info in info_list:
                        if not self.db.get_doc(COLLECTION, info) and type(info) != types.StringType:
                            for item in info:
                                msg = item + " @" + info[item]["price"] + " :" + info[item]["reason"]
                                record_msg(logger=self.logger, msg=msg)
                            self.db.insert_doc(COLLECTION, info)

                # except Exception, e:
                #     msg = "catch: " + e.message
                #     record_msg(logger=self.logger, msg=msg, email=self.email)
                #
                #     time.sleep(60)
                #     self.xq.autologin()

if __name__ == "__main__":
    e = catch_strategy()
    # e.main()
    e.update_name()
