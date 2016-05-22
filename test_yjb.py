# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import datetime
import logging
import logging.handlers
import sys
import time
import easytrader

TIME = datetime.datetime.now().strftime("%Y-%m-%d")
LOG_FILE = 'logs/' + TIME +'.log'

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

portfolio_list =[
    'ZH000893',#成长投资组合
    'ZH743053',#我爱新能源
]
while(1):
    for p in portfolio_list:
        xq.setattr("portfolio_code", p)
        time.sleep(8)
        position_xq = xq.get_position()
        entrust = xq.get_entrust()
        position_yb = yjb.get_position()
        balance = yjb.get_balance()[0]
        asset = balance["asset_balance"]
    # for e in user.get_balance()[0]:
    #     print e + ": " +str(user.get_balance()[0][e])

    # print "-"*50
    # for e in user.get_entrust():
    #     for i in e:
    #         print i + ": " + str(e[i])
    #     print "*"*50
    #
        # logger.info("-"*50)
        for trade in entrust:
            # logger.info(stock["stock_name"] + ": " + str(stock["percent"]))
            # print type(stock['stock_name'])
            code = str(trade["stock_code"][2:])
            price = trade["business_price"]
            dif = trade['entrust_amount']
            result = ""
            if dif > 0:
                result = yjb.buy(code, price*1.5, volume=asset)
            else:
                result = yjb.sell(code, price*2, volume=-dif*asset)

def is_today(report_time, delta):
    pass