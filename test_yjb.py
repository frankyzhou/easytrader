# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import datetime
import logging
import logging.handlers
import sys
import time
import easytrader
import pymongo
from easytrader import MongoDB as DB

XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "history_operation"

TIME = datetime.datetime.now().strftime("%Y-%m-%d")
LOG_FILE = 'logs/' + TIME + COLLECTION +'.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler
fmt = '%(asctime)s -  %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter

logger = logging.getLogger('tst')    # 获取名为tst的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.DEBUG)

xq = easytrader.use('xq')
xq.prepare('xq.json')
xq.setattr("portfolio_code", "ZH776826")
yjb = easytrader.use('yjb')
yjb.prepare('yjb.json')

portfolio_list ={
    'ZH000893':0.5,#成长投资组合
    'ZH743053':0.5,#我爱新能源
}

dbclient = DB.getDB()
db = dbclient[XUEQIU_DB_NAME]

def is_today(report_time):
    report_time = datetime.datetime.strptime(report_time,"%Y-%m-%d %H:%M:%S")
    now_time = datetime.datetime.now()
    if now_time < report_time + datetime.timedelta(days=1):
        return True
    else:
        return False

while(1):
    for k in portfolio_list.keys():
        xq.setattr("portfolio_code", k)
        time.sleep(8)
        position_xq = xq.get_position()
        entrust = xq.get_entrust()
        position_yb = yjb.get_position()
        balance = yjb.get_balance()[0]
        asset = balance["asset_balance"]

        for trade in entrust:
            if not is_today(trade["report_time"]):
                break
            else:
                trade["portfolio"] = k
                if not DB.get_doc(db, COLLECTION, trade):
                    logger.info("-"*50)
                    logger.info(k + " update new operaion!")
                    code = str(trade["stock_code"][2:])
                    price = trade["business_price"]
                    dif = trade['entrust_amount']
                    result = ""
                    volume = dif*asset*portfolio_list[k]
                    if dif > 0:
                        result = yjb.buy(code, price, volume= volume)
                        logger.info("买入 "+code+" @ " + str(price) + " 共 " + str(volume))
                    else:
                        result = yjb.sell(code, price, volume= -volume)
                        logger.info("买入 "+code+" @ " + str(price) + " 共 " + str(-volume))
                    out = ""
                    for key in result.keys():
                        out = out + key + " : " + result[key] + " "
                    logger.info(out)
                    DB.insert_doc(db, COLLECTION, trade)

