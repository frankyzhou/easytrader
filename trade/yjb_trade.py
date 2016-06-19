# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'

import easytrader
from trade.util import *

# declare basic vars
TEST_STATE = True
GET_POSITION = "get_position"
BUY = "buy"
READ_SIZE = 8192

class yjb_trade:
    def __init__(self):
        self.yjb = easytrader.use('yjb')
        self.yjb.prepare('config/yjb.json')
        self.server = get_server()

    def judge_opera(self, msg):
        msg = msg.split()
        type = msg[0]
        if type == GET_POSITION:
            return self.get_position_by_stock(msg[1])
        elif type == BUY:
            code, price, amount = msg[1], msg[2], msg[3]
            result = self.yjb.buy(stock_code=code, price=price, amount=amount)

    def get_position_by_stock(self, code):
        position_yjb = self.yjb.get_position()
        balance = self.yjb.get_balance()[0]
        asset = balance["asset_balance"]
        return self.yjb.get_position_by_stock(code, position_yjb, asset)

    def main(self):
        while(1):
            try:
                message, address = self.server.recvfrom(READ_SIZE)
                print "Got data from ", address

                self.server.sendto("Data is received succeefully.", address)
                print message

            except (KeyboardInterrupt, SystemExit):
                print "raise"
                raise
            except :
                print "traceback"
                traceback.print_exc()

if __name__ == '__main__':
    yjb = yjb_trade()
    yjb.main()
