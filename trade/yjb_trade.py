# -*- coding: utf-8 -*-
from easytrader import helpers
import easytrader
from trade.util import *
from cn_trade import *
import time

__author__ = 'frankyzhou'

# declare basic vars
COLLECTION = "yjb_operation"
GET_POSITION = "get_position"
BUY = "buy"
SELL = "sell"
STOP = "stop"
READ_SIZE = 8192


class YjbTrade(CNTrade):
    def __init__(self):
        # 固定部分
        self.yjb = easytrader.use('yjb')
        self.yjb.prepare('config/yjb.json')
        self.server = get_server()
        self.logger = get_logger(COLLECTION)
        # 每日更新
        self.last_trade_time = get_trade_date_series("CN")
        self.trade_time = get_date_now("CN")

    def judge_opera(self, msg):
        msg = msg.split()
        type= msg[0]

        if type == STOP:
            return STOP

        code = msg[1]
        if type == GET_POSITION:
            record_msg(logger=self.logger, msg="查询仓位：" + code)
            return self.get_position_by_stock(code)

        price, amount = msg[2], msg[3]
        if type == BUY:
            record_msg(logger=self.logger, msg="买入：" + code)
            return self.yjb.buy(stock_code=code, price=price, amount=amount)
        elif type == SELL:
            record_msg(logger=self.logger, msg="卖出：" + code)
            return self.yjb.sell(stock_code=code, price=price, amount=amount)

        return "Nothing."

    def get_position_by_stock(self, code):
        position_yjb = self.yjb.get_position()
        while not isinstance(position_yjb, list):
            self.yjb.autologin()
            time.sleep(5)
            record_msg(logger=self.logger, msg="获取持仓失败，重连中")
            position_yjb = self.yjb.get_position()
        balance = self.yjb.get_balance()[0]
        asset = balance["asset_balance"]
        return self.yjb.get_position_by_stock(code, position_yjb, asset), asset

    def main(self):
        while 1:
            #try:
                request, address = self.server.recvfrom(READ_SIZE)
                print "Got data from ", address

                response = self.judge_opera(request)
                self.server.sendto(str(response), address)
                if str(response) == STOP:
                    break
            #except Exception, e:
            #    print e

if __name__ == '__main__':
    yjb = YjbTrade()
    yjb.main()
