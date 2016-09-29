# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'

import easytrader
from trade.util import *
from cn_trade import *
# declare basic vars
COLLECTION = "yjb_operation"
GET_POSITION = "get_position"
BUY = "buy"
SELL = "sell"
READ_SIZE = 8192


class YjbTrade(CNTrade):
    def __init__(self):
        self.yjb = easytrader.use('yjb')
        self.yjb.prepare('config/yjb.json')
        self.server = get_server()
        self.logger = get_logger(COLLECTION)

    def judge_opera(self, msg):
        msg = msg.split()
        type, code = msg[0], msg[1]
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
        balance = self.yjb.get_balance()[0]
        asset = balance["asset_balance"]
        return self.yjb.get_position_by_stock(code, position_yjb, asset), asset

    def main(self):
        while(1):
            #try:
                request, address = self.server.recvfrom(READ_SIZE)
                print "Got data from ", address

                response = self.judge_opera(request)
                self.server.sendto(str(response), address)

            #except Exception, e:
            #    print e

if __name__ == '__main__':
    yjb = YjbTrade()
    yjb.main()
