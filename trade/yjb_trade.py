# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'

import easytrader
from trade.util import *

# declare basic vars
GET_POSITION = "get_position"
BUY = "buy"
SELL = "sell"
READ_SIZE = 8192


class yjb_trade:
    def __init__(self):
        self.yjb = easytrader.use('yjb')
        self.yjb.prepare('config/yjb.json')
        self.server = get_server()

    def judge_opera(self, msg):
        msg = msg.split()
        type, code = msg[0], msg[1]
        if type == GET_POSITION:
            #return self.get_position_by_stock(code)
            p = str(self.yjb.get_position()).replace('(', '[').replace(')', ']').replace('\'', '"')
            p1 = json_load_byteified(p)
            return self.yjb.get_position()

        price, amount = msg[2], msg[3]
        if type == BUY:
            return self.yjb.buy(stock_code=code, price=price, amount=amount)
        elif type == SELL:
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
    yjb = yjb_trade()
    yjb.judge_opera(msg="get_position all")
    yjb.main()
