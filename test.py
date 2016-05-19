# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import easytrader
import time
import datetime
import logging
import logging.handlers
import sys
sys.path.append("..")


TIME = datetime.datetime.now().strftime("%Y-%m-%d")
LOG_FILE = 'logs/' + TIME +'.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler
fmt = '%(asctime)s -  %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter

logger = logging.getLogger('tst')    # 获取名为tst的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.DEBUG)

# user = easytrader.use('xq')
# user.prepare('xq.json')
#
# user.setattr("portfolio_code", "ZH776826")
#
# portfolio_list =[
#     'ZH776826',
#     'ZH743053',
#     'ZH796463'
# ]
# while(1):
#     for p in portfolio_list:
#         user.setattr("portfolio_code", p)
#         time.sleep(8)
#         position = user.get_position()
#     # for e in user.get_balance()[0]:
#     #     print e + ": " +str(user.get_balance()[0][e])
#
#     # print "-"*50
#     # for e in user.get_entrust():
#     #     for i in e:
#     #         print i + ": " + str(e[i])
#     #     print "*"*50
#
#         logger.info("-"*50)
#         for stock in position:
#             logger.info(stock["stock_name"] + ": " + str(stock["percent"]))

