# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import datetime
import logging
import logging.handlers
import time
import easytrader
from easytrader import MongoDB as DB

XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "history_operation"
factor = 1

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
    'ZH000893':0.4,#成长投资组合
    'ZH743053':0.4,#我爱新能源
    'ZH016097':0.2,#绝对模拟
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

def get_position_by_stock(stockcode, position_yjb, asset):
    for e in position_yjb:
        if e["stock_code"] == stockcode:
            return e["market_value"]/asset
    return 0

def get_xq_entrust_checked(xq):
    entrust = None
    done = True
    while(not (entrust and done)):
        entrust = xq.get_entrust()
        for trade in entrust:
            if not is_today(trade["report_time"]):
                break
            if len(trade) !=12:
                done = False
                break
            else:
                for e in trade.keys():
                    if trade[e] is None:
                        done = False
                        break
    return entrust





while(1):
    for k in portfolio_list.keys():
        xq.setattr("portfolio_code", k)
        time.sleep(8)
        # position_xq = xq.get_position()
        entrust = get_xq_entrust_checked(xq)

        position_yjb = yjb.get_position()

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
                    # dif = trade['entrust_amount']/100
                    target_percent = trade["target_weight"] * portfolio_list[k] /100 if trade["target_weight"] > 2.0 else 0.0
                    before_percent = get_position_by_stock(code, position_yjb, asset)
                    dif = target_percent - before_percent
                    result = ""
                    volume = dif*asset

                    if dif > 0:
                        result = yjb.buy(code, price*factor, volume= volume)
                        logger.info("买入 "+code+" @ " + str(price*factor) + " 共 " + str(volume))
                    else:
                        result = yjb.sell(code, price/factor, volume= -volume)
                        logger.info("卖出 "+code+" @ " + str(price/factor) + " 共 " + str(-volume))

                    out = ""
                    for key in result.keys():
                        out = out + str(key) + " : " + str(result[key]) + " "
                    logger.info(out)

                    DB.insert_doc(db, COLLECTION, trade)

